from orchestrator.orchestrator import Orchestrator
from coder.coder import Coder


orchestrator = Orchestrator()


# ==========================================
# Get current task
# ==========================================

decision = (
    orchestrator
    .decide_next_action()
)


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

    orchestrator.start_task(
        decision["task"]["id"]
    )


# ==========================================
# Run AI Coder
# ==========================================

coder = Coder()

coder.execute_task()