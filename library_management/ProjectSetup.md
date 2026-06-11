# Project Setup

## Authentication Service

#### 1. Create Django Project
```
# Create the project directory
mkdir auth_service
cd auth_service

# Upgrade pip (Optional)
pip install --upgrade pip

# Create a virtual environment to isolate our package dependencies locally
# If you already have .venv, just activate it first and skip creating it.
python3 -m venv .venv
source .venv/bin/activate

# Install Django and Django REST framework into the virtual environment
pip install django djangorestframework

# Set up a new project with a single application
django-admin startproject auth_project .
python manage.py startapp django_app
```

#### 2. Install dependencies
```
# Install JTW
pip install PyJWT

pip install gunicorn
pip install psycopg2-binary
```

#### 3. Configure the Project
Add your new app to the INSTALLED_APPS in library_project/settings.py:
```
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_app',  # Add this line
    'rest_framework',  # Add this for DRF
]
```

#### 4. Apply migrations - Now sync your database for the first time:
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

#### 5. Create an admin user account in your Django project
Create an initial user named *admin* with a password. We'll authenticate as that user later in our example.

```
python manage.py createsuperuser --username admin --email admin@example.com
```
Django requires a user account with staff/superuser permissions to log into the admin site. This command creates that initial user so you can authenticate and manage data later.

In this project, you’ll use this admin account to sign in and verify authentication flow. It also gives you a ready-to-use user for testing admin-only or authenticated API behavior. This is the first real user in your app, and it gives you a known login (admin) to use while you build and test the project.

#### 6. Start the development server:
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