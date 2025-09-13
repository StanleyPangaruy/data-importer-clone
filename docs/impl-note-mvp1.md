## Implementation Note: Explanations and code stubs for MVP1

### 1. Define Core Data Structures & Interfaces

#### Explanation

This is the foundation of the application. The **data structures** are the objects passed between components, and the **interfaces** (abstract base classes) define the required methods that concrete classes must implement (the contracts).

#### Code Stubs

```python
# file: packages/parser/src/parser/common/data_structures.py
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any
import polars as pl

class ErrorCode(Enum):
    """A unique identifier for each type of error. Empty for MVP 1."""
    pass

@dataclass
class ValidationError:
    error_code: ErrorCode
    message: str

@dataclass
class DiagnosticsReport:
    engine_name: str
    status: str
    data: pl.DataFrame | None = None
    errors: list[ValidationError] = field(default_factory=list)
    coordinates: dict[str, Any] | None = None

@dataclass
class UserReport:
    """The final, top-level report for the entire file."""
    overall_status: str
    processed_data: dict[str, Any] = field(default_factory=dict)
    errors: list[ValidationError] = field(default_factory=list)
    remediation_log: list[str] = field(default_factory=list)
```

```python
# file: packages/parser/src/parser/diagnostics/base.py
import abc
from common.data_structures import DiagnosticsReport

class AbstractDiagnosticsEngine(abc.ABC):
    @abc.abstractmethod
    def run(self, **kwargs) -> DiagnosticsReport:
        pass
```

```python
# file: packages/parser/src/parser/orchestrators/base.py
import abc
from common.data_structures import UserReport

class AbstractFileProcessor(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def can_handle(cls, file_path) -> bool:
        pass

    @abc.abstractmethod
    def process(self) -> UserReport:
        pass
```

```python
# file: packages/parser/src/parser/schemas/base.py
from dataclasses import dataclass
from enum import Enum, auto
from typing import Type
from pydantic import BaseModel

class LocationMethod(Enum):
    ANCHOR_SEARCH = auto()
    NAMED_TABLE = auto()

@dataclass
class TableSchema:
    table_anchor: str
    pydantic_model: Type[BaseModel]
    location_method: LocationMethod = LocationMethod.ANCHOR_SEARCH
```

-----

### 2. Implement the Flexible `TableDiagnosticsEngine`

#### Explanation

This is the core class for this MVP. Its job is to find and extract tables. The `run` method will act as a dispatcher, calling one of two private methods for locating tables based on the strategy defined in its `TableSchema`. For MVP 1, the validation logic is skipped.

#### Code Stub

```python
# file: packages/parser/src/parser/diagnostics/engines.py
from .base import AbstractDiagnosticsEngine
from common.data_structures import DiagnosticsReport
from schemas.base import TableSchema, LocationMethod
import polars as pl
# Note: openpyxl will be needed for the named_table method
# import openpyxl

class TableDiagnosticsEngine(AbstractDiagnosticsEngine):
    def __init__(self, schema: TableSchema):
        self.schema = schema

    def run(self, sheet_df: pl.DataFrame, workbook_sheet, **kwargs) -> DiagnosticsReport:
        """Finds, extracts, and reports on a single table."""
        # For MVP 1, validation is skipped. We assume a "happy path".
        pass

    def _locate_by_anchor(self, sheet_df: pl.DataFrame) -> dict | None:
        """Finds a table by searching for its text anchor (for v2)."""
        pass

    def _locate_by_named_table(self, workbook_sheet) -> dict | None:
        """Finds a table using Excel's built-in named ranges (for v2.1)."""
        pass
```

-----

### 3. Create Schemas for Both Templates

#### Explanation

This file is the configuration registry. It defines the structure of each table via Pydantic models and creates `TableSchema` instances that tell the `TableDiagnosticsEngine` what to look for and which location strategy to use.

#### Code Stub

```python
# file: packages/parser/src/parser/schemas/summary_data.py
from .base import TableSchema, LocationMethod
from pydantic import BaseModel, Field

# --- Pydantic Models ---
class CompaniesV1Row(BaseModel):
    company_name: str = Field(alias="Company Name")

class CompaniesV2Row(BaseModel):
    company_name: str = Field(alias="Company Name")

class CompaniesV2p1Row(BaseModel):
    company_name: str = Field(alias="company_name_new")

# --- Examples of Concrete Schema Instances ---

COMPANIES_V1_SCHEMA = TableSchema(
    table_anchor="COMPANIES",
    pydantic_model=CompaniesV1Row,
    location_method=LocationMethod.ANCHOR_SEARCH
)

COMPANIES_V2_SCHEMA = TableSchema(
    table_anchor="Companies",
    pydantic_model=CompaniesV2Row,
    location_method=LocationMethod.ANCHOR_SEARCH
)

COMPANIES_V2P1_SCHEMA = TableSchema(
    # For named tables, the anchor is the Excel table name
    table_anchor="Table_Companies_1",
    pydantic_model=CompaniesV2p1Row,
    location_method=LocationMethod.NAMED_TABLE
)
```

