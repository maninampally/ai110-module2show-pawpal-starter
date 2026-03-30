"""
PawPal+ Demo Script
Demonstrates the full scheduling system: create owner, pets, tasks, and generate daily plan.
"""

from datetime import date
from pawpal_system import Owner, Pet, CareTask, TaskList, DailyConstraint, Scheduler, PlanExplainer


def main():
    """Run the PawPal+ demo."""

    # ========================================================================
    # STEP 1: Create Owner
    # ========================================================================
    print("\n" + "=" * 70)
    print("Creating Owner".ljust(70))
    print("=" * 70)

    owner = Owner(
        owner_id="owner_001",
        name="Alex",
        daily_time_budget_minutes=120,
    )
    print(f"✓ Owner created: {owner.name} ({owner.daily_time_budget_minutes} min/day)")

    # ========================================================================
    # STEP 2: Create Pets
    # ========================================================================
    print("\n" + "=" * 70)
    print("Creating Pets".ljust(70))
    print("=" * 70)

    buddy = Pet(
        pet_id="pet_001",
        name="Buddy",
        species="dog",
        age=3,
        activity_level="high",
    )

    luna = Pet(
        pet_id="pet_002",
        name="Luna",
        species="cat",
        age=5,
        activity_level="low",
    )

    owner.pets = [buddy, luna]
    print(f"✓ Pet created: {buddy.name} ({buddy.species}, age {buddy.age}, {buddy.activity_level} activity)")
    print(f"✓ Pet created: {luna.name} ({luna.species}, age {luna.age}, {luna.activity_level} activity)")

    # ========================================================================
    # STEP 3: Create Tasks for Buddy
    # ========================================================================
    print("\n" + "=" * 70)
    print("Creating Tasks for Buddy".ljust(70))
    print("=" * 70)

    buddy_tasks = TaskList(pet=buddy)

    task1 = CareTask(
        task_id="task_001",
        title="Morning Walk",
        category="walk",
        duration_minutes=30,
        priority="high",
        is_required=True,
        notes="Energetic dog needs morning exercise",
    )

    task2 = CareTask(
        task_id="task_002",
        title="Breakfast",
        category="feeding",
        duration_minutes=10,
        priority="high",
        is_required=True,
        notes="Premium dog food",
    )

    task3 = CareTask(
        task_id="task_003",
        title="Afternoon Play",
        category="enrichment",
        duration_minutes=20,
        priority="medium",
        is_required=False,
        notes="Optional indoor play session",
    )

    task4 = CareTask(
        task_id="task_004",
        title="Evening Walk",
        category="walk",
        duration_minutes=25,
        priority="high",
        is_required=True,
        notes="Evening exercise before bed",
    )

    buddy_tasks.add_task(task1)
    buddy_tasks.add_task(task2)
    buddy_tasks.add_task(task3)
    buddy_tasks.add_task(task4)

    print(f"✓ Task added: {task1.title} ({task1.priority}, {task1.duration_minutes} min, required)")
    print(f"✓ Task added: {task2.title} ({task2.priority}, {task2.duration_minutes} min, required)")
    print(f"✓ Task added: {task3.title} ({task3.priority}, {task3.duration_minutes} min, optional)")
    print(f"✓ Task added: {task4.title} ({task4.priority}, {task4.duration_minutes} min, required)")

    # ========================================================================
    # STEP 4: Create Tasks for Luna
    # ========================================================================
    print("\n" + "=" * 70)
    print("Creating Tasks for Luna".ljust(70))
    print("=" * 70)

    luna_tasks = TaskList(pet=luna)

    task5 = CareTask(
        task_id="task_005",
        title="Feeding",
        category="feeding",
        duration_minutes=10,
        priority="high",
        is_required=True,
        notes="Premium cat food",
    )

    task6 = CareTask(
        task_id="task_006",
        title="Litter Box Cleaning",
        category="enrichment",
        duration_minutes=15,
        priority="medium",
        is_required=True,
        notes="Daily litter box maintenance",
    )

    luna_tasks.add_task(task5)
    luna_tasks.add_task(task6)

    print(f"✓ Task added: {task5.title} ({task5.priority}, {task5.duration_minutes} min, required)")
    print(f"✓ Task added: {task6.title} ({task6.priority}, {task6.duration_minutes} min, required)")

    # ========================================================================
    # STEP 5: Create DailyConstraint
    # ========================================================================
    print("\n" + "=" * 70)
    print("Creating Daily Constraint".ljust(70))
    print("=" * 70)

    today = date.today()
    daily_constraint = DailyConstraint(
        date=today,
        available_minutes=120,
        allowed_time_windows=[],
        blocked_times=[],
    )
    print(f"✓ Constraint created for {today} with {daily_constraint.available_minutes} minutes available")

    # ========================================================================
    # STEP 6: Combine all tasks and schedule
    # ========================================================================
    print("\n" + "=" * 70)
    print("Scheduling Tasks".ljust(70))
    print("=" * 70)

    all_tasks = buddy_tasks.tasks + luna_tasks.tasks
    combined_task_list = TaskList()
    for task in all_tasks:
        combined_task_list.add_task(task)

    print(f"✓ Total tasks to schedule: {len(all_tasks)}")

    # Add conflict detection test tasks
    conflict_task_1 = CareTask(
        task_id="conflict_001",
        title="Vet Appointment",
        category="appointment",
        duration_minutes=30,
        priority="high",
        is_required=True,
        notes="Annual checkup for Buddy",
    )

    conflict_task_2 = CareTask(
        task_id="conflict_002",
        title="Grooming Session",
        category="grooming",
        duration_minutes=30,
        priority="high",
        is_required=True,
        notes="Professional grooming",
    )

    combined_task_list.add_task(conflict_task_1)
    combined_task_list.add_task(conflict_task_2)

    scheduler = Scheduler(strategy_name="priority-first")
    plan = scheduler.build_plan(combined_task_list, daily_constraint)

    print(f"✓ Schedule generated: {len(plan.entries)} scheduled, {len(plan.unscheduled_tasks)} unscheduled")

    # ========================================================================
    # STEP 7: Display the Schedule
    # ========================================================================
    print("\n" + "=" * 70)
    print("TODAY'S SCHEDULE".center(70))
    print("=" * 70)
    print()
    print(f"Date: {today}")
    print(f"Available Time: {daily_constraint.available_minutes} minutes")
    print()

    # Display scheduled entries
    print("SCHEDULED TASKS:")
    print("-" * 70)
    for entry in plan.entries:
        print(entry.to_display_text())

    print()

    # Display unscheduled tasks
    if plan.unscheduled_tasks:
        print("UNSCHEDULED TASKS (couldn't fit):")
        print("-" * 70)
        for task in plan.unscheduled_tasks:
            print(f"  ✗ {task.title:<30} ({task.priority.upper():6} priority, {task.duration_minutes:2} min)")
    else:
        print("✓ All tasks successfully scheduled!")

    print()
    print(f"Total Scheduled: {plan.total_scheduled_minutes} minutes")
    print(f"Remaining Time: {daily_constraint.available_minutes - plan.total_scheduled_minutes} minutes")
    print()

    # ========================================================================
    # STEP 8: Display Explanation
    # ========================================================================
    print("=" * 70)
    print("SCHEDULING EXPLANATION".center(70))
    print("=" * 70)
    print()
    print(plan.explanation_summary)

    # ========================================================================
    # STEP 9: Validate Plan
    # ========================================================================
    print()
    if plan.validate_plan():
        print("✓ Plan is valid (no scheduling conflicts)")
    else:
        print("✗ Plan has conflicts detected")

    # ========================================================================
    # STEP 10: Detect and Report Conflicts
    # ========================================================================
    print()
    print("=" * 70)
    print("CONFLICT DETECTION".center(70))
    print("=" * 70)

    conflicts = scheduler.detect_scheduling_conflicts(plan)

    if conflicts:
        for conflict in conflicts:
            print(f"⚠️ {conflict['message']}")
            print(f"  {conflict['task_1']}: {conflict['time_1']}")
            print(f"  {conflict['task_2']}: {conflict['time_2']}")
            print()
    else:
        print("✓ No conflicts detected")

    print()
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()