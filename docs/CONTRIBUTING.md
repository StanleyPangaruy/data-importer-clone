# Contributing to the project

We welcome contributions from the team. This document outlines the standards and procedures for our development workflow. For feature ideas or bug reports, please start by creating an issue.

## Development Setup

Follow these steps to set up your local development environment.

**1. Prerequisites**
Ensure you have **Python 3.13+** and **`uv`** installed.

**2. Clone & Install Dependencies**

```shell
# Clone the repository
git clone https://github.com/civicliteracies/eiti-data-importer.git
cd eiti-data-importer

# Install dependencies into the virtual environment
uv sync

# Set up pre-commit by installing it as  tool instead of a package. This avoids behavior inconsistencies.
uv tool install pre-commit
pre-commit install --hook-type pre-push --hook-type pre-commit -hook-type commit-msg
```

**3. Configure Environment Variables**
This project uses `.env` files for local configuration, which are read by Pydantic.

First, copy the templates:

```shell
cp .env.example .env
cp .env.test.example .env.test
```

After copying, populate the new files with your settings. These files are covered by `.gitignore` and must not be committed. 
The test suite automatically uses **`.env.test`**. A fixture in **`tests/conftest.py`** directs Pydantic to load this file, ensuring tests run in an isolated environment.

-----

## Development Workflow

### Branching Model

  * **`main`**: Contains only stable, production-ready releases.
  * **`mvpX-dev`** (e.g., `mvp1-dev`): The primary development branch for the current MVP. All feature and bugfix branches are merged here via pull requests.

The standard workflow is:

