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
		if name is not None:
			self.name = name

	def set_time_budget(self, minutes: int) -> None:
		"""Change daily available minutes for pet care."""
		self.daily_time_budget_minutes = minutes

	def set_preferences(self, preferences: dict[str, Any]) -> None:
		"""Update notification preferences."""
		self.notification_preferences = preferences

	def get_available_time(self) -> int:
		"""Return current daily time budget in minutes."""
		return self.daily_time_budget_minutes


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
		if name is not None:
			self.name = name
		if age is not None:
			self.age = age

	def add_health_note(self, note: str) -> None:
		"""Log new health information for the pet."""
		self.health_notes.append(note)

	def get_care_needs_summary(self) -> str:
		"""Return text description of pet's care requirements."""
		notes_str = "; ".join(self.health_notes) if self.health_notes else "No notes"
		return f"{self.name} ({self.species}, age {self.age}) — activity: {self.activity_level}, notes: {notes_str}"



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
		return bool(self.title) and self.duration_minutes > 0

	def mark_complete(self) -> CareTask | None:
		"""Record that task was completed and return the next occurrence if recurring."""
		self.completion_status = True
		return self.create_next_occurrence()

	def create_next_occurrence(self) -> CareTask | None:
		"""Create the next occurrence of a recurring task."""
		if self.frequency == "as-needed" or self.due_time_optional is None:
			return None
		
		if self.frequency == "daily":
			next_due_time = self.due_time_optional + timedelta(days=1)
		elif self.frequency == "weekly":
			next_due_time = self.due_time_optional + timedelta(days=7)
		else:
			return None
		
		return CareTask(
			task_id=f"{self.task_id}_next",
			title=self.title,
			category=self.category,
			duration_minutes=self.duration_minutes,
			priority=self.priority,
			due_time_optional=next_due_time,
			frequency=self.frequency,
			is_required=self.is_required,
			notes=self.notes,
			completion_status=False,
		)

	def update_task(self, **changes: Any) -> None:
		"""Modify any task property."""
		for key, value in changes.items():
			if hasattr(self, key):
				setattr(self, key, value)

	def is_overdue(self, current_time: datetime) -> bool:
		"""Check if task is past its due time."""
		if self.due_time_optional is None:
			return False
		return self.due_time_optional < current_time


