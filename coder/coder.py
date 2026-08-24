import os
import json
import time
import re

from dotenv import load_dotenv

from llm.llm_client import LLMClient

from state.project_state import load_state

from context.context_builder import ContextBuilder

from tools.file_tools import (
    list_files,
    read_file,
    create_file,
    modify_file
)


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# CODER
# ============================================================

class Coder:

    def __init__(self):

        self.state = load_state()

        self.context_builder = (
            ContextBuilder()
        )

        # Centralized LLM client.
        #
        # LLMClient handles:
        #
        # Gemini → primary
        # Groq   → fallback
        #
        self.llm = LLMClient()

        # Files read during the current task.
        #
        # Example:
        #
        # {
        #     "app/main.py": "...full content...",
        #     "app/models.py": "...full content..."
        # }
        #
        self.investigated_files = {}


    # ========================================================
    # REFRESH STATE
    # ========================================================

    def refresh_state(self):

        self.state = load_state()


    # ========================================================
    # CURRENT TASK
    # ========================================================

    def get_current_task(self):

        self.refresh_state()

        current_task_id = (
            self.state.get(
                "current_task"
            )
        )

        if current_task_id is None:

            return None

        for task in self.state.get(
            "tasks",
            []
        ):

            if task["id"] == current_task_id:

                return task

        return None


    # ========================================================
    # PROJECT FILES
    # ========================================================

    def get_project_files(self):

        return list_files()


    # ========================================================
    # READ PROJECT FILE
    # ========================================================

    def read_project_file(
        self,
        filename
    ):

        return read_file(
            filename
        )


    # ========================================================
    # CREATE PROJECT FILE
    # ========================================================

    def create_project_file(
        self,
        filename,
        content
    ):

        return create_file(
            filename,
            content
        )


    # ========================================================
    # MODIFY PROJECT FILE
    # ========================================================

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


    # ========================================================
    # JSON EXTRACTION
    # ========================================================

    def extract_json(
        self,
        text
    ):

        text = text.strip()


        # ----------------------------------------------------
        # Remove markdown fences
        # ----------------------------------------------------

        if text.startswith(
            "```"
        ):

            text = re.sub(
                r"^```(?:json)?\s*",
                "",
                text,
                flags=re.IGNORECASE
            )

            text = re.sub(
                r"\s*```$",
                "",
                text
            )


        text = text.strip()


        # ----------------------------------------------------
        # Direct JSON
        # ----------------------------------------------------

        try:

            return json.loads(
                text
            )

        except json.JSONDecodeError:

            pass


        # ----------------------------------------------------
        # Try extracting outer JSON object
        # ----------------------------------------------------

        start = text.find(
            "{"
        )

        end = text.rfind(
            "}"
        )


        if (
            start != -1
            and
            end != -1
            and
            end > start
        ):

            candidate = (
                text[start:end + 1]
            )

            try:

                return json.loads(
                    candidate
                )

            except json.JSONDecodeError:

                pass


        raise ValueError(
            "LLM returned invalid JSON:\n"
            + text
        )


    # ========================================================
    # VALIDATE PLAN
    # ========================================================

    def validate_plan(
        self,
        plan
    ):

        if not isinstance(
            plan,
            dict
        ):

            raise ValueError(
                "LLM plan must be a JSON object."
            )


        if "actions" not in plan:

            raise ValueError(
                "LLM plan does not contain actions."
            )


        if not isinstance(
            plan["actions"],
            list
        ):

            raise ValueError(
                "LLM actions must be a list."
            )


        valid_actions = {
            "create_file",
            "modify_file",
            "read_file",
            "list_files"
        }


        for action in plan["actions"]:

            if not isinstance(
                action,
                dict
            ):

                raise ValueError(
                    "Each action must be an object."
                )


            action_type = action.get(
                "action"
            )


            if action_type not in valid_actions:

                raise ValueError(
                    f"Unknown action: {action_type}"
                )


            if action_type in {
                "create_file",
                "modify_file",
                "read_file"
            }:

                if not action.get(
                    "filename"
                ):

                    raise ValueError(
                        f"{action_type} requires filename."
                    )


            if action_type == "create_file":

                if "content" not in action:

                    raise ValueError(
                        "create_file requires content."
                    )


            if action_type == "modify_file":

                if "old_text" not in action:

                    raise ValueError(
                        "modify_file requires old_text."
                    )


                if "new_text" not in action:

                    raise ValueError(
                        "modify_file requires new_text."
                    )


    # ========================================================
    # BUILD INVESTIGATED FILE CONTEXT
    # ========================================================

    def build_investigated_context(self):

        if not self.investigated_files:

            return "(none yet)"


        sections = []


        for filename, content in (
            self.investigated_files.items()
        ):

            sections.append(
                f"""
==================================================
FILE: {filename}
==================================================

{content}
"""
            )


        return "\n".join(
            sections
        )


    # ========================================================
    # BUILD SMALL PROJECT FILE LIST
    # ========================================================

    def build_file_list_context(
        self,
        files
    ):

        if not files:

            return "(no project files yet)"


        # list_files() normally returns a list.
        # Convert to a compact string rather than
        # dumping a large Python object representation.

        if isinstance(
            files,
            list
        ):

            return "\n".join(
                str(filename)
                for filename in files
            )


        return str(files)


    # ========================================================
    # ASK LLM
    # ========================================================

    def ask_gemini(self):

        self.refresh_state()


        task = (
            self.get_current_task()
        )


        if task is None:

            raise ValueError(
                "No current task available."
            )


        # ----------------------------------------------------
        # Build project context
        # ----------------------------------------------------

        context = (
            self.context_builder.build()
        )


        # ----------------------------------------------------
        # Project files
        # ----------------------------------------------------

        files = (
            self.get_project_files()
        )


        file_list = (
            self.build_file_list_context(
                files
            )
        )


        # ----------------------------------------------------
        # Files already investigated
        # ----------------------------------------------------

        investigated_context = (
            self.build_investigated_context()
        )


        # ----------------------------------------------------
        # Extract only the project information we actually need.
        #
        # IMPORTANT:
        # Do NOT send the entire context object again.
        #
        # ----------------------------------------------------

        project = context.get(
            "project",
            ""
        )


        tasks = context.get(
            "tasks",
            ""
        )


        # ----------------------------------------------------
        # PROMPT
        # ----------------------------------------------------

        prompt = f"""
You are the CODER AGENT of an autonomous
software engineering system.

Your job is to IMPLEMENT the current task.

You have access to the project workspace.

==================================================
PROJECT
==================================================

{project}


==================================================
CURRENT TASK
==================================================

{task["description"]}


==================================================
PROJECT FILES
==================================================

{file_list}


==================================================
FILES ALREADY READ DURING THIS TASK
==================================================

The following files have already been read.

Their COMPLETE CONTENTS are included below.

DO NOT issue read_file again for these files.

{investigated_context}


==================================================
TASK STATUS
==================================================

{tasks}


==================================================
AVAILABLE ACTIONS
==================================================

create_file
modify_file
read_file
list_files


==================================================
IMPORTANT RULES
==================================================

1. Implement the current task completely.

2. Inspect existing files when necessary.

3. If a file is already present in the
   FILES ALREADY READ section, do NOT request
   read_file for that file again.

4. If you have enough information already,
   IMPLEMENT immediately.

5. Do not stop after reading files.

6. Reading files is only an investigation step.

7. After receiving file contents, use them to
   produce implementation actions.

8. Use create_file for a new file.

9. Use modify_file for an existing file.

10. When using modify_file, old_text MUST
    exactly match the existing file.

11. Do not overwrite unrelated files.

12. Do not modify unrelated files.

13. Create every file required by the task.

14. Keep the generated project runnable.

15. Do not create fake placeholder implementations.

16. Do not create tests merely to make the
    current task pass unless the current task
    actually requires tests.

17. If your previous response only contained
    read_file or list_files actions, this response
    MUST use the information from those results
    and produce implementation actions.

18. Do not repeatedly read the same file.

19. If the required information is already
    available, do not use read_file.

20. Return actual implementation actions,
    not an explanation.

==================================================
CRITICAL MULTI-TURN RULE
==================================================

This is an iterative coding system.

If your previous response contained only:

read_file

or:

list_files

then this response MUST implement the task
using the information obtained from those actions.

DO NOT request the same files again.

For example:

TURN 1:

{{
    "actions": [
        {{
            "action": "read_file",
            "filename": "app/main.py"
        }}
    ]
}}

TURN 2:

The contents of app/main.py are now available
in FILES ALREADY READ.

Now produce implementation actions such as:

{{
    "actions": [
        {{
            "action": "modify_file",
            "filename": "app/main.py",
            "old_text": "exact existing code",
            "new_text": "updated code"
        }}
    ]
}}

==================================================
RESPONSE FORMAT
==================================================

Return ONLY valid JSON.

Example:

{{
    "actions": [
        {{
            "action": "create_file",
            "filename": "app/example.py",
            "content": "complete file content"
        }},
        {{
            "action": "modify_file",
            "filename": "app/main.py",
            "old_text": "exact existing code",
            "new_text": "updated existing code"
        }}
    ]
}}

No markdown.

No explanation.

Only JSON.
"""


        print(
            "\nSending task to LLM..."
        )


        # ====================================================
        # LLM REQUEST
        # ====================================================

        max_retries = 3

        response_text = None


        for attempt in range(
            1,
            max_retries + 1
        ):

            try:

                print(
                    f"\nLLM attempt "
                    f"{attempt}/{max_retries}..."
                )


                response_text = (
                    self.llm.generate(
                        prompt,
                        json_mode=True
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
                    "LLM ERROR"
                )

                print(
                    "=============================="
                )

                print(
                    error_text
                )


                # ------------------------------------------------
                # Temporary errors
                # ------------------------------------------------

                temporary_error = (
                    "503" in error_text
                    or
                    "UNAVAILABLE"
                    in error_text
                    or
                    "temporarily"
                    in error_text.lower()
                    or
                    "high demand"
                    in error_text.lower()
                )


                if not temporary_error:

                    raise


                if attempt == max_retries:

                    print(
                        "\n❌ LLM failed after "
                        f"{max_retries} attempts."
                    )

                    return None


                wait_time = (
                    10 * attempt
                )


                print(
                    f"\nRetrying in "
                    f"{wait_time} seconds..."
                )


                time.sleep(
                    wait_time
                )


        # ====================================================
        # CHECK RESPONSE
        # ====================================================

        if response_text is None:

            return None


        if not response_text:

            raise ValueError(
                "LLM returned an empty response."
            )


        text = (
            response_text.strip()
        )


        print("\n")
        print(
            "=============================="
        )

        print(
            "LLM CODER RESPONSE"
        )

        print(
            "=============================="
        )

        print(
            text
        )


        # ====================================================
        # PARSE JSON
        # ====================================================

        plan = (
            self.extract_json(
                text
            )
        )


        self.validate_plan(
            plan
        )


        return plan


    # ========================================================
    # ACTION FAILURE DETECTION
    # ========================================================

    def action_failed(
        self,
        result
    ):

        if result is None:

            return True


        if isinstance(
            result,
            str
        ):

            error_text = (
                result.lower()
            )


            # Only treat explicit failure
            # messages as failures.
            #
            # Do NOT search for the generic
            # word "error", because successful
            # output may contain that word.

            error_indicators = [
                "failed to",
                "failure:",
                "error:",
                "does not exist",
                "not found",
                "could not",
                "unable to"
            ]


            for indicator in (
                error_indicators
            ):

                if indicator in error_text:

                    return True


        return False


    # ========================================================
    # EXECUTE ACTIONS
    # ========================================================

    def execute_actions(
        self,
        plan
    ):

        actions = plan.get(
            "actions",
            []
        )


        if not actions:

            print(
                "\nCoder: LLM returned no actions."
            )

            return False


        code_changed = False

        failed = False

        read_count = 0


        print("\n")
        print(
            "=============================="
        )

        print(
            "EXECUTING LLM ACTIONS"
        )

        print(
            "=============================="
        )


        for action in actions:

            action_type = action.get(
                "action"
            )


            # =================================================
            # CREATE FILE
            # =================================================

            if action_type == "create_file":

                filename = action.get(
                    "filename"
                )

                content = action.get(
                    "content"
                )


                if not filename:

                    failed = True

                    print(
                        " create_file missing filename."
                    )

                    continue


                if content is None:

                    failed = True

                    print(
                        " create_file missing content."
                    )

                    continue


                print(
                    f"\n>>> CREATE FILE: {filename}"
                )


                try:

                    result = (
                        self.create_project_file(
                            filename,
                            content
                        )
                    )


                    print(
                        f"Result: {result}"
                    )


                    if self.action_failed(
                        result
                    ):

                        failed = True

                        print(
                            f" Failed to create "
                            f"{filename}"
                        )

                    else:

                        code_changed = True


                except Exception as e:

                    failed = True

                    print(
                        f" Exception while creating "
                        f"{filename}: {e}"
                    )


            # =================================================
            # MODIFY FILE
            # =================================================

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

                    failed = True

                    print(
                        " modify_file missing filename."
                    )

                    continue


                if old_text is None:

                    failed = True

                    print(
                        " modify_file missing old_text."
                    )

                    continue


                if new_text is None:

                    failed = True

                    print(
                        " modify_file missing new_text."
                    )

                    continue


                print(
                    f"\n>>> MODIFY FILE: {filename}"
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
                        f"Result: {result}"
                    )


                    if self.action_failed(
                        result
                    ):

                        failed = True

                        print(
                            f" Failed to modify "
                            f"{filename}"
                        )

                    else:

                        code_changed = True


                except Exception as e:

                    failed = True

                    print(
                        f" Exception while modifying "
                        f"{filename}: {e}"
                    )


            # =================================================
            # READ FILE
            # =================================================

            elif action_type == "read_file":

                filename = action.get(
                    "filename"
                )


                if not filename:

                    failed = True

                    print(
                        " read_file missing filename."
                    )

                    continue


                # ------------------------------------------------
                # Prevent duplicate reads ourselves.
                # ------------------------------------------------

                if filename in (
                    self.investigated_files
                ):

                    print(
                        f"\n>>> READ FILE SKIPPED: "
                        f"{filename}"
                    )

                    print(
                        "File was already read "
                        "during this task."
                    )

                    continue


                print(
                    f"\n>>> READ FILE: {filename}"
                )


                try:

                    result = (
                        self.read_project_file(
                            filename
                        )
                    )


                    print(
                        result
                    )


                    self.investigated_files[
                        filename
                    ] = result


                    read_count += 1


                except Exception as e:

                    failed = True

                    print(
                        f" Failed to read "
                        f"{filename}: {e}"
                    )


            # =================================================
            # LIST FILES
            # =================================================

            elif action_type == "list_files":

                print(
                    "\n>>> LIST PROJECT FILES"
                )


                try:

                    result = (
                        self.get_project_files()
                    )


                    print(
                        result
                    )


                except Exception as e:

                    failed = True

                    print(
                        f" Failed to list files: "
                        f"{e}"
                    )


            # =================================================
            # UNKNOWN ACTION
            # =================================================

            else:

                failed = True

                print(
                    f" Unknown action: "
                    f"{action_type}"
                )


        print("\n")
        print(
            "=============================="
        )

        print(
            "ACTIONS FINISHED"
        )

        print(
            "=============================="
        )


        if failed:

            print(
                "ONE OR MORE CODER ACTIONS FAILED"
            )

            return False


        if code_changed:

            print(
                "✅ ALL CODE ACTIONS COMPLETED"
            )

            return True


        if read_count > 0:

            print(
                "ℹ️ Coder only inspected files."
            )

            return False


        print(
            "❌ NO CODE CHANGES WERE MADE"
        )

        return False


    # ========================================================
    # EXECUTE CURRENT TASK
    # ========================================================

    def execute_task(self):

        task = (
            self.get_current_task()
        )


        if task is None:

            print(
                "Coder: No active task."
            )

            return False


        print("\n")
        print(
            "=============================="
        )

        print(
            "AI CODER"
        )

        print(
            "=============================="
        )


        print(
            "Current task:"
        )


        print(
            task["description"]
        )


        # ----------------------------------------------------
        # Reset investigation memory
        # ----------------------------------------------------

        self.investigated_files = {}


        # ----------------------------------------------------
        # Maximum LLM turns
        # ----------------------------------------------------

        max_coder_turns = 4


        for turn in range(
            1,
            max_coder_turns + 1
        ):

            print(
                f"\nCoder turn "
                f"{turn}/{max_coder_turns}..."
            )


            # =================================================
            # ASK LLM
            # =================================================

            try:

                plan = (
                    self.ask_gemini()
                )


            except Exception as e:

                print("\n")
                print(
                    "=============================="
                )

                print(
                    "CODER ERROR"
                )

                print(
                    "=============================="
                )


                print(
                    str(e)
                )


                return False


            if plan is None:

                print(
                    "\n CODER COULD NOT "
                    "GENERATE A PLAN"
                )

                return False


            actions = plan.get(
                "actions",
                []
            )


            # =================================================
            # Determine whether this is only investigation
            # =================================================

            only_reads = (
                len(actions) > 0
                and
                all(
                    action.get("action")
                    in {
                        "read_file",
                        "list_files"
                    }
                    for action in actions
                )
            )


            # =================================================
            # Execute actions
            # =================================================

            try:

                success = (
                    self.execute_actions(
                        plan
                    )
                )


            except Exception as e:

                print("\n")
                print(
                    "=============================="
                )

                print(
                    "CODER ACTION ERROR"
                )

                print(
                    "=============================="
                )


                print(
                    str(e)
                )


                return False


            # =================================================
            # SUCCESS
            # =================================================

            if success:

                print("\n")
                print(
                    "=============================="
                )

                print(
                    "CODER COMPLETED TASK"
                )

                print(
                    "=============================="
                )


                return True


            # =================================================
            # Investigation only
            # =================================================

            if only_reads:

                if turn < max_coder_turns:

                    print(
                        "\nCoder only inspected files "
                        "this turn."
                    )

                    print(
                        "Read contents have been saved "
                        "and will be supplied to LLM "
                        "on the next turn."
                    )


                    continue


            # =================================================
            # If there were reads AND modifications failed,
            # give LLM another opportunity to fix them.
            # =================================================

            if (
                turn < max_coder_turns
                and
                self.investigated_files
            ):

                print(
                    "\nCoder will give LLM "
                    "another implementation turn."
                )


                continue


            # =================================================
            # FAILURE
            # =================================================

            print(
                "\n CODER DID NOT "
                "COMPLETE THE TASK"
            )


            return False


        # ====================================================
        # OUT OF TURNS
        # ====================================================

        print(
            "\n CODER DID NOT COMPLETE THE TASK "
            f"(exceeded {max_coder_turns} turns)"
        )


        return False