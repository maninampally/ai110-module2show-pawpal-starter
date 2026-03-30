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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
