# Library Project

## Project Setup

### Create a project
The project structure is:
```
$PROJECT_NAME/
  manage.py
  $PROJECT_NAME/           <- config dir
    settings.py
  $APP_NAME/
```
Create a new Django project named **library_project**, then start a new app called **library_app**.

#### Option 1: Create manually
> Note: If you already have **.venv**, just activate it (```source .venv/bin/activate```) first and skip creating it. 

```
# Create the project directory
mkdir library_project
cd library_project

# Upgrade pip (Optional)
pip install --upgrade pip

# Create a virtual environment to isolate our package dependencies locally
# If you already have .venv, just activate it first and skip creating it.
python3 -m venv .venv
source .venv/bin/activate

# Install Django and Django REST framework into the virtual environment
pip install django djangorestframework

# Set up a new project with a single application
django-admin startproject library_project .
python manage.py startapp library_app
```

##### Configure the Project
Add your new app to the INSTALLED_APPS in library_project/settings.py:
```
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'library_app',  # Add this line
    'rest_framework',  # Add this for DRF
]
```

##### Apply migrations - Now sync your database for the first time:
After creating the project and activating the virtual environment, run it from the project root:
```
python manage.py migrate
```
This command "syncs" the database structure with your Django project for the first time.

```python manage.py migrate``` applies Django migrations to your database. Django migrations are database schema changes generated from your models and built-in apps.
Running this command creates the tables and fields your project needs.

For a new project, it sets up:
- auth/user tables
- admin tables
- session and content types tables
- any app models you have defined

As a result, your SQLite database (db.sqlite3) is initialized with the tables Django needs so the app can run.

##### Create an admin user account in your Django project
Create an initial user named *admin* with a password. We'll authenticate as that user later in our example.

```
python manage.py createsuperuser --username admin --email admin@example.com
```
Django requires a user account with staff/superuser permissions to log into the admin site. This command creates that initial user so you can authenticate and manage data later.

In this project, you’ll use this admin account to sign in and verify authentication flow. It also gives you a ready-to-use user for testing admin-only or authenticated API behavior. This is the first real user in your app, and it gives you a known login (admin) to use while you build and test the project.

##### Start the development server:
Option 1: Activate the project venv
```
source .venv/bin/activate
python --version
python manage.py runserver
```

Option 2: Run Python directly from the venv
```
.venv/bin/python --version
.venv/bin/python manage.py runserver
```

#### Option 2: Create via a script
- Accepts: --projectname <name> and --appname <name> (required), --username <name> and --email <email> (optional)
- Creates the project directory, virtualenv, installs Django and Django REST framework, scaffolds the project/app, applies migrations, and optionally creates a superuser
```
./scripts/createproject.sh --projectname library_project --appname library_app --username admin --email admin@example.com
```

Once you've set up the database and created the initial user, you're ready to start developing. The next sections will guide you through building the library application.

## Project Structure
To build this application using Clean Architecture in Django, we will strictly separate our concerns into layers: 
- Domain (Entities),
- Interfaces (Abstract Repositories/Ports), 
- Use Cases (Services),
- Infrastructure/Delivery (In-Memory Database and Django Views).

Following the Dependency Inversion principle, our Services will only depend on Interfaces, completely isolating our core business logic from Django and the database implementation.
```
library_project/
├── manage.py
├── library_project/          # Django core settings
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── library_app/              # Our application
    ├── __init__.py
    ├── apps.py
    ├── domain.py           # Layer 1: Entities
    ├── interfaces.py       # Layer 2: Abstract Ports (Contracts)
    ├── infrastructure.py   # Layer 3: DB Adapters
    ├── services.py         # Layer 4: Use Cases / Business Logic
    ├── dependencies.py     # Dependency Injection Container
    ├── views.py            # Layer 5: Delivery / Controllers
    └── urls.py             # Layer 5: Routing
```

- `Domain Layer (library_app/domain.py)` - This layer holds our enterprise business rules and entities. They are pure Python dataclasses with no knowledge of the outside world.
- `Interface Layer (library_app/interfaces.py)` - This layer defines the contracts (ports) that the outer layers must implement. The service layer will depend *only* on this interface.
- `Use Case / Service Layer (library_app/services.py)` - This layer contains the application-specific business rules. Notice how it strictly relies on IBookRepository and has zero knowledge of Django or how the database is implemented.
- `Infrastructure Layer (library_app/infrastructure.py)` - This layer implements the interfaces defined earlier. Here, we build our in-memory database adapter.
- `Dependency Injection (library_app/dependencies.py)` - To wire the application together cleanly, we instantiate our specific adapters and inject them into the services.
- `Delivery Layer / Controllers (library_app/views.py)` - The Django views act as simple delivery mechanisms. They parse the HTTP request, pass data to the Use Cases, and format the response.
- `Routing (library_app/urls.py & library_project/urls.py)` - Make sure to include your app's URLs in the main project configuration.

## API Paths:

### Authors
```
GET /api/authors/ 
GET /api/authors/{id} 
POST /api/authors/ 
PUT /api/authors/{id} 
DELETE /api/authors/{id}
```

#### GET /api/authors/
```
curl -X GET -H "Content-Type: application/json" http://127.0.0.1:8000/api/authors/
```

#### GET /api/authors/
```
curl -X GET -H "Content-Type: application/json" http://127.0.0.1:8000/api/authors/917840/
```

#### POST /api/authors/
```
curl -i -X POST -H "Content-Type: application/json" -d '{"name": "Jane", "surname":"Austin", "date_of_birth":"1880-02-12" }' http://127.0.0.1:8000/api/authors/
```

#### PUT /api/authors/{id}
```
curl -i -X PUT -H "Content-Type: application/json" -d '{"name": "Jane", "surname":"Austin", "date_of_birth":"1883-02-12"}' http://127.0.0.1:8000/api/authors/56a849b8-dc24-4555-89da-570946682009/
```

#### DELETE PUT /api/authors/{id}
```
curl -i -X DELETE -H "Content-Type: application/json" http://127.0.0.1:8000/api/authors/56a849b8-dc24-4555-89da-570946682009/
```

### Books
```
GET /api/books/
GET /api/books/{id}
POST /api/books/
PUT /api/books/{id}
DELETE /api/books/{id}
```

#### GET /api/books/
```
curl -X GET -H "Content-Type: application/json" http://127.0.0.1:8000/api/books/
```

#### GET /api/books/{id}
```
curl -X GET -H "Content-Type: application/json" http://127.0.0.1:8000/api/books/917840/
```

#### POST /api/books/
```
curl -i -X POST -H "Content-Type: application/json" -d '{"title":"pride", "published_year":1880,"author_id":"56a849b8-dc24-4555-89da-570946682009"}' http://127.0.0.1:8000/api/books/
```

#### PUT /api/books/{id}
```
curl -i -X PUT -H "Content-Type: application/json" -d '{"id":917840 , "title":"pride", "published_year":1990,"author_id":"56a849b8-dc24-4555-89da-570946682009"}' http://127.0.0.1:8000/api/books/bcbacaa7-ec36-4f25-8c50-41a52672ce6a/
```

#### DELETE PUT /api/books/{id}
```
curl -i -X DELETE -H "Content-Type: application/json" http://127.0.0.1:8000/api/books/bcbacaa7-ec36-4f25-8c50-41a52672ce6a/
```


