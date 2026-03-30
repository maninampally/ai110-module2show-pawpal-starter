import streamlit as st
from datetime import date
from pawpal_system import Owner, Pet, CareTask, TaskList, DailyConstraint, Scheduler

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if "owner" not in st.session_state:
    st.session_state.owner = Owner(
        owner_id="owner_001",
        name="Alex",
        daily_time_budget_minutes=120
    )

if "pets" not in st.session_state:
    st.session_state.pets = []

if "task_lists" not in st.session_state:
    st.session_state.task_lists = {}


# ============================================================================
# PAGE CONFIG & TITLE
# ============================================================================

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")
st.title("🐾 PawPal+")


# ============================================================================
# SIDEBAR — OWNER & PET SETUP
# ============================================================================

with st.sidebar:
    st.header("👤 Owner Profile")
    
    owner_name = st.text_input(
        "Owner Name",
        value=st.session_state.owner.name,
        key="owner_name_input"
    )
    
    time_budget = st.number_input(
        "Daily Time Budget (minutes)",
        min_value=30,
        max_value=1440,
        value=st.session_state.owner.daily_time_budget_minutes,
        step=15,
        key="time_budget_input"
    )
    
    if st.button("Update Owner Profile", key="update_owner_btn"):
        st.session_state.owner.update_profile(name=owner_name)
        st.session_state.owner.set_time_budget(time_budget)
        st.success(f"✅ Owner profile updated: {owner_name} ({time_budget} min/day)")
    
    st.divider()
    st.header("🐱 Add Pet")
    
    pet_name = st.text_input("Pet Name", placeholder="e.g., Buddy", key="pet_name_input")
    pet_species = st.selectbox("Species", ["dog", "cat", "bird", "rabbit", "other"], key="pet_species_select")
    pet_age = st.number_input("Age (years)", min_value=0, max_value=50, value=1, key="pet_age_input")
    pet_activity = st.selectbox("Activity Level", ["low", "medium", "high"], key="pet_activity_select")
    
    if st.button("Add Pet", key="add_pet_btn"):
        if pet_name.strip():
            new_pet = Pet(
                pet_id=f"pet_{len(st.session_state.pets) + 1}",
                name=pet_name,
                species=pet_species,
                age=pet_age,
                activity_level=pet_activity
            )
            st.session_state.pets.append(new_pet)
            st.session_state.owner.pets.append(new_pet)
            st.session_state.task_lists[new_pet.pet_id] = TaskList(pet=new_pet)
            st.success(f"✅ {pet_name} added!")
        else:
            st.error("Please enter a pet name")


# ============================================================================
# MAIN AREA — THREE SECTIONS
# ============================================================================

tab1, tab2, tab3 = st.tabs(["🐾 Your Pets", "➕ Add Tasks", "📅 Generate Schedule"])

# ============================================================================
# TAB 1: YOUR PETS
# ============================================================================

with tab1:
    st.header("Your Pets")
    
    if st.session_state.pets:
        for pet in st.session_state.pets:
            with st.expander(f"🐾 {pet.name} ({pet.species.capitalize()})", expanded=True):
                st.write(pet.get_care_needs_summary())
                
                # Add health note section
                health_note = st.text_input(f"Add health note for {pet.name}", key=f"health_note_{pet.pet_id}")
                if st.button(f"Save Note", key=f"save_note_{pet.pet_id}"):
                    if health_note.strip():
                        pet.add_health_note(health_note)
                        st.success(f"✅ Health note added")
                    else:
                        st.warning("Please enter a note")
                
                # Display health notes
                if pet.health_notes:
                    st.markdown("**Health Notes:**")
                    for note in pet.health_notes:
                        st.write(f"• {note}")
    else:
        st.info("📌 No pets yet. Add a pet in the sidebar to get started!")


# ============================================================================
# TAB 2: ADD TASKS
# ============================================================================

