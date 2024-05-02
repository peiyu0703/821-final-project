"""Run the application."""

from datetime import datetime

from definition import Project, Task, TaskOrganizer, validate_date


def main() -> None:
    """Run the program."""
    organizer = TaskOrganizer("task_organizer.db")
    organizer.handle_recurring_tasks()
    cursor = organizer.conn.cursor()
    cursor.execute("SELECT due_date, status FROM tasks")
    tasks = cursor.fetchall()
    if tasks:
        for due_date, status in tasks:
            due_date_obj = datetime.strptime(due_date, "%m/%d/%Y")
            current_date = datetime.now().date()
            if status != "completed" and due_date_obj.date() < current_date:
                status = "overdue"

    while True:
        print("\nTask and Project Organizer")
        print("Current Projects:")
        projects = organizer.list_projects()
        for project_id, project_name in projects:
            task_counts = organizer.get_task_counts(project_id)
            print(f"Project ID: {project_id}, Name: {project_name}")
            print(
                f"Completed: {task_counts['completed']}, "
                f"Pending: {task_counts['pending']}, "
                f"Overdue: {task_counts['overdue']}"
            )

        print("\nMenu:")
        print("1. Add Project")
        print("2. Add Task")
        print("3. Edit Task")
        print("4. List Tasks by Priority")
        print("5. Mark Task as Completed")
        print("6. Delete")
        print("7. Search Tasks or Projects")
        print("8. View History")
        print("0. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            project_id = input("Enter project ID: ")
            name = input("Enter project name: ")
            project = Project(project_id, name)
            organizer.add_project(project)
            print(f"Project '{name}' added.")
        elif choice == "2":
            project_id = input("Enter project ID: ")
            task_id = input("Enter task ID: ")
            description = input("Enter task description: ")
            while True:
                due_date = input("Enter task due date (MM/DD/YYYY): ")
                if validate_date(due_date):
                    break
                else:
                    print(
                        "Invalid date format. "
                        "Please enter the date in MM/DD/YYYY format."
                    )
            priority = input(
                "Enter task priority (choose from low, medium and high): "
            )
            recurrence = input(
                "Enter task recurrence (choose from daily, weekly, monthly and none): "
            )
            task = Task(
                task_id,
                description,
                due_date,
                priority=priority,
                recurrence=recurrence,
            )
            organizer.add_task(project_id, task)
            print(f"Task '{task_id}' added to project '{project_id}'.")
        elif choice == "3":
            project_id = input("Enter project ID: ")
            task_id = input("Enter task ID: ")
            description = input(
                "Enter new task description (leave blank to keep current): "
            )
            while True:
                due_date = input("Enter new task due date (MM/DD/YYYY): ")
                if due_date == "" or validate_date(due_date):
                    break
                else:
                    print(
                        "Invalid date format. "
                        "Please enter the date in MM/DD/YYYY format."
                    )
            status = input(
                "Enter new task status (leave blank to keep current): "
            )
            priority = input(
                "Enter new task priority (choose from low, medium and high): "
            )
            recurrence = input(
                "Enter new task recurrence (choose from daily, weekly, monthly and none): "  # noqa: E501
            )
            success = organizer.edit_task(
                project_id,
                task_id,
                description,
                due_date,
                status,
                priority,
                recurrence,
            )
            if success:
                print(f"Task '{task_id}' updated.")
            else:
                print("Project ID or Task ID not found.")
                print("Returning to main menu.")
        elif choice == "4":
            project_id = input("Enter project ID: ")
            tasks = organizer.list_tasks(project_id)
            if tasks:
                print(f"Tasks for Project '{project_id}':")
                for (
                    task_id,
                    description,
                    due_date,
                    status,
                    priority,
                    recurrence,
                ) in tasks:
                    print(
                        f"Task ID: {task_id}, Description: {description}, "
                        f"Due Date: {due_date}, Status: {status}, "
                        f"Priority: {priority}, Recurrence: {recurrence}"
                    )
            else:
                print(f"No tasks found for project '{project_id}'.")
        elif choice == "5":
            project_id = input("Enter project ID: ")
            tasks = organizer.list_tasks(project_id)
            if tasks:
                print(f"Tasks for Project '{project_id}':")
                for (
                    task_id,
                    description,
                    due_date,
                    status,
                    priority,
                    recurrence,
                ) in tasks:
                    print(
                        f"Task ID: {task_id}, Description: {description}, "
                        f"Due Date: {due_date}, Status: {status},"
                        f"Priority: {priority}, Recurrence: {recurrence}"
                    )
                task_id = input("Enter task ID to mark as completed: ")
                organizer.mark_task_completed(project_id, task_id)
                print(f"Task '{task_id}' marked as completed.")
            else:
                print(f"No tasks found for project '{project_id}'.")
        elif choice == "6":
            print("Delete Options:")
            print("1. Delete Project")
            print("2. Delete Task")
            delete_choice = input("Enter your choice: ")
            if delete_choice == "1":
                project_id = input("Enter project ID: ")
                confirm = input(
                    f"Are you sure you want to delete project '{project_id}' "
                    "and all its tasks? (1 - Yes, 2 - No): "
                )
                if confirm == "1":
                    organizer.delete_project(project_id)
                    print(
                        f"Project '{project_id}'"
                        "and all its tasks have been deleted."
                    )
                else:
                    print("Deletion cancelled. Returning to main menu.")
            elif delete_choice == "2":
                project_id = input("Enter project ID: ")
                tasks = organizer.list_tasks(project_id)
                if tasks:
                    print(f"Tasks for Project '{project_id}':")
                    for task_id, description, _, _, _, _ in tasks:
                        print(
                            f"Task ID: {task_id}, Description: {description}"
                        )
                    task_id = input("Enter task ID to delete: ")
                    confirm = input(
                        f"Are you sure you want to delete task '{task_id}'? "
                        "(1 - Yes, 2 - No): "
                    )
                    if confirm == "1":
                        organizer.delete_task(project_id, task_id)
                        print(f"Task '{task_id}' has been deleted.")
                    else:
                        print("Deletion cancelled. Returning to main menu.")
                else:
                    print(f"No tasks found for project '{project_id}'.")
            else:
                print("Invalid choice. Returning to main menu.")
        elif choice == "7":
            search_type = input(
                "Search (1) Projects or (2) Tasks? Enter number: "
            )
            keyword = input("Enter search keyword: ")
            if search_type == "1":
                projects = organizer.search_projects(keyword)
                if projects == []:
                    print("Can't find task.")
                else:
                    for project_id, project_name in projects:
                        print(
                            f"""Project ID: {project_id}, Project Name: {project_name}"""  # noqa: E501
                        )
            elif search_type == "2":
                tasks = organizer.search_tasks(keyword)
                if tasks == []:
                    print("Can't find task.")
                else:
                    for (
                        task_id,
                        description,
                        due_date,
                        status,
                        project_id,
                        priority,
                        recurrence,
                    ) in tasks:
                        print(f"Project ID: {project_id}")
                        print(f"Task ID: {task_id}")
                        print(f"Description: {description}")
                        print(f"Due Date: {due_date}")
                        print(f"Status: {status}")
                        print(f"Priority: {priority}")
                        print(f"Recurrence: {recurrence}")
        elif choice == "8":
            history = organizer.fetch_history()
            if history:
                for record in history:
                    entity_type, entity_id, action, details, timestamp = record
                    print(
                        f"{timestamp} - {entity_type} (ID: {entity_id}) {action}: {details}"  # noqa: E501
                    )
            else:
                print("No history records found.")
        elif choice == "0":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
