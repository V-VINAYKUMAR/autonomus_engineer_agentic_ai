from state.project_state import (
    load_state,
    update_task_status,
    clear_errors,
    reset_attempts
)

from planner.planner import Planner
from orchestrator.orchestrator import Orchestrator
from coder.coder import Coder
from tester.tester import Tester
from debugger.debugger import Debugger
from reviewer.reviewer import Reviewer


class AutonomousAgent:

    def __init__(self):

        self.planner = Planner()
        self.orchestrator = Orchestrator()
        self.coder = Coder()
        self.tester = Tester()
        self.debugger = Debugger()
        self.reviewer = Reviewer()


    # ==========================================
    # Get project input
    # ==========================================

    def get_project_input(self):

        print("\n")
        print("==========================================")
        print("     AUTONOMOUS SOFTWARE ENGINEER")
        print("==========================================")

        project_name = input(
            "\nProject name:\n> "
        ).strip()

        if not project_name:

            raise ValueError(
                "Project name cannot be empty."
            )

        goal = input(
            "\nWhat do you want to build?\n> "
        ).strip()

        if not goal:

            raise ValueError(
                "Project goal cannot be empty."
            )

        return project_name, goal


    # ==========================================
    # Create project plan
    # ==========================================

    def create_project(self):

        project_name, goal = (
            self.get_project_input()
        )

        print("\n")
        print("==========================================")
        print("GENERATING PROJECT PLAN")
        print("==========================================")

        tasks = self.planner.generate_plan(
            project_name,
            goal
        )

        self.planner.show_plan()

        return tasks


    # ==========================================
    # Check whether project is complete
    # ==========================================

    def project_completed(self):

        state = load_state()

        tasks = state.get(
            "tasks",
            []
        )

        if not tasks:

            return False

        for task in tasks:

            if task["status"] != "completed":

                return False

        return True


    # ==========================================
    # Run one task
    # ==========================================

    def execute_current_task(self, task):

        task_id = task["id"]

        print("\n")
        print("==========================================")
        print(
            f"STARTING TASK {task_id}"
        )
        print("==========================================")

        print(
            task["description"]
        )


        # ======================================
        # Mark task as in progress
        # ======================================

        update_task_status(
            task_id,
            "in_progress"
        )


        # ======================================
        # Refresh all agents
        # ======================================

        self.coder.refresh_state()
        self.tester.refresh_state()
        self.debugger.refresh_state()
        self.reviewer.refresh_state()


        # ======================================
        # CODER
        # ======================================

        print("\n>>> AI CODER")

        coder_result = (
            self.coder.execute_task()
        )


        # ======================================
        # Coder could not execute task
        # ======================================

        if coder_result is None:

            print(
                "\n❌ CODER COULD NOT EXECUTE TASK"
            )

            return False


        # ======================================
        # TESTER
        # ======================================

        print("\n>>> AI TESTER")

        test_result = (
            self.tester.test_project()
        )


        # ======================================
        # Task passed
        # ======================================

        if test_result["passed"]:

            print("\n")
            print("==========================================")
            print("TASK RESULT")
            print("==========================================")

            print(
                "✅ TASK PASSED"
            )


            update_task_status(
                task_id,
                "completed"
            )


            clear_errors()
            reset_attempts()


            return True


        # ======================================
        # Task failed
        # ======================================

        print("\n")
        print("==========================================")
        print("TASK RESULT")
        print("==========================================")

        print(
            "❌ TASK FAILED"
        )


        return self.debug_task(
            task_id
        )


    # ==========================================
    # Debug failed task
    # ==========================================

    def debug_task(self, task_id):

        max_attempts = 3


        for attempt in range(
            1,
            max_attempts + 1
        ):

            print("\n")
            print("------------------------------------------")
            print(
                f"DEBUG ATTEMPT "
                f"{attempt}/{max_attempts}"
            )
            print("------------------------------------------")


            # ==================================
            # DEBUGGER
            # ==================================

            print("\n>>> AI DEBUGGER")

            self.debugger.refresh_state()


            debug_result = (
                self.debugger.debug()
            )


            if debug_result is None:

                print(
                    "❌ Debugger could not "
                    "produce a fix."
                )

                continue


            # ==================================
            # TEST AGAIN
            # ==================================

            print("\n>>> AI TESTER")

            self.tester.refresh_state()


            test_result = (
                self.tester.test_project()
            )


            # ==================================
            # Fixed
            # ==================================

            if test_result["passed"]:

                print("\n")
                print("==========================================")
                print("DEBUG RESULT")
                print("==========================================")

                print(
                    "✅ DEBUGGER FIXED TASK"
                )


                update_task_status(
                    task_id,
                    "completed"
                )


                clear_errors()
                reset_attempts()


                return True


            print(
                "\n❌ Tests still failing."
            )


        # ======================================
        # Debugging exhausted
        # ======================================

        print("\n")
        print("==========================================")
        print("DEBUGGING FAILED")
        print("==========================================")


        print(
            f"Could not fix task {task_id} "
            f"after {max_attempts} attempts."
        )


        # Keep task pending/in progress,
        # but STOP the autonomous loop.
        # This prevents infinite execution.

        return False


    # ==========================================
    # Run autonomous project
    # ==========================================

    def run(self):

        # ======================================
        # Create new project
        # ======================================

        self.create_project()


        # ======================================
        # Reset runtime state
        # ======================================

        clear_errors()
        reset_attempts()


        print("\n")
        print("==========================================")
        print("STARTING AUTONOMOUS EXECUTION")
        print("==========================================")


        # ======================================
        # Main loop
        # ======================================

        while True:

            # ----------------------------------
            # Check completion
            # ----------------------------------

            if self.project_completed():

                print("\n")
                print("==========================================")
                print("ALL TASKS COMPLETED")
                print("==========================================")

                break


            # ----------------------------------
            # Get next action
            # ----------------------------------

            decision = (
                self.orchestrator
                .decide_next_action()
            )


            action = decision.get(
                "action"
            )

            task = decision.get(
                "task"
            )


            # ----------------------------------
            # No task
            # ----------------------------------

            if task is None:

                print("\n")
                print(
                    "❌ ORCHESTRATOR DID NOT "
                    "RETURN A TASK."
                )

                break


            # ----------------------------------
            # Execute task
            # ----------------------------------

            success = (
                self.execute_current_task(
                    task
                )
            )


            # ----------------------------------
            # Task failed after debugging
            # ----------------------------------

            if not success:

                print("\n")
                print("==========================================")
                print("AUTONOMOUS EXECUTION STOPPED")
                print("==========================================")

                print(
                    f"Task {task['id']} "
                    "could not be completed."
                )

                print(
                    "Fix the issue and run the "
                    "agent again."
                )

                return


        # ======================================
        # FINAL REVIEW
        # ======================================

        print("\n")
        print("==========================================")
        print("STARTING FINAL REVIEW")
        print("==========================================")


        self.reviewer.refresh_state()


        review_result = (
            self.reviewer.review()
        )


        # ======================================
        # Final result
        # ======================================

        if review_result["approved"]:

            print("\n")
            print("==========================================")
            print("🎉 PROJECT APPROVED")
            print("==========================================")

            print(
                review_result["reason"]
            )

        else:

            print("\n")
            print("==========================================")
            print("❌ PROJECT NOT APPROVED")
            print("==========================================")

            print(
                review_result["reason"]
            )


# ==========================================
# Main
# ==========================================

if __name__ == "__main__":

    try:

        agent = AutonomousAgent()

        agent.run()

    except KeyboardInterrupt:

        print("\n")
        print(
            "Autonomous execution stopped by user."
        )

    except Exception as e:

        print("\n")
        print("==========================================")
        print("FATAL ERROR")
        print("==========================================")

        print(
            str(e)
        )