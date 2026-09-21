"""Console commands (`flask <command>`) for admin tasks.

The app has no sign-up route: login accounts are created from here. This
is what lets you create the first admin on a freshly deployed server.
"""

import click
from flask.cli import with_appcontext

from app.database import SessionLocal
from app.models.admin import Admin
from app.repositories.admin_repository import AdminRepository


@click.command("create-admin")
@click.argument("username")
@click.password_option(
    "--password", help="Si se omite, se pide por teclado sin mostrarlo."
)
@with_appcontext
def create_admin(username: str, password: str) -> None:
    """Create a login account for the app.

    Raises a ClickException if the username is already taken.
    """
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
