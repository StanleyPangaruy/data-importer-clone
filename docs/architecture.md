# EITI Data Importer: Software Architecture Overview

The architecture uses a monorepo with decoupled packages for core logic and the user interface. This design ensures the business logic is testable, scalable, and reusable. The UI calls the core packages to execute a defined workflow.

The workflow combines automated data processing (parsing, validation, cleaning) with a mandatory user review step for any errors or ambiguities that cannot be resolved automatically.

## 1. Project Structure

The project is a workspace-style monorepo, with each component (`parser`, `importer`, `api`) defined as a separate package.

```
eiti-importer-app/
├── packages/
│   ├── parser/                 # Core engine for parsing, validation, and cleaning
│   └── importer/               # Service for database interaction and state management
├── services/
│   └── api/                    # The user-facing application
└── ...
```

## 2. Modules & Key Classes

*   **`importer.DataOperationPipeline`**: Manages the batch import lifecycle by updating the `import_batches` state table and calling the `parser` and `database_manager` packages.

*   **`parser.get_processor` (Factory)**: Inspects a file and returns the correct `...Processor` orchestrator for that file type and version.

*   **`parser.SummaryDataV2Processor` (Orchestrator)**: Manages the diagnostics and cleaning workflow for a specific file, delegating tasks to the diagnostics engines.

*   **`parser.TableDiagnosticsEngine` & `SheetDiagnosticsEngine`**: Perform diagnostics. The `TableDiagnosticsEngine` validates content within tables; the `SheetDiagnosticsEngine` validates the sheet as a container.

*   **`parser.CleaningService`**: Performs automated data cleaning by applying fixes for known, correctable errors found in a `DiagnosticsReport`.

*   **`importer.DatabaseManager`**: Manages all database connections and executes queries.


## 3. `import_batches` Table Schema

This table provides a persistent, auditable log for each import operation.

*   `batch_id` (TEXT, PK)

*   `status` (TEXT): Current state (`AWAITING_APPROVAL`, `PROMOTED`, etc.).

*   `source_filename` (TEXT)

*   `file_hash_sha256` (TEXT): Hash of the file content to prevent duplicates.

*   `temp_data_path` (TEXT): Path to the processed Parquet data file.

*   `created_at`, `updated_at` (TIMESTAMP)


## 4. Data Flow & Batch Lifecycle

### Flow 1: Import a New Batch

1.  **Upload**: The user uploads a file. The system rejects it if the file's hash already exists in the `import_batches` table.

2.  **Processing**: The `DataOperationPipeline` calls the `parser` package, which runs its full **Validate -\> Decide -\> Remediate** workflow, returning a `UserReport` with cleaned data, automated fix logs, and any unfixable errors.

3.  **Enrichment**: The cleaned data is processed for fuzzy matching of entity IDs and checked for semantic duplicates against the production database.

4.  **User Review**: The UI presents all unfixable errors and enrichment ambiguities to the user for resolution. This step is mandatory.

5.  **Commit to Staging**: After user resolution, the pipeline saves the final DataFrame to a Parquet file, inserts the data into staging tables with a new `batch_id`, and creates a record in `import_batches` with status `AWAITING_APPROVAL`. Post-commit data tests are run, and the batch is rolled back on failure.


### Flow 2: Manage Pending Batches

*   **Review**: The user views a list of all batches with status `AWAITING_APPROVAL`.

*   **Decision**:

    *   **Promote**: The pipeline commits the data from the Parquet file to the production database. The batch status becomes `PROMOTED`.

    *   **Discard**: The pipeline deletes the data from the staging tables and the Parquet file. The batch status becomes `DISCARDED`.

    *   **Retry**: If a promotion fails, the status becomes `PROMOTION_FAILED`, and the user is given an option to retry the operation.


### Flow 3: Manage Production Data

*   **Archive**: The user enters a `batch_id` to archive. After confirmation, the pipeline performs a soft delete (`is_archived = TRUE`) on all associated rows in the production database.
