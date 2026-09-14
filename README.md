# Trackrr API Backend

This repository contains the backend part of the Trackrr application. It exposes the API used by the frontend client and handles authentication, dashboard data, task management, and list organization.

This is not the full app UI; it is the server-side application that provides the data and business logic.

## Overview

The backend is built with:

- Python
- Flask
- Flask-SQLAlchemy
- Flask-JWT-Extended
- Flask-OpenAPI3
- SQLite by default for local development

## Project structure

```text
.
├── app.py                 # Flask application entry point
├── .env                   # Local environment variables (not committed)
├── .gitignore             # Safe ignore rules for secrets and local artifacts
├── requirements.txt       # Python dependencies
├── database/
│   └── base.py            # SQLAlchemy database setup
├── model/
│   ├── dashboard.py
│   ├── list.py
│   ├── task.py
│   └── user.py
├── routes/
│   ├── auth.py
│   ├── dashboards.py
│   ├── lists.py
│   └── tasks.py
├── services/
│   └── AuthService/
│       ├── build_user.py
│       └── validate_signup.py
└── venv/ or .venv/        # Local virtualenv
```

## Prerequisites

- Python 3.11+
- pip
- A virtual environment tool

## Local environment setup

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install project dependencies:

```bash
pip install -r requirements.txt
```

3. Create a local environment file:

```bash
cat > .env <<'EOF'
SQLALCHEMY_DATABASE_URI=sqlite:///trackrr.db
SQLALCHEMY_TRACK_MODIFICATIONS=False
JWT_SECRET_KEY=change-me-in-local-dev
EOF
```

4. Create the database tables:

```bash
flask --app app db_create
```

5. Run the backend:

```bash
flask --app app run --debug --host 0.0.0.0
```

The API will be available at:

- http://127.0.0.1:5000
- API docs: http://127.0.0.1:5000/openapi/swagger

## Development environment setup

Use environment variables for a shared dev or staging setup instead of committing secrets into the repository.

Example:

```bash
export SQLALCHEMY_DATABASE_URI="postgresql://user:password@host:5432/trackrr_dev"
export SQLALCHEMY_TRACK_MODIFICATIONS=False
export JWT_SECRET_KEY="strong-development-secret"
```

Then start the server:

```bash
flask --app app run --host 0.0.0.0 --port 5000
```

Recommended practices:

- use a dedicated database for development
- avoid production secrets in shared environments
- keep debug features limited to non-production use
- store credentials in deployment environment variables or secret managers

## Production environment setup

Production should not use the default local SQLite configuration. Configure a real database and secret values through environment variables.

Example:

```bash
export SQLALCHEMY_DATABASE_URI="postgresql://user:password@prod-db-host:5432/trackrr_prod"
export SQLALCHEMY_TRACK_MODIFICATIONS=False
export JWT_SECRET_KEY="a-long-random-production-secret"
```

Run the application with a production WSGI server:

```bash
gunicorn app:app --bind 0.0.0.0:8000
```

Production checklist:

- use a managed database service
- keep `JWT_SECRET_KEY` secret and unique
- disable debug mode
- protect sensitive endpoints with proper auth and network controls

## Useful commands

Create tables:

```bash
flask --app app db_create
```

Drop tables:

```bash
flask --app app db_drop
```

Seed a sample user:

```bash
flask --app app db_seed
```

## Notes

- This project is the backend only. The frontend client is separate.
- The API includes routes for authentication, dashboards, lists, and tasks.
- Sensitive configuration should always be stored in environment variables and never committed to Git.
