
import json
import os
from datetime import datetime

DATA_FILE = "tasks.json"
DATE_FORMAT = "%Y-%m-%d"

STATUSES = ["Todo", "In Progress", "Done"]
PRIORITIES = ["Low", "Medium", "High"]


def load_tasks():
    """Load tasks from the JSON file (empty list if file does not exist)."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        print("Warning: could not read data file. Starting with an empty list.")
        return []


def save_tasks(tasks):
    """Save tasks to the JSON file."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=4, ensure_ascii=False)


def next_id(tasks):
    """Generate the next unique task ID."""
    return max((t["id"] for t in tasks), default=0) + 1



def input_text(prompt, allow_empty=False):
    """Ask for text; keep asking until valid."""
    while True:
        value = input(prompt).strip()
        if value or allow_empty:
            return value
        print("  Error: this field cannot be empty.")


def input_date(prompt, allow_empty=False):
    """Ask for a date in YYYY-MM-DD format."""
    while True:
        value = input(prompt).strip()
        if not value and allow_empty:
            return ""
        try:
            datetime.strptime(value, DATE_FORMAT)
            return value
        except ValueError:
            print("  Error: invalid date. Use format YYYY-MM-DD (e.g. 2026-05-20).")


def input_choice(prompt, options, allow_empty=False):
    """Ask the user to pick one option from a list by number."""
    menu = ", ".join(f"{i}={opt}" for i, opt in enumerate(options, 1))
    while True:
        value = input(f"{prompt} ({menu}): ").strip()
        if not value and allow_empty:
            return ""
        if value.isdigit() and 1 <= int(value) <= len(options):
            return options[int(value) - 1]
        print(f"  Error: please enter a number from 1 to {len(options)}.")


def input_task_id(prompt, tasks):
    """Ask for an existing task ID."""
    while True:
        value = input(prompt).strip()
        if value.isdigit():
            task = find_task(tasks, int(value))
            if task:
                return task
        print("  Error: task ID not found.")


def find_task(tasks, task_id):
    for t in tasks:
        if t["id"] == task_id:
            return t
    return None



def display_tasks(tasks, title="TASK LIST"):
    """Print tasks in a clear table."""
    print(f"\n=== {title} ===")
    if not tasks:
        print("No tasks to show.")
        return
    header = f"{'ID':<4}{'Title':<25}{'Status':<13}{'Priority':<10}{'Due date':<12}"
    print(header)
    print("-" * len(header))
    for t in tasks:
        title_short = (t["title"][:22] + "...") if len(t["title"]) > 25 else t["title"]
        print(
            f"{t['id']:<4}{title_short:<25}{t['status']:<13}"
            f"{t['priority']:<10}{t['due_date']:<12}"
        )
    done = sum(1 for t in tasks if t["status"] == "Done")
    print(f"\nProgress: {done}/{len(tasks)} tasks completed "
          f"({done * 100 // len(tasks)}%)")


def show_task_detail(task):
    print(f"\n  ID          : {task['id']}")
    print(f"  Title       : {task['title']}")
    print(f"  Description : {task['description'] or '-'}")
    print(f"  Status      : {task['status']}")
    print(f"  Priority    : {task['priority']}")
    print(f"  Due date    : {task['due_date']}")


def add_task(tasks):
    print("\n--- Add new task ---")
    task = {
        "id": next_id(tasks),
        "title": input_text("Title: "),
        "description": input_text("Description (optional): ", allow_empty=True),
        "status": input_choice("Status", STATUSES),
        "priority": input_choice("Priority", PRIORITIES),
        "due_date": input_date("Due date (YYYY-MM-DD): "),
    }
    tasks.append(task)
    save_tasks(tasks)
    print(f"Task #{task['id']} added successfully.")


def edit_task(tasks):
    if not tasks:
        print("No tasks to edit.")
        return
    display_tasks(tasks)
    task = input_task_id("\nEnter the ID of the task to edit: ", tasks)
    show_task_detail(task)
    print("\nPress Enter to keep the current value.")

    new_title = input_text(f"Title [{task['title']}]: ", allow_empty=True)
    new_desc = input_text("Description: ", allow_empty=True)
    new_status = input_choice(f"Status [{task['status']}]", STATUSES, allow_empty=True)
    new_priority = input_choice(f"Priority [{task['priority']}]", PRIORITIES, allow_empty=True)
    new_date = input_date(f"Due date [{task['due_date']}]: ", allow_empty=True)

    if new_title:
        task["title"] = new_title
    if new_desc:
        task["description"] = new_desc
    if new_status:
        task["status"] = new_status
    if new_priority:
        task["priority"] = new_priority
    if new_date:
        task["due_date"] = new_date

    save_tasks(tasks)
    print("Task updated successfully.")


def delete_task(tasks):
    if not tasks:
        print("No tasks to delete.")
        return
    display_tasks(tasks)
    task = input_task_id("\nEnter the ID of the task to delete: ", tasks)
    confirm = input(f"Delete '{task['title']}'? (y/n): ").strip().lower()
    if confirm == "y":
        tasks.remove(task)
        save_tasks(tasks)
        print("Task deleted.")
    else:
        print("Deletion cancelled.")


def view_tasks(tasks):
    print("\n--- View tasks ---")
    print("1. All tasks")
    print("2. Filter by status")
    print("3. Filter by priority")
    print("4. Sort by due date")
    print("5. Sort by priority (High -> Low)")
    choice = input("Choose: ").strip()

    if choice == "1":
        display_tasks(tasks)
    elif choice == "2":
        status = input_choice("Status", STATUSES)
        display_tasks([t for t in tasks if t["status"] == status],
                      f"TASKS - {status.upper()}")
    elif choice == "3":
        priority = input_choice("Priority", PRIORITIES)
        display_tasks([t for t in tasks if t["priority"] == priority],
                      f"TASKS - {priority.upper()} PRIORITY")
    elif choice == "4":
        display_tasks(sorted(tasks, key=lambda t: t["due_date"]),
                      "TASKS SORTED BY DUE DATE")
    elif choice == "5":
        order = {p: i for i, p in enumerate(reversed(PRIORITIES))}
        display_tasks(sorted(tasks, key=lambda t: order[t["priority"]]),
                      "TASKS SORTED BY PRIORITY")
    else:
        print("Invalid choice.")



def main():
    tasks = load_tasks()
    while True:
        print("\n========== TASK MANAGEMENT SYSTEM ==========")
        print("1. Add task")
        print("2. Edit task")
        print("3. Delete task")
        print("4. View tasks")
        print("0. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_task(tasks)
        elif choice == "2":
            edit_task(tasks)
        elif choice == "3":
            delete_task(tasks)
        elif choice == "4":
            view_tasks(tasks)
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please choose 0-4.")


if __name__ == "__main__":
    main()
