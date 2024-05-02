# 821-final-project
## Task and Project Organizer

### Introduction
The Task and Project Organizer is a Python-based command-line application designed to help users efficiently manage their tasks and projects. It is ideally suited for individuals looking to organize their personal or professional tasks, offering a range of functionalities from task creation to organization within projects.

### Data Model
The application revolves around two main entities:
- **Tasks**: Each task has attributes such as an ID, description, due date, status (e.g., pending, completed and overdue), priority (e.g., low, medium and high), recurrence (e.g., daily, weekly, monthly and none).
- **Projects**: Each project has an ID, a name, and can contain multiple tasks.

### Features
- **Manage Tasks**: Create, modify, and mark tasks as completed.
- **Listing**: Tasks can be displayed filtered by project and priority.
- **Search**: Search for tasks or projects by keywords.
- **Recurring Tasks**: Set up tasks that recur on a daily, weekly, or monthly basis.
- **Task History**: View a log of changes made to tasks and projects.
- **Command-Line Interface (CLI)**: A user-friendly interface for managing tasks and projects directly from the command line.

### Installation
To install the Task and Project Organizer, follow these steps:
```bash
git clone https://example.com/821-final-project.git
cd 821-final-project
cd src
```

### Usage
To run the Task and Project Organizer:
```bash
python app.py
```
- **Add tasks**: Users can create tasks, specifying their details.
- **Add projects**: Users can create projects.
- **Edit tasks**: Users can modify task details.
- **List tasks by priority**: Display all tasks in one project ordered by priority.
- **Mark tasks as completed**: Update the status of tasks.
- **Delete**: Delete unwanted tasks and projects.
- **Search**: Search tasks or projects based on keywords.
- **View history**: View a log of changes made to tasks and projects.

### Running Tests
To execute the test suite, follow these steps:
```bash
python -m unittest test.py
```

### Contributions
Contributions are welcome! Please fork the repository and submit pull requests with any enhancements, bug fixes, or improvements.
