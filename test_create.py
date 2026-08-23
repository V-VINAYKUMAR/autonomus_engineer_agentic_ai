from tools.file_tools import create_file

result = create_file(
    "test.py",
    "print('Hello from the agent!')"
)

print(result)