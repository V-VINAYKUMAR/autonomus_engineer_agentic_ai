import subprocess

from state.project_state import (
    load_state,
    add_error,
    clear_errors
)


class Tester:

    def __init__(self):

        self.state = load_state()


    # ==========================================
    # Refresh state
    # ==========================================

    def refresh_state(self):

        self.state = load_state()


    # ==========================================
    # Run pytest
    # ==========================================

    def run_tests(self):

        print("\n==============================")
        print("AI TESTER")
        print("==============================")

        print("Running pytest...\n")

        try:

            result = subprocess.run(
                [
                    "pytest",
                    "-v"
                ],
                capture_output=True,
                text=True,
                cwd="workspace"
            )

            output = (
                result.stdout
                + "\n"
                + result.stderr
            )

            print(output)

            # pytest exit code 5 = "no tests collected".
            # Early tasks (setup/design) legitimately have no
            # tests yet, so don't treat that as a failure and
            # send it into an endless debug loop.
            no_tests_collected = (
                result.returncode == 5
                or "no tests ran" in output.lower()
            )

            passed = (
                result.returncode == 0
                or no_tests_collected
            )

            return {
                "passed": passed,
                "return_code": result.returncode,
                "output": output,
                "no_tests_collected": no_tests_collected
            }

        except FileNotFoundError:

            error = (
                "pytest is not installed "
                "or not available."
            )

            print(error)

            return {
                "passed": False,
                "return_code": -1,
                "output": error
            }


    # ==========================================
    # Test project
    # ==========================================

    def test_project(self):

        result = self.run_tests()


        # ======================================
        # Tests passed
        # ======================================

        if result["passed"]:

            print("\n==============================")
            print("TEST RESULT")
            print("==============================")

            print("✅ ALL TESTS PASSED")

            # Remove old errors
            clear_errors()

            return result


        # ======================================
        # Tests failed
        # ======================================

        print("\n==============================")
        print("TEST RESULT")
        print("==============================")

        print("❌ TESTS FAILED")


        # Save failure
        add_error(
            result["output"]
        )


        return result


    # ==========================================
    # Get latest failure
    # ==========================================

    def get_failure(self):

        self.refresh_state()

        errors = self.state.get(
            "errors",
            []
        )

        if not errors:

            return None

        return errors[-1]