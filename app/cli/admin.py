"""CLI commands for administrator account management."""

import click
from flask.cli import with_appcontext

from app import db
from app.models.repositories.user_repository import UserRepository
from app.services.auth_service import hash_password


@click.command("create-admin")
@with_appcontext
def create_admin_command():
    """Create an administrator account for the dictionary admin panel."""
    username = click.prompt("Username")
    password = click.prompt("Password", hide_input=True, confirmation_prompt=True)
    repository = UserRepository(db.session)
    if repository.find_by_username(username):
        click.echo(f"User '{username}' already exists.")
        return
    repository.create_user(username=username, password_hash=hash_password(password))
    db.session.commit()
    click.echo(f"Admin user '{username}' created.")
