from pathlib import Path
import subprocess


WORKSPACE = Path("workspace")


# ==========================================
# 1. Create a file
# ==========================================

def create_file(filename: str, content: str) -> str:

    file_path = WORKSPACE / filename

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    file_path.write_text(
        content,
        encoding="utf-8"
    )

    return f"File created successfully: {file_path}"


# ==========================================
# 2. Read a file
# ==========================================

def read_file(filename: str) -> str:

    file_path = WORKSPACE / filename

    if not file_path.exists():
        return f"Error: file '{filename}' does not exist."

    if not file_path.is_file():
        return f"Error: '{filename}' is not a file."

    return file_path.read_text(
        encoding="utf-8"
    )


# ==========================================
# 3. List all files
# ==========================================

def list_files() -> str:

    files = []

    for path in WORKSPACE.rglob("*"):

        if path.is_file():

            files.append(
                str(path.relative_to(WORKSPACE))
            )

    if not files:
        return "Workspace is empty."

    return "\n".join(files)


# ==========================================
# 4. Run a command
# ==========================================

def run_command(command: str) -> str:

    try:

        result = subprocess.run(
            command,
            shell=True,
            cwd=WORKSPACE,
            capture_output=True,
            text=True,
            timeout=10
        )

        output = ""

        if result.stdout:
            output += f"STDOUT:\n{result.stdout}\n"

        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"

        output += f"Exit code: {result.returncode}"

        return output

    except subprocess.TimeoutExpired:

        return "Error: command timed out."

    except Exception as e:

        return f"Error executing command: {e}"


# ==========================================
# 5. Modify an existing file
# ==========================================

def modify_file(
    filename: str,
    old_text: str,
    new_text: str
) -> str:

    file_path = WORKSPACE / filename

    if not file_path.exists():

        return (
            f"Error: file "
            f"'{filename}' does not exist."
        )

    if not file_path.is_file():

        return (
            f"Error: '{filename}' "
            f"is not a file."
        )

    content = file_path.read_text(
        encoding="utf-8"
    )

    if old_text not in content:

        return (
            "Error: the specified "
            "old_text was not found "
            "in the file."
        )

    updated_content = content.replace(
        old_text,
        new_text,
        1
    )

    file_path.write_text(
        updated_content,
        encoding="utf-8"
    )

    return (
        f"File '{filename}' "
        f"modified successfully."
    )


# ==========================================
# 6. Run project tests
# ==========================================

def run_tests() -> str:

    try:

        result = subprocess.run(
            ["python", "-m", "pytest"],
            cwd=WORKSPACE,
            capture_output=True,
            text=True,
            timeout=30
        )

        output = ""

        if result.stdout:
            output += (
                f"STDOUT:\n"
                f"{result.stdout}\n"
            )

        if result.stderr:
            output += (
                f"STDERR:\n"
                f"{result.stderr}\n"
            )

        output += (
            f"Exit code: "
            f"{result.returncode}"
        )

        if result.returncode == 0:
            output += "\nTEST STATUS: PASSED"
        else:
            output += "\nTEST STATUS: FAILED"

        return output

    except subprocess.TimeoutExpired:

        return "Error: tests timed out."

    except Exception as e:

        return f"Error running tests: {e}"