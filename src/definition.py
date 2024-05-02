"""Define classes and functions."""

import sqlite3
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple


class Task:
    """Task."""

    def __init__(
        self,
        task_id: str,
        description: str,
        due_date: str,
        status: str = "pending",
        priority: str = "medium",
        recurrence: str = "none",
    ) -> None:
        """Initialize Task object."""
        self.task_id = task_id
        self.description = description
        self.due_date = due_date
        self.status = status
        self.priority = priority
        self.recurrence = recurrence


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
                priority TEXT,
                recurrence TEXT,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                entity_type TEXT, 
                entity_id TEXT, 
                action TEXT, 
                details TEXT, 
                timestamp TEXT DEFAULT (datetime('now'))
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
        self.log_history(
            "Project",
            project.project_id,
            "Add",
            f"Added project {project.name}",
        )

    def add_task(self, project_id: str, task: Task) -> None:
        """Add task to the database."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO tasks (
                id, 
                description, 
                due_date, 
                status, 
                project_id, 
                priority, 
                recurrence
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                task.task_id,
                task.description,
                task.due_date,
                task.status,
                project_id,
                task.priority,
                task.recurrence,
            ),
        )
        self.conn.commit()
        self.log_history(
            "Task", task.task_id, "Add", f"Added task {task.description}"
        )

    def log_history(
        self, entity_type: str, entity_id: str, action: str, details: str
    ) -> None:
        """Log history in the database."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO history (entity_type, entity_id, action, details) 
            VALUES (?, ?, ?, ?)
            """,
            (entity_type, entity_id, action, details),
        )
        self.conn.commit()

    def fetch_history(self) -> List[Any]:
        """Fetch and return all history logs."""
        cursor = self.conn.cursor()
        cursor.execute(
            """SELECT entity_type, entity_id, action, details, timestamp 
            FROM history 
            ORDER BY timestamp DESC"""
        )
        return cursor.fetchall()

    def search_tasks(self, keyword: str) -> Any:
        """Search tasks in the database."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM tasks WHERE description LIKE ?",
            ("%" + keyword + "%",),
        )
        return cursor.fetchall()

    def search_projects(self, keyword: str) -> Any:
        """Search projects in the database."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM projects WHERE name LIKE ?", ("%" + keyword + "%",)
        )
        return cursor.fetchall()

    def handle_recurring_tasks(self) -> None:
        """Handle recurring tasks."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE recurrence != 'none'")
        recurring_tasks = cursor.fetchall()
        for task in recurring_tasks:
            (
                task_id,
                description,
                due_date,
                status,
                project_id,
                priority,
                recurrence,
            ) = task
            if status == "completed":
                next_due_date = datetime.strptime(
                    due_date, "%m/%d/%Y"
                ) + timedelta(days=self.get_recurrence_days(recurrence))
                new_task_id = task_id + "_next"
                cursor.execute(
                    """INSERT INTO tasks (
                        id, 
                        description, 
                        due_date, 
                        status, 
                        project_id, 
                        priority, 
                        recurrence
                        ) 
                        VALUES (?, ?, ?, 'pending', ?, ?, ?)""",
                    (
                        new_task_id,
                        description,
                        next_due_date.strftime("%m/%d/%Y"),
                        project_id,
                        priority,
                        recurrence,
                    ),
                )
            self.log_history(
                "Task",
                new_task_id,
                "Recur",
                f"New task {new_task_id} created based on recurrence settings",
            )
        self.conn.commit()

    def get_recurrence_days(self, recurrence: str) -> int:
        """Get recurrence days."""
        recurrence_days = {"daily": 1, "weekly": 7, "monthly": 30}
        return recurrence_days.get(recurrence, 0)

    def edit_task(
        self,
        project_id: str,
        task_id: str,
        description: Optional[str] = None,
        due_date: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        recurrence: Optional[str] = None,
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
            if priority is None:
                priority = task_data[5]
            if recurrence is None:
                recurrence = task_data[6]
            cursor.execute(
                """UPDATE tasks SET 
                description = ?, 
                due_date = ?, 
                status = ?, 
                priority = ?, 
                recurrence = ?
                WHERE project_id = ? AND id = ?""",
                (
                    description,
                    due_date,
                    status,
                    priority,
                    recurrence,
                    project_id,
                    task_id,
                ),
            )
            self.conn.commit()
            self.log_history("Task", task_id, "Edit", f"Task {task_id} edited")
            return True
        else:
            return False

    def list_tasks(self, project_id: str) -> List[Any]:
        """List tasks for a given project sorted by priority.."""
        cursor = self.conn.cursor()
        cursor.execute(
            """SELECT id, description, due_date, status, priority, recurrence
            FROM tasks
            WHERE project_id = ?
            ORDER BY CASE priority
            WHEN 'high' THEN 1
            WHEN 'medium' THEN 2
            WHEN 'low' THEN 3
            END;""",
            (project_id,),
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
        self.log_history(
            "Task", task_id, "Complete", f"Task {task_id} marked as completed"
        )

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
        counts = {"completed": 0, "pending": 0, "overdue": 0}
        for status, count in task_counts:
            counts[status] = count
        return counts

    def delete_project(self, project_id: str) -> None:
        """Delete project and its tasks."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE project_id = ?", (project_id,))
        cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        self.conn.commit()
        self.log_history(
            "Project", project_id, "Delete", f"Project {project_id} deleted"
        )

    def delete_task(self, project_id: str, task_id: str) -> None:
        """Delete task from a project."""
        cursor = self.conn.cursor()
        cursor.execute(
            "DELETE FROM tasks WHERE project_id = ? AND id = ?",
            (project_id, task_id),
        )
        self.conn.commit()
        self.log_history("Task", task_id, "Delete", f"Task {task_id} deleted")


def validate_date(date_string: str) -> bool:
    """Validate date format."""
    try:
        datetime.strptime(date_string, "%m/%d/%Y")
        return True
    except ValueError:
        return False
