import subprocess


class DockerBuilder:

    def __init__(
        self,
        workspace="workspace",
        image_name="autonomous-generated-app"
    ):

        self.workspace = workspace
        self.image_name = image_name

    # ==========================================
    # Check Dockerfile
    # ==========================================

    def check_dockerfile(self):

        dockerfile = (
            f"{self.workspace}/Dockerfile"
        )

        try:

            with open(
                dockerfile,
                "r",
                encoding="utf-8"
            ):

                return True

        except FileNotFoundError:

            return False

    # ==========================================
    # Build Docker image
    # ==========================================

    def build(self):

        print("\n==============================")
        print("DOCKER BUILD")
        print("==============================")

        # --------------------------------------
        # Dockerfile check
        # --------------------------------------

        if not self.check_dockerfile():

            print(
                "❌ Dockerfile not found."
            )

            print(
                f"Expected: "
                f"{self.workspace}/Dockerfile"
            )

            return {
                "success": False,
                "output": "Dockerfile not found."
            }

        print(
            f"Building image: "
            f"{self.image_name}"
        )

        # --------------------------------------
        # Docker build
        # --------------------------------------

        try:

            result = subprocess.run(
                [
                    "docker",
                    "build",
                    "-t",
                    self.image_name,
                    self.workspace
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

            # ----------------------------------
            # Build failed
            # ----------------------------------

            if result.returncode != 0:

                print(
                    "❌ Docker build failed."
                )

                return {
                    "success": False,
                    "output": output
                }

            # ----------------------------------
            # Build successful
            # ----------------------------------

            print(
                "✅ Docker image built successfully."
            )

            return {
                "success": True,
                "image": self.image_name,
                "output": output
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
# Standalone execution
# ==========================================

if __name__ == "__main__":

    builder = DockerBuilder()

    result = builder.build()

    print("\nResult:")
    print(result)