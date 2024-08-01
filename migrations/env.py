import logging
from logging.config import fileConfig

from alembic import context as alembic_context
from flask import current_app
from sqlalchemy import MetaData

from app.models.blog_post import blog_posts
from app.models.log import logs
from app.orm import start_mappers
from config import config as app_config  # Import the config dictionary

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = alembic_context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')


def process_revision_directives(_context, _revision, directives):
    if getattr(config.cmd_opts, 'autogenerate', False):
        script = directives[0]
        if script.upgrade_ops.is_empty():
            directives[:] = []
            logger.info('No changes in schema detected, migration skipped.')


def get_engine():
    try:
        # this works with Flask-SQLAlchemy<3 and Alchemical
        return current_app.extensions['migrate'].db.get_engine()
    except (TypeError, AttributeError):
        # this works with Flask-SQLAlchemy>=3
        return current_app.extensions['migrate'].db.engine


def get_engine_url():
    try:
        return get_engine().url.render_as_string(hide_password=False).replace(
            '%', '%%')
    except AttributeError:
        return str(get_engine().url).replace('%', '%%')


# Combine all the metadata objects
target_metadata = MetaData()

# Add the table objects directly to the metadata
for table in [blog_posts, logs]:
    table.tometadata(target_metadata)

# Debugging print statement to verify tables in metadata
print("Tables in target_metadata:", target_metadata.tables.keys())
logger.info("Tables in target_metadata: %s", target_metadata.tables.keys())

# Determine the appropriate config class based on the environment
flask_env = current_app.config.get('FLASK_ENV', 'default')
ConfigClass = app_config.get(flask_env, app_config['default'])

# Instantiate the config class to access the database URL
config_instance = ConfigClass()
db_url = config_instance.SQLALCHEMY_DATABASE_URI
config.set_main_option('sqlalchemy.url', db_url)

target_db = current_app.extensions['migrate'].db

# Initialize conf_args, use an empty dict as a fallback if not found
conf_args = getattr(current_app.extensions['migrate'], 'configure_args', {})

# Set the process_revision_directives if not already set
if conf_args.get("process_revision_directives") is None:
    conf_args["process_revision_directives"] = process_revision_directives


def get_metadata():
    if hasattr(target_db, 'metadatas'):
        return target_db.metadatas[None]
    return target_db.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to alembic_context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    alembic_context.configure(
        url=url, target_metadata=get_metadata(), literal_binds=True
    )

    with alembic_context.begin_transaction():
        alembic_context.run_migrations()


def run_migrations_online():
    start_mappers(current_app)  # Ensure mappers are initialized

    connectable = get_engine()
    with connectable.connect() as connection:
        alembic_context.configure(
            connection=connection,
            target_metadata=target_metadata,  # Ensure this is fully populated
            **conf_args
        )

        with alembic_context.begin_transaction():
            alembic_context.run_migrations()


if alembic_context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
