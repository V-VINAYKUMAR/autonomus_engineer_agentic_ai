from state.project_state import load_state

from tools.file_tools import (
    list_files,
    read_file,
    run_tests
)


class Reviewer:

    def __init__(self):

        self.state = load_state()


    # ==========================================
    # Refresh state
    # ==========================================

    def refresh_state(self):

        self.state = load_state()


    # ==========================================
    # Check project status
    # ==========================================

    def check_project_status(self):

        self.refresh_state()

        return self.state["project"]["status"]


    # ==========================================
    # Check whether all tasks are completed
    # ==========================================

    def all_tasks_completed(self):

        self.refresh_state()

        tasks = self.state["tasks"]

        if not tasks:

            return False

        for task in tasks:

            if task["status"] != "completed":

                return False

        return True


    # ==========================================
    # Inspect project files
    # ==========================================

    def inspect_project(self):

        print("\n==============================")
        print("REVIEWER: PROJECT FILES")
        print("==============================")

        files = list_files()

        print(files)

        return files


    # ==========================================
    # Inspect a file
    # ==========================================

    def inspect_file(self, filename):

        print("\n==============================")
        print("REVIEWER: FILE")
        print("==============================")

        content = read_file(filename)

        print(content)

        return content


    # ==========================================
    # Run final tests
    # ==========================================

    def run_final_tests(self):

        print("\n==============================")
        print("REVIEWER: FINAL TESTS")
        print("==============================")

        result = run_tests()

        print(result)

        return result


    # ==========================================
    # Check test result
    # ==========================================

    def tests_passed(self, result):

        return (
            "TEST STATUS: PASSED"
            in result
        )


    # ==========================================
    # Perform review
    # ==========================================

    def review(self):

        self.refresh_state()

        print("\n==============================")
        print("REVIEWER AGENT")
        print("==============================")


        # --------------------------------------
        # Check tasks
        # --------------------------------------

        tasks_completed = (
            self.all_tasks_completed()
        )


        if tasks_completed:

            print(
                "All project tasks are completed."
            )

        else:

            print(
                "Some project tasks "
                "are still incomplete."
            )


        # --------------------------------------
        # Inspect files
        # --------------------------------------

        self.inspect_project()


        # --------------------------------------
        # Run final tests
        # --------------------------------------

        test_result = (
            self.run_final_tests()
        )


        tests_ok = (
            self.tests_passed(
                test_result
            )
        )


        # --------------------------------------
        # Final decision
        # --------------------------------------

        if tasks_completed and tests_ok:

            print("\n==============================")
            print("REVIEW RESULT")
            print("==============================")

            print(
                "PROJECT APPROVED"
            )

            return {
                "approved": True,
                "reason": (
                    "All tasks are completed "
                    "and tests passed."
                )
            }


        print("\n==============================")
        print("REVIEW RESULT")
        print("==============================")

        print(
            "PROJECT NOT APPROVED"
        )

        return {
            "approved": False,
            "reason": (
                "Project still has "
                "incomplete tasks or "
                "failing tests."
            )
        }