
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


# Store tasks in the current project directory.
TASKS_FILE = Path(__file__).resolve().parent / "tasks.json"

VALID_STATUSES = {"todo", "in-progress", "done"}


def get_timestamp():
    """Return the current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_tasks():
    """Load tasks from JSON. Create the file if it doesn't exist."""
    if not TASKS_FILE.exists():
        save_tasks([])
        return []

    try:
        with TASKS_FILE.open("r", encoding="utf-8") as file:
            tasks = json.load(file)

        if not isinstance(tasks, list):
            raise ValueError("The JSON file must contain a list.")

        return tasks

    except json.JSONDecodeError as error:
        raise ValueError(
            "tasks.json is corrupted. Please repair the JSON file."
        ) from error

    except OSError as error:
        raise RuntimeError(
            f"Unable to read tasks.json: {error}"
        ) from error


def save_tasks(tasks):
    """Save tasks to the JSON file."""
    try:
        with TASKS_FILE.open("w", encoding="utf-8") as file:
            json.dump(tasks, file, indent=4, ensure_ascii=False)

    except OSError as error:
        raise RuntimeError(
            f"Unable to save tasks: {error}"
        ) from error


def get_task(tasks, task_id):
    """Find a task by its ID."""
    for task in tasks:
        if task["id"] == task_id:
            return task

    return None


def add_task(description):
    """Create a new task."""
    description = description.strip()

    if not description:
        raise ValueError("Task description cannot be empty.")

    tasks = load_tasks()

    # Generate the next unique ID.
    task_id = max(
        (task["id"] for task in tasks),
        default=0
    ) + 1

    timestamp = get_timestamp()

    task = {
        "id": task_id,
        "description": description,
        "status": "todo",
        "createdAt": timestamp,
        "updatedAt": timestamp,
    }

    tasks.append(task)
    save_tasks(tasks)

    print(f"Task added successfully (ID: {task_id})")


def update_task(task_id, description):
    """Update an existing task's description."""
    description = description.strip()

    if not description:
        raise ValueError("Task description cannot be empty.")

    tasks = load_tasks()
    task = get_task(tasks, task_id)

    if task is None:
        raise ValueError(f"Task with ID {task_id} not found.")

    task["description"] = description
    task["updatedAt"] = get_timestamp()

    save_tasks(tasks)

    print(f"Task {task_id} updated successfully.")


def delete_task(task_id):
    """Delete a task by its ID."""
    tasks = load_tasks()
    task = get_task(tasks, task_id)

    if task is None:
        raise ValueError(f"Task with ID {task_id} not found.")

    tasks.remove(task)
    save_tasks(tasks)

    print(f"Task {task_id} deleted successfully.")


def mark_task(task_id, status):
    """Change a task's status."""
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {status}")

    tasks = load_tasks()
    task = get_task(tasks, task_id)

    if task is None:
        raise ValueError(f"Task with ID {task_id} not found.")

    task["status"] = status
    task["updatedAt"] = get_timestamp()

    save_tasks(tasks)

    print(f"Task {task_id} marked as {status}.")


def list_tasks(status=None):
    """Display all tasks or filter by status."""
    if status is not None and status not in VALID_STATUSES:
        raise ValueError(
            f"Invalid status. Choose from: {', '.join(sorted(VALID_STATUSES))}"
        )

    tasks = load_tasks()

    if status is not None:
        tasks = [
            task for task in tasks
            if task["status"] == status
        ]

    if not tasks:
        print("No tasks found.")
        return

    print(
        f"{'ID':<5} {'STATUS':<15} DESCRIPTION"
    )
    print("-" * 60)

    for task in tasks:
        print(
            f"{task['id']:<5} "
            f"{task['status']:<15} "
            f"{task['description']}"
        )


def main():
    """Configure and execute CLI commands."""
    parser = argparse.ArgumentParser(
        description="A simple command-line task tracker."
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    # Add command.
    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("description")

    # Update command.
    update_parser = subparsers.add_parser("update")
    update_parser.add_argument("id", type=int)
    update_parser.add_argument("description")

    # Delete command.
    delete_parser = subparsers.add_parser("delete")
    delete_parser.add_argument("id", type=int)

    # Mark task commands.
    progress_parser = subparsers.add_parser("mark-in-progress")
    progress_parser.add_argument("id", type=int)

    done_parser = subparsers.add_parser("mark-done")
    done_parser.add_argument("id", type=int)

    # List command.
    list_parser = subparsers.add_parser("list")
    list_parser.add_argument(
        "status",
        nargs="?",
        choices=sorted(VALID_STATUSES)
    )

    args = parser.parse_args()

    try:
        if args.command == "add":
            add_task(args.description)

        elif args.command == "update":
            update_task(args.id, args.description)

        elif args.command == "delete":
            delete_task(args.id)

        elif args.command == "mark-in-progress":
            mark_task(args.id, "in-progress")

        elif args.command == "mark-done":
            mark_task(args.id, "done")

        elif args.command == "list":
            list_tasks(args.status)

    except (ValueError, RuntimeError) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    main()
