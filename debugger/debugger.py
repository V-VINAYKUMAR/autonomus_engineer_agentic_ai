import os
import json
import time
import re

from dotenv import load_dotenv
from google import genai

from state.project_state import (
    load_state,
    increment_attempts
)

from context.context_builder import ContextBuilder

from tools.file_tools import (
    list_files,
    read_file,
    create_file,
    modify_file
)


# ==========================================
# Load environment variables
# ==========================================

load_dotenv()

api_key = os.getenv(
    "GEMINI_API_KEY"
)


if not api_key:

    raise ValueError(
        "GEMINI_API_KEY not found in .env"
    )


# ==========================================
# Create Gemini client
# ==========================================

client = genai.Client(
    api_key=api_key
)


# ==========================================
# DEBUGGER
# ==========================================

class Debugger:

    def __init__(self):

        self.state = load_state()

        self.context_builder = (
            ContextBuilder()
        )


    # ==========================================
    # Refresh state
    # ==========================================

    def refresh_state(self):

        self.state = load_state()


    # ==========================================
    # Get latest error
    # ==========================================

    def get_latest_error(self):

        self.refresh_state()

        errors = self.state.get(
            "errors",
            []
        )


        if not errors:

            return None


        return errors[-1]


    # ==========================================
    # Get current task
    # ==========================================

    def get_current_task(self):

        self.refresh_state()

        current_task_id = (
            self.state.get(
                "current_task"
            )
        )


        if current_task_id is None:

            return None


        for task in self.state["tasks"]:

            if task["id"] == current_task_id:

                return task


        return None


    # ==========================================
    # Get project files
    # ==========================================

    def get_project_files(self):

        return list_files()


    # ==========================================
    # Read project file
    # ==========================================

    def read_project_file(
        self,
        filename
    ):

        return read_file(
            filename
        )


    # ==========================================
    # Create project file
    # ==========================================

    def create_project_file(
        self,
        filename,
        content
    ):

        print(
            f"\nCreating file: {filename}"
        )


        return create_file(
            filename,
            content
        )


    # ==========================================
    # Modify project file
    # ==========================================

    def modify_project_file(
        self,
        filename,
        old_text,
        new_text
    ):

        return modify_file(
            filename,
            old_text,
            new_text
        )


    # ==========================================
    # Check if file exists
    # ==========================================

    def file_exists(
        self,
        filename
    ):

        try:

            files = self.get_project_files()

            if isinstance(files, list):

                for item in files:

                    if isinstance(item, str):

                        if item == filename:

                            return True


                    elif isinstance(item, dict):

                        if (
                            item.get("path")
                            == filename
                        ):

                            return True


                        if (
                            item.get("filename")
                            == filename
                        ):

                            return True


            return False


        except Exception:

            return False


    # ==========================================
    # Ask Gemini to debug
    # ==========================================

    def ask_gemini(self):

        context = (
            self.context_builder.build()
        )


        prompt = f"""
You are the Debugger Agent in an
autonomous software engineering system.

Your responsibility is to analyze the
latest test failure and fix the current task.

==========================================
PROJECT
==========================================

{context["project"]}


==========================================
ALL TASKS
==========================================

{context["tasks"]}


==========================================
CURRENT TASK
==========================================

{context["current_task"]}


==========================================
PREVIOUS ERRORS
==========================================

{context["errors"]}


==========================================
DEBUG ATTEMPTS
==========================================

{context["attempts"]}


==========================================
PROJECT FILES
==========================================

{context["files"]}


==========================================
AVAILABLE ACTIONS
==========================================

1. create_file
2. modify_file
3. read_file
4. list_files


==========================================
IMPORTANT RULES
==========================================

1. Analyze the latest test failure.

2. Identify the actual root cause.

3. Do not fix a problem that does not
   actually exist.

4. Read a file before modifying it when
   the existing content is required.

5. If the target file DOES NOT EXIST,
   use create_file.

6. NEVER use modify_file to create a
   new file.

7. If the target file already exists,
   use modify_file.

8. Do not create placeholder tests just
   because pytest currently has no tests,
   unless the current task specifically
   requires creating tests.

9. If the current task is project
   initialization and tests are planned
   for a later task, do not invent a
   testing implementation for the current
   task.

10. Modify only files necessary to fix
    the actual failure.

11. Do not modify unrelated files.

12. Return complete file contents when
    using create_file.

13. For modify_file, old_text MUST match
    existing file content exactly.

==========================================
RESPONSE FORMAT
==========================================

Return ONLY valid JSON.

Example:

{{
    "diagnosis":
        "Brief explanation of root cause",

    "actions": [

        {{
            "action": "create_file",
            "filename": "tests/test_main.py",
            "content":
                "def test_example():\\n"
                "    assert True\\n"
        }},

        {{
            "action": "modify_file",
            "filename": "app/main.py",
            "old_text": "old code",
            "new_text": "new code"
        }}

    ]
}}

No markdown.

No explanation outside JSON.
"""


        # ======================================
        # Gemini retry
        # ======================================

        max_retries = 3

        response = None


        for attempt in range(
            1,
            max_retries + 1
        ):

            try:

                print(
                    f"\nGemini debugger attempt "
                    f"{attempt}/{max_retries}..."
                )


                response = (
                    client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt,
                        config={
                            "response_mime_type":
                                "application/json"
                        }
                    )
                )


                break


            except Exception as e:

                error_text = str(e)


                print("\n")
                print(
                    "=============================="
                )

                print(
                    "GEMINI DEBUGGER ERROR"
                )

                print(
                    "=============================="
                )


                print(
                    error_text
                )


                temporary_error = (
                    "503" in error_text
                    or
                    "429" in error_text
                    or
                    "UNAVAILABLE"
                    in error_text
                    or
                    "RESOURCE_EXHAUSTED"
                    in error_text
                    or
                    "temporarily"
                    in error_text.lower()
                )


                if not temporary_error:

                    raise


                # ----------------------------------
                # Quota exhausted
                # ----------------------------------

                if (
                    "RESOURCE_EXHAUSTED"
                    in error_text
                    or
                    "quota" in error_text.lower()
                ):

                    print(
                        "\n⚠️ Gemini quota appears "
                        "to be exhausted."
                    )

                    print(
                        "The debugger cannot continue "
                        "until Gemini quota is available."
                    )


                    return None


                if attempt == max_retries:

                    print(
                        "\n❌ Gemini debugger failed "
                        "after all retries."
                    )

                    return None


                wait_time = (
                    10 * attempt
                )


                # Try to extract Gemini's
                # suggested retry time.

                match = re.search(
                    r"retryDelay[\"']?\s*[:=]\s*"
                    r"[\"']?(\d+)",
                    error_text
                )


                if match:

                    wait_time = max(
                        wait_time,
                        int(match.group(1))
                    )


                print(
                    f"\nRetrying debugger in "
                    f"{wait_time} seconds..."
                )


                time.sleep(
                    wait_time
                )


        # ======================================
        # No response
        # ======================================

        if response is None:

            return None


        # ======================================
        # Get Gemini response
        # ======================================

        if not response.text:

            raise ValueError(
                "Gemini debugger returned "
                "an empty response."
            )


        text = response.text.strip()


        print("\n==============================")
        print("GEMINI DEBUGGER RESPONSE")
        print("==============================")


        print(
            text
        )


        # ======================================
        # Remove markdown JSON wrapper
        # ======================================

        text = (
            text
            .replace(
                "```json",
                ""
            )
            .replace(
                "```",
                ""
            )
            .strip()
        )


        # ======================================
        # Parse JSON
        # ======================================

        try:

            debug_plan = json.loads(
                text
            )


        except json.JSONDecodeError as e:

            raise ValueError(
                "Gemini returned invalid JSON:\n"
                f"{e}\n"
                f"{text}"
            )


        # ======================================
        # Validate response
        # ======================================

        if "actions" not in debug_plan:

            raise ValueError(
                "Debugger response does not "
                "contain 'actions'."
            )


        if not isinstance(
            debug_plan["actions"],
            list
        ):

            raise ValueError(
                "Debugger actions must "
                "be a list."
            )


        return debug_plan


    # ==========================================
    # Execute Gemini actions
    # ==========================================

    def execute_actions(
        self,
        debug_plan
    ):

        actions = debug_plan.get(
            "actions",
            []
        )


        if not actions:

            print(
                "\nDebugger returned no actions."
            )

            return False


        changed = False


        for action in actions:

            action_type = action.get(
                "action"
            )


            # ==================================
            # CREATE FILE
            # ==================================

            if action_type == "create_file":

                filename = action.get(
                    "filename"
                )

                content = action.get(
                    "content"
                )


                if not filename:

                    print(
                        "❌ create_file missing "
                        "filename."
                    )

                    continue


                if content is None:

                    print(
                        "❌ create_file missing "
                        "content."
                    )

                    continue


                print("\n")
                print(
                    "=============================="
                )

                print(
                    "DEBUGGER CREATE FILE"
                )

                print(
                    "=============================="
                )


                # ==================================
                # If file already exists, do not
                # overwrite it blindly.
                # ==================================

                if self.file_exists(
                    filename
                ):

                    print(
                        f"⚠️ File already exists: "
                        f"{filename}"
                    )

                    print(
                        "Skipping create_file."
                    )

                    continue


                try:

                    result = (
                        self.create_project_file(
                            filename,
                            content
                        )
                    )


                    print(
                        result
                    )


                    changed = True


                except Exception as e:

                    print(
                        f"❌ Failed to create "
                        f"{filename}: {e}"
                    )


            # ==================================
            # MODIFY FILE
            # ==================================

            elif action_type == "modify_file":

                filename = action.get(
                    "filename"
                )

                old_text = action.get(
                    "old_text"
                )

                new_text = action.get(
                    "new_text"
                )


                if not filename:

                    print(
                        "❌ modify_file missing "
                        "filename."
                    )

                    continue


                # ==================================
                # IMPORTANT:
                # Do not allow modify_file to
                # create a new file.
                # ==================================

                if not self.file_exists(
                    filename
                ):

                    print(
                        "\n⚠️ Debugger requested "
                        "modify_file for a file "
                        "that does not exist:"
                    )

                    print(
                        filename
                    )


                    # --------------------------------
                    # Automatically create it when
                    # possible.
                    # --------------------------------

                    if new_text is not None:

                        print(
                            "Converting "
                            "modify_file → create_file"
                        )


                        try:

                            result = (
                                self.create_project_file(
                                    filename,
                                    new_text
                                )
                            )


                            print(
                                result
                            )


                            changed = True


                        except Exception as e:

                            print(
                                f"❌ Failed to create "
                                f"{filename}: {e}"
                            )


                    continue


                # ==================================
                # Existing file → modify
                # ==================================

                if old_text is None:

                    print(
                        "❌ modify_file requires "
                        "old_text for an existing file."
                    )

                    continue


                if new_text is None:

                    print(
                        "❌ modify_file requires "
                        "new_text."
                    )

                    continue


                print("\n")
                print(
                    "=============================="
                )

                print(
                    "DEBUGGER MODIFY FILE"
                )

                print(
                    "=============================="
                )


                try:

                    result = (
                        self.modify_project_file(
                            filename,
                            old_text,
                            new_text
                        )
                    )


                    print(
                        result
                    )


                    changed = True


                except Exception as e:

                    print(
                        f"❌ Failed to modify "
                        f"{filename}: {e}"
                    )


            # ==================================
            # READ FILE
            # ==================================

            elif action_type == "read_file":

                filename = action.get(
                    "filename"
                )


                if not filename:

                    continue


                try:

                    result = (
                        self.read_project_file(
                            filename
                        )
                    )


                    print("\n")
                    print(
                        "=============================="
                    )

                    print(
                        "DEBUGGER READ"
                    )

                    print(
                        "=============================="
                    )


                    print(
                        result
                    )


                except Exception as e:

                    print(
                        f"❌ Failed to read "
                        f"{filename}: {e}"
                    )


            # ==================================
            # LIST FILES
            # ==================================

            elif action_type == "list_files":

                try:

                    result = (
                        self.get_project_files()
                    )


                    print("\n")
                    print(
                        "=============================="
                    )

                    print(
                        "DEBUGGER FILES"
                    )

                    print(
                        "=============================="
                    )


                    print(
                        result
                    )


                except Exception as e:

                    print(
                        f"❌ Failed to list files: "
                        f"{e}"
                    )


            # ==================================
            # UNKNOWN ACTION
            # ==================================

            else:

                print(
                    "❌ Unknown debugger action:",
                    action_type
                )


        return changed


    # ==========================================
    # Debug current failure
    # ==========================================

    def debug(self):

        # ======================================
        # Get latest error
        # ======================================

        error = (
            self.get_latest_error()
        )


        # ======================================
        # No error
        # ======================================

        if error is None:

            print(
                "Debugger: No error available."
            )

            return None


        # ======================================
        # Start debugger
        # ======================================

        print(
            "\n=============================="
        )

        print(
            "AI DEBUGGER"
        )

        print(
            "=============================="
        )


        print(
            "Analyzing latest test failure..."
        )


        # ======================================
        # Increase debug attempt counter
        # ======================================

        increment_attempts()


        # ======================================
        # Ask Gemini
        # ======================================

        try:

            debug_plan = (
                self.ask_gemini()
            )


        except Exception as e:

            print("\n")
            print(
                "❌ DEBUGGER GEMINI ERROR"
            )

            print(
                str(e)
            )


            return None


        if debug_plan is None:

            print(
                "\n❌ Debugger could not "
                "generate a fix."
            )

            return None


        # ======================================
        # Execute fixes
        # ======================================

        try:

            changed = (
                self.execute_actions(
                    debug_plan
                )
            )


        except Exception as e:

            print("\n")
            print(
                "❌ DEBUGGER ACTION ERROR"
            )

            print(
                str(e)
            )


            return None


        # ======================================
        # No changes
        # ======================================

        if not changed:

            print(
                "\n⚠️ Debugger made no "
                "project changes."
            )


        else:

            print(
                "\n✅ Debugger applied "
                "project changes."
            )


        # ======================================
        # Return debugging plan
        # ======================================

        return debug_plan