import json
from pathlib import Path


STATE_FILE = Path("project_state.json")


# ==========================================
# Default state
# ==========================================

def get_default_state():

    return {
        "project": {
            "name": "",
            "goal": "",
            "status": "not_started"
        },

        "tasks": [],

        "current_task": None,

        "errors": [],

        "attempts": 0
    }


# ==========================================
# Load state
# ==========================================

def load_state():

    if not STATE_FILE.exists():

        return get_default_state()

    with open(
        STATE_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ==========================================
# Save state
# ==========================================

def save_state(state):

    with open(
        STATE_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            state,
            file,
            indent=4
        )


# ==========================================
# Update project
# ==========================================

def update_project(
    name,
    goal
):

    state = load_state()

    state["project"]["name"] = name

    state["project"]["goal"] = goal

    state["project"]["status"] = "in_progress"

    save_state(state)


# ==========================================
# Reset tasks
# ==========================================

def reset_tasks():

    state = load_state()

    state["tasks"] = []

    state["current_task"] = None

    save_state(state)


# ==========================================
# Add task
# ==========================================

def add_task(
    task_id,
    description
):

    state = load_state()

    state["tasks"].append({
        "id": task_id,
        "description": description,
        "status": "pending"
    })

    save_state(state)


# ==========================================
# Update task status
# ==========================================

def update_task_status(
    task_id,
    status
):

    state = load_state()

    for task in state["tasks"]:

        if task["id"] == task_id:

            task["status"] = status

            if status == "in_progress":

                state["current_task"] = task_id

            elif (
                status == "completed"
                and
                state["current_task"] == task_id
            ):

                state["current_task"] = None

            break

    save_state(state)


# ==========================================
# Add error
# ==========================================

def add_error(error):

    state = load_state()

    state["errors"].append(
        error
    )

    save_state(state)


# ==========================================
# Clear errors
# ==========================================

def clear_errors():

    state = load_state()

    state["errors"] = []

    save_state(state)


# ==========================================
# Increment debugging attempts
# ==========================================

def increment_attempts():

    state = load_state()

    state["attempts"] += 1

    save_state(state)


# ==========================================
# Reset debugging attempts
# ==========================================

def reset_attempts():

    state = load_state()

    state["attempts"] = 0

    save_state(state)