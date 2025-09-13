# Parser Service Architecture

This document describes the proposed architecture for the parser service, the most complex part of the app.
This architecture covers the work to be done during MVP 1 to 3 (see README for Roadmap).

## Data Flow
  - The overall data flow is structured around 5 main steps: `get_processor`, the input manager; `FileProcessor` (e.g. `SummaryDataV2Processor`), the orchestrator; `TableDiagnosticsEngine`, the table-level diagnostics engine; `SheetDiagnosticsEngine`, the sheet-level diagnostics engine; `CleaningService`, the fixer.
  ### `get_processor`
  - Initiation : A file path for an EITI summary data file is passed to the main `get_processor` function.
  - Selection The factory tests the file against all registered `FileProcessors`. It selects `SummaryDataV2Processor` because its `can_handle` method returns `True`.
  ### `SummaryDataV2Processor`
  - Verification ✓: The processor reads the file, confirming it has the expected structure (e.g., required sheets are present).
  - Delegation to table-level `DiagnosticEngine` : The processor iterates through its internal configuration map. For each configured sheet (e.g., `"2_Economic contribution"`), it deploys the corresponding list of `DiagnosticEngine` (`TableDiagnosticsEngine`) instances, passing the full sheet DataFrame to each one and calling their standardized run() method.
  - Inspection : As each `TableDiagnosticsEngine` completes its work, the `SummaryDataV2Processor` collects the individual result dictionaries and inspects the status of the errors.
  - Routing : For each error, it calls `cleaning_service.can_fix(error.error_code)`:
    - If `Status.PASSED` (no errors): The data is clean. It proceeds directly to the final aggregation step.
    - If `Status.NEEDS_REPAIR` (all errors returned `True` from `can_fix`): The report contains fixable errors. The processor sends the `DiagnosticsReport` to the `CleaningService`.
    - If `Status.FAILED` (one or more errors returned `False` from `can_fix`): it halts processing for this table and logs the unfixable errors in the `UserReport`.
  - Delegation to sheet-level `DiagnosticEngine` : After all `TableDiagnosticsEngine` instances are done, it calls on the sheet-level `DiagnosticEngine` (`SheetDiagnosticsEngine`) using its standardized `run()` method, passing along the coordinates gathered from the `TableDiagnosticsEngine` instances.
  - Aggregation : `SummaryDataV2Processor` generates a comprehensive `UserReport` for the entire file based on the results of the inspection, the routing and the sheet-level diagnostics.
  ### `TableDiagnosticsEngine`
  - Location : The `TableDiagnosticsEngine` receives a full sheet DataFrame. Using its configured anchor (e.g., `"Requirement_3_1"`), it scans the sheet to find the boundaries of its target table.
  - Extraction : The `TableDiagnosticsEngine` uses the identified boundaries to slice and extract its target table into a new, clean DataFrame.
  - Validation : It executes its pre-configured validation chain on the clean table DataFrame to check structure, data types, and business rules.
    - Success Scenario Flow
      - The `TableDiagnosticsEngine` calls the first step (`StructureValidator`) with the clean table DataFrame and the `context` dictionary.
      - The `StructureValidator` runs, finds all columns are present, and makes no changes to the `context`. It then calls the next step in the chain (`DataTypeValidator`), passing the DataFrame and the same `context` dictionary forward.
      - The `DataTypeValidator` runs. For each row that passes validation against the Pydantic model, it adds the cleaned row data to the `context["valid_rows"]` list. If any row fails, it adds a descriptive error to `context["errors"]`.
      - When the final step in the chain is complete, it returns the final, modified `context` dictionary back to the `TableDiagnosticsEngine`.
    - Failure Scenario Flow
      - The `TableDiagnosticsEngine` calls the `StructureValidator` with the clean table and the initial `context`.
      - The `StructureValidator` discovers a required column is missing.
      - It adds a detailed error message to `context["errors"]` and sets `context["is_fatal"] = True`.
      - The base `ValidationStep`'s `handle` method checks this `is_fatal` flag. Because it is `True`, it stops the chain immediately. It does not call the `DataTypeValidator`.
      - It returns the `context` dictionary (now containing the fatal error) directly to the `TableDiagnosticsEngine`.
  - Reporting : It returns a `DiagnosticsReport` containing table coordinates, the clean dataframe, a list of structured `ValidationError` objects, and an overall status (PASSED, NEEDS_REPAIR, FAILED) back to the `SummaryDataV2Processor` for aggregation.
  ### `SheetDiagnosticsEngine`
  - Container Diagnostics : Receives a full sheet DataFrame and the coordinates of all known tables on that sheet. It performs checks like:
    - Finding any data in cells outside the known table boundaries.
    - Extracting specific metadata that might be in fixed cells (e.g., a report author's name).
    - Checking for other sheet-level anomalies.
  - Reporting : It returns a list of sheet-level findings (errors, warnings, or extracted metadata) to the `SummaryDataV2Processor`.
  ### `CleaningService`
  - Communicate : The service exposes a method, `can_fix(error_code: ErrorCode) -> bool` that checks an internal registry to see if a tool exists to fix that specific type of error.
  - Plan : The `CleaningService` receives the `DiagnosticsReport`. It iterates through the list of errors and, based on the `ErrorCode` values, define a `RepairPlan` which lists which fixing functions should be called and in what order.
  - Repair : The `CleaningService` passes the `RepairPlan` to its internal method which calls the fixing functions in order.
  - Logging : The `CleaningService` returns a `RemediationResult` to the `SummaryDataV2Processor`, which includes:
    - The repaired DataFrame.
    - A log of all actions taken (e.g., "Added missing column 'Country'").
  ### Schema
  ```mermaid
  sequenceDiagram
      actor User
      participant get_processor as get_processor()
      participant SummaryDataV2Processor as FileProcessor
      participant TableDiagnosticsEngine as Table Diagnostics
      participant SheetDiagnosticsEngine as Sheet Diagnostics
      participant CleaningService as Fixer

      User->>get_processor: process_file("path/to/eiti.xlsx")

      %% -- Phase 1: Selection --
      get_processor->>SummaryDataV2Processor: can_handle(path)?
      SummaryDataV2Processor-->>get_processor: True
      get_processor->>User: Returns instance of FileProcessor

      %% -- Phase 2: Orchestration & Table Diagnostics --
      User->>SummaryDataV2Processor: process()
      SummaryDataV2Processor->>TableDiagnosticsEngine: process_sheet(sheet_df)

      activate TableDiagnosticsEngine
      TableDiagnosticsEngine-->>SummaryDataV2Processor: Returns DiagnosticsReport
      deactivate TableDiagnosticsEngine

      %% -- Phase 3: Decision & Remediation --
      SummaryDataV2Processor->>CleaningService: can_fix(ErrorCode)?
      CleaningService-->>SummaryDataV2Processor: Returns True/False

      alt All Table Errors are Fixable
          SummaryDataV2Processor->>CleaningService: repair(DiagnosticsReport)
          activate CleaningService
          CleaningService-->>SummaryDataV2Processor: Returns RemediationResult
          deactivate CleaningService
      else Some Table Errors are Unfixable
          SummaryDataV2Processor->>SummaryDataV2Processor: Log errors for manual review
      end

      %% -- Phase 4: Sheet Diagnostics & Finalization --
      SummaryDataV2Processor->>SheetDiagnosticsEngine: check_sheet(sheet_df, all_coords)
      activate SheetDiagnosticsEngine
      SheetDiagnosticsEngine-->>SummaryDataV2Processor: Returns SheetFindings
      deactivate SheetDiagnosticsEngine

      SummaryDataV2Processor->>SummaryDataV2Processor: Aggregation
      SummaryDataV2Processor-->>User: Returns final UserReport
  ```

## Cookbook for Future Changes

  ### Scenario 1: Our Understanding of Data Errors Evolves
  As new error patterns and heuristics are discovered, the system's diagnostic capabilities will need to be refined.
  1. Updating an Existing Validation Step (Adding a Heuristic)
      - We will do this when we want to make an existing check smarter. For example, making the `StructureValidator` detect shifted columns.
      - Locate the Validator: Open the relevant `ValidationStep` class (e.g., `StructureValidator`).
      - Add the Heuristic: the new logic should be added inside its `process` method. For example, if the initial check for required columns fails, add a secondary check that looks for column names with high string similarity in adjacent cells.
      - Create a Specific `ErrorCode`: If the heuristic finds a match, generate a new, highly specific `ErrorCode` (e.g., `COLUMN_SHIFT_DETECTED`). This provides a clear signal for the `CleaningService`.

  2. Adding a New Validation Step
      - When a completely new category of error is identified, like a foreign language alias.
      - Create the New Validator: Create a new class that inherits from `ValidationStep` (e.g., `ColumnAliasValidator`). This class will contain the logic to check for known aliases and generate its own `ErrorCode` (e.g., `KNOWN_ALIAS_FOUND`).
      - Update the `TableSchema`: In the configuration file, add the new `ColumnAliasValidator` to the validation chain for the tables where the check needs to be run. This "activates" the new step.

  3. Enabling an Automatic Fix for an Error
      - Once a `ValidationStep` is found that can reliably identify an error with a unique `ErrorCode`, a new automatic fix can be enabled.
      - `CleaningService`: This is the only component that needs to be modified.
        - Add the Tool: Create a new private method that contains the fixing logic (e.g., `_rename_aliased_columns(...)`).
        - Register the Tool: Update the service's internal registry so its `can_fix(ErrorCode)` method returns `True` for the new `ErrorCode`.
        - Update the Dispatcher: Add logic to the main `repair` method to call the new tool when it sees that `ErrorCode`.

  ### Scenario 2: We Want to Do More with the Results
  After the initial diagnostics and repairs, we may want to add more layers of processing or integration.
  1. Adding a Sheet-Level Validation Check (Container Rules)
      - For rules that apply to a whole sheet but are outside any specific table. Useful for dealing with edge cases.
      - `SheetDiagnosticsEngine`: Steps
        - Add a new method to the `SheetDiagnosticsEngine` class that contains the new heuristic (e.g., `extract_report_author(...)`).
        - Ensure this method returns a structured finding (error, warning, or data).
        - The `SummaryDataV2Processor` will automatically call this new check as part of its "Sheet-Level Diagnostics" step.

  2. Integrating a Manual Fix UI or sending the file for further processing.
      - This change is isolated entirely to the central orchestrator.
      - `SummaryDataV2Processor`: Modify the `Routing` step. When the `CleaningService.can_fix()` check returns `False`, instead of just logging to the `UserReport`, add the code to make an API call or write the `DiagnosticsReport` to a database queue that the new service monitors.

  3. Adding a File-Level Validation Check
      - This is for checks that span multiple tables, like cross-table consistency.
      - `SummaryDataV2Processor`: This is the correct place for file-level logic. After it has collected all the clean and repaired data from every table, add a final validation method inside the processor itself (e.g., `_run_cross_table_checks(...)`) before it generates the final `UserReport`.

  4. Adding a New Kind of Diagnostic Engine
      - This is for adding a completely new category of validation that operates on a different scope, for example, a `CommentValidator` that specifically analyzes all user comments in a sheet.
      - Steps:
        - Create the New Engine: Create the new class (e.g., `CommentValidator`) and make it inherit from `AbstractDiagnosticsEngine`.
        - Implement the `run` Method: Add the specific logic for finding and analyzing comments inside the `run(**kwargs)` method. Ensure it returns a standard `DiagnosticsReport`.
        - Plug it In: Update the `SummaryDataV2Processor` to call the new engine at the appropriate point in its workflow. Because the new class follows the contract, the orchestrator can work with it without any custom logic.

  ### Scenario 3: We Need to Process New Kinds of Files
  This covers changes to the input data sources.
  1. Supporting a New Excel Template
      - This involves creating new configuration, not changing the core logic.
      - `schemas` Module: Define any new `TableSchema` and Pydantic model objects required for the new template.
      - New `FileProcessor`: Create a new orchestrator (e.g., `EitiReport2026Processor`) with a `can_handle` method to identify the new file and a `_get_specialists_config` method to load the new schemas.
      - `get_processor` Factory: No changes needed. The factory will automatically discover the new processor.

  2. Supporting a New File Format (CSV, JSON)
      - The goal is to load the new format into a DataFrame; all downstream logic can then be reused.
      - New `FileProcessor`: Create a `CsvEitiProcessor`. Its main job is to parse the CSV file and load the data into the expected DataFrame structure.
      - `TableDiagnosticsEngine` and `CleaningService`: No changes needed. These components are format-agnostic and work on DataFrames.

## Code references
  ### Base classes and data structures
  #### Core Data Structures
  The data structures that are passed between the components.

  ```Python
  # file: common/data_structures.py

  from dataclasses import dataclass, field
  from enum import Enum, auto
  from typing import Any
  import polars as pl

  class ErrorCode(Enum):
    """A unique identifier for each type of error."""
    MISSING_COLUMN = auto()
    COLUMN_SHIFT_DETECTED = auto()
    KNOWN_ALIAS_FOUND = auto()
    INVALID_DATATYPE = auto()
    # ... add more error codes as they are discovered

  @dataclass
  class ValidationError:
    """A structured object for reporting a single problem."""
    error_code: ErrorCode
    message: str
    row_index: int | None = None
    column_name: str | None = None

  @dataclass
  class DiagnosticsReport:
    """The standardized report returned by any diagnostics engine."""
    engine_name: str
    status: str # e.g., "PASSED", "NEEDS_REPAIR", "FAILED"
    data: pl.DataFrame | None = None
    errors: list[ValidationError] = field(default_factory=list)
    coordinates: dict[str, Any] | None = None
  ```

  #### The Orchestrator Interface
  This base class defines the contract for any high-level file processor, like `SummaryDataV2Processor`.

  ```Python
  # file: orchestrators/base.py

  import abc
  from pathlib import Path
  from common.data_structures import UserReport # Assuming UserReport is a defined structure

  class AbstractFileProcessor(abc.ABC):
    """
    The interface for an orchestrator that manages the entire
    validation and cleaning workflow for a specific file type.
    """

    @classmethod
    @abc.abstractmethod
    def can_handle(cls, file_path: Path) -> bool:
        """
        Returns True if this processor is the correct one for the given file.
        """
        pass

    @abc.abstractmethod
    def process(self) -> UserReport:
        """
        Executes the full workflow: delegation, inspection, routing,
        and aggregation, returning a final report for the user.
        """
        pass
  ```

  #### The Diagnostics Engine Interface
  This class defines the contract for both `TableDiagnosticsEngine` and `SheetDiagnosticsEngine`, ensuring they expose the same interface to the orchestrator.

  ```Python
  # file: diagnostics/base.py

  import abc
  from common.data_structures import DiagnosticsReport

  class AbstractDiagnosticsEngine(abc.ABC):
    """
    The common interface for all diagnostic components, whether they
    operate on tables, sheets, or any other scope.
    """

    @abc.abstractmethod
    def run(self, **kwargs) -> DiagnosticsReport:
        """
        Runs the diagnostic process and returns a standardized report.
        Uses **kwargs to allow for flexible inputs (e.g., a sheet_df,
        table coordinates, etc.).
        """
        pass
  ```

  #### The Validation Step Interface

  This defines the structure for each link in a validation chain used by a diagnostics engine.

  ```Python
  # file: diagnostics/validation.py

  import abc
  from typing import Optional, Any
  import polars as pl

  class AbstractValidationStep(abc.ABC):
    """

    The interface for a single, focused check in a validation chain.
    """
    _next_step: Optional['AbstractValidationStep'] = None

    def set_next(self, step: 'AbstractValidationStep') -> 'AbstractValidationStep':
        """Links this step to the next one in the chain."""
        self._next_step = step
        return step

    def handle(self, table_df: pl.DataFrame, context: dict[str, Any]) -> dict[str, Any]:
        """
        Executes the current step and passes control to the next.
        This method is concrete and shared by all subclasses.
        """
        context = self.process(table_df, context)

        if context.get("is_fatal", False):
            return context # Stop the chain if a fatal error occurred

        if self._next_step:
            return self._next_step.handle(table_df, context)

        return context

    @abc.abstractmethod
    def process(self, table_df: pl.DataFrame, context: dict[str, Any]) -> dict[str, Any]:
        """

        Contains the specific validation logic for this step. Subclasses
        must implement this method.
        """
        pass
  ```
  ### Stubs for key classes and configuration objects
  This is the complete skeleton of the application. The `pass` statements can be replaced with the business logic.
  #### 1. The Configuration ( `schemas` module)
  - This is where we define the "rules" for each table. It's the blueprint for the entire validation process.

    ```Python
    # file: schemas/eiti_schemas.py

    from dataclasses import dataclass, field
    from typing import Type, Any
    from pydantic import BaseModel, Field

    from diagnostics.validation import AbstractValidationStep # Assuming validation steps are defined elsewhere

    # --- Pydantic Models (Row-level Blueprints) ---

    class CompanyRow(BaseModel):
      """Defines the schema for a single row in the 'Companies' table."""
      company_name: str = Field(alias='Company Name')
      company_id: int = Field(alias='ID')
      country: str = Field(alias='Country')
      # ... other fields

    # --- Table Schema (The Complete Rulebook for a Table) ---

    @dataclass
    class TableSchema:
      """Holds all validation rules and metadata for one table."""
      table_anchor: str
      pydantic_model: Type[BaseModel]
      required_columns: list[str]
      validation_chain: list[AbstractValidationStep] = field(default_factory=list)

    # --- Concrete Schema Instances ---

    # This is where we build the specific rulebooks for each table.
    # There should be one of these for every table in the Excel file.
    COMPANIES_SCHEMA = TableSchema(
      table_anchor="Companies",
      pydantic_model=CompanyRow,
      required_columns=['Company Name', 'ID', 'Country'],
      # The chain of validation steps to run for this table
      validation_chain=[
          # StructureValidator(required_columns=['Company Name', 'ID', 'Country']),
          # DataTypeValidator(pydantic_model=CompanyRow),
      ]
    )
    ```

   #### 2. The Diagnostics ( `diagnostics` module)
  - These are the engines and validators that perform the actual checks.

    ```Python
    # file: diagnostics/engines.py

    from .base import AbstractDiagnosticsEngine
    from common.data_structures import DiagnosticsReport
    from schemas.eiti_schemas import TableSchema
    import polars as pl

    class TableDiagnosticsEngine(AbstractDiagnosticsEngine):
      """A diagnostics engine that finds, extracts, and validates a single table."""

      def __init__(self, schema: TableSchema):
          self.schema = schema

      def run(self, sheet_df: pl.DataFrame, **kwargs) -> DiagnosticsReport:
          """The main entry point to run all diagnostics for this table."""
          pass

      def _locate_table_boundaries(self, sheet_df: pl.DataFrame) -> dict | None:
          """Scans the sheet for the table's anchor and finds its start/end rows."""
          pass

      def _extract_table(self, sheet_df: pl.DataFrame, boundaries: dict) -> pl.DataFrame:
          """Slices the main sheet DataFrame to get a clean table DataFrame."""
          pass

      def _run_validation_chain(self, table_df: pl.DataFrame) -> dict:
          """Builds and executes the validation chain defined in the schema."""
          pass

    class SheetDiagnosticsEngine(AbstractDiagnosticsEngine):
      """A diagnostics engine that validates a sheet as a whole."""

      def run(self, sheet_df: pl.DataFrame, all_coords: list, **kwargs) -> DiagnosticsReport:
          """The main entry point to run all sheet-level checks."""
          # This is where we call specific methods like _check_out_of_bounds, etc.
          pass
    ```

   #### 3. The Cleaner ( `cleaning` module)
  - This service contains the toolkit for fixing known, fixable errors.

    ```Python
    # file: cleaning/service.py

    from common.data_structures import DiagnosticsReport, ErrorCode

    class CleaningService:
      """
      A service that contains a toolkit of functions to automatically
      fix known and fixable errors found in a DiagnosticsReport.
      """

      def __init__(self):
          # The internal registry of what this service knows how to fix.
          self._fixer_map = {
              ErrorCode.MISSING_COLUMN: self._fix_missing_column,
              # Add other ErrorCode -> function mappings here
          }

      def can_fix(self, error_code: ErrorCode) -> bool:
          """Checks the registry to see if a fix is available for an error."""
          return error_code in self._fixer_map

      def repair(self, report: DiagnosticsReport) -> dict:
          """
          Executes a repair plan on a DataFrame based on the errors
          in a DiagnosticsReport.
          """
          # 1. Build a repair plan based on the errors.
          # 2. Execute the plan by calling the internal tools.
          # 3. Return a RemediationResult.
          pass

      # --- Internal Toolkit of Fixer Methods ---

      def _fix_missing_column(self, df, error_details) -> pl.DataFrame:
          """An example of a private tool that fixes a specific error."""
          pass
    ```

   #### 4. The Orchestrator ( `orchestrators` module)
  - This is the high-level manager that controls the entire workflow for a specific file type.

    ```Python
    # file: orchestrators/eiti_orchestrator.py

    from .base import AbstractFileProcessor
    from common.data_structures import UserReport
    from diagnostics.engines import TableDiagnosticsEngine, SheetDiagnosticsEngine
    from cleaning.service import CleaningService
    from schemas.eiti_schemas import COMPANIES_SCHEMA # and others

    class SummaryDataV2Processor(AbstractFileProcessor):
      """The orchestrator for the 'Summary Data v2' EITI file template."""

      def __init__(self, file_path):
          self.file_path = file_path
          self.cleaning_service = CleaningService()
          self.sheet_diagnostics_engine = SheetDiagnosticsEngine()
          self.config = self._get_diagnostics_config()

      @classmethod
      def can_handle(cls, file_path) -> bool:
          """Checks if this is the right processor for the file."""
          # Logic to inspect the file (e.g., check sheet names)
          return "2_Economic contribution" in file_path.sheet_names # Example

      def process(self) -> UserReport:
          """Executes the full Validate -> Decide -> Remediate workflow."""
          # 1. Read Excel file into a dict of sheet DataFrames.
          # 2. Loop through sheets defined in self.config.
          # 3. For each sheet, run all configured TableDiagnosticsEngines.
          # 4. Inspect the reports and route to CleaningService if needed.
          # 5. Run the SheetDiagnosticsEngine on the sheet.
          # 6. Aggregate all results into a final UserReport.
          pass

      def _get_diagnostics_config(self) -> dict:
          """The central configuration map for this file type."""
          return {
              "3_Entities and projects List": [
                  TableDiagnosticsEngine(schema=COMPANIES_SCHEMA),
                  # ... other TableDiagnosticsEngine instances for this sheet
              ],
              # ... other sheets
          }
    ```

  #### 5. The Factory ( `main.py` or `factory.py` )
  - This is the main entry point that selects the correct orchestrator.

    ```Python
    # file: factory.py

    from orchestrators.eiti_orchestrator import SummaryDataV2Processor
    # Import other orchestrators here as they are created

    PROCESSOR_CLASSES = [
      SummaryDataV2Processor,
      # Add other orchestrator classes here
    ]

    def get_processor(file_path):
      """Finds and returns the correct orchestrator instance for the given file."""
      for processor_class in PROCESSOR_CLASSES:
          if processor_class.can_handle(file_path):
              return processor_class(file_path)
      raise ValueError(f"No suitable processor found for file: {file_path}")
    ```

## Testing strategy
  ### Examples

  #### 1. Unit Tests examples (Component Level)

  Unit tests verify individual classes and functions in isolation. They are the fastest and most numerous tests.
  - Testing a  `ValidationStep`  (e.g.,  `StructureValidator` )
   	- The goal is to ensure a validator correctly identifies a specific error.

   	  ```Python
   	  import polars as pl
   	  import pytest
   	  from common.data_structures import ErrorCode
   	  from diagnostics.validation_steps import StructureValidator

   	  def test_structure_validator_finds_missing_column():
   	    # Setup: Create a DataFrame missing the 'Country' column
   	    df = pl.DataFrame({
   	        "Company Name": ["Test Corp"],
   	        "ID": [123],
   	    })
   	    context = {"errors": [], "is_fatal": False}

   	    # Action: Instantiate and run the validator
   	    validator = StructureValidator(required_columns=['Company Name', 'ID', 'Country'])
   	    result_context = validator.process(df, context)

   	    # Assertion: Check that the correct error was added and the fatal flag is set
   	    assert result_context["is_fatal"] is True
   	    assert len(result_context["errors"]) == 1
   	    error = result_context["errors"][0]
   	    assert error.error_code == ErrorCode.MISSING_COLUMN
   	    assert "'Country'" in error.message
   	  ```
  - Testing a  `CleaningService`  Tool
   	- The goal is to verify that a specific fixing function works as expected.

   	  ```Python
   	  from cleaning.service import CleaningService
   	  from common.data_structures import ErrorCode

   	  def test_cleaning_service_adds_missing_column():
   	    # Setup: A DataFrame with a known issue
   	    df = pl.DataFrame({"Company Name": ["Test Corp"]})
   	    service = CleaningService()

   	    # Action: Call the specific internal tool (for testing purposes)
   	    # The error_details would be a ValidationError object
   	    repaired_df = service._fix_missing_column(df, error_details=...)

   	    # Assertion: The DataFrame should now be repaired
   	    assert "Country" in repaired_df.columns
   	    assert repaired_df["Country"].is_null().all()
   	  ```

  #### 2. Integration Tests examples (Interaction Level)

  Integration tests verify that components work together. They test the public interfaces between objects.
  - Testing a `TableDiagnosticsEngine`
    - The goal is to ensure the engine can locate, extract, and validate a table from a simulated sheet.

      ```Python
      from diagnostics.engines import TableDiagnosticsEngine
      from schemas.eiti_schemas import COMPANIES_SCHEMA

      def test_table_diagnostics_engine_full_run():
        # Setup: A DataFrame simulating a full sheet, with the table in the middle
        sheet_df = pl.DataFrame({
            "Column A": [None, "Some other data", "Companies", "Test Corp", None],
            "Column B": [None, "More data", "Company Name", "Real Name", None],
            # ... more columns
        })

        # Action: Instantiate the engine with its schema and run it
        engine = TableDiagnosticsEngine(schema=COMPANIES_SCHEMA)
        report = engine.run(sheet_df=sheet_df)

        # Assertion: Check the final report
        assert report.status == "PASSED" # Or NEEDS_REPAIR, depending on the test data
        assert len(report.errors) == 0
        # Assert that the extracted data is correct and clean
        assert report.data.shape == (1, 3) # Assumes the table has 1 row, 3 cols
        assert "Test Corp" not in report.data["Company Name"] # Header should be correct
      ```
  - Testing the `SummaryDataV2Processor` Routing Logic
    - The goal is to ensure the orchestrator calls the correct services based on a diagnostic report.

      ```Python
      from unittest.mock import MagicMock
      from orchestrators.eiti_orchestrator import SummaryDataV2Processor
      from common.data_structures import DiagnosticsReport, ValidationError, ErrorCode

      def test_processor_routes_to_cleaning_service_on_fixable_errors():
        # Setup:
        # 1. Create a mock CleaningService
        mock_remediator = MagicMock()
        mock_remediator.can_fix.return_value = True # Pretend it can fix the error

        # 2. Instantiate the processor, injecting the mock service
        processor = SummaryDataV2Processor(file_path="dummy.xlsx")
        processor.cleaning_service = mock_remediator

        # 3. Create a sample report with a fixable error
        error = ValidationError(error_code=ErrorCode.KNOWN_ALIAS_FOUND, message="...")
        report = DiagnosticsReport(engine_name="TestEngine", status="NEEDS_REPAIR", errors=[error])

        # Action: Call the processor's routing logic
        processor._route_and_process_report(report)

        # Assertion: Verify that the repair method was called
        mock_remediator.can_fix.assert_called_with(ErrorCode.KNOWN_ALIAS_FOUND)
        mock_remediator.repair.assert_called_once_with(report)
      ```

  #### 3. End-to-End Test example (Workflow Level)
  End-to-end tests validate the entire workflow using real files.
  - Testing the Full Workflow on a File
    - The goal is to confirm that a given input file produces the exact, expected final report.

      ```Python
      from factory import get_processor

      def test_e2e_full_process_on_file_with_fixable_errors(datadir):
        # Setup: 'datadir' is a pytest fixture providing the path to test files
        file_path = datadir / "summary_data_with_fixable_errors.xlsx"

        # Action: Run the entire system from the top-level entry point
        processor = get_processor(file_path)
        final_report = processor.process()

        # Assertion: Make detailed checks on the final UserReport object
        assert final_report.overall_status == "SUCCESS_WITH_REPAIRS"
        assert final_report.summary["tables_processed"] == 5
        assert final_report.summary["errors_found"] == 2
        assert final_report.summary["errors_fixed"] == 2

        # Check for specific log messages from the cleaning
        repair_log = final_report.logs["CleaningService"]
        assert "Renamed aliased column 'Cuntry' to 'Country'" in repair_log
      ```

  ### Testing map

  | Component                      | Test Type   | Primary Goal of the Test                                                                                                                               |
  | ------------------------------ | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
  | Pydantic Models (`CompanyRow`) | Unit        | Verify row-level data validation, type casting, and alias handling.                                                                                    |
  | `TableSchema` Objects          | Unit        | Confirm that the configuration (anchor text, required columns, etc.) is loaded correctly.                                                              |
  | `ValidationStep` Classes       | Unit        | Test the diagnostic logic in isolation. Ensure each validator correctly identifies its specific error and generates the right `ErrorCode`.             |
  | `CleaningService` Tools     | Unit        | Test each private fixing method (e.g., `_fix_column_shift`) as a pure function to confirm it correctly repairs a DataFrame.                            |
  | `RepairPlan` Logic             | Unit        | If the planning logic is complex, it should be tested to ensure it correctly orders repair steps based on error dependencies.                          |
  | `TableDiagnosticsEngine`       | Integration | Verify the full sequence: that it can `locate`, `extract`, `validate` a table from a simulated sheet, and return a correct `DiagnosticsReport`.        |
  | `SheetDiagnosticsEngine`       | Integration | Confirm it correctly identifies out-of-bounds data and other sheet-level anomalies from a simulated sheet DataFrame.                                   |
  | `get_processor` Factory        | Integration | Confirm the factory returns the correct `...Processor` instance for a given file type, based on the `can_handle` logic.                                |
  | `SummaryDataV2Processor` Logic | Integration | Test the `Routing` logic in isolation by providing mock `DiagnosticsReport`s and asserting that the `CleaningService` (mocked) is called correctly. |
  | Full `process()` Workflow      | End-to-End  | Test the entire system using real (but controlled) fixture files to verify the final `UserReport` is exactly as expected for various scenarios.        |

  ### Edge cases to test against

  File Structure Edge Cases
  * Missing Sheets: The file is missing a sheet that the `...Processor` expects to find.
  - Extra Sheets: The file contains unexpected sheets that should be ignored.
  - Password-Protected Files: The system should fail gracefully with a clear error message.
  - Empty Files: The file is a valid `.xlsx` file but contains no data or no sheets.
  - #### Table Structure Edge Cases
  - Anchor Not Found: The anchor text (e.g., "Companies") that a `TableDiagnosticsEngine` is looking for does not exist on the sheet.
  - Misspelled or Mismatched Anchor Casing: Testing how flexible the anchor-finding logic is (e.g., "companies" vs. "Companies").
  - Hidden Rows/Columns: The table contains hidden rows or columns that could affect data extraction.
  - Merged Cells: Merged cells, especially in the header row, can break table parsing.
  - Table with No Data: The table is found, but it only contains a header row and no data rows.
  - Duplicate Tables: A sheet contains two tables with the same anchor text. The test should verify if the system is designed to find the first one or find all of them.

  Data Content Edge Cases
  - Mixed Data Types: A column that should be numeric contains strings (e.g., "N/A", "Not reported").
  - Leading/Trailing Whitespace: Cell values have extra spaces that need to be trimmed (`" Value "` vs. `"Value"`).
  - Character Encoding: The data contains special characters (e.g., `é`, `ü`, `ø`) that must be handled correctly.
  - Numbers Formatted as Text: A common Excel issue where a cell containing `123` is treated as a string, not an integer.