with tab2:
    st.header("Add Tasks")
    
    if st.session_state.pets:
        selected_pet = st.selectbox(
            "Select Pet",
            st.session_state.pets,
            format_func=lambda p: f"{p.name} ({p.species})",
            key="pet_select_task"
        )
        
        st.markdown("### Task Details")
        
        task_title = st.text_input("Task Title", placeholder="e.g., Morning Walk", key="task_title_input")
        task_category = st.selectbox(
            "Category",
            ["walk", "feeding", "grooming", "medication", "enrichment", "playtime", "other"],
            key="task_category_select"
        )
        task_duration = st.number_input(
            "Duration (minutes)",
            min_value=5,
            max_value=480,
            value=30,
            step=5,
            key="task_duration_input"
        )
        task_priority = st.selectbox(
            "Priority",
            ["low", "medium", "high"],
            key="task_priority_select"
        )
        task_required = st.checkbox("Required Task?", value=False, key="task_required_check")
        
        if st.button("Add Task", key="add_task_btn"):
            if task_title.strip():
                new_task = CareTask(
                    task_id=f"task_{selected_pet.pet_id}_{len(st.session_state.task_lists[selected_pet.pet_id].tasks) + 1}",
                    title=task_title,
                    category=task_category,
                    duration_minutes=task_duration,
                    priority=task_priority,
                    is_required=task_required
                )
                
                if new_task.validate():
                    st.session_state.task_lists[selected_pet.pet_id].add_task(new_task)
                    st.success(f"✅ Task '{task_title}' added for {selected_pet.name}")
                else:
                    st.error("❌ Task validation failed. Please check your inputs.")
            else:
                st.error("Please enter a task title")
        
        # Display tasks for selected pet
        task_list = st.session_state.task_lists.get(selected_pet.pet_id)
        if task_list and task_list.tasks:
            st.markdown(f"### Tasks for {selected_pet.name}")
            
            task_df_data = []
            for task in task_list.tasks:
                task_df_data.append({
                    "Title": task.title,
                    "Category": task.category,
                    "Duration (min)": task.duration_minutes,
                    "Priority": task.priority,
                    "Required": "✓" if task.is_required else "✗",
                    "Complete": "✓" if task.completion_status else "✗"
                })
            
            st.table(task_df_data)
    else:
        st.info("📌 Add a pet first to create tasks!")


# ============================================================================
# TAB 3: GENERATE SCHEDULE
# ============================================================================

with tab3:
    st.header("Generate Daily Schedule")
    
    schedule_date = st.date_input("Schedule Date", value=date.today(), key="schedule_date_input")
    available_minutes = st.number_input(
        "Available Minutes Today",
        min_value=30,
        max_value=1440,
        value=st.session_state.owner.daily_time_budget_minutes,
        step=15,
        key="available_minutes_input"
    )
    
    if st.button("Generate Schedule", key="generate_schedule_btn"):
        # Combine all tasks from all pets into a single TaskList for scheduling
        combined_task_list = TaskList(pet=None)
        
        total_tasks = 0
        for pet in st.session_state.pets:
            pet_task_list = st.session_state.task_lists.get(pet.pet_id)
            if pet_task_list and pet_task_list.tasks:
                for task in pet_task_list.tasks:
                    combined_task_list.add_task(task)
                    total_tasks += 1
        
        if total_tasks == 0:
            st.warning("⚠️ No tasks to schedule. Add tasks first!")
        else:
            # Create constraint and generate schedule
            constraint = DailyConstraint(
                date=schedule_date,
                available_minutes=available_minutes
            )
            
            scheduler = Scheduler(strategy_name="priority-first")
            daily_plan = scheduler.build_plan(combined_task_list, constraint)
            
            # Display results
            st.markdown("### Schedule Generated")
            
            # Summary stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Tasks", total_tasks)
            with col2:
                st.metric("Scheduled", len(daily_plan.entries))
            with col3:
                st.metric("Time Used", f"{daily_plan.total_scheduled_minutes} / {available_minutes} min")
            
            # Scheduled tasks table
            if daily_plan.entries:
                st.success("✅ Scheduled Tasks")
                
                schedule_table_data = []
                for entry in sorted(daily_plan.entries, key=lambda e: e.start_time):
                    schedule_table_data.append({
                        "Time": f"{entry.start_time.strftime('%H:%M')} - {entry.end_time.strftime('%H:%M')}",
                        "Task": entry.task.title,
                        "Duration": f"{entry.duration()} min",
                        "Priority": entry.task.priority,
                    })
                
                st.table(schedule_table_data)
            
            # Unscheduled tasks
            if daily_plan.unscheduled_tasks:
                st.warning(f"⚠️ {len(daily_plan.unscheduled_tasks)} Tasks Did Not Fit")
                
                unscheduled_data = []
                for task in daily_plan.unscheduled_tasks:
                    unscheduled_data.append({
                        "Task": task.title,
                        "Duration": f"{task.duration_minutes} min",
                        "Priority": task.priority,
                        "Required": "✓" if task.is_required else "✗"
                    })
                
                st.table(unscheduled_data)
            
            # Validation status
            if daily_plan.validate_plan():
                st.info("✓ Plan is valid (no conflicts)")
            else:
                st.error("✗ Plan has conflicts (overlapping tasks)")
