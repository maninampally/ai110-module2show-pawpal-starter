# PawPal+ UML Class Diagram

This is the simplified UML diagram showing all 9 classes and their relationships.

## Mermaid.js Code

```mermaid
classDiagram
    class Owner {
        -owner_id: str
        -name: str
        -daily_time_budget_minutes: int
        +set_time_budget()
        +get_available_time()
    }

    class Pet {
        -pet_id: str
        -name: str
        -species: str
        +update_pet_info()
        +get_care_needs_summary()
    }

    class CareTask {
        -task_id: str
        -title: str
        -priority: str
        -duration_minutes: int
        +validate()
        +mark_complete()
    }

    class TaskList {
        -tasks: list~CareTask~
        -pet_id: str
        +add_task()
        +get_tasks_by_priority()
        +get_total_duration()
    }

    class DailyConstraint {
        -date: date
        -available_minutes: int
        -allowed_time_windows: list
        +can_fit()
        +remaining_minutes()
    }

    class ScheduleEntry {
        -task: CareTask
        -start_time: datetime
        -end_time: datetime
        -reason_selected: str
        +duration()
        +to_display_text()
    }

    class DailyPlan {
        -date: date
        -entries: list~ScheduleEntry~
        -unscheduled_tasks: list~CareTask~
        +add_entry()
        +sort_by_time()
        +validate_plan()
    }

    class Scheduler {
        -strategy_name: str
        -priority_weights: dict
        +build_plan()
        +rank_tasks()
        +allocate_time_slots()
    }

    class PlanExplainer {
        -include_scoring_details: bool
        +explain_task_choice()
        +generate_plan_explanation()
    }

    Owner "1" --> "*" Pet : owns
    Pet "1" --> "1" TaskList : has
    TaskList "1" --> "*" CareTask : contains
    Scheduler --> TaskList : schedules
    Scheduler --> DailyConstraint : applies
    Scheduler --> DailyPlan : produces
    DailyPlan "1" --> "*" ScheduleEntry : contains
    ScheduleEntry --> CareTask : references
    PlanExplainer --> DailyPlan : explains
```

## How to Use

- **In VS Code:** Copy the mermaid code and preview with the Markdown Preview or Mermaid extension
- **Online:** Paste into [Mermaid Live Editor](https://mermaid.live)
- **In Documentation:** Include the code block in markdown files

## Key Relationships

| Relationship | Cardinality | Meaning |
|--------------|-------------|---------|
| Owner → Pet | 1 to many | One owner can have multiple pets |
| Pet → TaskList | 1 to 1 | Each pet has exactly one task list |
| TaskList → CareTask | 1 to many | Task list contains multiple tasks |
| Scheduler → DailyPlan | 1 to 1 | Scheduler produces a daily plan |
| DailyPlan → ScheduleEntry | 1 to many | Plan contains multiple scheduled entries |

## Class Layers

**Layer 1 - Profile Management:** Owner, Pet
**Layer 2 - Task Management:** CareTask, TaskList
**Layer 3 - Scheduling:** DailyConstraint, Scheduler
**Layer 4 - Output:** DailyPlan, ScheduleEntry, PlanExplainer