1.  Ensure your local `mvp1-dev` is up to date: `git switch mvp1-dev && git pull origin mvp1-dev`.
2.  Create a descriptive feature or bugfix branch from `mvp1-dev`e.g. `git switch -c feat/add-table-extractor` or `git switch -c bug/restore-column-diagnostic`
3.  Make your changes on the feature or bugfix branch.
4.  Push your changes to github `git push origin <branch_name>` (use `-u` if the remote branch doesn't exist yet), git push origin <branch_name>
5.  Open a pull request targeting `mvp1-dev`.
6.  Clean up your branch once the PR is merged using `git branch -d <branch_name> && git push origin --delete <branch_name>`

> [!NOTE]
> pre-commit is set up to block direct pushes to main and mvp branches to enforce the PR workflow.
> Branch names are not enforced. please follow the pattern feat/* (features), bug/* (bugfixes) or exp/* (experiments) for naming branches.

### Commit and PR Guideline

  * A **commit** must represent a single, logical change.
  * A **pull request** should resolve one issue or implement one feature, and be small enough for a focused review.

Smaller, focused commits are easy to revert and serve as clean building blocks for a PR. Feature-focused PRs are quicker to review and make it easy to work on another part of the code while a PR is pending.

#### Commit Message Enforcement

We use `commitizen` to automatically enforce the Conventional Commits standard. A pre-commit hook will check your commit message format before a commit is created.
If your commit is blocked due to a formatting error, we recommend trying to rewrite it with the interactive helper by running `uv run cz commit`.

#### Commit examples

  * **Avoid (Mixed Concerns):**

    ```shell
    git commit -m "Build MVP 1 parser"
    ```

    *(This commit is too large and mixes the concerns of data modeling, engine logic, and the CLI, making it difficult to review or revert.)*

  * **Good (Separated, Logical Commits):**

    ```shell
    # First, define the foundational data structures
    git commit -m "feat(parser): Define UserReport and ValidationError structs"

    # Next, implement the engine that uses those structures
    git commit -m "feat(parser): Implement initial TableDiagnosticsEngine"

    # Finally, add the CLI entry point to run the engine
    git commit -m "feat(parser): Add CLI to process a file and print UserReport"
    ```

#### PR examples

  * **Avoid:**

  * **PR Title:** `feat: Build MVP1 Parser and add validation`
  * **Description:** "This PR adds the initial data structures, implements the `TableDiagnosticsEngine`, and adds the first set of validation steps to check data types. Also refactors the schema module."
  * **Why it's problematic:** The scope is too large, making it difficult to review, high-risk if one part needs changes, and hard to revert cleanly if a bug is found.

  * **Good:**

The work is broken down into a sequence of smaller pull requests.

  * **PR #1: Foundational Data Structures**

      * **PR Title:** `feat(parser): Define core data structures for reports and schemas`
      * **Description:** "Introduces `UserReport`, `ValidationError`, and the base `TableSchema`. This provides the agreed-upon foundation for the diagnostics engine."

  * **PR #2: Core Extraction Logic**

      * **PR Title:** `feat(parser): Implement table location and extraction engine`
      * **Description:** "Builds on PR #1. Implements the `TableDiagnosticsEngine` with the logic to `locate` and `extract` tables from a spreadsheet for the 'happy path'."

  * **PR #3: Add Validation**

      * **PR Title:** `feat(parser): Add initial data type validation step`
      * **Description:** "Builds on PR \#2. Enhances `TableDiagnosticsEngine` by adding the first `ValidationStep` to check for basic data type errors."


This approach matches well with our branching workflow. You create a short-lived **`feat/*`** branch from **`mvp1-dev`**, add your focused commits, and then open a small PR to merge back into **`mvp1-dev`**. This keeps our development branch stable and its history clean.

-----

## Code Style & Testing

### Formatting

A pre-commit hook runs Ruff for linting and formatting. If you want to do it manually, use the following:

```shell
ruff check --fix && ruff format
```

### Running Tests

A pre-push hook runs Pytest before every push. To do it manually instead, try:

```shell
uv run pytest
```
The test suite uses the configuration in your `.env.test` file.

-----

### Release Process

Creating a new version is a manual process managed by `commitizen`. It should only be performed on the `main` branch after all features for a release have been merged.

The release manager should follow these steps:

**1. Prepare the `main` branch:**
Ensure you have the latest changes.

```shell
git checkout main
git pull origin main
```

**2. Create the New Version**
Run the `cz bump` command. This will analyze all commits since the last tag, determine the correct semantic version, update the changelog, and create a new commit and tag after you confirm.

```shell
uv run cz bump --changelog
```

**3. Push the Release**
Push the new version commit and the new tag to the repository.

```shell
git push origin main --tags
```

-----

## Suggested repository organisation

```
eiti-data-importer/
├── packages/
│   ├── parser/
│   │   ├── src/
│   │   │   └── parser/
│   │   │       ├── __init__.py
│   │   │       ├── common/
│   │   │       │   └── data_structures.py  # ErrorCode, ValidationError, DiagnosticsReport, UserReport
│   │   │       ├── diagnostics/
│   │   │       │   ├── __init__.py
│   │   │       │   ├── base.py             # AbstractDiagnosticsEngine, AbstractValidationStep
│   │   │       │   └── engines.py          # TableDiagnosticsEngine, SheetDiagnosticsEngine
│   │   │       │   └── steps.py            # Concrete classes like StructureValidator
│   │   │       ├── orchestrators/
│   │   │       │   ├── __init__.py
│   │   │       │   ├── base.py             # AbstractFileProcessor
│   │   │       │   └── summary_data_v2.py  # SummaryDataV2Processor
│   │   │       ├── cleaning/
│   │   │       │   ├── __init__.py
│   │   │       │   └── service.py          # CleaningService
│   │   │       ├── schemas/
│   │   │       │   ├── __init__.py
│   │   │       │   ├── base.py             # TableSchema dataclass
│   │   │       │   └── summary_data.py     # Pydantic models (e.g., CompanyRow) & schemas (e.g., COMPANIES_SCHEMA)
│   │   │       ├── factory.py              # get_processor() function
│   │   │       └── cli.py                  # The CLI entry point function for MVP 1
│   │   └── pyproject.toml              # Defines the `parser` package
│   │
│   └── importer/
│       ├── src/
│       │   └── importer/
│       │       ├── __init__.py
│       │       └── ...                 # Future database importer code
│       └── pyproject.toml              # Defines the `importer` package
│
├── services/
│   └── api/
│       ├── src/
│       │   └── api/
│       │       ├── __init__.py
│       │       └── main.py             # Future FastAPI/Streamlit application
│       └── pyproject.toml              # Defines the `api` service
│
├── tests/
│   ├── fixtures/
│   │   └── summary_data_v2_clean.xlsx
│   └── e2e/
│       └── test_parser_mvp1.py
│
├── .gitignore
├── pyproject.toml                    # The ROOT workspace manifest
└── README.md
```
-----

## Frequently Asked Questions

***

### Q: Why did my `git push` to `main` fail?

A: We use a `pre-push` hook to protect key branches (`main`, `staging`, `dev`, and `mpX`) from direct pushes. This helps us ensure all changes are reviewed through a Pull Request.

***

### Q: The `pre-commit` hooks are not running when I commit. What should I do?

A: You likely have not installed the Git hooks correctly. You need to run `pre-commit install --hook-type pre-push --hook-type pre-commit -hook-type commit-msg` from the root of the repository. This command sets up the necessary hooks in your local `.git` directory.

***

### Q: I made a change on `main` by accident. How do I move it to a new branch?

A: The process depends on whether you have committed the change.

-   **If you have committed the change**:
    1.  Create and switch to a new branch: `git switch -c new-feature-branch`
    2.  Switch back to `main`: `git switch main`
    3.  Find the commit hash: `git log`
    4.  Cherry-pick the commit: `git cherry-pick <commit-hash>`
    5.  Revert the commit on `main`: `git revert <commit-hash>` 

-   **If you have staged the change**:
    1.  Un-stage the change: `git restore --staged .`
    2.  Create and switch to a new branch: `git switch -c new-feature-branch`
    3.  Stage and commit your changes: `git add .` and `git commit -m "feat: my new feature"`

-   **If the changes are not staged**:
    1.  Create and switch to a new branch: `git switch -c new-feature-branch`
    2.  Stage and commit your changes: `git add .` and `git commit -m "feat: my new feature"`
