#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat <<EOF
Usage: $(basename "$0") --projectname PROJECT_NAME --appname APP_NAME [--username USERNAME --email EMAIL]

Create a new Django project and app inside a fresh project directory.

Options:
  --projectname  Name of the Django project to create
  --appname      Name of the Django app to create
  --username     Optional admin username for createsuperuser
  --email        Optional admin email for createsuperuser
  --help         Show this help message
EOF
}

PROJECT_NAME=""
APP_NAME=""
USERNAME=""
EMAIL=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --projectname)
      PROJECT_NAME="$2"
      shift 2
      ;;
    --appname)
      APP_NAME="$2"
      shift 2
      ;;
    --username)
      USERNAME="$2"
      shift 2
      ;;
    --email)
      EMAIL="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      usage
      exit 1
      ;;
  esac
done

if [[ -z "$PROJECT_NAME" || -z "$APP_NAME" ]]; then
  echo "Error: --projectname and --appname are required."
  usage
  exit 1
fi

if [[ -n "$USERNAME" && -z "$EMAIL" ]] || [[ -z "$USERNAME" && -n "$EMAIL" ]]; then
  echo "Error: --username and --email must both be provided if one is used."
  usage
  exit 1
fi

if [[ -d "$PROJECT_NAME" ]]; then
  echo "Error: directory '$PROJECT_NAME' already exists."
  exit 1
fi

echo "Creating Django project '$PROJECT_NAME' with app '$APP_NAME'..."

mkdir "$PROJECT_NAME"
cd "$PROJECT_NAME"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install django djangorestframework

django-admin startproject "$PROJECT_NAME" .
cd "$PROJECT_NAME"
django-admin startapp "$APP_NAME"
cd ..

echo "Applying migrations..."
python manage.py migrate

if [[ -n "$USERNAME" && -n "$EMAIL" ]]; then
  echo "Creating superuser '$USERNAME'..."
  python manage.py createsuperuser --username "$USERNAME" --email "$EMAIL"
fi

echo "Project '$PROJECT_NAME' created successfully."
echo "Next steps:"
echo "  cd $PROJECT_NAME"
echo "  source .venv/bin/activate"
echo "  python manage.py runserver"
