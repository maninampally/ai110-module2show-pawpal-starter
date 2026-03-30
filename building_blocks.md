# PawPal+ System Design: Classes and Methods

## Overview

This document outlines the 9 core classes for the PawPal+ pet care scheduling system. Each class is responsible for a specific aspect of the system, organized in layers from data storage to algorithmic logic to output presentation.

---

## Layer 1: Profile Management

### 1. Owner
**Purpose:** Represents a pet owner and their time availability.

**Attributes:**
- `owner_id: str` — Unique identifier for the owner
- `name: str` — Owner's name
- `daily_time_budget_minutes: int` — Minutes available per day for pet care (e.g., 120)
- `preferred_time_windows: list[tuple[time, time]]` — List of time slots when owner is available (e.g., [(9:00, 11:00), (18:00, 20:00)])
- `notification_preferences: dict[str, Any]` — Settings for how/when to notify owner

**Methods:**
- `update_profile(name: str | None = None) -> None` — Update owner name or settings
- `set_time_budget(minutes: int) -> None` — Change daily available minutes
- `set_preferences(preferences: dict[str, Any]) -> None` — Update notification settings
- `get_available_time() -> int` — Return current time budget remaining

---

### 2. Pet
**Purpose:** Represents a pet and its basic information.

**Attributes:**
- `pet_id: str` — Unique identifier for the pet
- `name: str` — Pet's name
- `species: str` — Pet type (dog, cat, rabbit, bird, etc.)
- `age: int` — Pet's age in years
- `health_notes: list[str]` — Medical/care notes (allergies, conditions, etc.)
- `activity_level: str` — Energy level: "low", "medium", or "high"

**Methods:**
- `update_pet_info(name: str | None = None, age: int | None = None) -> None` — Update pet's name or age
- `add_health_note(note: str) -> None` — Log new health information
- `get_care_needs_summary() -> str` — Return text description of pet's care requirements

---

## Layer 2: Task Management

### 3. CareTask
**Purpose:** Represents a single care activity (walk, feed, medication, etc.).

**Attributes:**
- `task_id: str` — Unique identifier for the task
- `title: str` — Task name (e.g., "Morning Walk", "Afternoon Feeding")
- `category: str` — Task type: "walk", "feeding", "medication", "grooming", "enrichment", "appointment"
- `duration_minutes: int` — How long the task takes in minutes
- `priority: str` — Task urgency: "high", "medium", or "low"
- `due_time_optional: datetime | None` — Specific time needed (None if flexible)
- `frequency: str` — How often: "daily", "weekly", "as-needed"
- `is_required: bool` — True if task must be done, False if optional
- `notes: str` — Additional details about the task
- `completion_status: bool` — Whether task was completed (default: False)

**Methods:**
- `validate() -> bool` — Check if task data is valid (has required fields)
- `mark_complete() -> None` — Record that task was completed
- `update_task(**changes: Any) -> None` — Modify any task property
- `is_overdue(current_time: datetime) -> bool` — Check if past due time

---

### 4. TaskList
**Purpose:** Container for all tasks belonging to one pet.

**Attributes:**
- `tasks: list[CareTask]` — List of all CareTask objects
- `owner_id: str` — Who owns these tasks
- `pet_id: str` — Which pet these tasks belong to

**Methods:**
- `add_task(task: CareTask) -> None` — Add a new task to the list
- `edit_task(task_id: str, **changes: Any) -> None` — Modify an existing task
- `remove_task(task_id: str) -> None` — Delete a task by ID
- `get_tasks_by_priority() -> list[CareTask]` — Return tasks sorted by priority (high → medium → low)
- `get_required_tasks() -> list[CareTask]` — Return only tasks where `is_required = True`
- `get_total_duration() -> int` — Sum total minutes needed for all tasks

---

## Layer 3: Scheduling Constraints

### 5. DailyConstraint
**Purpose:** Defines time availability and restrictions for scheduling on a specific day.

**Attributes:**
- `date: date` — Which day this constraint applies to
- `available_minutes: int` — Total time budget for the day
- `allowed_time_windows: list[tuple[time, time]]` — Time intervals when tasks can be scheduled
- `max_tasks_optional: int | None` — Maximum number of tasks to schedule (None = no limit)
- `blocked_times: list[tuple[time, time]]` — Time periods that are unavailable (meetings, other activities)

**Methods:**
- `can_fit(task: CareTask) -> bool` — Check if a specific task fits within constraints
- `remaining_minutes() -> int` — Calculate how many minutes are left after scheduled tasks
- `apply_blocked_time() -> None` — Mark time range as unavailable

---

## Layer 4: Scheduling Output

### 6. ScheduleEntry
**Purpose:** Represents one scheduled task with specific time and reasoning.

