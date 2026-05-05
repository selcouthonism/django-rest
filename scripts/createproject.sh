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
  --email        Optional admin email for createsuperuser (will prompt for password)
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
      if [[ -z "${2:-}" ]]; then
        echo "Error: --projectname requires a value"
        exit 1
      fi
      PROJECT_NAME="$2"
      shift 2
      ;;
    --appname)
      if [[ -z "${2:-}" ]]; then
        echo "Error: --appname requires a value"
        exit 1
      fi
      APP_NAME="$2"
      shift 2
      ;;
    --username)
      if [[ -z "${2:-}" ]]; then
        echo "Error: --username requires a value"
        exit 1
      fi
      USERNAME="$2"
      shift 2
      ;;
    --email)
      if [[ -z "${2:-}" ]]; then
        echo "Error: --email requires a value"
        exit 1
      fi
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

if [[ ! "$PROJECT_NAME" =~ ^[a-zA-Z_][a-zA-Z0-9_]*$ ]]; then
  echo "Error: project name must be a valid Python identifier (letters, digits, underscores; cannot start with digit)"
  exit 1
fi

if [[ ! "$APP_NAME" =~ ^[a-zA-Z_][a-zA-Z0-9_]*$ ]]; then
  echo "Error: app name must be a valid Python identifier (letters, digits, underscores; cannot start with digit)"
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

if ! command -v python3 &> /dev/null; then
  echo "Error: python3 is not installed or not in PATH"
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
python manage.py startapp "$APP_NAME"

echo "Applying migrations..."
python manage.py migrate

if [[ -n "$USERNAME" && -n "$EMAIL" ]]; then
  echo "Creating superuser '$USERNAME'..."
  if [[ -z "${DJANGO_SUPERUSER_PASSWORD:-}" ]]; then
    python manage.py createsuperuser --username "$USERNAME" --email "$EMAIL"
  else
    DJANGO_SUPERUSER_PASSWORD="$DJANGO_SUPERUSER_PASSWORD" python manage.py createsuperuser --username "$USERNAME" --email "$EMAIL" --noinput
  fi
fi

echo "Project '$PROJECT_NAME' created successfully."
echo "Next steps:"
echo "  cd $PROJECT_NAME"
echo "  source .venv/bin/activate"
echo "  python manage.py runserver"