-----

### 4. Implement the Orchestrators

#### Explanation

These classes manage the workflow for a specific file version. The `_get_diagnostics_config` method is the key part, as it defines which tables exist on which sheets for that version. The `process` method will loop through this configuration and delegate the work to the engine.

#### Code Stub

```python
# file: packages/parser/src/parser/orchestrators/summary_data_v2.py
from .base import AbstractFileProcessor
from common.data_structures import UserReport
from diagnostics.engines import TableDiagnosticsEngine
from schemas.summary_data import COMPANIES_V2_SCHEMA

class SummaryDataV2Processor(AbstractFileProcessor):
	"""The orchestrator for the 'Summary Data v2' EITI file template."""
    def __init__(self, file_path):
        self.file_path = file_path
        self.config = self._get_diagnostics_config()

    @classmethod
    def can_handle(cls, file_path) -> bool:
        # Logic to identify a v2 file
        pass

    def process(self) -> UserReport:
        # 1. Read Excel file.
        # 2. Loop through sheets in self.config.
        # 3. For each sheet, run its configured TableDiagnosticsEngines.
        # 4. Aggregate results into a UserReport (with empty errors for MVP 1).
        pass

    def _get_diagnostics_config(self) -> dict:
	"""The central configuration map for the v2 file type."""
        return {
            "3_Entities and projects List": [
                TableDiagnosticsEngine(schema=COMPANIES_V2_SCHEMA),
            ]
        }
```

*(Similarly, `summary_data_v2p1.py` would be created for SummaryDataV1Processor while `summary_data_v2p1.py`, would be created for the `SummaryDataV2p1Processor`)*

-----

### 5. Implement the Factory

#### Explanation

This function inspects the file and returns the correct orchestrator instance for the job.

#### Code Stub

```python
# file: packages/parser/src/parser/factory.py
from .orchestrators.summary_data_v1 import SummaryDataV1Processor
from .orchestrators.summary_data_v2 import SummaryDataV2Processor
from .orchestrators.summary_data_v2p1 import SummaryDataV2p1Processor

# This list is automatically discoverable in a more advanced implementation
PROCESSOR_CLASSES = [
	SummaryDataV1Processor,
    SummaryDataV2Processor,
    SummaryDataV2p1Processor,
]

def get_processor(file_path):
    """Finds and returns the correct orchestrator instance."""
    for processor_class in PROCESSOR_CLASSES:
        if processor_class.can_handle(file_path):
            return processor_class(file_path)
    raise ValueError(f"No suitable processor found for file: {file_path}")
```

-----

### 6. Implement the CLI Entry Point

#### Explanation

This script serves as the user interface for MVP 1. It handles command-line arguments, orchestrates the call to the parser engine via the factory, and prints the final report.

#### Code Stub

```python
# file: packages/parser/src/parser/cli.py
import argparse
import json
from .factory import get_processor

def main():
    """CLI entry point for the parser."""
    parser = argparse.ArgumentParser(description="EITI Data Parser CLI")
    parser.add_argument("filepath", help="Path to the Excel file")
    args = parser.parse_args()

    try:
        processor = get_processor(args.filepath)
        report = processor.process()
        # Convert dataclass to dict for JSON serialization
        # and print with indentation.
        print(json.dumps(report.__dict__, default=str, indent=2))
    except Exception as e:
        print(f"An error occurred: {e}")
```
Once the entry point is working, it will be possible to add a script entry to `pyrpoject.toml`:

```toml
# In packages/parser/pyproject.toml
[project.scripts]
eiti-parser = "parser.cli:main" # Assumes a main() function in cli.py
```

This would allow the script to be run using a simple `uv run eiti-parser` instead of `uv run packages/parser/src/parser/cli.py`.

-----

### 7. Add E2E Tests

#### Explanation

This test provides the ultimate proof that MVP 1 is complete and correct. It simulates the user running the CLI on a real file and validates the structure and content of the JSON output.

#### Code Stub

```python
# file: tests/e2e/test_parser_mvp1.py
import subprocess
import json
import pytest

def test_happy_path_v2(datadir):
    """Tests the full CLI process on a clean v2 file."""
    # `datadir` is a pytest fixture that provides a path to test files
    file_path = datadir / "summary_data_v2_clean.xlsx"
    
    # Run the CLI as a subprocess
    result = subprocess.run(
        ["python", "-m", "parser.cli", str(file_path)],
        capture_output=True,
        text=True,
        check=True
    )

    # Assertions
    output = json.loads(result.stdout)
    assert output["overall_status"] == "SUCCESS"
    assert not output["errors"]
    assert not output["remediation_log"]
    assert "Companies" in output["processed_data"]
```
