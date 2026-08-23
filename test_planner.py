from planner.planner import Planner


planner = Planner()


tasks = planner.create_plan(
    "Calculator API",
    "Build a calculator API with tests"
)


planner.show_plan()


print("\n==============================")
print("NEXT TASK")
print("==============================")


next_task = planner.get_next_task()

print(next_task)