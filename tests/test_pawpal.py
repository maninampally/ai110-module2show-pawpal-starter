"""
PawPal+ Test Suite
Tests for core scheduling functionality using pytest.
"""

import pytest
from datetime import date, datetime, time, timedelta
from pawpal_system import (
    Owner, Pet, CareTask, TaskList, DailyConstraint,
    Scheduler, ScheduleEntry, DailyPlan, PlanExplainer
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def owner():
    """Create a test owner."""
    return Owner(
        owner_id="test_owner_001",
        name="Test Owner",
        daily_time_budget_minutes=120,
    )


@pytest.fixture
def pet():
    """Create a test pet."""
    return Pet(
        pet_id="test_pet_001",
        name="Test Pet",
        species="dog",
        age=3,
        activity_level="high",
    )


@pytest.fixture
def task_high():
    """Create a high priority task."""
    return CareTask(
        task_id="task_high",
        title="High Priority Task",
        category="walk",
        duration_minutes=30,
        priority="high",
        is_required=True,
    )


@pytest.fixture
def task_medium():
    """Create a medium priority task."""
    return CareTask(
        task_id="task_medium",
        title="Medium Priority Task",
        category="feeding",
        duration_minutes=20,
        priority="medium",
        is_required=False,
    )


@pytest.fixture
def task_low():
    """Create a low priority task."""
    return CareTask(
        task_id="task_low",
        title="Low Priority Task",
        category="enrichment",
        duration_minutes=15,
        priority="low",
        is_required=False,
    )


@pytest.fixture
def task_list(pet):
    """Create a task list for a pet."""
    return TaskList(pet=pet)


@pytest.fixture
def daily_constraint():
    """Create a daily constraint."""
    return DailyConstraint(
        date=date.today(),
        available_minutes=120,
    )


@pytest.fixture
def scheduler():
    """Create a scheduler."""
    return Scheduler(strategy_name="priority-first")


# ============================================================================
# CARETASK TESTS
# ============================================================================

class TestCareTask:
    """Tests for CareTask class."""

    def test_validate_valid_task(self, task_high):
        """Test that a valid task passes validation."""
        assert task_high.validate() is True

    def test_validate_invalid_title(self):
        """Test that a task with no title fails validation."""
        task = CareTask(
            task_id="invalid",
            title="",
            category="walk",
            duration_minutes=30,
            priority="high",
        )
        assert task.validate() is False

    def test_validate_invalid_duration(self):
        """Test that a task with zero duration fails validation."""
        task = CareTask(
            task_id="invalid",
            title="Task",
            category="walk",
            duration_minutes=0,
            priority="high",
        )
        assert task.validate() is False

    def test_mark_complete(self, task_high):
        """Test that marking a task complete changes completion_status."""
        assert task_high.completion_status is False
        task_high.mark_complete()
        assert task_high.completion_status is True

    def test_update_task(self, task_high):
        """Test that update_task modifies attributes."""
        assert task_high.duration_minutes == 30
        task_high.update_task(duration_minutes=45)
        assert task_high.duration_minutes == 45

    def test_is_overdue_with_no_due_time(self, task_high):
        """Test that a task with no due time is never overdue."""
        now = datetime.now()
        assert task_high.is_overdue(now) is False

    def test_is_overdue_when_past_due(self, task_high):
        """Test that a task is overdue if current time is past due time."""
        past_time = datetime.now()
        future_time = past_time + timedelta(hours=1)
        task_high.due_time_optional = past_time
        assert task_high.is_overdue(future_time) is True

    def test_is_not_overdue_when_before_due(self, task_high):
        """Test that a task is not overdue if current time is before due time."""
        past_time = datetime.now()
        future_time = past_time + timedelta(hours=1)
        task_high.due_time_optional = future_time
        assert task_high.is_overdue(past_time) is False


# ============================================================================
# TASKLIST TESTS
# ============================================================================

class TestTaskList:
    """Tests for TaskList class."""

    def test_add_task(self, task_list, task_high):
        """Test that adding a task increases task count."""
        assert len(task_list.tasks) == 0
        task_list.add_task(task_high)
        assert len(task_list.tasks) == 1

    def test_remove_task(self, task_list, task_high, task_medium):
        """Test that removing a task decreases task count."""
        task_list.add_task(task_high)
        task_list.add_task(task_medium)
        assert len(task_list.tasks) == 2
        task_list.remove_task(task_high.task_id)
        assert len(task_list.tasks) == 1

    def test_get_tasks_by_priority(self, task_list, task_high, task_medium, task_low):
        """Test that tasks are sorted correctly by priority."""
        task_list.add_task(task_low)
        task_list.add_task(task_high)
        task_list.add_task(task_medium)
        sorted_tasks = task_list.get_tasks_by_priority()
        assert sorted_tasks[0].priority == "high"
        assert sorted_tasks[1].priority == "medium"
        assert sorted_tasks[2].priority == "low"

    def test_get_required_tasks(self, task_list, task_high, task_medium):
        """Test that only required tasks are returned."""
        task_list.add_task(task_high)
        task_list.add_task(task_medium)
        required = task_list.get_required_tasks()
        assert len(required) == 1
        assert required[0].task_id == "task_high"

    def test_get_total_duration(self, task_list, task_high, task_medium, task_low):
        """Test that total duration is calculated correctly."""
        task_list.add_task(task_high)
        task_list.add_task(task_medium)
        task_list.add_task(task_low)
        total = task_list.get_total_duration()
        assert total == 65  # 30 + 20 + 15


# ============================================================================
# SCHEDULEENTRY TESTS
# ============================================================================

class TestScheduleEntry:
    """Tests for ScheduleEntry class."""

    def test_duration(self, task_high):
        """Test that duration is calculated correctly."""
        start = datetime(2026, 3, 30, 6, 0)
        end = datetime(2026, 3, 30, 6, 30)
        entry = ScheduleEntry(task=task_high, start_time=start, end_time=end)
        assert entry.duration() == 30

    def test_overlaps_with_yes(self, task_high, task_medium):
        """Test that overlapping entries are detected."""
        start1 = datetime(2026, 3, 30, 6, 0)
        end1 = datetime(2026, 3, 30, 6, 30)
        entry1 = ScheduleEntry(task=task_high, start_time=start1, end_time=end1)

        start2 = datetime(2026, 3, 30, 6, 15)
        end2 = datetime(2026, 3, 30, 6, 45)
        entry2 = ScheduleEntry(task=task_medium, start_time=start2, end_time=end2)

        assert entry1.overlaps_with(entry2) is True

    def test_overlaps_with_no(self, task_high, task_medium):
        """Test that non-overlapping entries are not flagged."""
        start1 = datetime(2026, 3, 30, 6, 0)
        end1 = datetime(2026, 3, 30, 6, 30)
        entry1 = ScheduleEntry(task=task_high, start_time=start1, end_time=end1)

        start2 = datetime(2026, 3, 30, 6, 30)
        end2 = datetime(2026, 3, 30, 7, 0)
        entry2 = ScheduleEntry(task=task_medium, start_time=start2, end_time=end2)

        assert entry1.overlaps_with(entry2) is False

    def test_to_display_text(self, task_high):
        """Test that display text is formatted correctly."""
        start = datetime(2026, 3, 30, 6, 0)
        end = datetime(2026, 3, 30, 6, 30)
        entry = ScheduleEntry(task=task_high, start_time=start, end_time=end)
        display = entry.to_display_text()
        assert "06:00" in display
        assert "06:30" in display
        assert "High Priority Task" in display
        assert "30 min" in display


# ============================================================================
# DAILYPLAN TESTS
# ============================================================================

class TestDailyPlan:
    """Tests for DailyPlan class."""

    def test_add_entry(self, task_high):
        """Test that adding entries updates total scheduled minutes."""
        plan = DailyPlan(date=date.today())
        start = datetime(2026, 3, 30, 6, 0)
        end = datetime(2026, 3, 30, 6, 30)
        entry = ScheduleEntry(task=task_high, start_time=start, end_time=end)

        assert plan.total_scheduled_minutes == 0
        plan.add_entry(entry)
        assert plan.total_scheduled_minutes == 30

    def test_validate_plan_no_conflicts(self, task_high, task_medium):
        """Test that a plan with no conflicts validates."""
        plan = DailyPlan(date=date.today())
        start1 = datetime(2026, 3, 30, 6, 0)
        end1 = datetime(2026, 3, 30, 6, 30)
        entry1 = ScheduleEntry(task=task_high, start_time=start1, end_time=end1)

        start2 = datetime(2026, 3, 30, 6, 30)
        end2 = datetime(2026, 3, 30, 6, 50)
        entry2 = ScheduleEntry(task=task_medium, start_time=start2, end_time=end2)

        plan.add_entry(entry1)
        plan.add_entry(entry2)
        assert plan.validate_plan() is True

    def test_validate_plan_with_conflicts(self, task_high, task_medium):
        """Test that a plan with conflicts fails validation."""
        plan = DailyPlan(date=date.today())
        start1 = datetime(2026, 3, 30, 6, 0)
        end1 = datetime(2026, 3, 30, 6, 30)
        entry1 = ScheduleEntry(task=task_high, start_time=start1, end_time=end1)

        start2 = datetime(2026, 3, 30, 6, 15)
        end2 = datetime(2026, 3, 30, 6, 45)
        entry2 = ScheduleEntry(task=task_medium, start_time=start2, end_time=end2)

        plan.add_entry(entry1)
        plan.add_entry(entry2)
        assert plan.validate_plan() is False


# ============================================================================
# SCHEDULER TESTS
# ============================================================================

class TestScheduler:
    """Tests for Scheduler class."""

    def test_rank_tasks_required_first(self, task_high, task_medium):
        """Test that required tasks are ranked before optional tasks."""
        tasks = [task_medium, task_high]
        scheduler = Scheduler()
        ranked = scheduler.rank_tasks(tasks)
        assert ranked[0].is_required is True
        assert ranked[1].is_required is False

    def test_rank_tasks_priority_order(self, task_high, task_medium, task_low):
        """Test that tasks are ranked by priority."""
        tasks = [task_low, task_high, task_medium]
        scheduler = Scheduler()
        ranked = scheduler.rank_tasks(tasks)
        assert ranked[0].priority == "high"
        assert ranked[1].priority == "medium"
        assert ranked[2].priority == "low"

    def test_build_plan_schedules_tasks(self, task_list, task_high, daily_constraint, scheduler):
        """Test that build_plan creates schedule entries."""
        task_list.add_task(task_high)
        plan = scheduler.build_plan(task_list, daily_constraint)
        assert len(plan.entries) > 0
        assert len(plan.entries) == 1

    def test_build_plan_respects_time_limit(self, task_list, daily_constraint, scheduler):
        """Test that build_plan respects available time."""
        # Add task that takes 100 minutes
        long_task = CareTask(
            task_id="long_task",
            title="Long Task",
            category="walk",
            duration_minutes=100,
            priority="high",
            is_required=True,
        )
        task_list.add_task(long_task)

        # Add task that takes 50 minutes (total 150, exceeds 120 limit)
        big_task = CareTask(
            task_id="big_task",
            title="Big Task",
            category="feeding",
            duration_minutes=50,
            priority="medium",
            is_required=False,
        )
        task_list.add_task(big_task)

        plan = scheduler.build_plan(task_list, daily_constraint)
        assert plan.total_scheduled_minutes <= daily_constraint.available_minutes


# ============================================================================
# PET TESTS
# ============================================================================

class TestPet:
    """Tests for Pet class."""

    def test_add_health_note(self, pet):
        """Test that health notes can be added."""
        assert len(pet.health_notes) == 0
        pet.add_health_note("Allergy to chicken")
        assert len(pet.health_notes) == 1
        assert "Allergy to chicken" in pet.health_notes

    def test_update_pet_info(self, pet):
        """Test that pet info can be updated."""
        pet.update_pet_info(name="New Name", age=4)
        assert pet.name == "New Name"
        assert pet.age == 4

    def test_get_care_needs_summary(self, pet):
        """Test that care needs summary is generated."""
        pet.add_health_note("Needs daily walks")
        summary = pet.get_care_needs_summary()
        assert pet.name in summary
        assert pet.species in summary
        assert str(pet.age) in summary


# ============================================================================
# OWNER TESTS
# ============================================================================

class TestOwner:
    """Tests for Owner class."""

    def test_set_time_budget(self, owner):
        """Test that time budget can be updated."""
        assert owner.daily_time_budget_minutes == 120
        owner.set_time_budget(150)
        assert owner.daily_time_budget_minutes == 150

    def test_get_available_time(self, owner):
        """Test that available time is returned correctly."""
        time_available = owner.get_available_time()
        assert time_available == 120

    def test_update_profile(self, owner):
        """Test that owner profile can be updated."""
        owner.update_profile(name="New Name")
        assert owner.name == "New Name"


# ============================================================================
# BEHAVIOR TESTS: SORTING (sort_by_due_time)
# ============================================================================

class TestSortByDueTime:
    """Tests for sort_by_due_time() sorting behavior."""

    @pytest.fixture
    def task_with_early_due(self):
        """Task with early due time."""
        return CareTask(
            task_id="task_early",
            title="Early Task",
            category="walk",
            duration_minutes=20,
            priority="low",
            due_time_optional=datetime(2026, 3, 30, 8, 0),
        )

    @pytest.fixture
    def task_with_late_due(self):
        """Task with late due time."""
        return CareTask(
            task_id="task_late",
            title="Late Task",
            category="feeding",
            duration_minutes=20,
            priority="high",
            due_time_optional=datetime(2026, 3, 30, 16, 0),
        )

    @pytest.fixture
    def task_no_due_high_priority(self):
        """Task without due time, high priority."""
        return CareTask(
            task_id="no_due_high",
            title="No Due High",
            category="enrichment",
            duration_minutes=20,
            priority="high",
        )

    @pytest.fixture
    def task_no_due_low_priority(self):
        """Task without due time, low priority."""
        return CareTask(
            task_id="no_due_low",
            title="No Due Low",
            category="enrichment",
            duration_minutes=20,
            priority="low",
        )

    def test_sort_by_due_time_earliest_first(self, task_with_early_due, task_with_late_due):
        # Verifies that tasks with due times are sorted chronologically earliest-first
        scheduler = Scheduler()
        tasks = [task_with_late_due, task_with_early_due]
        sorted_tasks = scheduler.sort_by_due_time(tasks)
        assert sorted_tasks[0].due_time_optional == datetime(2026, 3, 30, 8, 0)
        assert sorted_tasks[1].due_time_optional == datetime(2026, 3, 30, 16, 0)

    def test_sort_by_due_time_then_priority(self, task_with_early_due, task_no_due_high_priority, task_no_due_low_priority):
        # Verifies that tasks without due times follow timed tasks and are sorted by priority
        scheduler = Scheduler()
        tasks = [task_no_due_low_priority, task_with_early_due, task_no_due_high_priority]
        sorted_tasks = scheduler.sort_by_due_time(tasks)
        assert sorted_tasks[0] == task_with_early_due
        assert sorted_tasks[1].priority == "high"
        assert sorted_tasks[2].priority == "low"


# ============================================================================
# BEHAVIOR TESTS: RECURRING TASKS
# ============================================================================

class TestRecurringTasks:
    """Tests for create_next_occurrence() and mark_complete() behavior."""

    def test_marking_daily_task_returns_next_with_incremented_due(self):
        # Verifies that marking a daily task complete returns a new task with due time + 1 day
        original_due = datetime(2026, 3, 30, 8, 0)
        task = CareTask(
            task_id="daily_walk",
            title="Walk Buddy",
            category="walk",
            duration_minutes=20,
            priority="high",
            due_time_optional=original_due,
            frequency="daily",
        )
        next_task = task.mark_complete()
        assert task.completion_status is True
        assert next_task is not None
        assert next_task.due_time_optional == datetime(2026, 3, 31, 8, 0)

    def test_marking_as_needed_task_returns_none(self):
        # Verifies that marking an "as-needed" task complete returns None (no recurrence)
        task = CareTask(
            task_id="bath",
            title="Bath Time",
            category="grooming",
            duration_minutes=30,
            priority="medium",
            due_time_optional=datetime(2026, 3, 30, 10, 0),
            frequency="as-needed",
        )
        next_task = task.mark_complete()
        assert task.completion_status is True
        assert next_task is None


# ============================================================================
# BEHAVIOR TESTS: CONFLICT DETECTION
# ============================================================================

class TestConflictDetection:
    """Tests for detect_scheduling_conflicts() behavior."""

    def test_overlapping_tasks_return_conflict_dict(self):
        # Verifies that overlapping entries return conflict dict with task names and times
        task1 = CareTask(task_id="t1", title="Walk", category="walk", duration_minutes=30, priority="high")
        task2 = CareTask(task_id="t2", title="Feed", category="feeding", duration_minutes=20, priority="high")

        entry1 = ScheduleEntry(
            task=task1,
            start_time=datetime(2026, 3, 30, 6, 0),
            end_time=datetime(2026, 3, 30, 6, 30),
        )
        entry2 = ScheduleEntry(
            task=task2,
            start_time=datetime(2026, 3, 30, 6, 15),
            end_time=datetime(2026, 3, 30, 6, 45),
        )
        plan = DailyPlan(date=date(2026, 3, 30))
        plan.add_entry(entry1)
        plan.add_entry(entry2)

        scheduler = Scheduler()
        conflicts = scheduler.detect_scheduling_conflicts(plan)
        assert len(conflicts) == 1
        assert conflicts[0]["task_1"] == "Walk"
        assert conflicts[0]["task_2"] == "Feed"

    def test_back_to_back_tasks_not_flagged_as_conflict(self):
        # Verifies that adjacent tasks (one ends exactly when next starts) are NOT conflicts
        task1 = CareTask(task_id="t1", title="Walk", category="walk", duration_minutes=30, priority="high")
        task2 = CareTask(task_id="t2", title="Feed", category="feeding", duration_minutes=20, priority="high")

        entry1 = ScheduleEntry(
            task=task1,
            start_time=datetime(2026, 3, 30, 6, 0),
            end_time=datetime(2026, 3, 30, 6, 30),
        )
        entry2 = ScheduleEntry(
            task=task2,
            start_time=datetime(2026, 3, 30, 6, 30),
            end_time=datetime(2026, 3, 30, 6, 50),
        )
        plan = DailyPlan(date=date(2026, 3, 30))
        plan.add_entry(entry1)
        plan.add_entry(entry2)

        scheduler = Scheduler()
        conflicts = scheduler.detect_scheduling_conflicts(plan)
        assert len(conflicts) == 0


# ============================================================================
# BEHAVIOR TESTS: FILTERING (get_tasks_by_status)
# ============================================================================

class TestFilteringByStatus:
    """Tests for get_tasks_by_status() filtering behavior."""

    def test_get_completed_tasks_returns_only_completed(self):
        # Verifies that get_tasks_by_status(True) returns only completed tasks
        task_list = TaskList()
        task1 = CareTask(task_id="t1", title="Walk", category="walk", duration_minutes=20, priority="high")
        task2 = CareTask(task_id="t2", title="Feed", category="feeding", duration_minutes=15, priority="high")

        task_list.add_task(task1)
        task_list.add_task(task2)
        task1.completion_status = True

        completed = task_list.get_tasks_by_status(completed=True)
        assert len(completed) == 1
        assert completed[0].task_id == "t1"

    def test_get_completed_tasks_empty_when_none_complete(self):
        # Verifies that get_tasks_by_status(True) returns empty list when no tasks are complete
        task_list = TaskList()
        task1 = CareTask(task_id="t1", title="Walk", category="walk", duration_minutes=20, priority="high")
        task2 = CareTask(task_id="t2", title="Feed", category="feeding", duration_minutes=15, priority="high")

        task_list.add_task(task1)
        task_list.add_task(task2)

        completed = task_list.get_tasks_by_status(completed=True)
        assert len(completed) == 0
        assert isinstance(completed, list)
