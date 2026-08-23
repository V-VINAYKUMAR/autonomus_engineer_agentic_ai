from docker.docker_ingestion import DockerIngestion
from docker.docker_builder import DockerBuilder
from docker.docker_runner import DockerRunner
from docker.docker_health import DockerHealth


class DockerManager:

    def __init__(self):

        self.ingestion = DockerIngestion()

        self.builder = DockerBuilder()

        self.runner = DockerRunner()

        self.health = DockerHealth()

    # ==========================================
    # Full Docker deployment
    # ==========================================

    def deploy(self):

        print("\n==========================================")
        print("AUTONOMOUS DOCKER DEPLOYMENT")
        print("==========================================")

        # --------------------------------------
        # 1. Ingestion
        # --------------------------------------

        print("\n[1/4] Docker ingestion")

        ingestion_result = (
            self.ingestion.inspect()
        )

        if not ingestion_result:
            return {
                "success": False,
                "stage": "ingestion"
            }

        if not ingestion_result.get(
            "success",
            False
        ):
            return {
                "success": False,
                "stage": "ingestion",
                "result": ingestion_result
            }

        print("✅ Ingestion completed.")

        # --------------------------------------
        # 2. Build
        # --------------------------------------

        print("\n[2/4] Docker build")

        build_result = (
            self.builder.build()
        )

        if not build_result.get(
            "success",
            False
        ):
            return {
                "success": False,
                "stage": "build",
                "result": build_result
            }

        print("✅ Build completed.")

        # --------------------------------------
        # 3. Run
        # --------------------------------------

        print("\n[3/4] Docker run")

        run_result = (
            self.runner.run()
        )

        if not run_result.get(
            "success",
            False
        ):
            return {
                "success": False,
                "stage": "run",
                "result": run_result
            }

        print("✅ Container started.")

        # --------------------------------------
        # 4. Health
        # --------------------------------------

        print("\n[4/4] Docker health")

        health_result = (
            self.health.check()
        )

        if not health_result.get(
            "success",
            False
        ):
            return {
                "success": False,
                "stage": "health",
                "result": health_result
            }

        print("✅ Application is healthy.")

        # --------------------------------------
        # Complete
        # --------------------------------------

        print("\n==========================================")
        print("✅ DOCKER DEPLOYMENT SUCCESSFUL")
        print("==========================================")

        return {
            "success": True,
            "stage": "complete",
            "ingestion": ingestion_result,
            "build": build_result,
            "run": run_result,
            "health": health_result
        }


if __name__ == "__main__":

    manager = DockerManager()

    result = manager.deploy()

    print("\nResult:")
    print(result)