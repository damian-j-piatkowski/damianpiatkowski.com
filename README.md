# damianpiatkowski.com

Source code for the portfolio website hosted at [damianpiatkowski.com](https://damianpiatkowski.com).

## Environment Variables

The following environment variables need to be set for the Flask project to run correctly:

- `BASE_THUMBNAIL_PATH`: Path where blog post thumbnails will be stored.
- `SECRET_KEY`: Secret key for Flask session management.
- `FLASK_ENV`: The environment in which the Flask app is running (e.g., development, production). Determines the configuration to load and can affect debugging and logging.
- `PORTFOLIO_WEBSITE_FLASK_SECRET`: Additional secret key for extra security measures within the application.
- `MAIL_USERNAME`: The username for the email account used to send emails from the application.
- `MAIL_PASSWORD`: Application-specific password generated by Google for a Gmail account, specifically configured to allow your application to send emails via Gmail's SMTP server.
- `MAIL_RECIPIENT`: The default recipient email address for notifications or other email communications from the application.
- `DOWNLOAD_DIRECTORY`: The directory where downloaded files will be stored.
- `MYSQL_PASSWORD`: The password for the MySQL user.
- `MYSQL_ROOT_PASSWORD`: The password for the MySQL root user.
- `MYSQL_DATABASE`: The name of the MySQL database.
- `MYSQL_HOST`: The host address of the MySQL server (e.g., db or localhost).

Ensure that these environment variables are set in your environment before running the application.

## Docker Setup

### Install Docker

Ensure you have Docker Desktop installed on your machine. Docker Desktop includes Docker Engine, Docker CLI, and Docker Compose.

### Initial Setup

1. **Set environment variables in your system for development**.

    On Windows, you can set environment variables using the `setx` command in your Command Prompt. Open Command Prompt and execute the following commands:

    ```sh
    setx FLASK_ENV "development"
    setx FLASK_RUN_PORT "5000"
    setx DATABASE_URL "mysql+pymysql://user:your_dev_mysql_password@db/dev_db"
    setx MYSQL_DATABASE "dev_db"
    setx MYSQL_USER "user"
    setx MYSQL_PASSWORD "your_dev_mysql_password"
    setx MYSQL_ROOT_PASSWORD "your_dev_mysql_root_password"
    ```

2. **Build and start the services for the first time** for development:

    ```sh
    docker-compose up --build
    ```

### Running Tests

1. Use the separate `docker-compose.test.yml` for testing:

    ```sh
    docker-compose -f docker-compose.test.yml up --build
    ```
   The --abort-on-container-exit flag ensures that the services stop once the tests complete,
   which is useful for CI/CD pipelines.

### Subsequent Runs

- To start the services again without rebuilding the images
   (add a -d flag to start the Docker containers in detached mode):

**For Development**:

    ```sh
    docker-compose up

**For Testing**:

    ```sh
    docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

**Stopping the Services**

    ```sh
    docker-compose down

### Check Container Logs

Inspect the logs of your database container to ensure it started up correctly:

    ```sh
    docker-compose logs db

Look for any errors or warnings that might indicate issues with the database startup.

### Access the Web Container

To run commands inside the web container, you need to use `docker-compose exec`:

    ```sh
    docker-compose exec web bash


