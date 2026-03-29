from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time
from typing import Any


@dataclass
class Owner:
	owner_id: str
	name: str
	daily_time_budget_minutes: int
	preferred_time_windows: list[tuple[time, time]] = field(default_factory=list)
	notification_preferences: dict[str, Any] = field(default_factory=dict)

	def update_profile(self, name: str | None = None) -> None:
		pass

	def set_time_budget(self, minutes: int) -> None:
		pass

	def set_preferences(self, preferences: dict[str, Any]) -> None:
		pass

	def get_available_time(self) -> int:
		pass


@dataclass
class Pet:
	pet_id: str
	name: str
	species: str
	age: int
	health_notes: list[str] = field(default_factory=list)
	activity_level: str = "medium"

	def update_pet_info(self, name: str | None = None, age: int | None = None) -> None:
		pass

	def add_health_note(self, note: str) -> None:
		pass

	def get_care_needs_summary(self) -> str:
		pass


@dataclass
class CareTask:
	task_id: str
	title: str
	category: str
	duration_minutes: int
	priority: str
	due_time_optional: datetime | None = None
	frequency: str = "daily"
	is_required: bool = False
	notes: str = ""

	def validate(self) -> bool:
		pass

	def mark_complete(self) -> None:
		pass

	def update_task(self, **changes: Any) -> None:
		pass

	def is_overdue(self, current_time: datetime) -> bool:
		pass


@dataclass
class TaskList:
	tasks: list[CareTask] = field(default_factory=list)
	owner_id: str = ""
	pet_id: str = ""

	def add_task(self, task: CareTask) -> None:
		pass

	def edit_task(self, task_id: str, **changes: Any) -> None:
		pass

	def remove_task(self, task_id: str) -> None:
		pass

	def get_tasks_by_priority(self) -> list[CareTask]:
		pass

	def get_required_tasks(self) -> list[CareTask]:
		pass

	def get_total_duration(self) -> int:
		pass


@dataclass
class DailyConstraint:
	date: date
	available_minutes: int
	allowed_time_windows: list[tuple[time, time]] = field(default_factory=list)
	max_tasks_optional: int | None = None
	blocked_times: list[tuple[time, time]] = field(default_factory=list)

	def can_fit(self, task: CareTask) -> bool:
		pass

	def remaining_minutes(self) -> int:
		pass

	def apply_blocked_time(self) -> None:
		pass


@dataclass
class ScheduleEntry:
	task_id: str
	start_time: datetime
	end_time: datetime
	reason_selected: str = ""
	score: float = 0.0

	def duration(self) -> int:
		pass

	def overlaps_with(self, other_entry: ScheduleEntry) -> bool:
		pass

	def to_display_text(self) -> str:
		pass


@dataclass
class DailyPlan:
	date: date
	entries: list[ScheduleEntry] = field(default_factory=list)
	unscheduled_tasks: list[CareTask] = field(default_factory=list)
	total_scheduled_minutes: int = 0
	explanation_summary: str = ""

	def add_entry(self, entry: ScheduleEntry) -> None:
		pass

	def add_unscheduled_task(self, task: CareTask) -> None:
		pass

	def sort_by_time(self) -> None:
		pass

	def generate_summary(self) -> str:
		pass

	def validate_plan(self) -> bool:
		pass


class Scheduler:
	def __init__(
		self,
		strategy_name: str = "priority-first",
		priority_weights: dict[str, int] | None = None,
		constraint_rules: dict[str, Any] | None = None,
	) -> None:
		self.strategy_name = strategy_name
		self.priority_weights = priority_weights or {"high": 3, "medium": 2, "low": 1}
		self.constraint_rules = constraint_rules or {}

	def build_plan(self, task_list: TaskList, constraints: DailyConstraint) -> DailyPlan:
		pass

	def rank_tasks(self, tasks: list[CareTask]) -> list[CareTask]:
		pass

	def allocate_time_slots(self, tasks: list[CareTask], plan: DailyPlan) -> None:
		pass

	def handle_conflicts(self, plan: DailyPlan) -> None:
		pass

	def explain_decisions(self, plan: DailyPlan) -> str:
		pass


class PlanExplainer:
	def __init__(self, explanation_rules: dict[str, Any] | None = None, include_scoring_details: bool = True) -> None:
		self.explanation_rules = explanation_rules or {}
		self.include_scoring_details = include_scoring_details

	def explain_task_choice(self, task: CareTask, score: float) -> str:
		pass

	def explain_skipped_task(self, task: CareTask, reason: str) -> str:
		pass

	def generate_plan_explanation(self, plan: DailyPlan) -> str:
		pass
