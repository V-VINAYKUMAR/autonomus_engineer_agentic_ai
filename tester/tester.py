import hashlib
import subprocess
import sys
from pathlib import Path

from state.project_state import (
    load_state,
    add_error,
    clear_errors
)


class Tester:

    def __init__(self):

        self.state = load_state()

        # Use an absolute workspace path.
        # This prevents workspace/workspace/.venv
        # when subprocess cwd is already workspace.
        self.workspace = Path("workspace").resolve()

        self.project_venv = (
            self.workspace / ".venv"
        )

        self.requirements_file = (
            self.workspace / "requirements.txt"
        )

        self.requirements_hash_file = (
            self.workspace / ".requirements_hash"
        )


    # ==========================================
    # Refresh state
    # ==========================================

    def refresh_state(self):

        self.state = load_state()


    # ==========================================
    # Get project Python
    # ==========================================

    def get_project_python(self):

        if sys.platform == "win32":

            return (
                self.project_venv
                / "Scripts"
                / "python.exe"
            )

        return (
            self.project_venv
            / "bin"
            / "python"
        )


    # ==========================================
    # Get project pip
    # ==========================================

    def get_project_pip(self):

        if sys.platform == "win32":

            return (
                self.project_venv
                / "Scripts"
                / "pip.exe"
            )

        return (
            self.project_venv
            / "bin"
            / "pip"
        )


    # ==========================================
    # Calculate requirements hash
    # ==========================================

    def get_requirements_hash(self):

        if not self.requirements_file.exists():

            return None

        content = (
            self.requirements_file
            .read_bytes()
        )

        return hashlib.sha256(
            content
        ).hexdigest()


    # ==========================================
    # Read previous requirements hash
    # ==========================================

    def get_saved_requirements_hash(self):

        if not self.requirements_hash_file.exists():

            return None

        return (
            self.requirements_hash_file
            .read_text(
                encoding="utf-8"
            )
            .strip()
        )


    # ==========================================
    # Save requirements hash
    # ==========================================

    def save_requirements_hash(self, value):

        self.requirements_hash_file.write_text(
            value,
            encoding="utf-8"
        )


    # ==========================================
    # Create project virtual environment
    # ==========================================

    def create_project_environment(self):

        print("\n==============================")
        print("PROJECT ENVIRONMENT")
        print("==============================")

        print(
            "Creating isolated project "
            "virtual environment..."
        )

        try:

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "venv",
                    str(self.project_venv)
                ],
                capture_output=True,
                text=True,
                cwd=self.workspace
            )

            if result.returncode != 0:

                output = (
                    result.stdout
                    + "\n"
                    + result.stderr
                )

                print(
                    "❌ Failed to create "
                    "project environment."
                )

                print(output)

                return {
                    "passed": False,
                    "output": output
                }

            print(
                "✅ Project environment created."
            )

            return {
                "passed": True,
                "output": ""
            }

        except Exception as e:

            error = (
                "Failed to create project "
                f"environment: {e}"
            )

            print(error)

            return {
                "passed": False,
                "output": error
            }


    # ==========================================
    # Install project dependencies
    # ==========================================

    def install_dependencies(self):

        # --------------------------------------
        # No requirements file
        # --------------------------------------

        if not self.requirements_file.exists():

            print(
                "\nNo requirements.txt found."
            )

            print(
                "Skipping dependency installation."
            )

            return {
                "passed": True,
                "output": ""
            }


        # --------------------------------------
        # Create venv if necessary
        # --------------------------------------

        project_python = (
            self.get_project_python()
        )

        if not project_python.exists():

            result = (
                self.create_project_environment()
            )

            if not result["passed"]:

                return result


        # --------------------------------------
        # Check requirements changes
        # --------------------------------------

        current_hash = (
            self.get_requirements_hash()
        )

        saved_hash = (
            self.get_saved_requirements_hash()
        )


        # --------------------------------------
        # Application dependencies
        # --------------------------------------

        application_output = ""


        if (
            current_hash
            and
            current_hash == saved_hash
        ):

            print(
                "\nProject dependencies "
                "are already installed."
            )

        else:

            print("\n==============================")
            print("PROJECT DEPENDENCIES")
            print("==============================")

            print(
                "Installing project dependencies..."
            )

            pip = self.get_project_pip()

            try:

                result = subprocess.run(
                    [
                        str(pip),
                        "install",
                        "-r",
                        "requirements.txt"
                    ],
                    capture_output=True,
                    text=True,
                    cwd=self.workspace
                )

                application_output = (
                    result.stdout
                    + "\n"
                    + result.stderr
                )

                print(application_output)

                if result.returncode != 0:

                    print(
                        "❌ Dependency installation failed."
                    )

                    return {
                        "passed": False,
                        "output": application_output
                    }

            except Exception as e:

                error = (
                    "Dependency installation error: "
                    f"{e}"
                )

                print(error)

                return {
                    "passed": False,
                    "output": error
                }


        # ======================================
        # Install pytest
        # ======================================

        print("\n==============================")
        print("TEST DEPENDENCIES")
        print("==============================")

        print(
            "Checking pytest..."
        )

        pip = self.get_project_pip()

        try:

            pytest_check = subprocess.run(
                [
                    str(project_python),
                    "-c",
                    "import pytest"
                ],
                capture_output=True,
                text=True,
                cwd=self.workspace
            )


            if pytest_check.returncode == 0:

                print(
                    "✅ Pytest is already installed."
                )

                pytest_output = ""

            else:

                print(
                    "Pytest not found."
                )

                print(
                    "Installing pytest..."
                )

                result = subprocess.run(
                    [
                        str(pip),
                        "install",
                        "pytest"
                    ],
                    capture_output=True,
                    text=True,
                    cwd=self.workspace
                )

                pytest_output = (
                    result.stdout
                    + "\n"
                    + result.stderr
                )

                print(pytest_output)

                if result.returncode != 0:

                    print(
                        "❌ Failed to install pytest."
                    )

                    return {
                        "passed": False,
                        "output": (
                            application_output
                            + "\n"
                            + pytest_output
                        )
                    }

                print(
                    "✅ Pytest installed."
                )


        except Exception as e:

            error = (
                "Pytest installation error: "
                f"{e}"
            )

            print(error)

            return {
                "passed": False,
                "output": error
            }


        # --------------------------------------
        # Save successful requirements hash
        # --------------------------------------

        if current_hash:

            self.save_requirements_hash(
                current_hash
            )


        print(
            "\n✅ Dependencies ready."
        )

        return {
            "passed": True,
            "output": (
                application_output
                + "\n"
                + pytest_output
            )
        }


    # ==========================================
    # Run pytest
    # ==========================================

    def run_tests(self):

        print("\n==============================")
        print("AI TESTER")
        print("==============================")


        # ======================================
        # Check workspace
        # ======================================

        if not self.workspace.exists():

            error = (
                "workspace directory does not exist."
            )

            print(error)

            return {
                "passed": False,
                "return_code": -1,
                "output": error,
                "no_tests_collected": False
            }


        # ======================================
        # Install dependencies
        # ======================================

        dependency_result = (
            self.install_dependencies()
        )


        if not dependency_result["passed"]:

            return {
                "passed": False,
                "return_code": -1,
                "output": dependency_result["output"],
                "no_tests_collected": False
            }


        # ======================================
        # Get project Python
        # ======================================

        project_python = (
            self.get_project_python()
        )


        # ======================================
        # Run pytest
        # ======================================

        print("\n==============================")
        print("RUNNING PROJECT TESTS")
        print("==============================")

        print(
            "Running pytest using the "
            "project environment...\n"
        )


        try:

            result = subprocess.run(
                [
                    str(project_python),
                    "-m",
                    "pytest",
                    "-v"
                ],
                capture_output=True,
                text=True,
                cwd=self.workspace
            )

            output = (
                result.stdout
                + "\n"
                + result.stderr
            )

            print(output)


            # ==================================
            # Detect no tests
            # ==================================

            no_tests_collected = (
                result.returncode == 5
                or
                "no tests ran"
                in output.lower()
            )


            # ==================================
            # Determine result
            # ==================================

            passed = (
                result.returncode == 0
                or
                no_tests_collected
            )


            return {
                "passed": passed,
                "return_code": result.returncode,
                "output": output,
                "no_tests_collected": no_tests_collected
            }


        except FileNotFoundError:

            error = (
                "Project Python environment "
                "could not be found."
            )

            print(error)

            return {
                "passed": False,
                "return_code": -1,
                "output": error,
                "no_tests_collected": False
            }


        except Exception as e:

            error = (
                "Test execution error: "
                f"{e}"
            )

            print(error)

            return {
                "passed": False,
                "return_code": -1,
                "output": error,
                "no_tests_collected": False
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

            if result.get(
                "no_tests_collected",
                False
            ):

                print(
                    "⚠️ NO TESTS FOUND"
                )

            else:

                print(
                    "✅ ALL TESTS PASSED"
                )


            # Remove old errors

            clear_errors()

            return result


        # ======================================
        # Tests failed
        # ======================================

        print("\n==============================")
        print("TEST RESULT")
        print("==============================")

        print(
            "❌ TESTS FAILED"
        )


        # ======================================
        # Save failure
        # ======================================

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