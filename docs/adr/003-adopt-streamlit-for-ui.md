# ADR-003: Choose Streamlit for the Presentation Layer

**Status**: Accepted

**Context**: The application requires a data-centric UI for an internal team. Key criteria include rapid development, ease of iteration for a layer likely to receive many change requests, and the ability to host for free. A highly customized UI is a non-goal for this internal tool. The alternative considered was a FastAPI backend with a custom JavaScript frontend.

**Decision**: The UI will be built using **Streamlit**.

**Consequences**:
* **Positive**:
    * Streamlit's Python-only environment and component library allow for very fast development and iteration.
    * Free hosting options are readily available (e.g., Streamlit Community Cloud).
* **Negative**:
    * Hosted Streamlit applications have a startup delay ("wake-up time"), which is acceptable as this application is not time-sensitive.
* **Mitigation**: The architecture decouples the presentation layer from the backend services. If performance or customization needs change significantly in the future, the Streamlit UI can be replaced with another framework without rewriting the core business logic.
