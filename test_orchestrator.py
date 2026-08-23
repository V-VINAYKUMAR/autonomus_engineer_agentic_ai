import json
from pathlib import Path

from orchestrator.orchestrator import Orchestrator
from state.project_state import load_state


STATE_FILE = Path("project_state.json")


# ==========================================
# Start with a clean state
# ==========================================

initial_state = {
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

with open(
    STATE_FILE,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        initial_state,
        file,
        indent=4
    )


# ==========================================
# Create Orchestrator
# ==========================================

orchestrator = Orchestrator()


# ==========================================
# Create project plan
# ==========================================

orchestrator.create_plan(
    "Calculator API",
    "Build a calculator API with automated tests"
)


# ==========================================
# Show initial state
# ==========================================

print("\n==============================")
print("INITIAL PROJECT")
print("==============================")

orchestrator.show_status()


# ==========================================
# Test 1: Find first pending task
# ==========================================

decision = orchestrator.decide_next_action()

print("\n==============================")
print("TEST 1")
print("==============================")

print("Action:", decision["action"])
print("Task:", decision["task"])


assert decision["action"] == "start"

assert decision["task"]["id"] == 1

print("TEST 1 PASSED")


# ==========================================
# Test 2: Start Task 1
# ==========================================

orchestrator.start_task(1)

decision = orchestrator.decide_next_action()

print("\n==============================")
print("TEST 2")
print("==============================")

print("Action:", decision["action"])
print("Task:", decision["task"])


assert decision["action"] == "continue"

assert decision["task"]["id"] == 1

print("TEST 2 PASSED")


# ==========================================
# Test 3: Complete Task 1
# ==========================================

orchestrator.complete_task(1)

decision = orchestrator.decide_next_action()

print("\n==============================")
print("TEST 3")
print("==============================")

print("Action:", decision["action"])
print("Task:", decision["task"])


assert decision["action"] == "start"

assert decision["task"]["id"] == 2

print("TEST 3 PASSED")


# ==========================================
# Complete remaining tasks
# ==========================================

for task_id in range(2, 8):

    orchestrator.start_task(task_id)

    orchestrator.complete_task(task_id)


# ==========================================
# Test 4: All tasks completed
# ==========================================

decision = orchestrator.decide_next_action()

print("\n==============================")
print("TEST 4")
print("==============================")

print("Action:", decision["action"])
print("Task:", decision["task"])


assert decision["action"] == "complete"

assert decision["task"] is None

print("TEST 4 PASSED")


# ==========================================
# Final project status
# ==========================================

print("\n==============================")
print("FINAL PROJECT")
print("==============================")

orchestrator.show_status()

print("\n==============================")
print("ALL ORCHESTRATION TESTS PASSED")
print("==============================")