# Library Management
This repository contains a library management architecture designed for containerized deployment. It demonstrates a secure authentication service, Nginx request routing, and a sample downstream service integration.

- [Launch The Library Management System](#launch-the-library-management-system)
- [Nginx](#nginx)
- [Database](#database)
- [Authentication Service](#authentication-service)
- [.env](#env-file)

## Launch The Library Management System
This section explains how to start the library management stack using Docker Compose. It includes the gateway, auth service, and database containers required for the end-to-end demo.

```
docker-compose up --build -d
```
This command will pull the necessary images, build the Auth Service, start the database, apply migrations, launch Gunicorn, and spin up Nginx to act as your API Gateway and Auth Request proxy.

### End-to-End Testing (via cURL)
We will test Nginx routing, the Authentication Service, and the Nginx auth_request interception.

#### 1. Login to get the JWT
Hit Nginx on port 80, which will proxy the request directly to the auth_service.
```
curl -X POST http://localhost/api/v1/login \
     -H "Content-Type: application/json" \
     -d '{"username": "test_admin", "password": "securepassword123"}'
```

Expected Response:
```
{
  "access_token": "eyJ0eXAi...<jwt_string>...",
  "token_type": "Bearer",
  "expires_in": 900,
  "refresh_token": "eyJ0eXAi...<jwt_string>..."
}
```

#### 2. Access the Downstream Service WITHOUT a Token
Let's attempt to access the textbook_rental service without providing the token. Nginx should intercept this and consult the auth_service's verify endpoint.

```
curl -i http://localhost/api/v1/textbook_rental
```

Response:
```
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{"error": "Unauthorized - Please log in"}
```
Nginx successfully blocked the request before it ever reached the textbook service.

#### 3. Access the Downstream Service WITH a Token
Copy the access_token from Test 1 and pass it in the Authorization header.

##### Extract Token
```
TOKEN=$(curl -s -X POST http://localhost/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test_admin", "password": "securepassword123"}' \
  | jq -r '.access_token')
```

##### Call textbook service
```
curl -i http://localhost/api/v1/textbook_rental \
     -H "Authorization: Bearer $TOKEN"
```

##### Expected Response:
Because we used the ```mendhak/http-https-echo``` image for our textbook rental placeholder, it will echo back the exact request it received from Nginx.
```
{
  "path": "/",
  "headers": {
    "x-user-id": "1",
    "x-user-roles": "ADMIN",
    "host": "localhost",
    "user-agent": "curl/8.7.1",
    "accept": "*/*",
    "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6InRlc3RfYWRtaW4iLCJyb2xlcyI6WyJBRE1JTiJdLCJleHAiOjE3ODEwODE5NzMsImlhdCI6MTc4MTA4MTA3M30.6KREGoKQ0QzE-3vy4QZ1P_IPzngoNUB7m598jERuZpw"
  },
  "method": "GET",
  "body": "",
  "fresh": false,
  "hostname": "localhost",
  "ip": "::ffff:172.19.0.4",
  "ips": [],
  "protocol": "http",
  "query": {},
  "subdomains": [],
  "xhr": false,
  "os": {
    "hostname": "2c2143e54717"
  },
  "connection": {}
}
```
Look at the headers block in the response. Nginx extracted ```x-user-id``` and ```x-user-roles``` from the auth_service and successfully injected them into the downstream request. The textbook_rental service now knows exactly who is making the request without having to parse the JWT itself.

#### 3. Refresh The Token
Access tokens are designed to be short-lived for security reasons. When an access token expires, instead of asking the user to log in again, the client can use the **refresh token** to obtain a new access token without requiring credentials.

**How it works:**
- The `login` endpoint returns both an `access_token` (short-lived, 15 minutes) and a `refresh_token` (long-lived, 7 days by default)
- When the access token expires, the client sends the refresh token to the `/refresh` endpoint
- The auth service validates the refresh token and issues a new access token
- This keeps the user session alive without storing session state on the server (stateless authentication)

**Security benefits:**
- If an access token is compromised, its exposure window is limited (15 minutes)
- Refresh tokens are typically stored securely and sent less frequently
- Refresh tokens can be revoked server-side if needed

See: https://auth0.com/blog/refresh-tokens-what-are-they-and-when-to-use-them/#What-Is-a-Refresh-Token- for more details.

##### Extract Refresh Token
```
REFRESH_TOKEN=$(curl -s -X POST http://localhost/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test_admin", "password": "securepassword123"}' \
  | jq -r '.refresh_token')
```

##### Call refresh token api
```
curl -i http://localhost/api/v1/refresh \
     -d "{\"refresh_token\":\"$REFRESH_TOKEN\"}"
```


## Nginx

Nginx serves as the API Gateway and authentication proxy for the library management system. It acts as the entry point for all client requests, handling routing, request interception, and token validation before forwarding requests to downstream services.

### Key Responsibilities

- **Request Routing** - Routes incoming requests to the appropriate backend service (auth service or downstream services)
- **Authentication Interception** - Uses the `auth_request` directive to validate JWT tokens with the authentication service before allowing access to protected endpoints
- **Header Injection** - Extracts user identity information (user ID and roles) from the auth service and injects them as custom headers (`x-user-id`, `x-user-roles`) into downstream requests
- **Reverse Proxy** - Acts as a reverse proxy for the backend services, shielding them from direct client access

### Configuration

The Nginx configuration is defined in `nginx/nginx.conf` and is automatically loaded when the Docker container starts. It handles:
- Port 80 listening for HTTP traffic
- JWT validation through auth_request calls
- Secure header manipulation and request forwarding

## Database
PostgreSQL is used as the primary database in production environments. When the Docker container is initialized via `docker-compose up`, the database is automatically provisioned with all necessary schemas, tables, and seed records.

### Database Initialization

The database initialization scripts are located in the `database/` folder:

- **`01_schema.sql`** - Defines the database schema and namespaces
- **`02_tables.sql`** - Creates all required tables (users, roles, user_roles, etc.)
- **`03_records.sql`** - Seeds the database with initial data (test users, roles, and permissions)

These SQL files are executed automatically during container startup, ensuring a fully initialized database ready for the authentication service and downstream applications.

## Authentication Service
- [Project Structure](#1-project-structure)
- [Launch the Application](#2-launching-the-application)
- [Unit Test](#unit-testing)

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
#Activate virtual environment
source .venv/bin/activate

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
#Extract Access Token
ACCESS_TOKEN=$(curl -s -X POST http://0.0.0.0:8000/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test_admin", "password": "securepassword123"}' \
  | jq -r '.access_token')

#Check token status
curl -i http://0.0.0.0:8000/api/v1/verify \
     -H "Authorization: Bearer $ACCESS_TOKEN"
```

##### Testing Refresh API
```
#Extract Both Access Token and Refresh Token
read ACCESS_TOKEN REFRESH_TOKEN < <(
  curl -s -X POST http://0.0.0.0:8000/api/v1/login \
    -H "Content-Type: application/json" \
    -d '{"username":"test_admin","password":"securepassword123"}' \
  | jq -r '[.access_token, .refresh_token] | @tsv'
)

echo "$ACCESS_TOKEN"
echo "$REFRESH_TOKEN"

#Generate new token
curl -i -X POST http://0.0.0.0:8000/api/v1/refresh \
     -d "{\"refresh_token\":\"$REFRESH_TOKEN\"}"
```

#### For Production (PostgreSQL):
In production, you would typically run this behind an application server like Gunicorn, rather than Django's built-in dev server.

##### Launch via python runserver
```
export ENVIRONMENT=prod
python manage.py migrate
gunicorn auth_project.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

### Unit Testing
```
python -m unittest core/tests/application/use_cases/test_login_use_case.py
python -m unittest core/tests/application/use_cases/test_verify_token_use_case.py
python -m unittest core/tests/application/use_cases/test_refresh_token_use_case.py
```

This Demonstrates Architectural Excellence:

- **Zero Setup Time:** You can run ```python -m unittest core/tests/test_use_cases.py``` without Docker, without setting up PostgreSQL, and without running Django migrations.

- **True Isolation:** If the test fails, you know exactly where the problem is: the business logic. It isn't failing because of a database connection timeout or a missing environment variable.

- **Behavior Driven:** The tests strictly validate business rules (e.g., "Inactive users cannot log in" or "Failing passwords do not generate tokens") rather than framework quirks.

- **Refactoring Safety:** If you decide to swap PyJWT for an external authentication provider (like Auth0 or AWS Cognito) later, your LoginUseCase and these tests will not change. You only rewrite the adapter (JwtTokenService) in the infrastructure layer.

## Notes:
### Verifying the dev sqlite migration state:
```
python3 manage.py showmigrations && echo 'DB:' && ls -l db.sqlite3 && echo 'MIGRATIONS FILE:' && ls -l django_app/migrations
```

### Verify Database:
```
docker compose exec db psql -U "db_auth_user" -d "${DB_NAME}" -c "SELECT * FROM auth."user" LIMIT 5;"

docker exec postgres_db psql -U auth_db_user -d auth_db -c "SELECT * FROM auth."user" LIMIT 5;"
```

## .env file
```
DB_NAME=auth_db
DB_USER=auth_db_user
DB_PASSWORD=auth_db_password
DB_HOST=db # Matches the Docker Compose service name
DB_PORT=5432

ENVIRONMENT=prod
SECRET_KEY=your-super-secret-django-key
LOG_LEVEL=ERROR
```