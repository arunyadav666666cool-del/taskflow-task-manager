"""
=========================================================
  TASKFLOW - Multi Role Task Manager (Beginner Version)
=========================================================
Roles:
  - Admin    : default login (admin / admin123) - can create Managers & Employees
  - Manager  : can assign tasks to Employees
  - Employee : can see their tasks and update status

How to run:
  1) Make sure Python is installed (3.8+)
  2) Save this file as task_manager.py
  3) Open terminal in that folder and run:
         python task_manager.py
  4) A 'tasks.db' file will be created automatically.

Default Admin Login:
  Username: admin
  Password: admin123
=========================================================
"""

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


# =========================================================
# STEP 1: DATABASE SETUP
# =========================================================
DB_NAME = "tasks.db"


def get_connection():
    """Open a connection to the database."""
    return sqlite3.connect(DB_NAME)


def setup_database():
    """Create tables if they don't exist, and add a default admin."""
    conn = get_connection()
    cursor = conn.cursor()

    # Table for all users (Admin, Manager, Employee)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            username  TEXT UNIQUE NOT NULL,
            password  TEXT NOT NULL,
            role      TEXT NOT NULL,
            full_name TEXT NOT NULL
        )
    """)

    # Table for tasks
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            description TEXT,
            priority    TEXT DEFAULT 'Medium',
            status      TEXT DEFAULT 'Pending',
            created_at  TEXT,
            manager_id  INTEGER,
            employee_id INTEGER
        )
    """)

    conn.commit()

    # Create default admin account if no admin exists yet
    cursor.execute("SELECT * FROM users WHERE role = 'Admin'")
    if cursor.fetchone() is None:
        cursor.execute(
            "INSERT INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)",
            ("admin", "admin123", "Admin", "Administrator")
        )
        conn.commit()

    conn.close()


# =========================================================
# STEP 2: LOGIN WINDOW
# =========================================================
class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("TaskFlow - Login")
        self.root.geometry("350x350")

        tk.Label(root, text="TaskFlow Login", font=("Arial", 18, "bold")).pack(pady=20)

        tk.Label(root, text="Username:").pack()
        self.username_entry = tk.Entry(root)
        self.username_entry.pack(pady=5)

        tk.Label(root, text="Password:").pack()
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack(pady=5)

        tk.Button(root, text="Login", width=15, command=self.login).pack(pady=15)
        tk.Button(root, text="Sign Up (Manager/Employee)", command=self.open_signup).pack()

        tk.Label(root, text="\nDefault Admin Login:\nadmin / admin123",
                 fg="gray").pack(pady=10)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if username == "" or password == "":
            messagebox.showwarning("Error", "Please enter username and password")
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, role, full_name FROM users WHERE username=? AND password=?",
            (username, password)
        )
        user = cursor.fetchone()
        conn.close()

        if user is None:
            messagebox.showerror("Error", "Invalid username or password")
            return

        user_id, role, full_name = user
        self.root.destroy()

        new_root = tk.Tk()
        if role == "Admin":
            AdminWindow(new_root, user_id, full_name)
        elif role == "Manager":
            ManagerWindow(new_root, user_id, full_name)
        else:
            EmployeeWindow(new_root, user_id, full_name)
        new_root.mainloop()

    def open_signup(self):
        signup_root = tk.Toplevel(self.root)
        SignupWindow(signup_root)


# =========================================================
# STEP 3: SIGNUP WINDOW (for Manager / Employee)
# =========================================================
class SignupWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Sign Up")
        self.root.geometry("300x300")

        tk.Label(root, text="Create Account", font=("Arial", 14, "bold")).pack(pady=10)

        tk.Label(root, text="Full Name:").pack()
        self.name_entry = tk.Entry(root)
        self.name_entry.pack(pady=5)

        tk.Label(root, text="Username:").pack()
        self.username_entry = tk.Entry(root)
        self.username_entry.pack(pady=5)

        tk.Label(root, text="Password:").pack()
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack(pady=5)

        tk.Label(root, text="Role:").pack()
        self.role_var = tk.StringVar(value="Employee")
        ttk.Combobox(root, textvariable=self.role_var,
                     values=["Manager", "Employee"], state="readonly").pack(pady=5)

        tk.Button(root, text="Create Account", command=self.signup).pack(pady=15)

    def signup(self):
        name = self.name_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        role = self.role_var.get()

        if name == "" or username == "" or password == "":
            messagebox.showwarning("Error", "Please fill all fields")
            return

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)",
                (username, password, role, name)
            )
            conn.commit()
            messagebox.showinfo("Success", "Account created! You can now login.")
            self.root.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")
        finally:
            conn.close()


