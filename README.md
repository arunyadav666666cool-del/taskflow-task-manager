# TaskFlow - Multi Role Task Manager

A desktop task management application built with **Python**, **Tkinter**, and **SQLite**, featuring role-based login for Admin, Manager, and Employee users.

## Features

- **Multi-role login system** — Admin, Manager, and Employee accounts
- **Admin dashboard** — view all registered users
- **Manager dashboard** — assign tasks to employees with title, description, and priority; view tasks assigned to each employee and their current status
- **Employee dashboard** — view assigned tasks and update task status (Pending / In Progress / Done)
- **Sign-up window** for creating new Manager or Employee accounts
- **SQLite database** (`tasks.db`) — created automatically on first run

## Default Admin Login

```
Username: admin
Password: admin123
```

## Requirements

- Python 3.8 or higher
- Tkinter (included with standard Python installation)

## How to Run

1. Clone or download this repository
2. Open a terminal in the project folder
3. Run:
   ```
   python task_manager_gui.py
   ```
4. The `tasks.db` file will be created automatically on first run

## Usage

1. Log in as **Admin** (admin / admin123) to view all users
2. Click **Sign Up** to create Manager and Employee accounts
3. Log in as a **Manager** to assign tasks to employees
4. Log in as an **Employee** to view assigned tasks and update their status
5. The Manager can refresh their dashboard to see updated task statuses

## Screenshot

![Login Screen](login_screen.png)

## Tech Stack

- Python
- Tkinter (GUI)
- SQLite (database)

## Project Structure

```
task_manager_gui.py   # Main application file
tasks.db               # Auto-generated SQLite database (ignored in git)
```

## Notes

- Passwords are stored as plain text in this version for simplicity — not recommended for production use.
- This is a beginner-friendly project intended for learning role-based access control and basic CRUD operations with SQLite and Tkinter.
