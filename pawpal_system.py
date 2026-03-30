from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from typing import Any


# ============================================================================
# LAYER 1: PROFILE MANAGEMENT
# ============================================================================

@dataclass
class Owner:
	"""Represents a pet owner and their time availability."""

	owner_id: str
	name: str
	daily_time_budget_minutes: int
	pets: list[Pet] = field(default_factory=list)
	preferred_time_windows: list[tuple[time, time]] = field(default_factory=list)
	notification_preferences: dict[str, Any] = field(default_factory=dict)

	def update_profile(self, name: str | None = None) -> None:
		"""Update owner name or other profile settings."""
		pass

	def set_time_budget(self, minutes: int) -> None:
		"""Change daily available minutes for pet care."""
		pass

	def set_preferences(self, preferences: dict[str, Any]) -> None:
		"""Update notification preferences."""
		pass

	def get_available_time(self) -> int:
		"""Return current daily time budget in minutes."""
		pass


@dataclass
class Pet:
	"""Represents a pet and its basic information."""

	pet_id: str
	name: str
	species: str
	age: int
	health_notes: list[str] = field(default_factory=list)
	activity_level: str = "medium"

	def update_pet_info(self, name: str | None = None, age: int | None = None) -> None:
		"""Update pet's name or age."""
		pass

	def add_health_note(self, note: str) -> None:
		"""Log new health information for the pet."""
		pass

	def get_care_needs_summary(self) -> str:
		"""Return text description of pet's care requirements."""
		pass


# ============================================================================
# LAYER 2: TASK MANAGEMENT
# ============================================================================

@dataclass
class CareTask:
	"""Represents a single care activity (walk, feed, medication, etc.)."""

	task_id: str
	title: str
	category: str
	duration_minutes: int
	priority: str
	due_time_optional: datetime | None = None
	frequency: str = "daily"
	is_required: bool = False
	notes: str = ""
	completion_status: bool = False

	def validate(self) -> bool:
		"""Check if task data is valid (has required fields)."""
		pass

	def mark_complete(self) -> None:
		"""Record that task was completed."""
		pass

	def update_task(self, **changes: Any) -> None:
		"""Modify any task property."""
		pass

	def is_overdue(self, current_time: datetime) -> bool:
		"""Check if task is past its due time."""
		pass


class TaskList:
	"""Container for all tasks belonging to one pet."""

	def __init__(self, pet: Pet | None = None) -> None:
		"""Initialize an empty task list for a pet."""
		self.tasks: list[CareTask] = []
		self.pet: Pet | None = pet

	def add_task(self, task: CareTask) -> None:
		"""Add a new task to the list."""
		pass

	def edit_task(self, task_id: str, **changes: Any) -> None:
		"""Modify an existing task."""
		pass

	def remove_task(self, task_id: str) -> None:
		"""Delete a task by ID."""
		pass

	def get_tasks_by_priority(self) -> list[CareTask]:
		"""Return tasks sorted by priority (high → medium → low)."""
		pass

	def get_required_tasks(self) -> list[CareTask]:
		"""Return only tasks where is_required = True."""
		pass

	def get_total_duration(self) -> int:
		"""Sum total minutes needed for all tasks."""
		pass


# ============================================================================
# LAYER 3: SCHEDULING CONSTRAINTS
# ============================================================================

class DailyConstraint:
	"""Defines time availability and restrictions for a specific day."""

	def __init__(
		self,
		date: date,
		available_minutes: int,
		allowed_time_windows: list[tuple[time, time]] | None = None,
		max_tasks_optional: int | None = None,
		blocked_times: list[tuple[time, time]] | None = None,
	) -> None:
		"""Initialize daily constraints for scheduling."""
		self.date: date = date
		self.available_minutes: int = available_minutes
		self.allowed_time_windows: list[tuple[time, time]] = allowed_time_windows or []
		self.max_tasks_optional: int | None = max_tasks_optional
		self.blocked_times: list[tuple[time, time]] = blocked_times or []

	def can_fit(self, task: CareTask) -> bool:
		"""Check if a specific task fits within constraints."""
		pass

	def remaining_minutes(self) -> int:
		"""Calculate how many minutes are left after scheduled tasks."""
		pass


