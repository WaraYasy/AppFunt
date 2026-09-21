"""Comandos de consola (`flask <comando>`) para tareas de administración.

La aplicación no tiene ruta de registro: las cuentas de acceso se crean
desde aquí, que es lo que permite dar de alta el primer admin en un
servidor recién desplegado.
"""
import click
from flask.cli import with_appcontext

from app.database import SessionLocal
from app.models.admin import Admin
from app.repositories.admin_repository import AdminRepository


@click.command("create-admin")
@click.argument("username")
@click.password_option("--password", help="Si se omite, se pide por teclado sin mostrarlo.")
@with_appcontext
def create_admin(username: str, password: str) -> None:
    """Crea una cuenta de acceso a la aplicación."""
    username = username.strip()
    db = SessionLocal()

    if AdminRepository(db).get_by_username(username):
        raise click.ClickException(f"Ya existe un admin con username {username!r}.")

    admin = Admin(username=username)
    admin.set_password(password)
    db.add(admin)
    db.commit()

    click.echo(f"Admin {username!r} creado (id {admin.id}).")


def init_app(app):
    app.cli.add_command(create_admin)
