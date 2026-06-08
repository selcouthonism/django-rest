# Library Management


 - [Authentication Service](#authentication-service)
Textbook Rent Service
Nginx
Database

## Launch The Library Management System

## Authentication Service
- [Project Structure](#1-project-structure)
- [Launch the Application](#2-launching-the-application)

### 1. Project Structure
This project has been structured strictly separating the Domain, Application (Use Cases), Infrastructure (Adapters/Frameworks), and Presentation layers. The inner layers (Domain, Application) have zero dependencies on Django or external libraries; they solely depend on abstract interfaces.

```
auth_service/
├── core/                       # Clean Architecture layers
│   ├── domain/                 # Pure Python Entities & Interfaces (Ports)
│   ├── application/            # Use Cases (Business Logic)
│   ├── infrastructure/         # Concrete Implementations (Adapters: DB, JWT, Hash)
│   └── presentation/           # Django Views (Controllers)
├── django_app/                 # Standard Django App bridging the ORM
│   ├── models.py               # Django ORM Models
│   └── urls.py                 # Endpoint routing
├── auth_project/               # Django Core Settings
│   └── settings.py
└── requirements.txt
```

### 2. Launching the Application
The environment dictates whether we use the in-memory SQLite database (for dev) or PostgreSQL (for prod). Because we structured the settings.py to read the ENVIRONMENT variable, launching the app is straightforward.

#### For Development (In-Memory Database):
Because SQLite in-memory databases are wiped as soon as the process stops, you will need to run migrations every time you start the dev server, or handle database initialization on startup.

##### Launch via python runserver
```
# Set the environment, run migrations, and start the server
export ENVIRONMENT=dev
python manage.py makemigrations django_app
python manage.py migrate
#python manage.py runserver
python manage.py runserver 0.0.0.0:8000
```

###### Seeding the Database
The domain logic requires a user with a hashed password, we can create a quick Django management script to inject a test user into the in-memory sqllite database.
```
python seed_db.py
```

##### Testing Login API
```
curl -i -X POST http://0.0.0.0:8000/api/v1/login \
     -H "Content-Type: application/json" \
     -d '{"username": "test_admin", "password": "securepassword123"}'                                       
```

##### Testing Verify API
```
#Extract Token
TOKEN=$(curl -s -X POST http://0.0.0.0:8000/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test_admin", "password": "securepassword123"}' \
  | jq -r '.access_token')

#Check token status
curl -i http://0.0.0.0:8000/api/v1/verify \
     -H "Authorization: Bearer $TOKEN"                                          
```

#### For Production (PostgreSQL):
In production, you would typically run this behind an application server like Gunicorn, rather than Django's built-in dev server.

##### Launch via python runserver
```
export ENVIRONMENT=prod
python manage.py migrate
gunicorn auth_project.wsgi:application --bind 0.0.0.0:8000 --workers 3
```
