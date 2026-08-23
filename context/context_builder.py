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

        return self.state["project"]

    # ==========================================
    # Get all tasks
    # ==========================================

    def get_tasks(self):

        self.refresh()

        return self.state["tasks"]

    # ==========================================
    # Get current task
    # ==========================================

    def get_current_task(self):

        self.refresh()

        current_task_id = self.state.get(
            "current_task"
        )

        if current_task_id is None:
            return None

        for task in self.state["tasks"]:

            if task["id"] == current_task_id:
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

    def read_file(self, filename):

        return read_file(filename)

    # ==========================================
    # Build complete context
    # ==========================================

    def build(self):

        self.refresh()

        context = {
            "project": self.get_project(),
            "tasks": self.get_tasks(),
            "current_task": self.get_current_task(),
            "errors": self.get_errors(),
            "attempts": self.get_attempts(),
            "files": self.get_files()
        }

        return context

    # ==========================================
    # Display context
    # ==========================================

    def show(self):

        context = self.build()

        print("\n==============================")
        print("PROJECT CONTEXT")
        print("==============================")

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