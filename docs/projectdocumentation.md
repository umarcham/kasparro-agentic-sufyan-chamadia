# Project Documentation: Deterministic Agentic Flow

This document details the internal logic and defensive programming strategies used in the Kasparro Agentic System.

## Data Structures & Validation

We use **Pydantic V2** for all state management and output schemas. Key innovations include:

### 1. The Comparison Schema
The `ComparisonTable` model includes a custom validator that forces:
- **Keys**: All dictionary keys are transformed to `snake_case`.
- **Types**: `price_inr` is strictly cast to `int`, and `target_skin_type` is strictly cast to `List[str]`.
- **Logic**: Prevents LLM "lazy list" output (e.g., comma-separated strings).

### 2. FAQ Contract Enforcement
The `QuestionGenerationAgent` validates its own output count. If the LLM generates 14 or 16 items instead of 15, the agent returns an error to the orchestrator, triggering a re-generation loop.

## Robustness & Resilience Gaps (Addressed)

- **LLM Flakiness**: `LLMService` implements exponential backoff retries (Attempts: 3).
- **Missing Dependencies**: `ProductParser` uses safe imports and `try-except` blocks for the `spec_validator` tool, ensuring the system can either halt gracefully or continue with a warning instead of a crash.
- **Infinite Loops**: The orchestrator enforces a `max_iterations=3` limit. If the Quality Auditor fails the content three times, the system halts to prevent token waste and report a critical failure.
- **State Leakage**: `AgentState` uses `default_factory` for all mutable fields (list, dict), ensuring each run starts with a clean isolated state.

## Output Artifacts

All outputs are saved to the `output/` directory as structured JSON:
- `product_page.json`: Deep technical details and benefits.
- `faq.json`: Exactly 15 questions across 5 categories.
- `comparison_page.json`: Machine-readable relative positioning data.

## Logging & Monitoring

The system generates a time-stamped log in `logs/execution_YYYYMMDD.log` containing:
- Node transitions
- Tool invocation results
- LLM retry attempts
- Quality gate decisions
