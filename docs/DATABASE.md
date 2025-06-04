# Database Management Guide

This guide provides essential information and commands for managing the MySQL database used by this project, including accessing it via the command line and performing common tasks like verifying table creation.

---

## Table of Contents

* [1. Database Overview](#1-database-overview)
* [2. Accessing the Database via Command Line](#2-accessing-the-database-via-command-line)
* [3. Verifying Table Creation](#3-verifying-table-creation)
* [4. Retrieving Data from Tables](#4-retrieving-data-from-tables)
* [5. (Optional) Advanced Database Tasks](#5-optional-advanced-database-tasks)

---

## 1. Database Overview

This project uses a MySQL database, which is containerized using Docker and configured for persistent storage via Docker volumes. This ensures that your data remains intact even if the database container is stopped or recreated.

* **Database Type:** MySQL
* **Docker Service Name:** `db` (as defined in `docker-compose.yml`)
* **Data Persistence:** Managed via Docker Volumes
* **Configuration:** Database credentials (username, password, database name) are managed through your `.env` file.

## 2. Accessing the Database via Command Line

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
    docker exec -it damianpiatkowskicom-db-1 mysql -u dbuser -p dbname
    ```
    You will then be prompted to enter the password.

Once successfully connected, you will see the `mysql>` prompt.

## 3\. Verifying Table Creation

After running database migrations (e.g., `flask db upgrade`), you can verify that the expected tables have been created in your database.

1.  Connect to the MySQL prompt as described in [Accessing the Database via Command Line](https://www.google.com/search?q=%232-accessing-the-database-via-command-line).
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

## 4\. Retrieving Data from Tables

Once tables exist and your application has been running (potentially inserting data), you can query them to retrieve records.

1.  Connect to the MySQL prompt as described in [Accessing the Database via Command Line](https://www.google.com/search?q=%232-accessing-the-database-via-command-line).

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

## 5\. (Optional) Advanced Database Tasks

This section can be expanded in the future to include more advanced database management topics such as:

  * Importing/Exporting Database Dumps
  * Creating/Managing Database Users
  * Troubleshooting Database Connection Issues
  * Database Backups and Restoration Strategies

-----