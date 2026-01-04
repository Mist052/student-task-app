# Student Tasking (Django)

A simple, fully functional student task tracking web app built with **Python + Django**.

## Features
- Accounts (sign up / log in / log out)
- Tasks CRUD (create, edit, delete)
- Mark tasks done / undone
- Courses (to group tasks)
- Tags (to label tasks)
- Dashboard with counts, upcoming tasks, recently completed
- Filters: status, priority, course, due (overdue/today/soon), search

## Quick start

### 1) Create a virtual environment
```bash
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate
```

### 2) Install dependencies
```bash
pip install -r requirements.txt
```

### 3) Initialize the database
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 4) Run the server
```bash
python manage.py runserver
```

Open:
- App: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

## Notes
- This project uses SQLite by default (`db.sqlite3`).
- For production, set `DEBUG = False`, configure `ALLOWED_HOSTS`, and use a real database.