# =========================================================
# STEP 4: ADMIN WINDOW (manage users)
# =========================================================
class AdminWindow:
    def __init__(self, root, user_id, full_name):
        self.root = root
        self.user_id = user_id
        self.root.title("TaskFlow - Admin Dashboard")
        self.root.geometry("600x450")

        tk.Label(root, text=f"Welcome Admin: {full_name}",
                 font=("Arial", 14, "bold")).pack(pady=10)

        # Table showing all users
        columns = ("id", "username", "full_name", "role")
        self.tree = ttk.Treeview(root, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=130)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Button(root, text="Logout", command=self.logout).pack(pady=5)

        self.load_users()

    def load_users(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, full_name, role FROM users")
        for row in cursor.fetchall():
            self.tree.insert("", tk.END, values=row)
        conn.close()

    def logout(self):
        self.root.destroy()
        new_root = tk.Tk()
        LoginWindow(new_root)
        new_root.mainloop()


# =========================================================
# STEP 5: MANAGER WINDOW (assign tasks)
# =========================================================
class ManagerWindow:
    def __init__(self, root, user_id, full_name):
        self.root = root
        self.user_id = user_id
        self.root.title("TaskFlow - Manager Dashboard")
        self.root.geometry("700x500")

        tk.Label(root, text=f"Welcome Manager: {full_name}",
                 font=("Arial", 14, "bold")).pack(pady=10)

        # ---- Form to assign a new task ----
        form_frame = tk.Frame(root)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Task Title:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.title_entry = tk.Entry(form_frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Description:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.desc_entry = tk.Entry(form_frame, width=30)
        self.desc_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Priority:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.priority_var = tk.StringVar(value="Medium")
        ttk.Combobox(form_frame, textvariable=self.priority_var,
                     values=["High", "Medium", "Low"], state="readonly", width=27).grid(row=2, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Assign To:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.employee_var = tk.StringVar()
        self.employee_combo = ttk.Combobox(form_frame, textvariable=self.employee_var,
                                            state="readonly", width=27)
        self.employee_combo.grid(row=3, column=1, padx=5, pady=5)
        self.load_employees()

        tk.Button(form_frame, text="Assign Task", command=self.assign_task).grid(row=4, column=0, columnspan=2, pady=10)

        # ---- Table showing tasks assigned by this manager ----
        tk.Label(root, text="Tasks You Assigned:", font=("Arial", 12, "bold")).pack(pady=(10, 0))

        columns = ("id", "title", "employee", "priority", "status")
        self.tree = ttk.Treeview(root, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=120)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Refresh", command=self.load_tasks).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Logout", command=self.logout).pack(side="left", padx=5)

        self.load_tasks()

    def load_employees(self):
        """Fill the dropdown with all employees from the database."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, full_name FROM users WHERE role = 'Employee'")
        self.employees = cursor.fetchall()  # list of (id, name)
        conn.close()

        names = [f"{name} (ID:{emp_id})" for emp_id, name in self.employees]
        self.employee_combo["values"] = names

    def assign_task(self):
        title = self.title_entry.get().strip()
        description = self.desc_entry.get().strip()
        priority = self.priority_var.get()
        selected = self.employee_var.get()

        if title == "":
            messagebox.showwarning("Error", "Please enter a task title")
            return

        if selected == "":
            messagebox.showwarning("Error", "Please select an employee")
            return

        # Find which employee was selected
        index = self.employee_combo.current()
        employee_id = self.employees[index][0]

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tasks (title, description, priority, status, created_at, manager_id, employee_id)
            VALUES (?, ?, ?, 'Pending', ?, ?, ?)
        """, (title, description, priority, created_at, self.user_id, employee_id))
        conn.commit()
        conn.close()

        # Clear the form
        self.title_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.priority_var.set("Medium")
        self.employee_var.set("")

        messagebox.showinfo("Success", "Task assigned successfully!")
        self.load_tasks()

    def load_tasks(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tasks.id, tasks.title, users.full_name, tasks.priority, tasks.status
            FROM tasks
            JOIN users ON tasks.employee_id = users.id
            WHERE tasks.manager_id = ?
            ORDER BY tasks.id DESC
        """, (self.user_id,))
        for row in cursor.fetchall():
            self.tree.insert("", tk.END, values=row)
        conn.close()

    def logout(self):
        self.root.destroy()
        new_root = tk.Tk()
        LoginWindow(new_root)
        new_root.mainloop()


# =========================================================
# STEP 6: EMPLOYEE WINDOW (view tasks + update status)
# =========================================================
class EmployeeWindow:
    def __init__(self, root, user_id, full_name):
        self.root = root
        self.user_id = user_id
        self.root.title("TaskFlow - Employee Dashboard")
        self.root.geometry("700x450")

        tk.Label(root, text=f"Welcome: {full_name}",
                 font=("Arial", 14, "bold")).pack(pady=10)

        tk.Label(root, text="Your Assigned Tasks:", font=("Arial", 12, "bold")).pack()

        columns = ("id", "title", "description", "priority", "status")
        self.tree = ttk.Treeview(root, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=120)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # ---- Status update buttons ----
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        tk.Label(btn_frame, text="Update Status to:").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Pending", command=lambda: self.update_status("Pending")).pack(side="left", padx=5)
        tk.Button(btn_frame, text="In Progress", command=lambda: self.update_status("In Progress")).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Done", command=lambda: self.update_status("Done")).pack(side="left", padx=5)

        bottom_frame = tk.Frame(root)
        bottom_frame.pack(pady=5)
        tk.Button(bottom_frame, text="Refresh", command=self.load_tasks).pack(side="left", padx=5)
        tk.Button(bottom_frame, text="Logout", command=self.logout).pack(side="left", padx=5)

        self.load_tasks()

    def load_tasks(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, description, priority, status
            FROM tasks
            WHERE employee_id = ?
            ORDER BY id DESC
        """, (self.user_id,))
        for row in cursor.fetchall():
            self.tree.insert("", tk.END, values=row)
        conn.close()

    def update_status(self, new_status):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Error", "Please select a task first")
            return

        task_id = self.tree.item(selected[0])["values"][0]

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id))
        conn.commit()
        conn.close()

        self.load_tasks()
        messagebox.showinfo("Updated", f"Task status changed to '{new_status}'")

    def logout(self):
        self.root.destroy()
        new_root = tk.Tk()
        LoginWindow(new_root)
        new_root.mainloop()


# =========================================================
# STEP 7: RUN THE APP
# =========================================================
if __name__ == "__main__":
    setup_database()
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()
