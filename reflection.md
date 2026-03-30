# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

**Three Core User Actions:**

1. **Create and manage owner + pet profiles**
   - User enters their name, daily time budget (minutes available), and preferred time windows
   - User creates pets with details (name, species, age, health notes, activity level)
   - User can update this information anytime

2. **Add and edit care tasks**
   - User creates tasks for each pet (walk, feeding, medication, enrichment, grooming, etc.)
   - Each task has duration (minutes), priority level (high/medium/low), category, and optional due time
   - User can mark tasks as required or recurring (daily, weekly, as-needed)
   - User can edit or remove tasks

3. **Generate and view a daily schedule**
   - User specifies today's constraints (available time, time windows, blocked times)
   - System generates a prioritized daily plan that fits within time and preference constraints
   - Plan displays scheduled tasks with times and includes an explanation of why each task was chosen
   - Unscheduled tasks (that didn't fit) are clearly marked

**UML Design Overview:**

The design uses 9 classes organized in layers:
- **Owner & Pet classes**: Store profile information and preferences
- **CareTask & TaskList classes**: Represent individual tasks and collections of tasks per pet
- **DailyConstraint class**: Captures time availability and blocked periods for scheduling
- **Scheduler class**: Algorithm that takes tasks and constraints, produces an optimized daily plan
- **DailyPlan & ScheduleEntry classes**: Output structure showing scheduled tasks with times and reasons
- **PlanExplainer class**: Generates human-readable explanations of scheduling decisions

**b. Design changes**

Yes, design evolved after Copilot reviewed the skeleton:

1. **Added `pets: list[Pet]` to Owner**
   - Reason: Enables direct Owner → Pet navigation instead of scattered IDs
   - Benefit: Cleaner OOP design, owner can access all their pets directly

2. **Changed TaskList to hold Pet reference instead of pet_id**
   - Reason: Embeds Pet object for context; avoids ID lookups
   - Benefit: TaskList knows which pet it serves; stronger encapsulation

3. **Removed `apply_blocked_time()` method**
   - Reason: No clear use case for MVP; signature was ambiguous
   - Benefit: Reduces surface area; blocked times handled via constructor params

**Rejected suggestions:**
- Did NOT add Owner context to DailyConstraint — would create circular dependencies
- Did NOT remove `constraint_rules` and `explanation_rules` dicts — kept for extensibility (future strategies)

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three main constraints:
1. **Time Budget**: Total available minutes per day (set by owner; typically 120 min)
2. **Task Duration**: Each task requires a fixed number of minutes
3. **Operating Hours**: Tasks scheduled between 06:00 and 22:00 (16-hour window)

Priority order:
- Required tasks scheduled first (must have)
- Then by priority weight: high > medium > low
- Within same priority, first-come-first-served

**Why it matters:** Required tasks (e.g., medication) cannot be skipped. High-priority tasks (e.g., walking) are typically health/behavior essentials. This ordering ensures critical pet care happens first.

**b. Tradeoffs**

**Tradeoff 1: Greedy scheduling vs. optimal allocation**

The scheduler **greedily allocates tasks in ranked order** without trying to find the globally optimal fit (e.g., no backtracking if a large task blocks many small ones).

**Why reasonable for MVP:** 
- Pet care scheduling is rarely time-critical; a reasonable plan today beats a perfect plan tomorrow
- Greedy is simple to explain (transparency important for user trust)
- For typical owner scenarios (6-10 daily tasks, 120-240 min budget), greedy works well
- Future versions could use optimization if edge cases emerge

**Tradeoff 2: Single-pass rank_tasks() vs. readability**

The scheduler uses a single-pass sort for `rank_tasks()` which is efficient but slightly less readable than a two-pass approach. Copilot suggested a helper method alternative for better maintainability. I kept the current version because performance is negligible for small task lists and the logic is clear enough for this use case. The scheduler also only detects exact time overlaps, not near-conflicts — a future version could add minimum buffer time between tasks.

---

## 3. AI Collaboration

**a. How you used AI**

Used AI (Copilot) for:
1. **Design brainstorming**: Proposed the 9-class layered architecture; helped refine which classes belonged in which layer
2. **UML visualization**: Generated Mermaid diagram representing class relationships and data flow
3. **Code scaffolding**: Created method stubs with docstrings for all classes
4. **Implementation guidance**: Advised on dataclass use, type hints, and parameter validation
5. **Test generation**: Suggested comprehensive pytest structure with fixtures, parametrized tests, edge cases
6. **Debugging**: Clarified confusing method signatures (e.g., what `apply_blocked_time()` should do)

**Most helpful prompts:**
- "Here's my UML design [diagram]. Does this architecture make sense? Any suggestions?" → Led to pet_list addition
- "How should I structure TaskList.get_tasks_by_priority()?" → Clear implementation guidance with sorting logic
- "Write a main.py demo that creates an Owner, Pets, Tasks, and generates a schedule" → Validated entire system end-to-end
- "Generate a comprehensive pytest suite for pawpal_system.py" → 30 well-organized tests covering all key behaviors

**b. Judgment and verification**

**Moment 1: Rejected circular dependency suggestion**
- AI suggested: "Add owner_id to DailyConstraint so it knows who the owner is"
- Why rejected: Would create Owner ↔ DailyConstraint circularity; DailyConstraint should be independent of specific owner
- How verified: Traced data flow — DailyConstraint is created fresh each day; doesn't need owner context

**Moment 2: Kept "constraint_rules" dict despite minimalism push**
- AI suggested: "Remove constraint_rules and explanation_rules dicts — just hardcode logic"
- Why kept: These dicts make strategy-swapping possible (future feature: "balanced" vs "speed" vs "health-first" scheduling)
- How verified: Imagined adding new strategy without dict — would require duplicating entire Scheduler class

**Moment 3: Validated greedy algorithm choice**
- AI suggested: "Consider implementing A* or dynamic programming for optimal scheduling"
- Why rejected (for MVP): Overcomplicated; main.py demo showed greedy works for typical scenarios
- How verified: Ran demo with 6 tasks, 120-min budget — greedy produced 100% valid schedule with good time utilization (110/120 min used)

---

---

## 4. Testing and Verification

**a. What you tested**

Created `tests/test_pawpal.py` with **30 pytest test cases** organized in 6 test classes:

**CareTask tests (8 tests):**
- Valid task validation passes; invalid (empty title, zero duration) fail
- Marking complete changes completion_status
- Updating task modifies attributes
- Overdue detection: returns False with no due time, True if past due, False if before due

**TaskList tests (5 tests):**
- Adding/removing tasks updates count
- get_tasks_by_priority sorts correctly (high → medium → low)
- get_required_tasks filters to only required=True
- get_total_duration sums all task durations

**ScheduleEntry tests (4 tests):**
- duration() calculates end_time - start_time
- overlaps_with() detects overlapping entries; non-overlapping returns False
- to_display_text() formats time and task info correctly

**DailyPlan tests (3 tests):**
- add_entry() increments total_scheduled_minutes
- validate_plan() returns True for non-overlapping entries
- validate_plan() returns False if entries overlap

**Scheduler tests (4 tests):**
- rank_tasks() prioritizes required tasks first
- rank_tasks() sorts by priority (high → medium → low)
- build_plan() creates schedule entries
- build_plan() respects time limit (doesn't schedule beyond available_minutes)

**Pet and Owner tests (6 tests):**
- add_health_note() and health_notes list works
- update_pet_info() modifies name, age, etc.
- get_care_needs_summary() returns text with pet name/species/age
- set_time_budget() updates daily_time_budget_minutes
- get_available_time() returns budget
- update_profile() modifies owner attributes

**Why these tests matter:**
- Core classes (CareTask, TaskList, Scheduler) represent the business logic; failures here break the whole system
- ScheduleEntry and DailyPlan handle the output; must ensure times are correct, no overlaps
- Edge cases (overdue checking, conflict detection) are where bugs hide
- Together, tests verify that the system can create realistic schedules without errors

**b. Confidence**

**Very high confidence (95%+) that scheduler works correctly:**
- All 30 tests pass ✓
- main.py demo created realistic schedule with 6 tasks, no conflicts, good time utilization ✓
- validate_plan() correctly detects overlaps (tested with both overlapping and non-overlapping entries) ✓
- rank_tasks() correctly prioritizes required + high-priority tasks ✓

**What I'm confident about:**
1. **Scheduling algorithm is sound**: Greedy ranking + time slot allocation works as intended
2. **Data structures are reliable**: Tasks persist, lists update correctly, constraints are enforced
3. **No runtime crashes**: All 30 tests run to completion; no import errors, no type errors
4. **Output is valid**: Formatted schedule timestamps are correct; plans validate without errors

**Edge cases I would test next (if more time):**
1. **Degenerate cases:**
   - Owner with 0 minutes available → plan should have 0 entries
   - Tasks with very long durations (500 min) for 120-min budget → should schedule what fits in order
   - Tasks with identical priorities → verify consistent ordering (e.g., by task_id)

2. **Recurring tasks:** If implemented, test that weekly tasks properly repeat
3. **Time window preferences:** If implemented, test that tasks outside preferred hours are deprioritized
4. **Multiple owners:** Test that each owner's tasks are independent
5. **Constraint interactions:** Test conflicting rules (e.g., "no tasks after 18:00" but a required 2-hour task exists)

**Current system status:** Ready for Phase 4 (Streamlit UI integration)

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
