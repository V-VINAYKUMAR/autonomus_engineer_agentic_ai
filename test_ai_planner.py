from planner.planner import Planner


planner = Planner()


tasks = planner.generate_plan(
    "Calculator API",
    "Build a calculator API with automated tests"
)


print("\n==============================")
print("GENERATED PLAN")
print("==============================")


for task in tasks:

    print(
        f"{task['id']}. "
        f"{task['description']}"
    )