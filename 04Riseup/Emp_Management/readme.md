# 📘 Leave Management System – README

A complete Leave Management REST API built with Django + Django REST Framework, featuring role-based permissions for Employees, HR, and Team Leads, with a robust business-logic layer using service classes.

## 🚀 Features
- Employee Leave Request (Create / List / Retrieve)
- HR & Team Lead Leave Approval Workflow
- Role-based access (Employee, HR, Team Lead)
- Withdraw leave (Employee & HR/Lead)
- DRF ViewSet architecture with service layer
- PostgreSQL Database
- JWT Authentication (optional if you're using simple login)
- Auto-generated Swagger / OpenAPI documentation
- Dockerized project — runs with a single command
- Full unit test support (pytest / DRF)

## 🏗 Tech Stack
- Python 3.10+
- Django 4+
- Django REST Framework
- drf-spectacular (Swagger)
- PostgreSQL
- Docker + Docker Compose
- pytest

## 📁 Project Structure (Short Overview)
```
├── employee/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── permissions.py
│   ├── test_leave_requests.py
│   ├── validators.py
│   ├── urls.py
├── leave_manage/
│   ├── settings.py
│   ├── urls.py
├── manage.py
├── Dockerfile
├── docker-compose.yml
├── .pre-commit-config.yaml
├── requirements.txt
├── test_requirements.txt
├── README.md
```
## ⚙️ Environment Variables
Create a `.env` file in project root:
```ini
DEBUG=True
SECRET_KEY=your-secret-key

DB_NAME=leave_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```
## 🖥 Running the Project (Local Machine)
1. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```
2. Install dependencies
```bash
pip install -r requirements.txt
```
3. Test/Extra Install dependencies
```bash
pip install -r test_requirements.txt

# command for store extra dependancies on test_requirements.txt
pip freeze | grep -E "black|blacken-docs|Faker|flake8|isort|pre-commit" >> test_requirements.txt
```
3. Run makemigrations and migrate
```bash
python manage.py makemigrations
# Then
python manage.py migrate
```
4. Start development server
```bash
python manage.py runserver
```

## 🐳 Running the Project with Docker (Recommended)

1. Build & run (one command)
```bash
docker-compose up --build
```
2. Apply migrations inside container
```bash
docker-compose exec web python manage.py migrate
```
3. Create superuser
```bash
docker-compose exec web python manage.py createsuperuser
```

### 1️⃣ Dockerfile
### English:
- A `Dockerfile` is a **set of instructions to build a single Docker image**.
- It defines how your container will look: base OS, Python version, dependencies, code copy, environment variables, commands to run, etc.
- Essentially, it’s like a recipe to create a Docker image.
- Once you build an image from a `Dockerfile`, you can run it as a container anywhere.

### Bengali:
- `Dockerfile` হলো একটি কনটেইনার ইমেজ তৈরির নির্দেশাবলী।
- এটি নির্ধারণ করে কনটেইনারটি কেমন হবে: কোন OS, Python ভার্সন, dependency গুলি, কোড কপি করা, environment - variables, run command ইত্যাদি।
- এটা মূলত একটি রেসিপি যা Docker image তৈরি করে।
- `Dockerfile` থেকে image তৈরি হলে, আপনি এটি যেকোনো মেশিনে চালাতে পারেন।
```Dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]
```
- এখানে বলা হয়েছে: `Python base, dependency install,` কোড কপি এবং gunicorn দিয়ে run করা।

### 2️⃣ docker-compose.yml
### English:
- docker-compose.yml is a configuration file to run multiple containers together.
- It defines services (like web app, db, cache) and how they interact.
- It handles ports, volumes, environment variables, dependencies between services.
- You don’t write commands to build images here (optional), but you link multiple containers and run them together using docker-compose up.

### Bengali:
- docker-compose.yml হলো একাধিক কনটেইনার একসাথে চালানোর configuration ফাইল।
- এটি বিভিন্ন service (যেমন web app, db, cache) এবং তাদের মধ্যে সম্পর্ক define করে।
- এটি handle করে ports, volumes, environment variables, container dependency।
- এখানে image তৈরি করার instruction optional; মূল কাজ হলো container গুলোকে একসাথে orchestrate করা।

### Example:
```yaml
version: "3.9"

