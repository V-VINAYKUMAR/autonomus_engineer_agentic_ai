import os
import json

from dotenv import load_dotenv
from google import genai

from state.project_state import (
    load_state,
    add_task,
    update_project,
    reset_tasks

)


# ==========================================
# Load environment
# ==========================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found in .env"
    )


# ==========================================
# Gemini client
# ==========================================

client = genai.Client(
    api_key=api_key
)


class Planner:

    def __init__(self):

        self.state = load_state()


    # ==========================================
    # Generate AI project plan
    # ==========================================

    def generate_plan(
        self,
        project_name,
        goal
    ):

        prompt = f"""
You are the planning agent of an
autonomous software engineering team.

Project name:
{project_name}

Project goal:
{goal}

Break this software project into clear,
ordered implementation tasks.

Rules:

1. Generate 5 to 10 tasks.
2. Tasks must be practical engineering tasks.
3. Do not write code.
4. Start with project setup/design.
5. Include implementation.
6. Include automated testing.
7. Include running tests.
8. Include fixing failures.
9. Include final review.
10. Return ONLY valid JSON.

Required format:

{{
    "tasks": [
        {{
            "id": 1,
            "description": "..."
        }},
        {{
            "id": 2,
            "description": "..."
        }}
    ]
}}
"""

        print("\n==============================")
        print("AI PLANNER")
        print("==============================")

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        response_text = response.text.strip()

        print("\nGemini response:")
        print(response_text)


        # ======================================
        # Parse JSON
        # ======================================

        try:

            plan = json.loads(
                response_text
            )

        except json.JSONDecodeError:

            # Gemini sometimes wraps JSON
            # inside markdown code blocks.

            cleaned = (
                response_text
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

            plan = json.loads(
                cleaned
            )


        # ======================================
        # Validate plan
        # ======================================

        if "tasks" not in plan:

            raise ValueError(
                "Gemini response does not "
                "contain 'tasks'."
            )


        if not isinstance(
            plan["tasks"],
            list
        ):

            raise ValueError(
                "'tasks' must be a list."
            )


        # ======================================
        # Save project information
        # ======================================

        update_project(
            project_name,
            goal
        )
        reset_tasks()


        # ======================================
        # Save generated tasks
        # ======================================

        for task in plan["tasks"]:

            add_task(
                task["id"],
                task["description"]
            )


        self.state = load_state()

        return self.state["tasks"]


    # ==========================================
    # Show plan
    # ==========================================

    def show_plan(self):

        self.state = load_state()

        print("\n==============================")
        print("PROJECT PLAN")
        print("==============================")

        print(
            "Project:",
            self.state["project"]["name"]
        )

        print(
            "Goal:",
            self.state["project"]["goal"]
        )

        print("\nTasks:")

        for task in self.state["tasks"]:

            print(
                f"[{task['status']}] "
                f"{task['id']}. "
                f"{task['description']}"
            )


    # ==========================================
    # Get next task
    # ==========================================

    def get_next_task(self):

        self.state = load_state()

        for task in self.state["tasks"]:

            if task["status"] == "pending":

                return task

        return None