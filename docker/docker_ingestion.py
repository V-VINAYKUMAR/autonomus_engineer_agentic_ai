from pathlib import Path


class DockerIngestion:

    def __init__(self, workspace="workspace"):
        self.workspace = Path(workspace)

    # ==========================================
    # Detect project type
    # ==========================================

    def detect_project_type(self):

        if (self.workspace / "requirements.txt").exists():
            return "python"

        if (self.workspace / "package.json").exists():
            return "node"

        if (self.workspace / "pom.xml").exists():
            return "java"

        return "unknown"

    # ==========================================
    # Generate Python Dockerfile
    # ==========================================

    def generate_python_dockerfile(self):

        dockerfile = self.workspace / "Dockerfile"

        content = """FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

        dockerfile.write_text(
            content,
            encoding="utf-8"
        )

        print("✅ Python Dockerfile created.")

        return content

    # ==========================================
    # Inspect workspace
    # ==========================================

    def inspect(self):

        print("\n==============================")
        print("DOCKER INGESTION")
        print("==============================")

        # --------------------------------------
        # Workspace check
        # --------------------------------------

        if not self.workspace.exists():

            print("❌ Workspace does not exist.")

            return {
                "success": False,
                "dockerfile_exists": False,
                "generated": False
            }

        dockerfile = (
            self.workspace / "Dockerfile"
        )

        # --------------------------------------
        # Dockerfile already exists
        # --------------------------------------

        if dockerfile.exists():

            print("✅ Dockerfile found.")

            content = dockerfile.read_text(
                encoding="utf-8"
            )

            return {
                "success": True,
                "dockerfile_exists": True,
                "generated": False,
                "project_type": self.detect_project_type(),
                "content": content
            }

        # --------------------------------------
        # Dockerfile missing
        # --------------------------------------

        print("⚠️ Dockerfile not found.")

        project_type = (
            self.detect_project_type()
        )

        print(
            f"Detected project type: "
            f"{project_type}"
        )

        # --------------------------------------
        # Python
        # --------------------------------------

        if project_type == "python":

            content = (
                self.generate_python_dockerfile()
            )

            return {
                "success": True,
                "dockerfile_exists": True,
                "generated": True,
                "project_type": "python",
                "content": content
            }

        # --------------------------------------
        # Unsupported
        # --------------------------------------

        print(
            "❌ Unsupported project type."
        )

        return {
            "success": False,
            "dockerfile_exists": False,
            "generated": False,
            "project_type": project_type
        }


# ==========================================
# Standalone execution
# ==========================================

if __name__ == "__main__":

    ingestion = DockerIngestion()

    result = ingestion.inspect()

    print("\nResult:")
    print(result)