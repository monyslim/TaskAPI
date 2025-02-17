# FastAPI Task Manager

## 📌 Project Overview
This project is a simple **Task Management API** built using **FastAPI**. The API allows users to:
- **Create Tasks**
- **View Tasks**
- **Update Tasks**
- **Delete Tasks**

It is containerized with **Docker** and deployed on a **Kubernetes cluster**.

---

## 🖥️ Installation & Setup

### Prerequisites
Ensure you have the following installed:
- [Python 3.9+](https://www.python.org/downloads/)
- [Docker](https://www.docker.com/products/docker-desktop/)
- [Kubernetes (kubectl)](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- [Minikube (for local clusters)](https://minikube.sigs.k8s.io/docs/start/)

---

## 📂 Project Structure
```
Task/
│── main.py               # FastAPI server
│── Dockerfile            # Docker configuration
│── requirements.txt      # Python dependencies
└── deployment.yaml       # Kubernetes deployment config
```

---

## 🚀 API Endpoints

| Method | Endpoint        | Description              |
|--------|---------------|--------------------------|
| `POST`   | `/tasks/`       | Create a new task       |
| `GET`    | `/tasks/`       | Retrieve all tasks     |
| `PUT`    | `/tasks/{id}`   | Update a task          |
| `DELETE` | `/tasks/{id}`   | Delete a task          |

### API Request/Response Examples
#### Create Task
```json
POST /tasks/
{
  "title": "Complete Project",
  "description": "Finish the FastAPI project",
  "completed": false
}
```
Response:
```json
{
  "id": 1,
  "title": "Complete Project",
  "description": "Finish the FastAPI project",
  "completed": false
}
```

#### View Tasks
```json
GET /tasks/
```
Response:
```json
[
  {
    "id": 1,
    "title": "Complete Project",
    "description": "Finish the FastAPI project",
    "completed": false
  }
]
```

---

## 🖥️ FastAPI Backend Code (`main.py`)
```python
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
```

## Install Dependcies
- Make sure you have Python and *pip* installed.
```
pip install -r requirements.txt
```

## Run locally
```
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
- The API will be available at: http://127.0.0.1:8000/docs

---

## 🐳 Docker Setup
📌 `Dockerfile`
```dockerfile
FROM python:3.9

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

📌 `requirements.txt`
```
fastapi
uvicorn
```

---

## ☸️ Kubernetes Deployment
📌 `deployment.yaml`
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: task-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: task-api
  template:
    metadata:
      labels:
        app: task-api
    spec:
      containers:
      - name: task-api
        image: your-dockerhub-username/task-api:latest
        ports:
        - containerPort: 8000
        imagePullPolicy: Always

---
apiVersion: v1
kind: Service
metadata:
  name: task-api-service
spec:
  selector:
    app: task-api
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
```

---

##  Deployment Instructions
### Run Locally with Docker
```bash
docker build -t task-api .
docker run -p 8000:8000 task-api
```
Access API: **http://localhost:8000/docs**

### Deploy to Kubernetes
#### Build & Push Docker Image
```bash
docker build -t your-dockerhub-username/task-api:latest .
docker login
docker push your-dockerhub-username/task-api:latest
```

#### Apply Kubernetes Configurations
```bash
kubectl apply -f deployment.yaml
```

#### Check Deployment Status
```bash
kubectl get pods
kubectl get services
```

#### Expose API in Minikube
```bash
minikube service task-api-service
```

For cloud-based Kubernetes (AWS/GKE/AKS), check the external IP:
```bash
kubectl get services
```

Then access:
```
http://<EXTERNAL-IP>/docs
```
---

## 🔄 CI/CD Deployment
GitHub Actions Workflow
The project includes an automation pipeline that:

Builds the Docker image
Pushes it to DockerHub
Deploys the app to Kubernetes
- Trigger: Every push to the *master* branch.

## Fix: Ensure Kubernetes Context Is Set in GitHub Actions
- If deploying to **AWS EKS**, modify the workflow like this:
```yaml
      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1  # Change to your AWS region

      - name: Update kubeconfig for EKS
        run: aws eks update-kubeconfig --name YOUR_EKS_CLUSTER_NAME --region us-east-1

      - name: Deploy to Kubernetes
        run: |
          kubectl apply -f deployment.yaml
          kubectl apply -f ingress.yaml
```
---
- If deploying to **Azure AKS**, use this:
```yaml
      - name: Azure Login
        uses: azure/login@v2
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Get AKS Credentials
        run: az aks get-credentials --resource-group YOUR_RESOURCE_GROUP --name YOUR_AKS_CLUSTER_NAME

      - name: Deploy to Kubernetes
        run: |
          kubectl apply -f deployment.yaml
          kubectl apply -f ingress.yaml
```

## Final Steps
1. Add the correct authentication method to your GitHub Actions.
2. Store the necessary credentials in GitHub Secrets.
3. Push the changes and re-run the workflow.


## 🎯 Conclusion
✅ FastAPI-based Task Manager  
✅ Dockerized for containerization  
✅ Deployed on Kubernetes  


## 🔗 Contact
#### Author: David
#### GitHub: monyslim
#### Email: dewcapon@ymail.com

🚀😊