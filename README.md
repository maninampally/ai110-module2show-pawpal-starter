# PawPal+ 🐾

PawPal+ is an intelligent pet care scheduling assistant that helps busy pet owners plan and organize daily tasks for their pets. The system combines constraint-based scheduling with algorithmic task prioritization to generate optimized daily care plans. PawPal+ includes built-in conflict detection, recurring task management, and detailed scheduling explanations to keep pet owners informed and on track.

## Features

- **Pet & Owner Profiles** — Register pets with species, age, activity level, and health notes; manage owner time availability
- **Task Management** — Create and organize pet care tasks with priority levels, duration estimates, and recurring schedules
- **Intelligent Scheduling** — Generate optimized daily schedules based on priority, required status, and time constraints
- **Conflict Detection** — Identify and display overlapping tasks in the generated schedule
- **Recurring Tasks** — Automatically generate next occurrences for daily and weekly tasks upon completion
- **Status Filtering** — Filter tasks by completion status to track progress and pending items
- **Scheduling Explanations** — View detailed reasoning behind scheduling decisions and why tasks were or weren't included

## Smarter Scheduling

PawPal+ implements four core algorithmic features to produce intelligent schedules. The **priority-first sorting** algorithm ranks tasks by required status and priority level (high → medium → low) to ensure critical care is never missed. The **conflict detection** system identifies overlapping schedule entries and alerts users to scheduling collisions. **Recurring task management** automatically creates next-day or next-week occurrences when daily or weekly tasks are marked complete, supporting consistent pet care routines. Finally, **status-based filtering** allows users to query and organize tasks by completion status, enabling flexible task organization and progress tracking.

## Setup

### Requirements

- Python 3.10+
- pip package manager

### Installation

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## How to Run

### Web Interface (Streamlit)

```bash
python -m streamlit run app.py
```

The app will open at `http://localhost:8502`. Use the tabs to:
1. Manage your pet profiles and health notes
2. Add and organize pet care tasks
3. Generate and review daily schedules

### Command Line (Main Script)

```bash
python main.py
```

## Testing PawPal+

Run the complete test suite with pytest:

```bash
python -m pytest tests/test_pawpal.py -v
```

The test suite includes 36 comprehensive tests covering core scheduling behaviors: task validation, priority sorting, recurring task generation, conflict detection, task filtering, and schedule planning. Test coverage includes both happy-path scenarios and edge cases to ensure reliability. **Confidence Level: ★★★★☆ (4/5)** — All critical behaviors have passing tests; additional edge cases and integration tests could further strengthen coverage.

## System Architecture

PawPal+ is built on a layered architecture with 9 core classes: `Owner`, `Pet`, `CareTask`, `TaskList`, `DailyConstraint`, `ScheduleEntry`, `DailyPlan`, `Scheduler`, and `PlanExplainer`. See [uml_final.md](uml_final.md) for the complete class diagram and relationships.

## Project Structure

```
.
├── pawpal_system.py       # Core scheduling logic and data models
├── app.py                 # Streamlit web interface
├── main.py                # Command-line interface (optional)
├── tests/
│   └── test_pawpal.py     # Comprehensive test suite
├── requirements.txt       # Python dependencies
├── uml_final.md          # System architecture diagram
└── README.md             # This file
```

## Key Methods & Algorithms

- `Scheduler.build_plan()` — Main scheduling algorithm that ranks and allocates tasks
- `Scheduler.sort_by_due_time()` — Sorts tasks with due times first (earliest), then by priority
- `Scheduler.detect_scheduling_conflicts()` — Identifies overlapping task entries
- `CareTask.create_next_occurrence()` — Generates next occurrence for recurring tasks
- `TaskList.get_tasks_by_status()` — Filters tasks by completion status

## Development Notes

This project demonstrates advanced scheduling, object-oriented design, and test-driven development practices. The implementation includes six layers: Profile Management, Task Management, Scheduling Constraints, Scheduling Output, Algorithmic Logic, and Explanation & Communication.
