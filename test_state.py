from state.project_state import load_state


# ==========================================
# Read current project state
# ==========================================

state = load_state()


# ==========================================
# Display state
# ==========================================

print("\n==============================")
print("PROJECT STATE")
print("==============================")

print(
    "Project:",
    state["project"]["name"]
)

print(
    "Goal:",
    state["project"]["goal"]
)

print(
    "Status:",
    state["project"]["status"]
)

print(
    "\nTasks:"
)

for task in state["tasks"]:

    print(
        f"[{task['status']}] "
        f"{task['id']}. "
        f"{task['description']}"
    )


print(
    "\nCurrent task:",
    state["current_task"]
)

print(
    "Errors:",
    state["errors"]
)

print(
    "Debug attempts:",
    state["attempts"]
)