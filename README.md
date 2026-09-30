# AppFunt

Aplicación web en Flask para gestionar personas y activos (assets).

## Stack

- Flask 3
- SQLAlchemy 2 + PyMySQL (MySQL)
- Flask-Login (autenticación)
- Flask-WTF (formularios y CSRF)

## Requisitos

- Python 3.11+
- MySQL

## Instalación

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Para desarrollo (incluye black, isort, ruff):

```bash
pip install -r requirements-dev.txt
```

## Configuración

Copia `.env.example` a `.env` y completa los valores:

```
FLASK_ENV=development
SECRET_KEY=cambia-esto
DATABASE_URL=mysql+pymysql://usuario:password@localhost:3306/appwara
```

`SECRET_KEY` es obligatoria: firma las cookies de sesión y CSRF. Genera una propia con:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Base de datos

Las tablas se crean automáticamente al levantar la app (`Base.metadata.create_all`), no hay migraciones. Ver [docs/produccion.md](docs/produccion.md) para el detalle y el checklist de despliegue.

## Uso

Levantar la app:

```bash
python run.py
```

Crear la primera cuenta de acceso:

```bash
flask create-admin <username>
```

## Estructura

```
app/
  controllers/    rutas (blueprints)
  models/         modelos de SQLAlchemy
  repositories/   acceso a datos
  templates/       vistas Jinja
  static/          assets estáticos
  translations/    i18n
docs/              documentación (despliegue, etc.)
```
