"""Tests for the application."""

import unittest
from unittest.mock import patch

from definition import Project, Task, TaskOrganizer


class TestTaskOrganizer(unittest.TestCase):
    """Test class."""

    def setUp(self) -> None:
        """Set up the tests with patched database connection."""
        self.patcher = patch("definition.sqlite3.connect", autospec=True)
        self.mock_connect = self.patcher.start()
        self.mock_conn = self.mock_connect.return_value
        self.mock_cursor = self.mock_conn.cursor.return_value
        self.organizer = TaskOrganizer("test_db.sqlite")

    def tearDown(self) -> None:
        """End the tests."""
        self.patcher.stop()

    def test_add_project(self) -> None:
        """Test adding projects."""
        project = Project("1", "Test Project")
        self.organizer.add_project(project)
        print(self.mock_cursor.execute.mock_calls)
        self.mock_cursor.execute.assert_any_call(
            "INSERT INTO projects (id, name) VALUES (?, ?)",
            (project.project_id, project.name),
        )

    def test_add_task(self) -> None:
        """Test adding tasks."""
        task = Task(
            "1", "Test Task", "01/01/2024", "pending", "medium", "none"
        )
        self.organizer.add_task("1", task)
        self.mock_cursor.execute.assert_any_call(
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
                "1",
                task.priority,
                task.recurrence,
            ),
        )

    def test_edit_task(self) -> None:
        """Test editing tasks."""
        self.mock_cursor.fetchone.return_value = (
            "1",
            "Old Description",
            "01/01/2024",
            "pending",
            "1",
            "medium",
            "none",
        )
        success = self.organizer.edit_task(
            "1", "1", description="New Description"
        )
        self.assertTrue(success)
        self.mock_cursor.execute.assert_any_call(
            """UPDATE tasks SET 
                description = ?, 
                due_date = ?, 
                status = ?, 
                priority = ?, 
                recurrence = ?
                WHERE project_id = ? AND id = ?""",
            (
                "New Description",
                "01/01/2024",
                "pending",
                "medium",
                "none",
                "1",
                "1",
            ),
        )

    def test_handle_recurring_tasks(self) -> None:
        """Test handling of recurring tasks."""
        self.mock_cursor.fetchall.return_value = [
            (
                "1",
                "Recur Task",
                "01/01/2024",
                "completed",
                "1",
                "medium",
                "daily",
            )
        ]
        self.organizer.handle_recurring_tasks()
        self.assertTrue(self.mock_cursor.execute.called)
        self.mock_cursor.execute.assert_called()

    def test_fetch_history(self) -> None:
        """Test fetching history records."""
        self.organizer.fetch_history()
        self.mock_cursor.execute.assert_any_call(
            """SELECT entity_type, entity_id, action, details, timestamp 
            FROM history 
            ORDER BY timestamp DESC"""
        )

    def test_search_tasks(self) -> None:
        """Test searching tasks."""
        self.organizer.search_tasks("test")
        self.mock_cursor.execute.assert_any_call(
            "SELECT * FROM tasks WHERE description LIKE ?",
            ("%test%",),
        )

    def test_list_tasks(self) -> None:
        """Test listing tasks."""
        project_id = "1"
        self.organizer.list_tasks(project_id)
        self.mock_cursor.execute.assert_called_with(
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

    def test_mark_task_completed(self) -> None:
        """Test marking task as comleted."""
        project_id = "1"
        task_id = "101"
        self.organizer.mark_task_completed(project_id, task_id)
        self.mock_cursor.execute.assert_any_call(
            "UPDATE tasks SET status = 'completed' "
            "WHERE project_id = ? AND id = ?",
            (project_id, task_id),
        )

    def test_delete_project(self) -> None:
        """Test deleting project."""
        project_id = "1"
        self.organizer.delete_project(project_id)
        self.mock_cursor.execute.assert_any_call(
            "DELETE FROM tasks WHERE project_id = ?", (project_id,)
        )
        self.mock_cursor.execute.assert_any_call(
            "DELETE FROM projects WHERE id = ?", (project_id,)
        )


if __name__ == "__main__":
    unittest.main()
