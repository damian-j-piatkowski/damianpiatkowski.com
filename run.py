"""This script initializes and runs the Flask application.

The script performs the following tasks:
1. Determines the environment (`development`, `testing`, `production`) using
   the `FLASK_ENV` environment variable, defaulting to `development`.
2. Maps the environment to a configuration class via `ENVIRONMENT_CONFIG_MAPPING`.
3. Validates the selected configuration to ensure required variables are set.
4. Creates a Flask application instance using the `create_app` factory function.
5. Logs the application version and environment on startup.
6. Runs the application if executed directly.
"""

import os

from __version__ import __version__
from app import create_app
from config import ENVIRONMENT_CONFIG_MAPPING, Environment

# Determine the environment and configuration
flask_env = os.getenv('FLASK_ENV', Environment.DEVELOPMENT.value)
environment = Environment(flask_env)  # Enum validation happens here
config_class = ENVIRONMENT_CONFIG_MAPPING[environment]

# Validate the configuration
config_instance = config_class()
config_instance.validate()

# Create the app using the validated configuration
app = create_app(config_class)
app.logger.info(f"Application version {__version__} started in {environment.value} environment.")

if __name__ == "__main__":
    app.run()