**Attributes:**
- `task_id: str` — Which task this schedules
- `start_time: datetime` — When task starts (e.g., 9:30 AM)
- `end_time: datetime` — When task ends (e.g., 10:00 AM)
- `reason_selected: str` — Why scheduler chose this task (e.g., "High priority, fits time window")
- `score: float` — Numeric score used for ranking tasks

**Methods:**
- `duration() -> int` — Return minutes this entry takes
- `overlaps_with(other_entry: ScheduleEntry) -> bool` — Check conflict with another ScheduleEntry
- `to_display_text() -> str` — Format nicely for UI (e.g., "9:30 AM - Walk Buddy (20 min)")

---

### 7. DailyPlan
**Purpose:** The generated schedule for a day (output of Scheduler).

**Attributes:**
- `date: date` — Which day this plan is for
- `entries: list[ScheduleEntry]` — List of scheduled tasks
- `unscheduled_tasks: list[CareTask]` — Tasks that didn't fit in the schedule
- `total_scheduled_minutes: int` — Sum of all scheduled task durations
- `explanation_summary: str` — Text explaining scheduling decisions

**Methods:**
- `add_entry(entry: ScheduleEntry) -> None` — Add a scheduled task
- `add_unscheduled_task(task: CareTask) -> None` — Mark a task as not scheduled
- `sort_by_time() -> None` — Sort entries chronologically
- `generate_summary() -> str` — Create text summary of the plan
- `validate_plan() -> bool` — Check for conflicts or errors

---

## Layer 5: Algorithmic Logic

### 8. Scheduler
**Purpose:** The "brain" that ranks tasks and builds optimal daily schedules.

**Attributes:**
- `strategy_name: str` — Algorithm type (e.g., "priority-first", "fit-as-many")
- `priority_weights: dict[str, int]` — How much each priority level matters (e.g., {"high": 3, "medium": 2, "low": 1})
- `constraint_rules: dict[str, Any]` — Custom scheduling rules

**Methods:**
- `build_plan(task_list: TaskList, constraints: DailyConstraint) -> DailyPlan` — **Main method:** Takes tasks + constraints, returns optimized plan
- `rank_tasks(tasks: list[CareTask]) -> list[CareTask]` — Sort tasks by priority and scoring
- `allocate_time_slots(tasks: list[CareTask], plan: DailyPlan) -> None` — Assign start/end times to each task
- `handle_conflicts(plan: DailyPlan) -> None` — Resolve overlapping tasks
- `explain_decisions(plan: DailyPlan) -> str` — Generate reasoning for scheduling decisions

---

## Layer 6: Explanation & Communication

### 9. PlanExplainer
**Purpose:** Generates human-readable explanations of scheduling decisions.

**Attributes:**
- `explanation_rules: dict[str, Any]` — Patterns for generating explanations
- `include_scoring_details: bool` — Whether to show scoring logic (default: True)

**Methods:**
- `explain_task_choice(task: CareTask, score: float) -> str` — Why was this task included? (e.g., "High priority, owner available 9-11 AM")
- `explain_skipped_task(task: CareTask, reason: str) -> str` — Why wasn't this task included? (e.g., "No time available, low priority")
- `generate_plan_explanation(plan: DailyPlan) -> str` — Full explanation of entire day's plan

---

## Data Flow Diagram

```
Owner
  └── creates Pets
      └── each Pet has TaskList
          └── TaskList contains CareTasks
              ↓
              User specifies DailyConstraint
              ↓
              Scheduler.build_plan(TaskList + DailyConstraint)
              ↓
              Produces DailyPlan
                  ├── entries: list[ScheduleEntry]
                  └── unscheduled_tasks: list[CareTask]
              ↓
              PlanExplainer.generate_plan_explanation()
              ↓
              Display in UI
```

---

## Implementation Priority

**Start simple → progress to complex:**

1. **Owner** — Basic getters/setters (easy)
2. **Pet** — Basic getters/setters (easy)
3. **CareTask** — Validation, mark_complete (medium)
4. **TaskList** — Collection management (medium)
5. **DailyConstraint** — Time logic (medium)
6. **Scheduler** — Core algorithm (hard) ⭐
7. **DailyPlan & ScheduleEntry** — Output formatting (medium)
8. **PlanExplainer** — Text generation (easy)

---

## Key Design Patterns

- **Dataclass Pattern** — All classes use `@dataclass` for clean attribute definition
- **Container Pattern** — TaskList contains CareTask objects; Owner contains Pets
- **Separation of Concerns** — Data layer (Owner, Pet) separate from logic layer (Scheduler)
- **Strategy Pattern** — Scheduler uses different strategies (priority-first, fit-as-many, etc.)
- **Factory Pattern** — Look for opportunities to generate objects (e.g., creating ScheduleEntry from CareTask)

---

## Next Steps

See `pawpal_system.py` for class stubs. Implementation begins by filling in method bodies following this design.
