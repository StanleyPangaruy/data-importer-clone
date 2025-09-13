# EITI Data Importer
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg?style=flat-square)](https://conventionalcommits.org)


## Overview

The EITI Data Importer is an internal tool used by the EITI Secretariat's Data team to upload new data to their upcoming Companies database.
It assists the team with validating, reviewing, correcting and enriching the data before uploading it to the database. 

This repository is in active development.

## Contributing

Review our docs/CONTRIBUTING.md to get started.

## Roadmap

### Overview

- [ ] MVP 1: The "Happy Path" Extractor with Final Reporting
- [ ] MVP 2: The Core Diagnostics Engine
- [ ] MVP 3: The Automated Remediation Service
- [ ] MVP 4: The End-to-End Staging Pipeline
- [ ] MVP 5: The Human-in-the-Loop Triage UI
- [ ] MVP 6: Data Enrichment and Advanced Diagnostics
- [ ] MVP 7: Production Lifecycle Management

### Breakdown

#### MVP 1: The "Happy Path" Extractor with Final Reporting

*   **Goal**: Prove the system can correctly locate and extract all tables from a valid v1, v2 or v2.1 file and package the results into the final, standardized report structure.

*   **Feature Focus**: Table location, data extraction, and `UserReport` generation.

*   **Outcome**: A command-line tool that takes a clean Excel file and outputs a complete **`UserReport`** as a JSON file. This initial report will contain the extracted clean data, an empty list of errors, and an empty cleaning log.

* **Modified files**:
  *   `packages/parser/src/parser/common/data_structures.py`: To define `UserReport`, `DiagnosticsReport`, `ValidationError`, `ErrorCode`.
  *   `packages/parser/src/parser/schemas/base.py`: To define the `TableSchema` dataclass.
  *   `packages/parser/src/parser/schemas/summary_data.py`: To define Pydantic models and concrete `TableSchema` instances for the tables in the clean test file.
  *   `packages/parser/src/parser/diagnostics/base.py`: To define `AbstractDiagnosticsEngine`.
  *   `packages/parser/src/parser/diagnostics/engines.py`: To implement `TableDiagnosticsEngine` (focusing on the `locate` and `extract` logic).
  *   `packages/parser/src/parser/orchestrators/base.py`: To define `AbstractFileProcessor`.
  *   `packages/parser/src/parser/orchestrators/summary_data_v1.py`: To implement `SummaryDataV1Processor`.
  *   `packages/parser/src/parser/orchestrators/summary_data_v2.py`: To implement `SummaryDataV2Processor`.
  *   `packages/parser/src/parser/orchestrators/summary_data_v2p1.py`: To implement `SummaryDataV2P1Processor`.
  *   `packages/parser/src/parser/factory.py`: To implement the `get_processor()` function.
  *   `packages/parser/src/parser/cli.py`: The CLI entry point function that takes a file path and prints the `UserReport` JSON.
  *   `tests/fixtures/summary_data_v1_clean.xlsx`: The "happy path" test file for v1.
  *   `tests/fixtures/summary_data_v2_clean.xlsx`: The "happy path" test file for v2.
  *   `tests/fixtures/summary_data_v2p1_clean.xlsx`: The "happy path" test file for v2.1.
  *   `tests/e2e/test_parser_mvp1.py`: The test that runs the CLI on the clean fixture file and validates the output `UserReport`.

* **No-goes**
  *   `packages/parser/src/parser/diagnostics/steps.py`: The `ValidationChain` inside the `TableDiagnosticsEngine` will be empty. No concrete `ValidationStep` classes are needed yet.
  *   `packages/parser/src/parser/diagnostics/engines.py` (`SheetDiagnosticsEngine`): The `SheetDiagnosticsEngine` is for handling edge cases and is not part of the happy path.
  *   `packages/parser/src/parser/cleaning/`: The entire `CleaningService` is not needed, as MVP 1 assumes a perfect file with no errors to fix.
  *   `packages/importer/` and `services/api/`: The database importer and the user-facing application are part of later MVPs.
  *   Unit and integration tests are not needed yet.


#### MVP 2: The Core Diagnostics Engine

*   **Goal**: Enhance the engine to detect and report all structural and data-type errors within the tables.

*   **Feature Focus**: In-table validation (structure, data types), and unit tests.

*   **Outcome**: The CLI tool now processes an imperfect file. The output `UserReport` is enhanced to populate the `errors` section with a detailed list of structured `ValidationError` objects.

* **Modified files**: TBD

* **No-goes**: TBD


#### MVP 3: The Automated Remediation Service

*   **Goal**: Introduce the ability to automatically fix a defined subset of known, simple errors.

*   **Feature Focus**: Automated data cleaning.

*   **Outcome**: The CLI tool's `UserReport` is now fully dynamic. For a file with fixable errors, the `cleaning_log` section is populated with actions taken, the `errors` list contains only unfixable issues, and the data reflects the automated corrections.

* **Modified files**: TBD

* **No-goes**: TBD

#### MVP 4: The End-to-End Staging Pipeline

*   **Goal**: Connect the engine to the database and a basic UI, proving that clean or auto-repaired data can be successfully uploaded and persistently staged.

*   **Feature Focus**: Persistence and state management.

*   **Outcome**: A simple Streamlit page where a user can upload a file. If the engine's `UserReport` indicates no manual fixes are needed, a "Commit to Staging" button appears, which saves the data and updates the `import_batches` state table.

* **Modified files**: TBD

* **No-goes**: TBD

#### MVP 5: The Human-in-the-Loop Triage UI

*   **Goal**: Build the user interface for handling errors that require human intervention.

*   **Feature Focus**: Interactive manual error correction.

*   **Outcome**: When a `UserReport` contains unfixable errors, the Streamlit app now presents a "Triage" screen. This UI displays each error and provides the user with options to correct the data before committing to staging.

* **Modified files**: TBD

* **No-goes**: TBD

#### MVP 6: Data Enrichment and Advanced Diagnostics

*   **Goal**: Add value by enriching the data against existing records and catching more subtle, business-level issues.

*   **Feature Focus**: Data enrichment and advanced (semantic) diagnostics.

*   **Outcome**: The system now integrates the `ApiEnricher` and advanced validators. The Triage UI is enhanced to include these new findings (e.g., potential duplicates, low-confidence fuzzy matches) alongside the initial file validation errors for user resolution.

* **Modified files**: TBD

* **No-goes**: TBD

#### MVP 7: Production Lifecycle Management

*   **Goal**: Make the application fully operational for the data management team.

*   **Feature Focus**: Production data lifecycle management.

*   **Outcome**: A complete application with pages for reviewing staged batches, promoting them to the production database, and safely archiving old data via soft deletes.

* **Modified files**: TBD

* **No-goes**: TBD

