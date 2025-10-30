# Task Specifications Directory

This directory contains task specifications for the agentic_bookkeeper project,
organized according to the agile workflow structure (Phases → Sprints → Tasks).

---

## Directory Structure

```text
specs/
├── README.md                    # This file
├── PHASE_1/                     # Phase 1: Project Setup
│   └── SPRINT_1/                # Sprint 1: Initial Setup
│       └── T-001_example_task.md
├── PHASE_2/                     # Phase 2: Core Development (planned)
│   └── SPRINT_1/
│       └── (task specs)
└── ...                          # Additional phases as needed
```

---

## Workflow Overview

### State Machine Workflow

This project uses an automated state machine workflow managed by the `/next-task`
command. The workflow:

1. Reads the next task specification from PROJECT_STATUS.md
2. Loads the task requirements and context
3. Executes the task according to its specification
4. Updates PROJECT_STATUS.md with results
5. Prepares for the next task

### Key Files

- **PROJECT_STATUS.md**: Tracks project status and workflow state
- **CONTEXT.md**: Maintains persistent cross-task context
- **specs/**: Contains all task specifications (this directory)

---

## Task Specification Format

All task specifications follow a standardized format. See `T-001_example_task.md`
for a complete example.

### Required Sections

1. **Header**: Task metadata (ID, name, phase, sprint, status, etc.)
2. **Objective**: Clear statement of what the task accomplishes
3. **Context**: Why the task exists and how it relates to other tasks
4. **Requirements**: Functional and non-functional requirements
5. **Acceptance Criteria**: Must have, should have, nice to have, out of scope
6. **Implementation Plan**: Step-by-step execution plan
7. **Testing Requirements**: How to verify the task was completed correctly
8. **Dependencies**: External, internal, and task dependencies
9. **Risks & Mitigation**: Identified risks and mitigation strategies
10. **Completion Criteria**: Definition of done

### Optional Sections

- Implementation Notes
- Post-Completion Actions
- Notes and Open Questions
- Revision History

---

## Creating New Task Specifications

### Step 1: Copy Template

```bash
# Copy the example task as a starting point
cp specs/PHASE_1/SPRINT_1/T-001_example_task.md specs/PHASE_X/SPRINT_Y/T-XXX_new_task.md
```

### Step 2: Update Task Metadata

Edit the header section with:

- New task ID (e.g., T-002, T-003, etc.)
- Task name describing what it accomplishes
- Correct phase and sprint
- Priority and estimated effort
- Status (usually "Pending" for new tasks)

### Step 3: Define Requirements

Fill in:

- **Objective**: What does this task accomplish?
- **Functional Requirements**: What functionality must be implemented?
- **Non-Functional Requirements**: Performance, security, maintainability, etc.
- **Acceptance Criteria**: How do we know it's done?

### Step 4: Create Implementation Plan

Break the task into steps:

1. Each step should have a clear objective
2. List specific actions to take
3. Define expected output
4. Specify validation criteria

### Step 5: Document Dependencies

List:

- External dependencies (libraries, tools, etc.)
- Internal dependencies (other components)
- Task dependencies (which tasks must complete first)

### Step 6: Update PROJECT_STATUS.md

After creating the task spec, update PROJECT_STATUS.md:

```yaml
NEXT_TASK_ID: T-XXX
NEXT_TASK_SPEC: specs/PHASE_X/SPRINT_Y/T-XXX_new_task.md
```

---

## Executing Tasks

### Using /next-task

The simplest way to execute tasks:

```bash
/next-task
```

This command:

1. Reads NEXT_TASK_SPEC from PROJECT_STATUS.md
2. Loads the task specification
3. Reads CONTEXT.md for cross-task knowledge
4. Executes the task step-by-step
5. Updates PROJECT_STATUS.md with results
6. Updates CONTEXT.md with learnings

### Task Execution Flow

```text
                    ┌─────────────────────┐
                    │ PROJECT_STATUS.md   │
                    │ NEXT_TASK_SPEC      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Load Task Spec      │
                    │ (e.g., T-001.md)    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Load CONTEXT.md     │
                    │ (cross-task memory) │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Execute Task        │
                    │ Step-by-Step        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Update Status       │
                    │ Update Context      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Ready for Next Task │
                    └─────────────────────┘
```

---

## Task States

Tasks can be in one of these states:

- **Pending**: Not yet started
- **In Progress**: Currently being executed
- **Blocked**: Cannot proceed due to dependencies or issues
- **Completed**: Successfully finished
- **Failed**: Attempted but failed (requires resolution)
- **Skipped**: Intentionally skipped (with reason documented)

---

## Naming Conventions

### Task IDs

- Format: `T-XXX` (e.g., T-001, T-002, T-010, T-100)
- Sequential numbering across entire project
- Leading zeros for sorting (T-001 to T-099, then T-100+)

### Task Files

- Format: `T-XXX_brief_description.md`
- Use lowercase with underscores
- Keep description short but meaningful
- Examples:
  - `T-001_example_task.md`
  - `T-002_setup_database.md`
  - `T-010_implement_auth.md`

### Phases

- Format: `PHASE_X` (e.g., PHASE_1, PHASE_2)
- Numbered sequentially
- Each phase has clear objective

### Sprints

- Format: `SPRINT_X` (e.g., SPRINT_1, SPRINT_2)
- Numbered sequentially within each phase
- Each sprint has clear goal and timeline

---

## Phase and Sprint Structure

### Phase 1: Project Setup

**Objective:** Establish project foundation

#### Sprint 1: Initial Setup

- Project scaffolding
- Workflow initialization
- Development environment

### Phase 2: Core Development

**Objective:** Implement core functionality
(Sprints to be planned)

### Phase 3: Testing & Quality Assurance

**Objective:** Ensure quality and reliability
(Sprints to be planned)

### Phase 4: Deployment & Documentation

**Objective:** Prepare for production
(Sprints to be planned)

---

## Best Practices

### Writing Task Specifications

1. **Be Specific**: Clear, unambiguous requirements
2. **Be Realistic**: Achievable within estimated effort
3. **Be Testable**: Clear acceptance criteria
4. **Be Complete**: All sections filled in
5. **Be Consistent**: Follow the standard format

### Task Sizing

- **Small Task**: 1-2 hours (ideal size)
- **Medium Task**: 3-4 hours (acceptable)
- **Large Task**: 5+ hours (consider splitting)

If a task is too large, break it into multiple smaller tasks.

### Dependencies

Always document:

- What this task depends on (must complete first)
- What depends on this task (will be blocked until this completes)
- External dependencies (libraries, tools, services)

### Context Updates

After each task:

- Update CONTEXT.md with new patterns
- Document gotchas or issues discovered
- Add new utilities or helpers created
- Note architectural decisions made

---

## Troubleshooting

### Task Spec Not Found

If /next-task reports task spec not found:

1. Check NEXT_TASK_SPEC path in PROJECT_STATUS.md
2. Verify the file exists at that path
3. Check for typos in the path
4. Ensure specs directory structure is correct

### Task Execution Failed

If a task fails:

1. Review error messages in task output
2. Check CONTEXT.md for known gotchas
3. Verify dependencies are met
4. Update task spec with mitigation steps
5. Retry execution with /next-task

### Blocked Task

If a task is blocked:

1. Update task status to "Blocked" in PROJECT_STATUS.md
2. Document blocker in BLOCKED ITEMS section
3. Create resolution task if needed
4. Update NEXT_TASK_SPEC to skip to next unblocked task

---

## Related Commands

- `/next-task` - Execute the next task in workflow
- `/init-workflow [type]` - Initialize workflow (already done)
- `/create-tasks` - Create task list from feature spec
- `/quick-plan [prompt]` - Create concise engineering plan
- `/feature [description]` - Create feature specification
- `/bug [description]` - Create bug fix specification

---

## Examples

### Example 1: Simple Task

```markdown
# Task Specification: T-005

**Task Name:** Add Configuration Loading
**Task ID:** T-005
**Status:** Pending

## OBJECTIVE
Implement configuration file loading from .env and config.yaml files.

## REQUIREMENTS
1. Load environment variables from .env
2. Load settings from config.yaml
3. Merge with defaults
4. Validate required settings

## ACCEPTANCE CRITERIA
- [ ] .env file loaded successfully
- [ ] config.yaml parsed correctly
- [ ] Missing required settings raise error
- [ ] Tests pass with 100% coverage
```

### Example 2: Complex Task

See `T-001_example_task.md` for a complete example of a complex task with
all sections filled in.

---

## Version History

| Version | Date       | Author | Changes                              |
|---------|------------|--------|--------------------------------------|
| 1.0     | 2025-10-29 | Claude | Initial specs directory documentation|

---

**End of README.md**

For more information:

- See PROJECT_STATUS.md for current workflow state
- See CONTEXT.md for cross-task context and patterns
- See T-001_example_task.md for complete task spec example
