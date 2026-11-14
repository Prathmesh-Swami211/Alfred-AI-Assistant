import os
import subprocess
import webbrowser
from pathlib import Path


# ============================================================
# APPLICATIONS
# ============================================================

APPLICATIONS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "paint": "mspaint.exe",
    "file explorer": "explorer.exe",
    "explorer": "explorer.exe",
}


# ============================================================
# FOLDERS
# ============================================================

FOLDERS = {
    "documents": Path.home() / "Documents",
    "downloads": Path.home() / "Downloads",
    "desktop": Path.home() / "Desktop",
    "pictures": Path.home() / "Pictures",
    "videos": Path.home() / "Videos",
    "music": Path.home() / "Music",
}


# ============================================================
# WEBSITES
# ============================================================

WEBSITES = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "gmail": "https://mail.google.com",
    "github": "https://github.com",
    "physics wallah": "https://www.pw.live",
    "pw": "https://www.pw.live",
    "pw live": "https://www.pw.live",
}


# ============================================================
# OPEN APPLICATION
# ============================================================

def open_application(name):
    name = name.lower().strip()

    if name not in APPLICATIONS:
        return False, f"I don't have permission to open {name}."

    try:
        subprocess.Popen(
            APPLICATIONS[name],
            shell=False
        )

        return True, f"Opening {name}."

    except Exception as error:
        return False, f"I couldn't open {name}: {error}"


# ============================================================
# OPEN FOLDER
# ============================================================

def open_folder(name):
    name = name.lower().strip()

    if name not in FOLDERS:
        return False, f"I don't have access to the {name} folder."

    folder = FOLDERS[name]

    try:
        if not folder.exists():
            return False, f"The {name} folder doesn't exist."

        os.startfile(str(folder))

        return True, f"Opening {name}."

    except Exception as error:
        return False, f"I couldn't open {name}: {error}"


# ============================================================
# OPEN WEBSITE
# ============================================================

def open_website(name):
    name = name.lower().strip()

    if name not in WEBSITES:
        return False, f"I don't have permission to open {name}."

    try:
        webbrowser.open_new_tab(WEBSITES[name])

        return True, f"Opening {name}."

    except Exception as error:
        return False, f"I couldn't open {name}: {error}"


# ============================================================
# OPEN PHYSICS WALLAH
# ============================================================

def open_physics_wallah():
    try:
        webbrowser.open_new_tab("https://www.pw.live")

        return True, "Opening Physics Wallah."

    except Exception as error:
        return False, f"I couldn't open Physics Wallah: {error}"


# ============================================================
# OPEN VS CODE
# ============================================================

def open_vscode():
    try:
        subprocess.Popen(
            ["code"],
            shell=False
        )

        return True, "Opening Visual Studio Code."

    except Exception:
        return False, "Visual Studio Code isn't available from the system PATH."


# ============================================================
# OPEN ALFRED PROJECT
# ============================================================

def open_alfred_project():
    project = (
        Path.home()
        / "Documents"
        / "Alfred"
    )

    try:
        if not project.exists():
            return False, "I couldn't find the Alfred project folder."

        os.startfile(str(project))

        return True, "Opening the Alfred project folder."

    except Exception as error:
        return False, f"I couldn't open the Alfred project: {error}"


# ============================================================
# SYSTEM CONTROL ROUTER
# ============================================================

def execute_system_command(command):

    command = command.lower().strip()


    # ========================================================
    # PHYSICS WALLAH / PW
    # ========================================================

    if command in (
        "open pw",
        "open pw live",
        "open physics wallah",
        "open physicswallah",
        "launch pw",
        "launch pw live",
        "launch physics wallah",
        "go to pw",
        "go to pw live",
        "go to physics wallah",
        "start pw",
        "start pw live",
        "start physics wallah",
    ):

        return open_physics_wallah()


    # ========================================================
    # APPLICATIONS
    # ========================================================

    for app_name in APPLICATIONS:

        if (
            command == f"open {app_name}"
            or command == f"launch {app_name}"
            or command == f"start {app_name}"
        ):

            return open_application(app_name)


    # ========================================================
    # VS CODE
    # ========================================================

    if (
        command == "open vscode"
        or command == "open vs code"
        or command == "launch vscode"
        or command == "launch vs code"
        or command == "start vscode"
        or command == "start vs code"
    ):

        return open_vscode()


    # ========================================================
    # FOLDERS
    # ========================================================

    for folder_name in FOLDERS:

        if (
            command == f"open {folder_name}"
            or command == f"open my {folder_name}"
            or command == f"open the {folder_name} folder"
        ):

            return open_folder(folder_name)


    # ========================================================
    # ALFRED PROJECT
    # ========================================================

    if (
        command == "open alfred"
        or command == "open alfred project"
        or command == "open my alfred project"
        or command == "open alfred folder"
    ):

        return open_alfred_project()


    # ========================================================
    # OTHER WEBSITES
    # ========================================================

    for site_name in WEBSITES:

        if (
            command == f"open {site_name}"
            or command == f"open {site_name}.com"
            or command == f"go to {site_name}"
            or command == f"launch {site_name}"
            or command == f"start {site_name}"
        ):

            return open_website(site_name)


    # ========================================================
    # NO MATCH
    # ========================================================

    return False, None