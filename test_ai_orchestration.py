from orchestrator.orchestrator import (
    Orchestrator
)


orchestrator = Orchestrator()


# ==========================================
# User's project request
# ==========================================

project_name = "Calculator API"

goal = """
Build a calculator API with addition,
subtraction, multiplication, division,
validation, and automated tests.
"""


# ==========================================
# AI Planner
# ==========================================

tasks = orchestrator.create_plan(
    project_name,
    goal
)


# ==========================================
# Display plan
# ==========================================

orchestrator.show_status()


# ==========================================
# Ask Orchestrator what happens next
# ==========================================

decision = (
    orchestrator
    .decide_next_action()
)


print("\n==============================")
print("ORCHESTRATOR DECISION")
print("==============================")


print(
    "Action:",
    decision["action"]
)


print(
    "Task:",
    decision["task"]
)