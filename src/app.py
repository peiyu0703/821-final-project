"""For to do list."""

import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class Task:
    """Task."""

    def __init__(
        self,
        task_id: str,
        description: str,
        due_date: str,
        status: str = "incomplete",
    ) -> None:
        """Initialize Task object."""
        self.task_id = task_id
        self.description = description
        self.due_date = due_date
        self.status = status


class Project:
    """Project include task."""

    def __init__(self, project_id: str, name: str) -> None:
        """Initialize Project object."""
        self.project_id = project_id
        self.name = name


class TaskOrganizer:
    """SQL."""

    def __init__(self, db_name: str) -> None:
        """Initialize TaskOrganizer object."""
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self) -> None:
        """Create tables in the database."""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                description TEXT,
                due_date TEXT,
                status TEXT,
                project_id TEXT,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        """)
        self.conn.commit()

    def add_project(self, project: Project) -> None:
        """Add project to the database."""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO projects (id, name) VALUES (?, ?)",
            (project.project_id, project.name),
        )
        self.conn.commit()

    def add_task(self, project_id: str, task: Task) -> None:
        """Add task to the database."""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (id, description, due_date, status, project_id)"
            "VALUES (?, ?, ?, ?, ?)",
            (
                task.task_id,
                task.description,
                task.due_date,
                task.status,
                project_id,
            ),
        )
        self.conn.commit()

    def edit_task(
        self,
        project_id: str,
        task_id: str,
        description: Optional[str] = None,
        due_date: Optional[str] = None,
        status: Optional[str] = None,
    ) -> bool:
        """Edit task in the database."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM tasks WHERE project_id = ? AND id = ?",
            (project_id, task_id),
        )
        task_data = cursor.fetchone()
        if task_data:
            if description is None:
                description = task_data[1]
            if due_date is None:
                due_date = task_data[2]
            if status is None:
                status = task_data[3]
            cursor.execute(
                "UPDATE tasks SET description = ?, due_date = ?, status = ?"
                "WHERE project_id = ? AND id = ?",
                (description, due_date, status, project_id, task_id),
            )
            self.conn.commit()
            return True
        else:
            return False

    def list_tasks(self, project_id: str) -> List[Tuple[str, str, str, str]]:
        """List tasks for a project."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM tasks WHERE project_id = ?", (project_id,)
        )
        tasks = cursor.fetchall()
        return tasks

    def mark_task_completed(self, project_id: str, task_id: str) -> None:
        """Mark task as completed."""
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE tasks SET status = 'completed' "
            "WHERE project_id = ? AND id = ?",
            (project_id, task_id),
        )
        self.conn.commit()

    def list_projects(self) -> List[Tuple[str, str]]:
        """List all projects."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM projects")
        projects = cursor.fetchall()
        return projects

    def get_task_counts(self, project_id: str) -> Dict[str, int]:
        """Get task counts for a project."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT status, COUNT(*) "
            "FROM tasks WHERE project_id = ? GROUP BY status",
            (project_id,),
        )
        task_counts = cursor.fetchall()
        counts = {"completed": 0, "incomplete": 0, "overdue": 0}
        for status, count in task_counts:
            counts[status] = count
        return counts

    def delete_project(self, project_id: str) -> None:
        """Delete project and its tasks."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE project_id = ?", (project_id,))
        cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        self.conn.commit()

    def delete_task(self, project_id: str, task_id: str) -> None:
        """Delete task from a project."""
        cursor = self.conn.cursor()
        cursor.execute(
            "DELETE FROM tasks WHERE project_id = ? AND id = ?",
            (project_id, task_id),
        )
        self.conn.commit()


def validate_date(date_string: str) -> bool:
    """Validate date format."""
    try:
        datetime.strptime(date_string, "%m/%d/%Y")
        return True
    except ValueError:
        return False


def main() -> None:
    """Run the program."""
    organizer = TaskOrganizer("task_organizer.db")

    while True:
        print("\nTask and Project Organizer")
        print("Current Projects:")
        projects = organizer.list_projects()
        for project_id, project_name in projects:
            task_counts = organizer.get_task_counts(project_id)
            print(f"Project ID: {project_id}, Name: {project_name}")
            print(
                f"   Completed: {task_counts['completed']}, "
                f"Incomplete: {task_counts['incomplete']}, "
                f"Overdue: {task_counts['overdue']}"
            )

        print("\nMenu:")
        print("1. Add Project")
        print("2. Add Task")
        print("3. Edit Task")
        print("4. List Tasks")
        print("5. Mark Task as Completed")
        print("6. Delete")
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
            task = Task(task_id, description, due_date)
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
            success = organizer.edit_task(
                project_id, task_id, description, due_date, status
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
                for task_id, description, due_date, status in tasks:
                    due_date_obj = datetime.strptime(due_date, "%m/%d/%Y")
                    current_date = datetime.now().date()
                    if (
                        status != "completed"
                        and due_date_obj.date() < current_date
                    ):
                        status = "overdue"
                    print(
                        f"Task ID: {task_id}, Description: {description}, "
                        f"Due Date: {due_date}, Status: {status}"
                    )
                task_id = input(
                    "Enter task ID for more details (leave blank to skip): "
                )
                if task_id:
                    for task_id, description, due_date, status in tasks:
                        if task_id == task_id:
                            print(f"Task ID: {task_id}")
                            print(f"Description: {description}")
                            print(f"Due Date: {due_date}")
                            print(f"Status: {status}")
                            break
            else:
                print(f"No tasks found for project '{project_id}'.")
        elif choice == "5":
            project_id = input("Enter project ID: ")
            tasks = organizer.list_tasks(project_id)
            if tasks:
                print(f"Tasks for Project '{project_id}':")
                for task_id, description, _, _ in tasks:
                    print(f"Task ID: {task_id}, Description: {description}")
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
                    for task_id, description, _, _ in tasks:
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
        elif choice == "0":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
