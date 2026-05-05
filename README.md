# Library Project

## Project Setup

Python version: Python 3.9.5

### Create a project
Create a new Django project named **library_project**, then start a new app called **library_app**.

#### Option 1: Create manually
```
# Create the project directory
mkdir library_project
cd library_project

# Create a virtual environment to isolate our package dependencies locally
python3 -m venv .venv
source .venv/bin/activate

# Install Django and Django REST framework into the virtual environment
pip install djangorestframework

# Set up a new project with a single application
django-admin startproject library_project .
cd library_project
django-admin startapp library_app
cd ..
```

##### Apply migrations - Now sync your database for the first time:
After creating the project and activating the virtual environment (```source .venv/bin/activate```), run it from the project root:
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

#### Start the development server:
```
python manage.py runserver
```

> Note: If you already have **.venv**, just activate it (```source .venv/bin/activate```) first and skip creating it. 

#### Option 2: Create via a script
- Accepts: --projectname <name> and --appname <name> (required), --username <name> and --email <email> (optional)
- Creates the project directory, virtualenv, installs Django and Django REST framework, scaffolds the project/app, applies migrations, and optionally creates a superuser
```
./scripts/createproject.sh --projectname library_project --appname library_app --username admin --email admin@example.com
```

Once you've set up a database and the initial user is created and ready to go, open up the app's directory and we'll get coding...

