from orchestrator.orchestrator import Orchestrator
from coder.coder import Coder


# ==========================================
# Create Orchestrator
# ==========================================

orchestrator = Orchestrator()


# ==========================================
# Create Coder
# ==========================================

coder = Coder()


# ==========================================
# Get next action
# ==========================================

decision = orchestrator.decide_next_action()


print("\n==============================")
print("ORCHESTRATOR")
print("==============================")

print(
    "Action:",
    decision["action"]
)

print(
    "Task:",
    decision["task"]
)


# ==========================================
# Start task if needed
# ==========================================

if decision["action"] == "start":

    task_id = decision["task"]["id"]

    orchestrator.start_task(
        task_id
    )


# ==========================================
# Coder executes task
# ==========================================

coder.create_project_file(
    "hello.py",
    "print('Hello from Coder Agent')"
)
coder.execute_task()