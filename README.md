# Banking App

**Banking APP** built with Django REST Framework, PostgreSQL, Docker, Redis, RabbitMQ, Celery, and Nginx, secured with JWT authentication.

## Tech Stack

- **Backend Framework:** Django 4.2.15 + Django REST Framework 3.15.2
- **Authentication:** Djoser + JWT
- **Database:** PostgreSQL
- **Caching / Message Broker:** Redis, RabbitMQ
- **Async Task Processing:** Celery (worker + beat scheduler), monitored via Flower
- **API Documentation:** drf-spectacular (OpenAPI schema)
- **Media Storage:** Cloudinary
- **Password Hashing:** Argon2
- **PDF Generation:** ReportLab
- **Local Email Testing:** Mailpit
- **Web Server / Reverse Proxy:** Nginx
- **Production Server:** Gunicorn
- **Containerization:** Docker & Docker Compose
- **Dependency Management:** Pipenv
## Prerequisites

Make sure you have the following installed:

- [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/)
- [Python 3.x](https://www.python.org/downloads/) (for local tooling, e.g. Pipenv)
- [Pipenv](https://pipenv.pypa.io/) (optional, if running outside Docker)
- `make` (comes preinstalled on most Linux/macOS systems)

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/sandramilosevic/banking-app.git
cd banking-app
```

### 2. Configure environment variables

Copy the example environment file and fill in your own values:

```bash
cp .env.example .env
```

| Variable | Description |
|---|---|
| `DEBUG` | Django debug mode (`True`/`False`) |
| `SITE_NAME` | Name of the site/project |
| `SECRET_KEY` | Django secret key |
| `ADMIN_URL` | Custom URL path for the Django admin panel |
| `EMAIL_HOST` | SMTP host (use `mailpit` for local dev) |
| `DEFAULT_FROM_EMAIL` | Default sender email address |
| `DOMAIN` | Base domain of the application |
| `POSTGRES_HOST` | PostgreSQL host (`postgres` in Docker) |
| `POSTGRES_POST` | PostgreSQL port |
| `POSTGRES_DB` | PostgreSQL database name |
| `POSTGRES_USER` | PostgreSQL username |
| `POSTGRES_PASSWORD` | PostgreSQL password |
| `BANK_NAME` | Display name of the bank |
| `CSRF_TRUSTED_ORIGINS` | Trusted origins for CSRF protection |
| `CELERY_FLOWER_USER` | Basic auth username for Flower dashboard |
| `CELERY_FLOWER_PASSWORD` | Basic auth password for Flower dashboard |
| `CELERY_BROKER_URL` | RabbitMQ/Redis broker URL for Celery |
| `CELERY_RESULT_BACKEND` | Backend used to store Celery task results |
| `CLOUDINARY_API_KEY` | Cloudinary API key |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name |

### 3. Create the external Docker network

The `local.yml` compose file expects an external network:

```bash
docker network create banker_local_nw
```

### 4. Build and run the containers

Using the provided `Makefile`:

```bash
make build   # Build images and start containers in detached mode
```

Or manually with Docker Compose:

```bash
docker compose -f local.yml up --build -d --remove-orphans
```

### 5. Run database migrations

```bash
make migrate
```

### 6. Create a superuser

```bash
make superuser
```

### 7. Collect static files

```bash
make collectstatic
```

Your API should now be running and accessible through Nginx.

## Useful Make Commands

| Command | Description |
|---|---|
| `make build` | Build and start all containers |
| `make up` | Start containers (without rebuilding) |
| `make down` | Stop and remove containers |
| `make down-v` | Stop containers and remove volumes |
| `make makemigrations` | Generate new Django migrations |
| `make migrate` | Apply migrations to the database |
| `make collectstatic` | Collect static files |
| `make superuser` | Create a Django superuser |
| `make flush` | Flush the database |
| `make network-inspect` | Inspect the `banker_local_nw` Docker network |
| `make banker-db` | Open a `psql` shell inside the Postgres container |

## Services & Ports (Local Development)

| Service | Purpose | Port |
|---|---|---|
| Nginx | Reverse proxy / entrypoint | `8080` |
| PostgreSQL | Primary database | `5432` |
| RabbitMQ | Message broker + management UI | `5672` / `15672` |
| Flower | Celery task monitoring dashboard | `5555` |
| Mailpit | Local SMTP testing / email inbox UI | `8025` (UI) / `1025` (SMTP) |
| Django API | Application server (internal only, proxied via Nginx) | `8000` (internal) |

Access Flower at `http://localhost:5555` (protected by `CELERY_FLOWER_USER` / `CELERY_FLOWER_PASSWORD`), Mailpit at `http://localhost:8025`, and RabbitMQ management at `http://localhost:15672`.

## API Documentation

This project uses **drf-spectacular** to generate an OpenAPI schema. Once the server is running, API documentation is typically available at endpoints such as:

- `/api/schema/` – raw OpenAPI schema
- `/api/schema/swagger-ui/` – Swagger UI
- `/api/schema/redoc/` – ReDoc UI

> ⚠️ Confirm the exact paths against your `config/urls.py`, as they depend on how `drf-spectacular` is wired into the project.

## Background Tasks (Celery)

The project runs three Celery-related services:

- **`celeryworker`** – processes asynchronous tasks (e.g. emails, notifications)
- **`celerybeat`** – schedules periodic tasks (via `django-celery-beat`)
- **`flower`** – web dashboard for monitoring task queues and workers

RabbitMQ is used as the message broker, with results/state handled through the configured `CELERY_RESULT_BACKEND`.

## Dependency Management

Dependencies are split by environment under `requirements/`:

- `base.txt` – core dependencies shared across all environments (Django, DRF, Celery, Cloudinary, etc.)
- `local.txt` – adds local development tools (`watchfiles`, `black`)
- `production.txt` – adds production-only dependencies (`gunicorn`)

Alternatively, `Pipfile` / `Pipfile.lock` are provided for Pipenv-based dependency management.

## Running Tests

```bash
docker compose -f local.yml run --rm api python manage.py test
```

## Stopping the Project

```bash
make down       # Stop containers, keep data
make down-v     # Stop containers and remove volumes (⚠️ deletes data)
```
