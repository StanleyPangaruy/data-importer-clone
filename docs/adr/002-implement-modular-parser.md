# ADR-002: Implement a Staged, Hierarchical Processing Pipeline

**Status**: Accepted

**Context**: The EITI summary data files are manually filled, contain various typos and inconsistencies, and have varying quality standards across different historical versions. A simple parser would fail to provide meaningful feedback, as fundamental structural errors (e.g., a missing column) can cause many misleading downstream errors (e.g., apparent data type mismatches). The system must be able to pinpoint the root cause of validation failures.

**Decision**: The processing pipeline will be structured in stages to handle a **hierarchy of issues**, using modular, single-responsibility components.
1.  **Diagnostics**: `DiagnosticsEngine` components will run an ordered `ValidationChain`. The chain will halt on fundamental, fatal errors to prevent reporting spurious, cascading errors.
2.  **Orchestration**: A `...Processor` will manage the workflow, inspect the resulting `DiagnosticsReport`, and decide on the next action.
3.  **Cleaning**: A separate `CleaningService` will handle automated fixes, keeping this logic decoupled from the diagnostic components.

**Consequences**:
* **Positive**:
    * Provides granular and meaningful error feedback by respecting the hierarchy of issues.
    * The modular design makes the data flow easier to reason about and is highly extensible for future features (like new cleaning functions).
    * Allows to gradually improve the parser as we identify new strategies to fix common issues without side effects.
* **Negative**:
    * The architecture involves more components than a monolithic parser, making it harder to understand at first.
