## Implementation Note: Processing tweaks across template versions.

### Overview

The core architecture is designed to process the `v1`, `v2`, and `v2.1` summary data templates within the same unified pipeline. The primary difference between the templates lies in two areas: the **strategy used to locate tables** and the **set of sheets and tables** defined in each version.

The `v2.1` template is the most reliable to parse due to its structured nature, while the older `v1` and `v2` templates require a more fragile, search-based approach.

-----

### Key Difference: Table Location Strategy

The `TableDiagnosticsEngine` supports both location methods by selecting a strategy based on its configuration.

#### Summary Data v1 & v2 (Heuristic Search)

  * **Problem**: In the older `v1` and `v2` templates, tables are simply ranges of cells with no formal, machine-readable definition.
  * **Solution**: To find a table, the `TableDiagnosticsEngine` must perform a **heuristic search**. It scans the sheet's DataFrame row by row, looking for a pre-defined text string (an "anchor") to identify where the table begins.
  * **Implication**: This method is flexible but can be brittle. It is sensitive to variations in the anchor text, which could cause the location logic to fail.

#### Summary Data v2.1 (Direct Lookup)

  * **Problem**: This is solved in the `v2.1` template by using Excel's built-in **"Named Table"** feature.
  * **Solution**: The `TableDiagnosticsEngine` can perform a **direct lookup**, querying the sheet for a table with a specific, formal name.
  * **Implication**: This method is significantly faster and more reliable.

-----

### Impact on the Codebase

The differences between all three templates are managed cleanly through configuration, isolating the changes to the orchestrator level.

  * **Configuration (`TableSchema`)**: The `location_method` field in the `TableSchema` acts as the "switch" to control the location strategy.

    ```python
    # Schema for a v1 or v2 table
    SCHEMA_V1_OR_V2 = TableSchema(
        ...,
        location_method=LocationMethod.ANCHOR_SEARCH
    )

    # Schema for a v2.1 table
    SCHEMA_V2P1 = TableSchema(
        ...,
        location_method=LocationMethod.NAMED_TABLE
    )
    ```

  * **Orchestrators (`...Processor`)**: This is where the template-specific logic is defined. A dedicated orchestrator is created for each version (`SummaryDataV1Processor`, `SummaryDataV2Processor`, `SummaryDataV2p1Processor`). The primary difference between them is their `_get_diagnostics_config` method. This method defines the unique map of sheets and tables for that specific template version, loading the correct `TableSchema` objects for each. This cleanly isolates the unique structure of each template.

  * **Implementation (`TableDiagnosticsEngine`)**: 
 
 The engine itself requires **no changes**. It already contains the logic for both `_locate_by_anchor` and `_locate_by_named_table`. It acts as a flexible tool that is directed by its configuration.

The following code shows how the engine dispatches to the correct private method based on the schema and contains the implementation for the _locate_by_named_table method, which is adapted from a [previous v2.1 extraction script](https://github.com/civicliteracies/db-v2-schema-testing/blob/main/utils/reference-tables-extraction.py).

```python
# file: packages/parser/src/parser/diagnostics/engines.py

class TableDiagnosticsEngine(AbstractDiagnosticsEngine):
    def __init__(self, schema: TableSchema):
        self.schema = schema

    def run(self, sheet_df: pl.DataFrame, workbook_sheet, **kwargs) -> DiagnosticsReport:
        """The main entry point to run all diagnostics for this table."""
        
        # Dispatch to the correct location method based on the schema
        boundaries = None
        match self.schema.location_method:
            case LocationMethod.ANCHOR_SEARCH:
                boundaries = self._locate_by_anchor(sheet_df)
            case LocationMethod.NAMED_TABLE:
                boundaries = self._locate_by_named_table(workbook_sheet)
        
        if not boundaries:
            # ... handle table not found and return a failure report ...
            pass
        
        # ... continue with extraction and validation using the found boundaries ...
        pass

    def _locate_by_anchor(self, sheet_df: pl.DataFrame) -> dict | None:
        """Finds a table by searching for its text anchor (for v1/v2)."""
        # ... existing heuristic search logic ...
        pass

    def _locate_by_named_table(self, workbook_sheet) -> dict | None:
        """
        Finds a table using Excel's built-in named ranges (for v2.1).
        This method adapts the logic from the original script.
        """
        if not workbook_sheet.tables:
            return None

        # The schema's anchor is the formal name of the Excel Table
        table_name_to_find = self.schema.table_anchor

        for table in workbook_sheet.tables.values():
            if table.name == table_name_to_find:
                # Convert the table.ref (e.g., "A1:G10") into the 
                # boundary coordinate dictionary the engine expects.
                # (Implementation for conversion logic goes here)
                return {"range": table.ref, "start_row": 1, "end_row": 10, ...}
        
        return None # Table with the specified name not found
```

`def _locate_by_named_table` uses the `sheet.tables` attribute. This is a dictionary-like object provided by `openpyxl` that contains all formally defined "Tables" on that worksheet. Accessing it is a **direct lookup**, not a search, which is why it is both fast and robust.

**In Summary:**

1.  **Component**: The logic resides within the **`TableDiagnosticsEngine`**.
2.  **Method**: It forms the implementation for the private method **`_locate_by_named_table()`**.
3.  **Activation**: This method is called when the `TableDiagnosticsEngine` is configured with a `TableSchema` object where the `location_method` is set to `LocationMethod.NAMED_TABLE`.
