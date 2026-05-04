# Library Project

## Project Setup

Python version: Python 3.9.5

Create a new Django project named **library_project**, then start a new app called **library_app**.
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

Now sync your database for the first time:
```
python manage.py migrate
```

Create an initial user named admin with a password. We'll authenticate as that user later in our example.
```
python manage.py createsuperuser --username admin --email admin@example.com
```

Once you've set up a database and the initial user is created and ready to go, open up the app's directory and we'll get coding...