# ============================================================================
# LAYER 4: SCHEDULING OUTPUT
# ============================================================================

@dataclass
class ScheduleEntry:
	"""Represents one scheduled task with specific time and reasoning."""

	task: CareTask
	start_time: datetime
	end_time: datetime
	reason_selected: str = ""
	score: float = 0.0

	def duration(self) -> int:
		"""Return minutes this entry takes."""
		pass

	def overlaps_with(self, other_entry: ScheduleEntry) -> bool:
		"""Check if this entry conflicts with another ScheduleEntry."""
		pass

	def to_display_text(self) -> str:
		"""Format nicely for UI (e.g., '9:30 AM - Walk Buddy (20 min)')."""
		pass


@dataclass
class DailyPlan:
	"""The generated schedule for a day (output of Scheduler)."""

	date: date
	entries: list[ScheduleEntry] = field(default_factory=list)
	unscheduled_tasks: list[CareTask] = field(default_factory=list)
	total_scheduled_minutes: int = 0
	explanation_summary: str = ""

	def add_entry(self, entry: ScheduleEntry) -> None:
		"""Add a scheduled task to the plan."""
		pass

	def add_unscheduled_task(self, task: CareTask) -> None:
		"""Mark a task as not scheduled."""
		pass

	def sort_by_time(self) -> None:
		"""Sort entries chronologically."""
		pass

	def generate_summary(self) -> str:
		"""Create text summary of the plan."""
		pass

	def validate_plan(self) -> bool:
		"""Check for conflicts or errors in the plan."""
		pass


# ============================================================================
# LAYER 5: ALGORITHMIC LOGIC
# ============================================================================

class Scheduler:
	"""The 'brain' that ranks tasks and builds optimal daily schedules."""

	def __init__(
		self,
		strategy_name: str = "priority-first",
		priority_weights: dict[str, int] | None = None,
		constraint_rules: dict[str, Any] | None = None,
	) -> None:
		"""Initialize the scheduler with a strategy and parameters."""
		self.strategy_name: str = strategy_name
		self.priority_weights: dict[str, int] = priority_weights or {
			"high": 3,
			"medium": 2,
			"low": 1,
		}
		self.constraint_rules: dict[str, Any] = constraint_rules or {}

	def build_plan(self, task_list: TaskList, constraints: DailyConstraint) -> DailyPlan:
		"""Main method: takes tasks + constraints, returns optimized plan."""
		pass

	def rank_tasks(self, tasks: list[CareTask]) -> list[CareTask]:
		"""Sort tasks by priority and scoring logic."""
		pass

	def allocate_time_slots(self, tasks: list[CareTask], plan: DailyPlan) -> None:
		"""Assign start/end times to each task."""
		pass

	def handle_conflicts(self, plan: DailyPlan) -> None:
		"""Resolve overlapping tasks."""
		pass

	def explain_decisions(self, plan: DailyPlan) -> str:
		"""Generate reasoning for scheduling decisions."""
		pass


# ============================================================================
# LAYER 6: EXPLANATION & COMMUNICATION
# ============================================================================

class PlanExplainer:
	"""Generates human-readable explanations of scheduling decisions."""

	def __init__(
		self,
		explanation_rules: dict[str, Any] | None = None,
		include_scoring_details: bool = True,
	) -> None:
		"""Initialize the explainer with rules and options."""
		self.explanation_rules: dict[str, Any] = explanation_rules or {}
		self.include_scoring_details: bool = include_scoring_details

	def explain_task_choice(self, task: CareTask, score: float) -> str:
		"""Explain why this task was included in the schedule."""
		pass

	def explain_skipped_task(self, task: CareTask, reason: str) -> str:
		"""Explain why this task was not included in the schedule."""
		pass

	def generate_plan_explanation(self, plan: DailyPlan) -> str:
		"""Generate full explanation of the entire day's plan."""
		pass
