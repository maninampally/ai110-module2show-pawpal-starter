# PawPal+ Final UML Class Diagram

This is the updated UML diagram reflecting the final implementation of all 9 classes and their relationships, including new methods and attributes.

## Mermaid.js Code

```mermaid
classDiagram
    class Owner {
        -owner_id: str
        -name: str
        -daily_time_budget_minutes: int
        -pets: list~Pet~
        -preferred_time_windows: list~tuple~
        -notification_preferences: dict
        +update_profile()
        +set_time_budget()
        +set_preferences()
        +get_available_time()
    }

    class Pet {
        -pet_id: str
        -name: str
        -species: str
        -age: int
        -health_notes: list~str~
        -activity_level: str
        +update_pet_info()
        +add_health_note()
        +get_care_needs_summary()
    }

    class CareTask {
        -task_id: str
        -title: str
        -category: str
        -duration_minutes: int
        -priority: str
        -due_time_optional: datetime | None
        -frequency: str
        -is_required: bool
        -notes: str
        -completion_status: bool
        +validate()
        +mark_complete()
        +create_next_occurrence()
        +update_task()
        +is_overdue()
    }

    class TaskList {
        -tasks: list~CareTask~
        -pet: Pet | None
        +add_task()
        +edit_task()
        +remove_task()
        +get_tasks_by_priority()
        +get_required_tasks()
        +get_tasks_by_status()
        +get_total_duration()
    }

    class DailyConstraint {
        -date: date
        -available_minutes: int
        -allowed_time_windows: list~tuple~
        -max_tasks_optional: int | None
        -blocked_times: list~tuple~
        +can_fit()
        +remaining_minutes()
    }

    class ScheduleEntry {
        -task: CareTask
        -start_time: datetime
        -end_time: datetime
        -reason_selected: str
        -score: float
        +duration()
        +overlaps_with()
        +to_display_text()
    }

    class DailyPlan {
        -date: date
        -entries: list~ScheduleEntry~
        -unscheduled_tasks: list~CareTask~
        -total_scheduled_minutes: int
        -explanation_summary: str
        +add_entry()
        +add_unscheduled_task()
        +sort_by_time()
        +generate_summary()
        +validate_plan()
    }

    class Scheduler {
        -strategy_name: str
        -priority_weights: dict~str,int~
        -constraint_rules: dict~str,Any~
        +build_plan()
        +rank_tasks()
        +sort_by_due_time()
        +filter_tasks_by_pet()
        +allocate_time_slots()
        +handle_conflicts()
        +detect_scheduling_conflicts()
        +explain_decisions()
    }

    class PlanExplainer {
        -explanation_rules: dict~str,Any~
        -include_scoring_details: bool
        +explain_task_choice()
        +explain_skipped_task()
        +generate_plan_explanation()
    }

    Owner "1" --> "*" Pet : owns
    Pet "1" --> "1" TaskList : has
    TaskList "1" --> "*" CareTask : contains
    Scheduler --> TaskList : schedules
    Scheduler --> DailyConstraint : applies
    Scheduler --> DailyPlan : produces
    DailyPlan "1" --> "*" ScheduleEntry : contains
    DailyPlan "1" --> "*" CareTask : unscheduled
    ScheduleEntry --> CareTask : references
    PlanExplainer --> DailyPlan : explains
```

## Updates from Original Design

### Owner
- **New attributes:** `pets` (list), `preferred_time_windows`, `notification_preferences`
- **New methods:** `set_preferences()`, `update_profile()`

### Pet
- **New attributes:** `health_notes` (list), `activity_level`
- **New methods:** `add_health_note()`

### CareTask
- **New attributes:** `due_time_optional`, `frequency`, `is_required`, `notes`, `completion_status`
- **New methods:** `create_next_occurrence()`, `update_task()`, `is_overdue()`
- **Behavior:** Recurring task support (daily, weekly, as-needed)

### TaskList
- **Changed:** `pet_id` (str) → `pet` (Pet | None reference)
- **New methods:** `edit_task()`, `get_required_tasks()`, `get_tasks_by_status()`

### ScheduleEntry
- **New attributes:** `score` (float)
- **New methods:** `overlaps_with()`

### DailyPlan
- **New attributes:** `total_scheduled_minutes`, `explanation_summary`
- **New methods:** `add_unscheduled_task()`, `generate_summary()`
- **Relationship:** Explicit link to unscheduled CareTask objects

### Scheduler
- **New attributes:** `constraint_rules` (dict)
- **New methods:** `sort_by_due_time()`, `filter_tasks_by_pet()`, `handle_conflicts()`, `detect_scheduling_conflicts()`, `explain_decisions()`
- **Functionality:** Enhanced algorithmic logic for intelligent task ranking and conflict detection

### PlanExplainer
- **New attributes:** `explanation_rules` (dict)
- **New methods:** `explain_skipped_task()`

## Key Relationships
- **Owner** manages **Pet**(s) — 1-to-many relationship
- **Pet** has **TaskList** — 1-to-1 relationship
- **TaskList** contains **CareTask**(s) — 1-to-many relationship
- **Scheduler** processes **TaskList** and applies **DailyConstraint** to produce **DailyPlan**
- **DailyPlan** contains **ScheduleEntry**(s) and unscheduled **CareTask**(s)
- **ScheduleEntry** references specific **CareTask**
- **PlanExplainer** generates explanations for **DailyPlan**
