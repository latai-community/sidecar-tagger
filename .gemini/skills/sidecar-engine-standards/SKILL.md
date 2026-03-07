# sidecar-engine-standards

## Purpose
To enforce Java-grade engineering standards, strict typing, and clean code principles within the Sidecar-tagger Python SDK and CLI. This skill acts as a Quality Gate for all architectural decisions and code implementations.

## Triggers
- "refactor code", "implement new feature", "review architecture", "apply clean code", "add new parser", "fix architecture", "improve typing"

## Core Mandates (The 8 Pillars)

1. **Strict Typing (Java-Standard)**:
   - Mandatory use of Python `typing` module (`List`, `Dict`, `Optional`, `Union`, `Callable`).
   - All function signatures must have complete type hints: `def method(param: type) -> return_type:`.
   - No implicit returns; always define `-> None` or specific types. No `Any` without architectural justification.

2. **Interface-Driven Parsers**:
   - All parsers must inherit from a `BaseParser` Abstract Base Class (ABC).
   - Enforce the `extract(file_path: str, **kwargs) -> ParserResult` contract.

3. **Semantic Error Handling**:
   - Prohibit returning error strings (e.g., `"[Error]..."`).
   - Use a custom exception hierarchy: `SidecarException` -> `ParserError`, `LLMClientError`, `CacheError`.
   - Implement "Catch, Wrap, and Re-throw" patterns in the `Processor` layer.

4. **Traceability & Logging**:
   - Replace all `print()` statements with a structured `logging` configuration.
   - Mandatory log levels: `DEBUG` (Cache details/vectors), `INFO` (Process milestones), `WARNING/ERROR` (Failures).

5. **Validation-First (CLEAR Framework)**:
   - No feature is "Complete" without an associated test in `/tests`.
   - Mandatory test coverage: 1 Success Path, 1 Exception Path, 1 Edge Case (Empty/Large/Corrupt).

6. **Self-Documenting Models (Pydantic)**:
   - Every field in `sdk/models/` must include `Field(description="...")`.
   - Use Pydantic's `ConfigDict` to enable JSON schema extraction for LLM prompts.

7. **Resource Management**:
   - Mandatory use of `with` statements (Context Managers) for all I/O, file, and network operations.
   - Explicit cleanup of temporary files in `finally` blocks or via `atexit`.

8. **Dual-Target Documentation (Human & Agent)**:
   - **Module Headers**: Every `.py` file must start with a docstring containing: `Title`, `Abstract` (The "Why"), `Dependencies`, and `LLM-Hints`.
   - **Architectural "Why"**: Comments must explain the rationale behind complex logic or trade-offs.
   - **Executable Examples**: Every module must include a `if __name__ == "__main__":` block with a standalone usage example.

## Implementation Workflow
1. **Research**: Map existing patterns and dependencies.
2. **Design**: Propose an interface-based plan with type definitions.
3. **Draft**: Implement the logic following the 8 Pillars.
4. **Verify**: Run tests and check type-safety (e.g., `mypy` style checks).
5. **Document**: Add Pydantic descriptions and module headers.

## Quality Standards
- Functions should be < 25 lines.
- Classes should follow the Single Responsibility Principle.
- Variable names must be intention-revealing (e.g., `document_vector` vs `v`).
