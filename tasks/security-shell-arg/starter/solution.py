import subprocess


def run_report(user_arg: str):
    """Run report-tool with one user-provided argument."""
    command = f"report-tool {user_arg}"
    return subprocess.run(command, shell=True, check=False, capture_output=True, text=True)
