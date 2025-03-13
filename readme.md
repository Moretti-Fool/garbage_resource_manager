# Resource Manager API
[![Deployed on Railway](https://img.shields.io/badge/Deployed%20on-Railway-131313?style=for-the-badge&logo=railway)](https://resourcemanager-production.up.railway.app/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.11-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14%2B-blue?logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7%2B-red?logo=redis&logoColor=white)](https://redis.io)
[![Celery](https://img.shields.io/badge/Celery-5.4.0-green?logo=celery)](https://docs.celeryq.dev)
[![Docker](https://img.shields.io/badge/Docker-24.0%2B-blue?logo=docker&logoColor=white)](https://docker.com)
[![JWT](https://img.shields.io/badge/JWT-Auth-orange?logo=jsonwebtokens)](https://jwt.io)


A high-performance backend for managing temporary file uploads with expiration, audit logging, and role-based access control.

## Features
- 🔒 JWT Authentication & Role-based access control
- ⏳ File uploads with auto-expiry and notifications
- 📊 Admin dashboard for audit logs and resource management
- 📨 Email verification workflow
- 🐳 Dockerized (Dev/Prod) with Celery + Redis

## Tech Stack
- **API**: FastAPI (Python)  
- **Database**: PostgreSQL (async)  
- **Caching/Streaming**: Redis  
- **Background Tasks**: Celery  
- **Auth**: JWT

## Live Demo
Explore interactive docs:  
🔗 [Swagger UI](https://resourcemanager-production.up.railway.app/doc) | [ReDoc](https://resourcemanager-production.up.railway.app/redoc)

## Setup

1️⃣ Clone the Repository
```bash
git clone https://github.com/Moretti-Fool/garbage_resource_manager.git
cd garbage_resource_manager
```

2️⃣ Create a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

4️⃣ Setup Environment Variables
```bash
Rename .env.example to .env and update the database credentials.
```

5️⃣ Run Database Migrations
```bash
alembic upgrade head
```

6️⃣ Initialize Admin User  
```bash
python admin_create.py create-admin
```

7️⃣ Start the Application
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

##🐳 Docker Setup

### To run the application using Docker:
```bash
docker-compose -f docker-compose-prod.yml up --build
```
