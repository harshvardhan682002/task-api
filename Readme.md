# Task API

A REST API for managing personal tasks, built with FastAPI, SQLAlchemy and SQLite.
Users register, log in with a JWT token, and can only see and change their own tasks.

## Features
- User registration and login (passwords hashed with bcrypt)
- JWT authentication
- Create, read, update and delete tasks
- Each user can access only their own tasks
- Data stored in SQLite through SQLAlchemy

## Tech stack
Python, FastAPI, SQLAlchemy, SQLite, PyJWT, bcrypt

## Run it locally
```bash
git clone https://github.com/harshvardhan682002/task-api.git
cd task-api
python -m venv venv
venv\Scripts\activate        # Windows (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
```

Create a `.env` file in the project folder:
```
SECRET_KEY=replace-with-a-long-random-string
```
Generate a key with:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Start the server:
```bash
python -m uvicorn main:app --reload
```
Open http://127.0.0.1:8000/docs to try the API.

## Endpoints
| Method | Path | Description |
|---|---|---|
| POST | /register | Create a user |
| POST | /login | Get an access token |
| POST | /tasks | Create a task |
| GET | /tasks | List your tasks |
| GET | /tasks/{id} | Get one of your tasks |
| PUT | /tasks/{id} | Update a task |
| DELETE | /tasks/{id} | Delete a task |

## Planned
- Automated tests with pytest
- PostgreSQL, Redis caching and Docker