services:
  web:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: leave_db
    ports:
      - "5432:5432"
```
- এখানে web container তৈরি হয় Dockerfile থেকে, db container pull হয় postgres image থেকে।
- depends_on নিশ্চিত করে web container আগে db ready হবে।

### 3️⃣ Why we need both

### English:
- Dockerfile → build one image for your app.
- docker-compose.yml → run multiple containers together (app + db + cache etc.), define relationships, volumes, ports.
- Using only Dockerfile → you can run one container manually.
- Using only docker-compose.yml without Dockerfile → you can only use existing images, cannot build custom images easily.

### Bengali:
- Dockerfile → আপনার app এর জন্য একটি ইমেজ তৈরি করে।
- docker-compose.yml → একসাথে multiple container চালায় (app + db + cache), relationship, volume, ports define করে।
- শুধু Dockerfile use করলে → একটি container manual চালাতে হবে।
- শুধু docker-compose.yml use করলে → শুধু existing image use করতে পারবেন, custom image তৈরি করা কঠিন।

## Swagger Documentation (drf-spectacular)
### Install
```bash
pip install drf-spectacular
```
### settings.py
```bash
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}
```
### project-level urls.py
```python
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.urls import path, include

urlpatterns = [
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/", include("leaves.urls")),
]
```
### Add nice docs to your actions
```python
from drf_spectacular.utils import extend_schema, OpenApiResponse

class LeaveRequestViewSet(ModelViewSet):
    ...

    @extend_schema(
        summary="Approve a leave request",
        request=LeaveActionSerializer,
        responses={200: LeaveRequestSerializer},
    )
    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        ...
```

### API runs at:
👉 http://localhost:8000

### Swagger:
👉 http://localhost:8000/api/docs/

### Schema JSON:
👉 http://localhost:8000/api/schema/

| Endpoint                 | Method | Description    |
| ------------------------ | ------ | -------------- |
| `/leaves/`               | GET    | List leaves    |
| `/leaves/`               | POST   | Create leave   |
| `/leaves/{id}/`          | GET    | Retrieve       |
| `/leaves/{id}/approve/`  | POST   | Approve leave  |
| `/leaves/{id}/reject/`   | POST   | Reject leave   |
| `/leaves/{id}/withdraw/` | POST   | Withdraw leave |


## 🟦 Leave Request API
Base Path:
```bash
/api/leaves/
```
1️⃣ Create Leave Request (Employee)
```bash
POST /api/leaves/
```
2️⃣ List Leave Requests
- Employee → sees own
- HR → sees all
- Team Lead → sees team
```bash
GET /api/leaves/
```
3️⃣ Retrieve Leave Request
```bash
GET /api/leaves/{id}/
```
4️⃣ Approve Leave (HR / Team Lead)
```bash
POST /api/leaves/{id}/approve/
```
5️⃣ Reject Leave
```bash
POST /api/leaves/{id}/reject/
```
6️⃣ Withdraw Leave
- Employee → if PENDING
- HR / Team Lead → if APPROVED
```bash
POST /api/leaves/{id}/withdraw/
```
## 📝 Example Request Bodies
📌 Create Leave
```json
{
  "leave_type": "SICK",
  "start_date": "2025-01-10",
  "end_date": "2025-01-12",
  "reason": "Fever"
}
```
📌 Approve / Reject / Withdraw
```json
{
  "note": "Approved. Get well soon."
}
```
## 📑 Swagger Documentation
Once server is running:
| Path           | Description  |
| -------------- | ------------ |
| `/api/schema/` | OpenAPI JSON |
| `/api/docs/`   | Swagger UI   |

## 🧪 Run Tests
### Using pytest
```bash
pytest -v
```
### Inside Docker
```bash
docker-compose exec web pytest -v
```

## 📦 Docker Files Overview
### docker-compose.yml
- web → Django app
- db → PostgreSQL

### Dockerfile
- Uses python:3.10
- Installs dependencies
- Runs Django
