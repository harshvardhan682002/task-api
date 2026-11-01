from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from database import engine, Base, get_db
from models import Task, User
from auth import hash_password, verify_password, create_access_token, get_current_user

Base.metadata.create_all(bind=engine)

app = FastAPI()


class UserCreate(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    model_config = ConfigDict(from_attributes=True)


class TaskCreate(BaseModel):
    title: str
    done: bool = False


class TaskOut(BaseModel):
    id: int
    title: str
    done: bool
    model_config = ConfigDict(from_attributes=True)


def get_user_task(db: Session, task_id: int, user: User) -> Task:
    """Find a task that belongs to this user, or raise 404."""
    task = (
        db.query(Task)
        .filter(Task.id == task_id, Task.owner_id == user.id)
        .first()
    )
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.get("/")
def home():
    return {"message": "Hello, Task API"}


@app.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    new_user = User(username=user.username, hashed_password=hash_password(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form.username).first()
    if user is None or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    return {"access_token": create_access_token(user.username), "token_type": "bearer"}


@app.post("/tasks", response_model=TaskOut)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_task = Task(title=task.title, done=task.done, owner_id=current_user.id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@app.get("/tasks", response_model=list[TaskOut])
def list_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Task).filter(Task.owner_id == current_user.id).all()


@app.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_task(db, task_id, current_user)


@app.put("/tasks/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    updated: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = get_user_task(db, task_id, current_user)
    task.title = updated.title
    task.done = updated.done
    db.commit()
    db.refresh(task)
    return task


@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = get_user_task(db, task_id, current_user)
    db.delete(task)
    db.commit()
    return {"message": "Task deleted"}