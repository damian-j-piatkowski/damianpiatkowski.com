# Database Management Guide

This guide provides essential information and commands for managing the MySQL database used by this project, including accessing it via the command line and performing common tasks like verifying table creation.

---

## Table of Contents

* [1. Database Overview](#1-database-overview)
* [2. Verifying Persistent Storage Volume](#2-verifying-persistent-storage-volume)
* [3. Accessing the Database via Command Line](#3-accessing-the-database-via-command-line)
* [4. Resetting Database Setup](#4-resetting-database-setup)
    * [4.1. Complete Schema Reset](#41-complete-schema-reset)
    * [4.2. Data-Only Reset](#42-data-only-reset)
    * [4.3. Verify Setup](#43-verify-setup)
* [5. Database Initialization & Migrations](#5-database-initialization--migrations)
* [6. Verifying Table Creation](#6-verifying-table-creation)
* [7. Retrieving Data from Tables](#7-retrieving-data-from-tables)
* [8. (Optional) Advanced Database Tasks](#8-optional-advanced-database-tasks)

---

## 1. Database Overview

This project uses a MySQL database, which is containerized using Docker and configured for persistent storage via Docker volumes. This ensures that your data remains intact even if the database container is stopped or recreated.

* **Database Type:** MySQL
* **Docker Service Name:** `db` (as defined in `docker-compose.yml`)
* **Data Persistence:** Managed via Docker Volumes
* **Configuration:** Database credentials (username, password, database name) are managed through your `.env` file.

---

## 2. Verifying Persistent Storage Volume

To confirm that your MySQL database data is being stored persistently on a dedicated Docker volume outside the container, you can inspect the volume created by Docker Compose.

1.  **Ensure your `db` service has run at least once:**
    Docker automatically creates named volumes when a service that references them is successfully started for the first time. If your database container has never been brought up, the volume might not exist yet. You can run `docker compose up -d db` to ensure it's created.

2.  **Inspect the Docker Volume:**
    Your `docker-compose.yml` uses a named volume called `mysql_data` for the database files. Docker Compose prefixes named volumes with your project's directory name (e.g., `damianpiatkowskicom`).

    Use the following command to get details about your database's data volume:
    ```bash
    docker volume inspect damianpiatkowskicom_mysql_data
    ```

    The output will be a JSON object, similar to this:
    ```json
    [
        {
            "CreatedAt": "2025-06-01T13:14:02+07:00",
            "Driver": "local",
            "Labels": {
                "com.docker.compose.config-hash": "63c07c86f95c20e5f0782d704109afb4e8f89aac718f1e33b35103c015a5d2a0",
                "com.docker.compose.project": "damianpiatkowskicom",
                "com.docker.compose.version": "2.36.2",
                "com.docker.compose.volume": "mysql_data"
            },
            "Mountpoint": "/var/lib/docker/volumes/damianpiatkowskicom_mysql_data/_data",
            "Name": "damianpiatkowskicom_mysql_data",
            "Options": null,
            "Scope": "local"
        }
    ]
    ```

3.  **Identify the `Mountpoint`:**
    From the JSON output, locate the `"Mountpoint"` field. This path indicates the exact directory on your host system where Docker stores the volume's data. In the example above, it's:
    `/var/lib/docker/volumes/damianpiatkowskicom_mysql_data/_data`

4.  **Verify the Files on Your Host System:**
    Navigate to this `Mountpoint` directory on your machine to see the actual database files.
    ```bash
    sudo ls -l /var/lib/docker/volumes/damianpiatkowskicom_mysql_data/_data
    ```
    You should see various MySQL data files and directories (e.g., `ibdata1`, `ib_logfile0`, `ib_logfile1`, and subfolders representing your databases). The presence of these files confirms that your database data is indeed being stored persistently on a Docker volume outside the container.

---

## 3. Accessing the Database via Command Line

You can connect directly to your running MySQL database container using `docker exec` to run the `mysql` client. This allows you to execute SQL queries directly against your database.

Before attempting to connect, ensure your `db` container is running:

```bash
docker compose ps # Verify 'db' service status is 'Up'
````

To connect to the MySQL prompt:

```bash
docker exec -it damianpiatkowskicom-db-1 mysql -u dbuser -pdbpassword dbname
```

**Important Notes:**

  * Replace `damianpiatkowskicom-db-1` with the actual name of your running database container if it differs (you can find this with `docker ps`).

  * Replace `dbuser`, `dbpassword`, and `dbname` with the exact values configured in your project's `.env` file.

  * The `mysql: [Warning] Using a password on the command line interface can be insecure.` warning is standard when providing the password directly in the command. For a more secure, interactive login (where you are prompted for the password), you can omit `-pdbpassword`:

    ```bash
    docker exec -it damianpiatkowskicom-db-1 mysql -u damian-j-piatkowski -p damian-piatkowski-com-db
    ```

    You will then be prompted to enter the password.

Once successfully connected, you will see the `mysql>` prompt.

To exit the MySQL session, you can use any of these methods:
* Type `exit;` and press Enter
* Type `quit;` and press Enter
* Press `Ctrl + D`

---

## 4. Resetting Database Setup

> **Quick Decision Guide:**
> - Need to modify database schema? → Use [4.1. Complete Schema Reset](#41-complete-schema-reset)
> - Just want to clear data? → Use [4.2. Data-Only Reset](#42-data-only-reset)

***

### 4.1. Complete Schema Reset

> ⚠️ **WARNING**: This will delete ALL data and schema history. Use only when:
> - Making major schema changes
> - Setting up a fresh development environment
> - Troubleshooting schema-related issues

```
bash
# 1. Stop everything and clean up
docker compose down
docker volume rm damianpiatkowskicom_mysql_data
rm -r migrations/*

# 2. Initialize new migration environment
docker compose run --rm web flask db init
docker compose run --rm web flask db migrate -m "Initial schema"
docker compose run --rm web flask db upgrade
```
### 4.2. Data-Only Reset

> 💡 **NOTE**: This preserves your schema but removes all data. Use when:
> - Testing with fresh data
> - Clearing test data
> - Resolving data-related issues

```
bash
# Stop all containers
docker compose down

# Remove the MySQL volume
docker volume rm damianpiatkowskicom_mysql_data

# Start services again
docker compose up -d
```

***

### 4.3. Verify Setup

After either reset method, verify the setup:
```
docker exec -it damianpiatkowskicom-db-1 mysql -u damian-j-piatkowski -p damian-piatkowski-com-db
# At MySQL prompt:
SHOW TABLES;
DESCRIBE blog_posts;
```

---

## 5. Database Initialization & Migrations

When setting up the project for the first time, or after significant database schema changes, you'll need to ensure your MySQL database is properly initialized and updated with the latest schema. The Flask application includes a custom SQLAlchemy logger that attempts to write logs to the database from startup. If the `logs` table (or other application tables) doesn't exist yet, this will cause your application to crash immediately upon launch.

Follow these steps to initialize your database tables:

1. **Temporarily Disable Database Logging:**
   To allow the database migration tool (Alembic) to run without your application's logger immediately failing, you need to temporarily disable logging to the database by setting the appropriate environment variable.

    * Edit your `.env` file and add or modify the `LOG_TO_DB` setting:
      ```
      LOG_TO_DB=false
      ```

2. **Run Database Migrations:**
   This command will execute the Alembic migration scripts to create your `alembic_version`, `blog_posts`, and `logs` tables in your MySQL database.

   ```bash
   docker compose down              # Stop all services to ensure a clean state
   docker compose up -d db         # Start only the database service
   docker compose run --rm web flask db upgrade
   ```

   You should see output similar to `INFO [alembic.runtime.migration] Running upgrade ... Initial migration.` If this command completes without errors or a traceback, your tables have been created!

3. **Verify Table Creation (Optional but Recommended):**
   You can confirm that the tables exist by connecting directly to your MySQL container and listing the tables.

   ```bash
   docker exec -it damianpiatkowskicom-db-1 mysql -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE
   ```

   Once at the `mysql>` prompt, run:
   ```sql
   SHOW TABLES;
   ```

   You should see `alembic_version`, `blog_posts`, and `logs` listed. Type `exit;` to leave the MySQL prompt.

4. **Re-enable Database Logging:**
   Now that your `logs` table exists, you can re-enable logging to the database.

    * Edit your `.env` file again and set `LOG_TO_DB` back to true:
      ```
      LOG_TO_DB=true
      ```

5. **Start Your Full Application:**
   Finally, bring up all your services. Your application should now start and log to the database without issues.

   ```bash
   docker compose down              # Stop all services to pick up the env changes
   docker compose up -d             # Start all services in detached mode
   ```

   You can check your application's logs (`docker compose logs web`) to confirm it's running cleanly.

---

## 6. Verifying Table Creation

After running database migrations (e.g., `flask db upgrade`), you can verify that the expected tables have been created in your database.

1.  Connect to the MySQL prompt as described in [Accessing the Database via Command Line](https://www.google.com/search?q=%233-accessing-the-database-via-command-line).

2.  At the `mysql>` prompt, run the following command:

    ```sql
    SHOW TABLES;
    ```

    You should see a list of tables similar to this (depending on your migrations):

    ```
    +------------------+
    | Tables_in_dbname |
    +------------------+
    | alembic_version  |
    | blog_posts       |
    | logs             |
    +------------------+
    ```

    The `alembic_version` table is used by the migration tool itself, while `blog_posts` and `logs` are your application's tables.

## 7. Retrieving Data from Tables

Once tables exist and your application has been running (potentially inserting data), you can query them to retrieve records.

1.  Connect to the MySQL prompt as described in [Accessing the Database via Command Line](https://www.google.com/search?q=%233-accessing-the-database-via-command-line).

2.  Use `SELECT` statements to fetch data. Remember to end each SQL query with a semicolon (`;`).

      * **To retrieve all columns and all rows from a table:**

        ```sql
        SELECT * FROM logs;
        ```

      * **To retrieve a limited number of records (recommended for large tables to avoid overwhelming output):**

        ```sql
        SELECT * FROM logs LIMIT 10; -- Shows the first 10 records
        ```

      * **To retrieve the most recent records (very useful for logs, assuming a timestamp column):**

        ```sql
        SELECT * FROM logs ORDER BY timestamp DESC LIMIT 10; -- Shows the 10 most recent records
        ```

      * **To retrieve specific columns:**

        ```sql
        SELECT id, message, timestamp FROM logs LIMIT 5;
        ```

      * **To filter records based on a condition:**

        ```sql
        SELECT * FROM logs WHERE level = 'ERROR' ORDER BY timestamp DESC LIMIT 5;
        ```

## 8. (Optional) Advanced Database Tasks

This section can be expanded in the future to include more advanced database management topics such as:

  * Importing/Exporting Database Dumps
  * Creating/Managing Database Users
  * Troubleshooting Database Connection Issues
  * Database Backups and Restoration Strategies
