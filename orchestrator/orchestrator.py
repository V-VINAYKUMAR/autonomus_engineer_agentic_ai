from state.project_state import (
    load_state,
    update_project,
    update_task_status
)

from planner.planner import Planner


class Orchestrator:

    def __init__(self):

        self.state = load_state()

        self.planner = Planner()


    # ==========================================
    # Refresh state
    # ==========================================

    def refresh_state(self):

        self.state = load_state()


    # ==========================================
    # Create AI project plan
    # ==========================================

    def create_plan(
        self,
        project_name,
        goal
    ):

        print("\n==============================")
        print("ORCHESTRATOR")
        print("==============================")

        print(
            "Sending project to AI Planner..."
        )

        tasks = self.planner.generate_plan(
            project_name,
            goal
        )

        self.refresh_state()

        print(
            f"\nAI Planner created "
            f"{len(tasks)} tasks."
        )

        return tasks


    # ==========================================
    # Get current task
    # ==========================================

    def get_current_task(self):

        self.refresh_state()

        current_task_id = (
            self.state["current_task"]
        )

        if current_task_id is None:

            return None


        for task in self.state["tasks"]:

            if task["id"] == current_task_id:

                return task


        return None


    # ==========================================
    # Get next pending task
    # ==========================================

    def get_next_pending_task(self):

        self.refresh_state()

        for task in self.state["tasks"]:

            if task["status"] == "pending":

                return task


        return None


    # ==========================================
    # Start a new project
    # ==========================================

    def start_new_project(self):

        print("\n")
        print("==========================================")
        print("NEW PROJECT")
        print("==========================================")


        project_name = input(
            "\nProject name: "
        ).strip()


        goal = input(
            "\nProject goal: "
        ).strip()


        # ======================================
        # Validate input
        # ======================================

        if not project_name:

            print(
                "\n❌ Project name cannot be empty."
            )

            return False


        if not goal:

            print(
                "\n❌ Project goal cannot be empty."
            )

            return False


        # ======================================
        # Save project
        # ======================================

        update_project(
            project_name,
            goal
        )


        # ======================================
        # Generate plan
        # ======================================

        tasks = self.create_plan(
            project_name,
            goal
        )


        # ======================================
        # Check plan
        # ======================================

        if not tasks:

            print(
                "\n❌ Planner did not create any tasks."
            )

            return False


        self.refresh_state()


        print("\n")
        print("==========================================")
        print("PROJECT INITIALIZED")
        print("==========================================")


        print(
            "Project:",
            project_name
        )


        print(
            "Goal:",
            goal
        )


        print(
            f"Tasks created: {len(tasks)}"
        )


        return True


    # ==========================================
    # Decide next action
    # ==========================================

    def decide_next_action(self):

        self.refresh_state()


        project = self.state["project"]

        tasks = self.state["tasks"]


        # ======================================
        # FRESH PROJECT
        # ======================================

        if (
            project["status"] == "not_started"
            and not tasks
        ):

            success = (
                self.start_new_project()
            )


            if not success:

                return {
                    "action": "error",
                    "task": None
                }


            self.refresh_state()


            # Get first task

            first_task = (
                self.get_next_pending_task()
            )


            if first_task:

                return {
                    "action": "start",
                    "task": first_task
                }


            return {
                "action": "error",
                "task": None
            }


        # ======================================
        # Current task
        # ======================================

        current_task = (
            self.get_current_task()
        )


        if current_task:

            if (
                current_task["status"]
                == "in_progress"
            ):

                return {
                    "action": "continue",
                    "task": current_task
                }


        # ======================================
        # Find next pending task
        # ======================================

        next_task = (
            self.get_next_pending_task()
        )


        if next_task:

            return {
                "action": "start",
                "task": next_task
            }


        # ======================================
        # Verify actual completion
        # ======================================

        if tasks:

            all_completed = all(
                task["status"] == "completed"
                for task in tasks
            )


            if all_completed:

                return {
                    "action": "complete",
                    "task": None
                }


        # ======================================
        # Something is inconsistent
        # ======================================

        print("\n")
        print("==========================================")
        print("⚠️ ORCHESTRATOR STATE INCONSISTENCY")
        print("==========================================")


        print(
            "Project contains tasks, but "
            "no pending/current task was found "
            "and the tasks are not all completed."
        )


        return {
            "action": "error",
            "task": None
        }


    # ==========================================
    # Start task
    # ==========================================

    def start_task(
        self,
        task_id
    ):

        update_task_status(
            task_id,
            "in_progress"
        )

        self.refresh_state()


    # ==========================================
    # Complete task
    # ==========================================

    def complete_task(
        self,
        task_id
    ):

        update_task_status(
            task_id,
            "completed"
        )

        self.refresh_state()


    # ==========================================
    # Show status
    # ==========================================

    def show_status(self):

        self.refresh_state()

        print("\n==============================")
        print("PROJECT STATUS")
        print("==============================")


        project = self.state["project"]


        print(
            "Project:",
            project["name"]
        )


        print(
            "Goal:",
            project["goal"]
        )


        print(
            "Status:",
            project["status"]
        )


        print("\nTasks:")


        if not self.state["tasks"]:

            print(
                "No tasks created."
            )


        for task in self.state["tasks"]:

            print(
                f"[{task['status']}] "
                f"{task['id']}. "
                f"{task['description']}"
            )