from state.project_state import load_state
from tools.file_tools import list_files, read_file


class ContextBuilder:

    def __init__(self):
        self.state = load_state()

    # ==========================================
    # Refresh state
    # ==========================================

    def refresh(self):
        self.state = load_state()

    # ==========================================
    # Get project information
    # ==========================================

    def get_project(self):

        self.refresh()

        return self.state.get(
            "project",
            {}
        )

    # ==========================================
    # Get all tasks
    # ==========================================

    def get_tasks(self):

        self.refresh()

        return self.state.get(
            "tasks",
            []
        )

    # ==========================================
    # Get current task
    # ==========================================

    def get_current_task(self):

        self.refresh()

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

            if task.get("id") == current_task_id:

                return task

        return None

    # ==========================================
    # Get previous errors
    # ==========================================

    def get_errors(self):

        self.refresh()

        return self.state.get(
            "errors",
            []
        )

    # ==========================================
    # Get debugging attempts
    # ==========================================

    def get_attempts(self):

        self.refresh()

        return self.state.get(
            "attempts",
            0
        )

    # ==========================================
    # Get project files
    # ==========================================

    def get_files(self):

        return list_files()

    # ==========================================
    # Read project file
    # ==========================================

    def read_file(
        self,
        filename
    ):

        return read_file(
            filename
        )

    # ==========================================
    # Build COMPLETE context
    #
    # Used mainly for debugging/display.
    # Do NOT use this directly for large
    # Gemini prompts.
    # ==========================================

    def build(self):

        self.refresh()

        return {
            "project": self.get_project(),
            "tasks": self.get_tasks(),
            "current_task": self.get_current_task(),
            "errors": self.get_errors(),
            "attempts": self.get_attempts(),
            "files": self.get_files()
        }

    # ==========================================
    # Build SMALL CODER context
    #
    # This is the important new method.
    # ==========================================

    def build_coder_context(self):

        self.refresh()

        current_task = (
            self.get_current_task()
        )

        # --------------------------------------
        # Only include useful task information
        # --------------------------------------

        task_summary = []

        for task in self.get_tasks():

            task_summary.append({
                "id": task.get("id"),
                "status": task.get("status"),
                "description": task.get(
                    "description",
                    ""
                )
            })

        # --------------------------------------
        # Only keep recent errors
        #
        # Don't send the entire error history.
        # --------------------------------------

        errors = self.get_errors()

        recent_errors = errors[-2:] if errors else []

        # --------------------------------------
        # Project files are ONLY filenames here.
        #
        # File contents are NOT loaded.
        # Gemini can request a specific file
        # using read_file.
        # --------------------------------------

        files = self.get_files()

        return {
            "project": self.get_project(),
            "current_task": current_task,
            "tasks": task_summary,
            "errors": recent_errors,
            "attempts": self.get_attempts(),
            "files": files
        }

    # ==========================================
    # Display context
    # ==========================================

    def show(self):

        context = self.build()

        print(
            "\n=============================="
        )

        print(
            "PROJECT CONTEXT"
        )

        print(
            "=============================="
        )

        print(
            "\nProject:",
            context["project"]
        )

        print(
            "\nCurrent task:",
            context["current_task"]
        )

        print(
            "\nTasks:"
        )

        for task in context["tasks"]:

            print(
                f"[{task['status']}] "
                f"{task['id']}. "
                f"{task['description']}"
            )

        print(
            "\nErrors:",
            len(context["errors"])
        )

        print(
            "Debug attempts:",
            context["attempts"]
        )

        print(
            "\nFiles:"
        )

        print(
            context["files"]
        )