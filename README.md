# AppFunt

> [README en español](README.es.md)

Flask web app to manage personas (employees) and assets (tech equipment).

## Stack

- Flask 3
- SQLAlchemy 2 + PyMySQL (MySQL)
- Flask-Login (authentication)
- Flask-WTF (forms and CSRF)

## Requirements

- Python 3.11+
- MySQL

## Installation

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

For development (includes black, isort, ruff):

```bash
pip install -r requirements-dev.txt
```

## Configuration

Copy `.env.example` to `.env` and fill in the values:

```
FLASK_ENV=development
SECRET_KEY=cambia-esto
DATABASE_URL=mysql+pymysql://usuario:password@localhost:3306/appwara
```

`SECRET_KEY` is required: it signs session and CSRF cookies. Generate your own with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Database

Tables are created automatically when the app starts (`Base.metadata.create_all`) — there are no migrations. See [docs/produccion.md](docs/produccion.md) for details and the deployment checklist.

## Usage

Start the app:

```bash
python run.py
```

Create the first login account:

```bash
flask create-admin <username>
```

## Structure

```
app/
  controllers/    routes (blueprints)
  models/         SQLAlchemy models
  repositories/   data access
  templates/       Jinja views
  static/          static assets
  translations/    i18n
docs/              documentation (deployment, etc.)
```
