# ADR-001: Adopt a Decoupled Multi-Package Structure

**Status**: Accepted

**Context**: The application consists of several logically distinct but related components: a core file parser, a database import service, and a user interface. To facilitate modular development, independent testing, and future reuse, these components should be isolated from each other within the single project repository.

**Decision**: The monorepo will be structured with separate, independently testable Python packages for each major component: `parser` (the backend service layer), `importer` (the storage layer), and `api` (the presentation layer). The `uv` workspace feature will be used to manage these local packages and their dependencies. This explicitly decouples the backend logic from the UI.

**Consequences**:
* **Positive**:
    * Enhances modularity, allowing components to be worked on in parallel.
    * Each package can be tested independently.
    * The `parser` backend is fully decoupled, making it reusable in other projects or with a different UI framework in the future.
* **Negative**:
    * The initial `pyproject.toml` workspace setup is more complex than that of a single-package project.
