"""Simple task checklist helpers for planning project work."""

DEFAULT_TASKS = [
    "Set up the project folder",
    "Register workers and save their details",
    "Record attendance and calculate wages",
    "Track paid and unpaid shifts",
    "Check the program with sample data",
    "Write the project documentation",
]


def list_tasks(tasks=None):
    """Return the current task list as a new list."""
    return list(DEFAULT_TASKS if tasks is None else tasks)


def add_task(tasks, description):
    """Add a task after making sure its description is not blank."""
    description = str(description).strip()
    if not description:
        raise ValueError("A task needs a short description.")
    updated = list(tasks)
    updated.append(description)
    return updated


def complete_task(tasks, task_number):
    """Mark a task as complete using its 1-based list number."""
    updated = list(tasks)
    if not isinstance(task_number, int) or not 1 <= task_number <= len(updated):
        raise ValueError("Choose a task number from the list.")
    task = updated[task_number - 1]
    if not task.startswith("[x] "):
        updated[task_number - 1] = "[x] " + task.removeprefix("[ ] ")
    return updated
