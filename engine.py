from orchestrator.orchestrator import Orchestrator
from coder.coder import Coder
from tester.tester import Tester
from debugger.debugger import Debugger
from reviewer.reviewer import Reviewer

from state.project_state import (
    load_state,
    update_task_status,
)


class AutonomousEngine:

    def __init__(
        self,
        max_debug_attempts=3
    ):

        self.orchestrator = Orchestrator()

        self.coder = Coder()

        self.tester = Tester()

        self.debugger = Debugger()

        self.reviewer = Reviewer()

        self.max_debug_attempts = (
            max_debug_attempts
        )


    # ==========================================
    # Check whether all tasks are really complete
    # ==========================================

    def all_tasks_completed(self):

        state = load_state()

        tasks = state.get(
            "tasks",
            []
        )


        # No tasks means project is NOT complete

        if not tasks:

            return False


        for task in tasks:

            if task.get("status") != "completed":

                return False


        return True


    # ==========================================
    # Get first incomplete task
    # ==========================================

    def get_first_incomplete_task(self):

        state = load_state()

        tasks = state.get(
            "tasks",
            []
        )


        for task in tasks:

            if task.get("status") != "completed":

                return task


        return None


    # ==========================================
    # Execute one task
    # ==========================================

    def execute_task(
        self,
        task
    ):

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
        # Mark task in progress
        # ======================================

        update_task_status(
            task_id,
            "in_progress"
        )


        # ======================================
        # CODER
        # ======================================

        print("\n>>> AI CODER")


        coder_result = (
            self.coder.execute_task()
        )


        # ======================================
        # Coder failed
        # ======================================

        if not coder_result:

            print("\n")
            print("==========================================")

            print(
                "❌ CODER DID NOT COMPLETE THE TASK"
            )

            print(
                "Task will NOT be marked completed."
            )

            print("==========================================")


            return False


        # ======================================
        # Coder succeeded
        # ======================================

        print("\n")
        print(
            "✅ CODER COMPLETED THE TASK"
        )


        # ======================================
        # TESTER
        # ======================================

        print("\n>>> TESTER")


        test_result = (
            self.tester.test_project()
        )


        # ======================================
        # Tests passed
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


            return True


        # ======================================
        # Tests failed
        # ======================================

        print("\n")
        print("==========================================")

        print(
            "❌ TASK FAILED"
        )

        print("==========================================")


        print(
            "Starting debugger..."
        )


        # ======================================
        # DEBUG LOOP
        # ======================================

        for attempt in range(
            1,
            self.max_debug_attempts + 1
        ):

            print("\n")
            print("------------------------------------------")


            print(
                f"DEBUG ATTEMPT "
                f"{attempt}/"
                f"{self.max_debug_attempts}"
            )


            print("------------------------------------------")


            # ==================================
            # DEBUGGER
            # ==================================

            debug_result = (
                self.debugger.debug()
            )


            if debug_result is None:

                print(
                    "Debugger could not "
                    "produce a fix."
                )

                continue


            # ==================================
            # TEST AGAIN
            # ==================================

            print("\n>>> TESTER")


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
                    "✅ DEBUGGER FIXED THE TASK"
                )


                update_task_status(
                    task_id,
                    "completed"
                )


                return True


            print(
                "❌ Tests still failing."
            )


        # ======================================
        # Debugging failed
        # ======================================

        print("\n")
        print("==========================================")

        print(
            "TASK COULD NOT BE COMPLETED"
        )

        print("==========================================")


        return False


    # ==========================================
    # Run autonomous system
    # ==========================================

    def run(self):

        print("\n")
        print("==========================================")
        print(
            "     AUTONOMOUS ENGINEERING SYSTEM"
        )
        print("==========================================")


        # ======================================
        # Main loop
        # ======================================

        while True:

            # ==================================
            # Ask orchestrator
            # ==================================

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


            # ==================================
            # Project complete
            # ==================================

            if action == "complete":

                # ==================================
                # IMPORTANT:
                # Never blindly trust the
                # orchestrator.
                # ==================================

                if self.all_tasks_completed():

                    print("\n")
                    print("==========================================")

                    print(
                        "ALL TASKS COMPLETED"
                    )

                    print("==========================================")


                    break


                # ==================================
                # Orchestrator incorrectly claimed
                # that the project was complete.
                # ==================================

                print("\n")
                print("==========================================")

                print(
                    "⚠️ ORCHESTRATOR CLAIMED COMPLETION"
                )

                print(
                    "BUT SOME TASKS ARE STILL INCOMPLETE"
                )

                print("==========================================")


                incomplete_task = (
                    self.get_first_incomplete_task()
                )


                # ==================================
                # No incomplete task found
                # ==================================

                if incomplete_task is None:

                    print(
                        "No incomplete task could be found."
                    )

                    break


                print("\n")
                print(
                    "Continuing with incomplete task:"
                )


                print(
                    f"Task {incomplete_task['id']}: "
                    f"{incomplete_task['description']}"
                )


                # ==================================
                # Execute incomplete task
                # ==================================

                success = (
                    self.execute_task(
                        incomplete_task
                    )
                )


                if not success:

                    print("\n")
                    print("==========================================")

                    print(
                        "AUTONOMOUS EXECUTION STOPPED"
                    )

                    print("==========================================")


                    print(
                        f"Task {incomplete_task['id']} "
                        "was not completed."
                    )


                    return


                continue


            # ==================================
            # No task
            # ==================================

            if task is None:

                print("\n")
                print("==========================================")

                print(
                    "⚠️ ORCHESTRATOR RETURNED NO TASK"
                )

                print("==========================================")


                # ==================================
                # Check actual state before stopping
                # ==================================

                if self.all_tasks_completed():

                    print(
                        "All tasks are actually completed."
                    )

                    break


                incomplete_task = (
                    self.get_first_incomplete_task()
                )


                if incomplete_task is not None:

                    print(
                        "\nContinuing with:"
                    )

                    print(
                        f"Task {incomplete_task['id']}: "
                        f"{incomplete_task['description']}"
                    )


                    success = (
                        self.execute_task(
                            incomplete_task
                        )
                    )


                    if not success:

                        print("\n")
                        print(
                            "AUTONOMOUS EXECUTION STOPPED"
                        )


                        return


                    continue


                print(
                    "No task available."
                )

                break


            # ======================================
            # Execute task
            # ======================================

            success = (
                self.execute_task(
                    task
                )
            )


            # ======================================
            # Task failed permanently
            # ======================================

            if not success:

                print("\n")
                print("==========================================")

                print(
                    "AUTONOMOUS EXECUTION STOPPED"
                )

                print("==========================================")


                print(
                    f"Task {task['id']} "
                    "was not completed."
                )


                return


        # ======================================
        # FINAL SAFETY CHECK
        # ======================================

        if not self.all_tasks_completed():

            print("\n")
            print("==========================================")

            print(
                "❌ FINAL REVIEW BLOCKED"
            )

            print(
                "Not all tasks are actually completed."
            )

            print("==========================================")


            return


        # ======================================
        # FINAL REVIEW
        # ======================================

        print("\n")
        print("==========================================")

        print(
            "STARTING FINAL REVIEW"
        )

        print("==========================================")


        review = (
            self.reviewer.review()
        )


        # ======================================
        # Review approved
        # ======================================

        if review["approved"]:

            print("\n")
            print("==========================================")

            print(
                "🎉 PROJECT COMPLETED"
            )

            print("==========================================")


            print(
                review["reason"]
            )


        # ======================================
        # Review rejected
        # ======================================

        else:

            print("\n")
            print("==========================================")

            print(
                "❌ PROJECT NOT APPROVED"
            )

            print("==========================================")


            print(
                review["reason"]
            )


# ==========================================
# Main
# ==========================================

if __name__ == "__main__":

    engine = AutonomousEngine(
        max_debug_attempts=3
    )


    engine.run()