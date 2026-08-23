import subprocess


class DockerRunner:

    def __init__(
        self,
        image_name="autonomous-generated-app",
        container_name="autonomous-generated-container",
        host_port=8000,
        container_port=8000
    ):

        self.image_name = image_name
        self.container_name = container_name
        self.host_port = host_port
        self.container_port = container_port

    # ==========================================
    # Check whether container already exists
    # ==========================================

    def container_exists(self):

        result = subprocess.run(
            [
                "docker",
                "ps",
                "-a",
                "--filter",
                f"name=^{self.container_name}$",
                "--format",
                "{{.Names}}"
            ],
            capture_output=True,
            text=True
        )

        return self.container_name in (
            result.stdout.strip().splitlines()
        )

    # ==========================================
    # Remove existing container
    # ==========================================

    def remove_existing_container(self):

        if not self.container_exists():

            return True

        print(
            f"⚠️ Removing existing container "
            f"{self.container_name}..."
        )

        result = subprocess.run(
            [
                "docker",
                "rm",
                "-f",
                self.container_name
            ],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:

            print(
                "❌ Failed to remove existing "
                "container."
            )

            print(result.stderr)

            return False

        print(
            "✅ Existing container removed."
        )

        return True

    # ==========================================
    # Run Docker container
    # ==========================================

    def run(self):

        print("\n==============================")
        print("DOCKER RUNNER")
        print("==============================")

        print(
            f"Image: {self.image_name}"
        )

        print(
            f"Container: "
            f"{self.container_name}"
        )

        print(
            f"Port: "
            f"{self.host_port}:"
            f"{self.container_port}"
        )

        # --------------------------------------
        # Remove old container
        # --------------------------------------

        if not self.remove_existing_container():

            return {
                "success": False,
                "container": self.container_name
            }

        # --------------------------------------
        # Start container
        # --------------------------------------

        try:

            result = subprocess.run(
                [
                    "docker",
                    "run",
                    "-d",
                    "--name",
                    self.container_name,
                    "-p",
                    f"{self.host_port}:"
                    f"{self.container_port}",
                    self.image_name
                ],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:

                print(
                    "❌ Docker container failed "
                    "to start."
                )

                print(result.stderr)

                return {
                    "success": False,
                    "container": self.container_name,
                    "output": (
                        result.stdout
                        + "\n"
                        + result.stderr
                    )
                }

            container_id = (
                result.stdout.strip()
            )

            print(
                "✅ Docker container started."
            )

            print(
                f"Container ID: "
                f"{container_id}"
            )

            return {
                "success": True,
                "container": self.container_name,
                "container_id": container_id,
                "host_port": self.host_port,
                "container_port": self.container_port
            }

        except FileNotFoundError:

            print(
                "❌ Docker command not found."
            )

            return {
                "success": False,
                "output": (
                    "Docker is not installed "
                    "or Docker Desktop is not running."
                )
            }

    # ==========================================
    # Get container status
    # ==========================================

    def status(self):

        result = subprocess.run(
            [
                "docker",
                "ps",
                "-a",
                "--filter",
                f"name=^{self.container_name}$",
                "--format",
                "{{.Status}}"
            ],
            capture_output=True,
            text=True
        )

        status = result.stdout.strip()

        if status:

            print(
                f"Container status: {status}"
            )

        else:

            print(
                "Container not found."
            )

        return status

    # ==========================================
    # Get container logs
    # ==========================================

    def logs(self):

        result = subprocess.run(
            [
                "docker",
                "logs",
                self.container_name
            ],
            capture_output=True,
            text=True
        )

        output = (
            result.stdout
            + "\n"
            + result.stderr
        )

        print(output)

        return output


# ==========================================
# Standalone execution
# ==========================================

if __name__ == "__main__":

    runner = DockerRunner()

    result = runner.run()

    print("\nResult:")
    print(result)

    if result["success"]:

        print("\n==============================")
        print("CONTAINER STATUS")
        print("==============================")

        runner.status()

        print("\n==============================")
        print("CONTAINER LOGS")
        print("==============================")

        runner.logs()