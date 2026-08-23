import subprocess
import time
import urllib.request
import urllib.error


class DockerHealth:

    def __init__(
        self,
        container_name="autonomous-generated-container",
        url="http://localhost:8000",
        retries=10,
        delay=2
    ):
        self.container_name = container_name
        self.url = url
        self.retries = retries
        self.delay = delay

    # ==========================================
    # Check container status
    # ==========================================

    def container_running(self):

        result = subprocess.run(
            [
                "docker",
                "inspect",
                "-f",
                "{{.State.Running}}",
                self.container_name
            ],
            capture_output=True,
            text=True
        )

        return result.stdout.strip() == "true"

    # ==========================================
    # Check API
    # ==========================================

    def check_api(self):

        try:

            response = urllib.request.urlopen(
                self.url,
                timeout=3
            )

            return {
                "success": True,
                "status_code": response.status
            }

        except urllib.error.HTTPError as e:

            # Server responded, so the container
            # and HTTP server are reachable.
            return {
                "success": True,
                "status_code": e.code
            }

        except Exception as e:

            return {
                "success": False,
                "error": str(e)
            }

    # ==========================================
    # Full health check
    # ==========================================

    def check(self):

        print("\n==============================")
        print("DOCKER HEALTH CHECK")
        print("==============================")

        # --------------------------------------
        # Container check
        # --------------------------------------

        if not self.container_running():

            print(
                "❌ Container is not running."
            )

            return {
                "success": False,
                "container_running": False
            }

        print(
            "✅ Container is running."
        )

        # --------------------------------------
        # API check
        # --------------------------------------

        print(
            f"Checking API: {self.url}"
        )

        for attempt in range(
            1,
            self.retries + 1
        ):

            result = self.check_api()

            if result["success"]:

                print(
                    f"✅ API is responding "
                    f"(HTTP {result['status_code']})."
                )

                return {
                    "success": True,
                    "container_running": True,
                    "status_code": result[
                        "status_code"
                    ]
                }

            print(
                f"Attempt {attempt}/"
                f"{self.retries} failed."
            )

            if attempt < self.retries:

                time.sleep(self.delay)

        print(
            "❌ API health check failed."
        )

        return {
            "success": False,
            "container_running": True
        }


# ==========================================
# Standalone execution
# ==========================================

if __name__ == "__main__":

    health = DockerHealth()

    result = health.check()

    print("\nResult:")
    print(result)