from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import uvicorn

app = FastAPI()

tasks: Dict[int, Dict] = {}
task_id_counter = 1

class Task(BaseModel):
    title: str
    description: str
    completed: bool = False

@app.post("/tasks/", response_model=Dict)
def create_task(task: Task):
    global task_id_counter
    task_data = task.dict()
    tasks[task_id_counter] = task_data
    tasks[task_id_counter]["id"] = task_id_counter
    task_id_counter += 1
    return tasks[task_id_counter - 1]

@app.get("/tasks/", response_model=List[Dict])
def get_tasks():
    return list(tasks.values())

@app.put("/tasks/{task_id}", response_model=Dict)
def update_task(task_id: int, updated_task: Task):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    tasks[task_id].update(updated_task.dict())
    return tasks[task_id]

@app.delete("/tasks/{task_id}", response_model=Dict)
def delete_task(task_id: int):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks.pop(task_id)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)