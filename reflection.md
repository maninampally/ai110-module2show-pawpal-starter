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

My scheduler considers three constraints: total available time (daily_time_budget_minutes), task priority (high/medium/low), and required status (is_required). I decided required tasks matter most because missing a medication or feeding has real consequences for the pet, so those always schedule first regardless of priority level.

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

I used Copilot for four things: generating class skeletons from my UML, implementing method bodies, drafting test functions, and reviewing my design for missing relationships. The most helpful prompts were specific ones that included rules (e.g. "use @dataclass for these classes, regular class for these others"). Vague prompts produced over-engineered results.

**b. Judgment and verification**

Copilot suggested removing notification_preferences and constraint_rules as "over-engineered". I rejected this because they are harmless empty dicts that leave room for future features without adding complexity now. I verified by checking that no existing logic depended on them being absent.

---

---

## 4. Testing and Verification

**a. What you tested**

I tested task validation, completion marking, priority sorting, recurring task generation, conflict detection, and status filtering — 38 tests total. These were important because the scheduler's correctness depends entirely on ranking and time allocation working correctly.

**b. Confidence**

I am 4/5 confident. All 38 tests pass and cover both happy paths and edge cases. I would next test what happens when all tasks are required but exceed the time budget, and whether recurring tasks with no due_time_optional behave correctly across multiple completions.

---

## 5. Reflection

**a. What went well**

The algorithm is surprisingly elegant. The greedy approach with clear priority rules (required first, then priority level) produces intuitive schedules that users can understand. The test suite gave me confidence early — when all 38 tests passed on first run, I knew the core system was sound. The Streamlit UI integration was smooth because the backend was well-designed with clean separation between logic (pawpal_system.py) and presentation (app.py). I'm also satisfied with the conflict detection feature — it catches overlapping tasks without false positives, which builds user trust.

**b. What you would improve**

I would add a "smart gap filling" feature where the scheduler tries to fill small gaps between large tasks with shorter tasks (e.g., fit a 15-min enrichment activity between two 30-min walks). The current greedy algorithm doesn't optimize time utilization. I would also add time window preferences — owners often have preferred times for walks (morning/evening) and I hardcoded 06:00-22:00 instead of making it dynamic. Finally, I'd implement recurring task history tracking so users can see patterns (e.g., "this dog gets walked 5x/week on average").

**c. Key takeaway**

Designing for clarity beats designing for completeness. I kept the architecture simple (9 classes, clear responsibilities) rather than adding advanced features like constraint satisfaction solvers or multi-day scheduling. This simplicity made testing easier, explained reasoning clearer, and kept the system maintainable. Working with AI, I learned that specific prompts with rules and examples produce much better results than vague requests. "Here's my UML, review it" got useful feedback; "make a scheduler" would have produced over-engineered garbage. The best AI collaboration happens when I bring structure and the AI helps refine it.
