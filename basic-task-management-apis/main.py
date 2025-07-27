from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI(title="Basic Task Management API", version="1.0.0")

# Task data model
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = ""

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

class Task(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    created_at: datetime
    updated_at: datetime

# In-memory storage
tasks_storage: List[Task] = []
task_id_counter = 1

# Helper function to find task by ID
def find_task_by_id(task_id: int) -> Optional[Task]:
    return next((task for task in tasks_storage if task.id == task_id), None)

# API Endpoints
@app.get("/tasks", response_model=List[Task])
async def get_all_tasks():
    """Fetch all tasks"""
    return tasks_storage

@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(task_data: TaskCreate):
    """Create a new task"""
    global task_id_counter
    
    now = datetime.now()
    new_task = Task(
        id=task_id_counter,
        title=task_data.title,
        description=task_data.description,
        completed=False,
        created_at=now,
        updated_at=now
    )
    
    tasks_storage.append(new_task)
    task_id_counter += 1
    
    return new_task

@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: int, task_update: TaskUpdate):
    """Update an existing task"""
    task = find_task_by_id(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    
    # Update fields if provided
    if task_update.title is not None:
        task.title = task_update.title
    if task_update.description is not None:
        task.description = task_update.description
    if task_update.completed is not None:
        task.completed = task_update.completed
    
    task.updated_at = datetime.now()
    
    return task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_200_OK)
async def delete_task(task_id: int):
    """Delete a task"""
    task = find_task_by_id(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    
    tasks_storage.remove(task)
    return {"message": f"Task {task_id} deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 