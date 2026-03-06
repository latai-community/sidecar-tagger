# Workflow Standards: Sidecar-tagger Development

This document defines the mandatory steps that must be followed by any AI agent or contributor after implementing new features or making changes to the codebase.

## 1. Traceability: The Changelog
Every new functionality, bug fix, or refactor MUST be documented in the `CHANGELOG.md` file.
*   **What**: Clearly state what was changed.
*   **Why**: Explain the rationale behind the change (the "reasoning").
*   **Impact**: Note any breaking changes or required configuration updates (e.g., new `.env` variables).

## 2. Quality: Mandatory Testing
Tests must be executed before considering a task finished.
*   **Execution**: Run `pytest` to ensure existing parsers and the SDK are functional.
*   **New Features**: If a new feature is added, a corresponding test case in `tests/` is mandatory.
*   **Validation**: No code is "final" until tests pass.

## 3. Communication: Intent & Rationale
When presenting changes to the user, the agent must:
*   Clearly explain **why** the technical path was chosen.
*   Distinguish between Directives (actions taken) and Inquiries (proposals).

## 4. Documentation & Skill Sync
After every significant change, the agent **MUST ASK** the user:
> "I have implemented the changes. Would you like me to update the project documentation (README, references) or the AI Skills to reflect these updates?"

**Skill Modification Rules:**
*   **Mandatory References**: Whenever a skill is modified, you MUST verify that its `references/` folder is up to date and that the `## Related Skills` section in `SKILL.md` correctly links to other relevant parts of the project.
*   **Cross-linking**: Ensure that the new functionality is reflected in the skill's internal logic and external references.

## 5. Implementation Checklist
- [ ] Code is implemented and linted.
- [ ] Tests have been executed and passed.
- [ ] `CHANGELOG.md` has been updated with the "What" and "Why".
- [ ] User was asked about Documentation/Skill updates.
