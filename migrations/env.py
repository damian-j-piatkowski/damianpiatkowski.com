import logging
from logging.config import fileConfig
import os

from alembic import context as alembic_context
from flask import current_app
from sqlalchemy import MetaData

# === MODIFIED: Import create_app and your specific config classes directly ===
from app import create_app
from app.config import DevelopmentConfig, ProductionConfig, TestingConfig # <--- IMPORTANT: Import these directly
from app.models.tables.blog_post import blog_posts
from app.models.tables.log import logs
from app.orm import start_mappers

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = alembic_context.config

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

# =============================================================================
# MODIFIED SECTION START - Corrected Config Mapping
# =============================================================================

# Define a dictionary to map FLASK_ENV strings to your config classes
CONFIG_MAPPING = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig, # Fallback if FLASK_ENV is not set or recognized
}

def get_alembic_url():
    """Dynamically loads Flask app config to get SQLAlchemy URL for Alembic."""
    try:
        # Try to get the URL from current_app if already within an app context.
        # This is what Flask-Migrate tries to set up for online migrations.
        if current_app:
            return current_app.config.get('SQLALCHEMY_DATABASE_URI')
    except RuntimeError:
        # If not in an app context (e.g., initial env.py load or offline mode),
        # create a temporary minimal app instance to get the config.
        pass # We will handle this outside the try-except

    # Get FLASK_ENV from alembic.ini (if set) or environment variables
    flask_env = config.get_main_option('FLASK_ENV') or os.environ.get('FLASK_ENV', 'default')

    ConfigClass = CONFIG_MAPPING.get(flask_env) # <--- THIS IS THE FIX for AttributeError
    if not ConfigClass:
        raise ValueError(f"Unknown FLASK_ENV '{flask_env}'. Add it to CONFIG_MAPPING in env.py or set FLASK_ENV.")

    # Create a temporary Flask app instance to load the configuration
    temp_app = create_app(ConfigClass)
    with temp_app.app_context():
        return temp_app.config.get('SQLALCHEMY_DATABASE_URI')

# =============================================================================
# MODIFIED SECTION END
# =============================================================================


def process_revision_directives(_context, _revision, directives):
    if getattr(config.cmd_opts, 'autogenerate', False):
        script = directives[0]
        if script.upgrade_ops.is_empty():
            directives[:] = []
            logger.info('No changes in schema detected, migration skipped.')


def get_engine():
    # This function is typically called within an app context.
    # We rely on current_app being available here.
    try:
        return current_app.extensions['migrate'].db.get_engine()
    except (TypeError, AttributeError):
        return current_app.extensions['migrate'].db.engine


def get_engine_url():
    # This function is typically called within an app context.
    # We rely on current_app being available here.
    try:
        return get_engine().url.render_as_string(hide_password=False).replace(
            '%', '%%')
    except AttributeError:
        return str(get_engine().url).replace('%', '%%')


# Combine all the metadata objects (now using the function approach)
def get_target_metadata():
    combined_metadata = MetaData()
    for table in [blog_posts, logs]:
        table.tometadata(combined_metadata)
    return combined_metadata

target_metadata = get_target_metadata()

# Debugging print statement to verify tables in metadata
print("Tables in target_metadata (from env.py):", target_metadata.tables.keys())
logger.info("Tables in target_metadata (from env.py): %s", target_metadata.tables.keys())


# Set the SQLAlchemy URL for Alembic using the safe function
alembic_config_url = get_alembic_url()
if not alembic_config_url:
    raise ValueError("SQLALCHEMY_DATABASE_URI not found in Flask app configuration.")
config.set_main_option('sqlalchemy.url', alembic_config_url)


# Initialize conf_args, using current_app.extensions['migrate'] as it should be
# available when run_migrations_online is called.
conf_args = getattr(current_app.extensions['migrate'], 'configure_args', {})

# Set the process_revision_directives if not already set
if conf_args.get("process_revision_directives") is None:
    conf_args["process_revision_directives"] = process_revision_directives


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    alembic_context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True
    )

    with alembic_context.begin_transaction():
        alembic_context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    start_mappers(current_app)

    connectable = get_engine()
    with connectable.connect() as connection:
        alembic_context.configure(
            connection=connection,
            target_metadata=target_metadata,
            **conf_args
        )

        with alembic_context.begin_transaction():
            alembic_context.run_migrations()


if alembic_context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()