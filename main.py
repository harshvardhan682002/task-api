from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from database import SessionLocal, engine, Base
from models import Task

Base.metadata.create_all(bind=engine)     # creates the tasks table if it doesn't exist

app = FastAPI()


class TaskCreate(BaseModel):              # data the client sends
    title: str
    done: bool = False


class TaskOut(BaseModel):                 # data we send back
    id: int
    title: str
    done: bool
    model_config = ConfigDict(from_attributes=True)   # lets it read database objects


def get_db():                             # opens a session, always closes it afterwards
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {"message": "Hello, Task API"}


@app.post("/tasks", response_model=TaskOut)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    new_task = Task(title=task.title, done=task.done)
    db.add(new_task)          # stage the new row
    db.commit()               # save it to the file
    db.refresh(new_task)      # reload it so the generated id is filled in
    return new_task


@app.get("/tasks", response_model=list[TaskOut])
def list_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()


@app.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.put("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, updated: TaskCreate, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    task.title = updated.title
    task.done = updated.done
    db.commit()
    db.refresh(task)
    return task


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"message": "Task deleted"}