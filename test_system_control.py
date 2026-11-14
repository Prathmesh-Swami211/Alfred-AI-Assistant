from system_control import execute_system_command


commands = [
    "open calculator",
    "open notepad",
    "open youtube",
    "open downloads",
    "open alfred project",
]


for command in commands:

    print()
    print("COMMAND:", command)

    success, message = execute_system_command(command)

    print("SUCCESS:", success)
    print("ALFRED:", message)