class TaskList:
	"""Container for all tasks belonging to one pet."""

	def __init__(self, pet: Pet | None = None) -> None:
		"""Initialize an empty task list for a pet."""
		self.tasks: list[CareTask] = []
		self.pet: Pet | None = pet

	def add_task(self, task: CareTask) -> None:
		"""Add a new task to the list."""
		self.tasks.append(task)

	def edit_task(self, task_id: str, **changes: Any) -> None:
		"""Modify an existing task. If marking complete, auto-add next occurrence if recurring."""
		for task in self.tasks:
			if task.task_id == task_id:
				if changes.get('completion_status') == True and not task.completion_status:
					next_task = task.mark_complete()
					task.update_task(**changes)
					if next_task is not None:
						self.add_task(next_task)
				else:
					task.update_task(**changes)
				return

	def remove_task(self, task_id: str) -> None:
		"""Delete a task by ID."""
		self.tasks = [task for task in self.tasks if task.task_id != task_id]

	def get_tasks_by_priority(self) -> list[CareTask]:
		"""Return tasks sorted by priority (high → medium → low)."""
		priority_order = {"high": 0, "medium": 1, "low": 2}
		return sorted(self.tasks, key=lambda t: priority_order.get(t.priority, 3))

	def get_required_tasks(self) -> list[CareTask]:
		"""Return only tasks where is_required = True."""
		return [task for task in self.tasks if task.is_required]

	def get_tasks_by_status(self, completed: bool) -> list[CareTask]:
		"""Return only tasks where completion_status matches the parameter."""
		return [task for task in self.tasks if task.completion_status == completed]

	def get_total_duration(self) -> int:
		"""Sum total minutes needed for all tasks."""
		return sum(task.duration_minutes for task in self.tasks)



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
		return task.duration_minutes <= self.available_minutes

	def remaining_minutes(self) -> int:
		"""Calculate how many minutes are left after scheduled tasks."""
		return self.available_minutes



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
		delta = self.end_time - self.start_time
		return int(delta.total_seconds() / 60)

	def overlaps_with(self, other_entry: ScheduleEntry) -> bool:
		"""Check if this entry conflicts with another ScheduleEntry."""
		return not (self.end_time <= other_entry.start_time or self.start_time >= other_entry.end_time)

	def to_display_text(self) -> str:
		"""Format nicely for UI (e.g., '9:30 AM - Walk Buddy (20 min)')."""
		start_str = self.start_time.strftime("%H:%M")
		end_str = self.end_time.strftime("%H:%M")
		return f"{start_str} - {end_str} | {self.task.title} ({self.duration()} min)"


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
		self.entries.append(entry)
		self.total_scheduled_minutes += entry.duration()

	def add_unscheduled_task(self, task: CareTask) -> None:
		"""Mark a task as not scheduled."""
		self.unscheduled_tasks.append(task)

	def sort_by_time(self) -> None:
		"""Sort entries chronologically."""
		self.entries.sort(key=lambda e: e.start_time)

	def generate_summary(self) -> str:
		"""Create text summary of the plan."""
		self.sort_by_time()
		summary_lines = [f"Daily Plan for {self.date}"]
		summary_lines.append("=" * 50)
		for entry in self.entries:
			summary_lines.append(entry.to_display_text())
		if self.unscheduled_tasks:
			summary_lines.append("\nUnscheduled Tasks:")
			for task in self.unscheduled_tasks:
				summary_lines.append(f"  - {task.title} ({task.priority} priority, {task.duration_minutes} min)")
		summary_lines.append(f"\nTotal Scheduled: {self.total_scheduled_minutes} minutes")
		return "\n".join(summary_lines)

	def validate_plan(self) -> bool:
		"""Check for conflicts or errors in the plan."""
		for i, entry1 in enumerate(self.entries):
			for entry2 in self.entries[i + 1 :]:
				if entry1.overlaps_with(entry2):
					return False
		return True


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
		ranked_tasks = self.rank_tasks(task_list.tasks)
		plan = DailyPlan(date=constraints.date)
		
		# Start scheduling at 06:00
		current_time = datetime.combine(constraints.date, time(6, 0))
		end_of_day = datetime.combine(constraints.date, time(22, 0))
		available_minutes = constraints.available_minutes
		
		for task in ranked_tasks:
			if current_time.time() >= time(22, 0):
				plan.add_unscheduled_task(task)
				continue
			
			# Check if task fits
			if task.duration_minutes <= available_minutes:
				# Create schedule entry
				task_end = current_time + timedelta(minutes=task.duration_minutes)
				
				# Don't go past 22:00
				if task_end > end_of_day:
					plan.add_unscheduled_task(task)
					continue
				
				entry = ScheduleEntry(
					task=task,
					start_time=current_time,
					end_time=task_end,
					reason_selected=f"Priority: {task.priority}, Required: {task.is_required}",
					score=self.priority_weights.get(task.priority, 0),
				)
				plan.add_entry(entry)
				available_minutes -= task.duration_minutes
				current_time = task_end
			else:
				plan.add_unscheduled_task(task)
		
		self.handle_conflicts(plan)
		plan.explanation_summary = self.explain_decisions(plan)
		return plan

	def rank_tasks(self, tasks: list[CareTask]) -> list[CareTask]:
		"""Sort tasks by priority and scoring logic."""
		# Sort: required first, then by priority
		priority_order = {"high": 0, "medium": 1, "low": 2}
		return sorted(
			tasks,
			key=lambda t: (not t.is_required, priority_order.get(t.priority, 3))
		)

	def sort_by_due_time(self, tasks: list[CareTask]) -> list[CareTask]:
		"""Sort tasks so those with due_time_optional come first (earliest first),
		then tasks without a due time sorted by priority."""
		priority_order = {"high": 0, "medium": 1, "low": 2}
		
		# Separate tasks with due times and without
		tasks_with_due = [t for t in tasks if t.due_time_optional is not None]
		tasks_without_due = [t for t in tasks if t.due_time_optional is None]
		
		# Sort tasks with due time by the due_time_optional
		tasks_with_due.sort(key=lambda t: t.due_time_optional)
		
		# Sort tasks without due time by priority
		tasks_without_due.sort(key=lambda t: priority_order.get(t.priority, 3))
		
		# Combine: due times first, then no due times
		return tasks_with_due + tasks_without_due

	def filter_tasks_by_pet(self, tasks: list[CareTask], pet_name: str) -> list[CareTask]:
		"""Return only tasks where title contains the pet name (case-insensitive)."""
		pet_name_lower = pet_name.lower()
		return [task for task in tasks if pet_name_lower in task.title.lower()]

	def allocate_time_slots(self, tasks: list[CareTask], plan: DailyPlan) -> None:
		"""Assign start/end times to each task."""
		# This is handled in build_plan
		pass

	def handle_conflicts(self, plan: DailyPlan) -> None:
		"""Resolve overlapping tasks."""
		for i, entry1 in enumerate(plan.entries):
			for entry2 in plan.entries[i + 1 :]:
				if entry1.overlaps_with(entry2):
					entry1.reason_selected += " [CONFLICT]"
					entry2.reason_selected += " [CONFLICT]"

	def detect_scheduling_conflicts(self, plan: DailyPlan) -> list[dict[str, str]]:
		"""Detect overlapping tasks and return detailed conflict information."""
		conflicts = []
		
		for i, entry1 in enumerate(plan.entries):
			for entry2 in plan.entries[i + 1:]:
				if entry1.overlaps_with(entry2):
					time_1 = f"{entry1.start_time.strftime('%H:%M')} - {entry1.end_time.strftime('%H:%M')}"
					time_2 = f"{entry2.start_time.strftime('%H:%M')} - {entry2.end_time.strftime('%H:%M')}"
					
					conflict_dict = {
						"task_1": entry1.task.title,
						"task_2": entry2.task.title,
						"time_1": time_1,
						"time_2": time_2,
						"message": f"⚠️ Conflict: {entry1.task.title} overlaps with {entry2.task.title}"
					}
					conflicts.append(conflict_dict)
		
		return conflicts

	def explain_decisions(self, plan: DailyPlan) -> str:
		"""Generate reasoning for scheduling decisions."""
		lines = ["Scheduling Summary:"]
		lines.append(f"✓ Scheduled ({len(plan.entries)} tasks, {plan.total_scheduled_minutes} min):")
		for entry in plan.entries:
			lines.append(f"  - {entry.task.title}: {entry.reason_selected}")
		if plan.unscheduled_tasks:
			lines.append(f"✗ Unscheduled ({len(plan.unscheduled_tasks)} tasks):")
			for task in plan.unscheduled_tasks:
				lines.append(f"  - {task.title}: No time remaining")
		return "\n".join(lines)


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
		reason = f"✓ {task.title} scheduled (score: {score})"
		if task.is_required:
			reason += " — Required task"
		reason += f" — Priority: {task.priority}"
		return reason

	def explain_skipped_task(self, task: CareTask, reason: str) -> str:
		"""Explain why this task was not included in the schedule."""
		return f"✗ {task.title} not scheduled — {reason}"

	def generate_plan_explanation(self, plan: DailyPlan) -> str:
		"""Generate full explanation of the entire day's plan."""
		lines = [f"Plan for {plan.date}:", ""]
		lines.append(f"Total scheduled: {plan.total_scheduled_minutes} minutes")
		lines.append(f"Scheduled tasks: {len(plan.entries)}")
		lines.append(f"Unscheduled tasks: {len(plan.unscheduled_tasks)}")
		lines.append("")
		lines.append(plan.explanation_summary)
		return "\n".join(lines)
