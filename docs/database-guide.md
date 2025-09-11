# Database Management Guide

This guide provides essential information and commands for managing the MySQL database used by this project, including accessing it via the command line and performing common tasks like verifying table creation.

---

## Table of Contents

* [1. Database Overview](#1-database-overview)
* [2. Accessing the Database via Command Line](#2-accessing-the-database-via-command-line)
* [3. Resetting Database Setup](#3-resetting-database-setup)
    * [3.1. Complete Schema Reset](#31-complete-schema-reset)
    * [3.2. Data-Only Reset](#32-data-only-reset)
    * [3.3. Verify Setup](#33-verify-setup)
* [4. Database Initialization & Migrations](#4-database-initialization--migrations)
* [5. Verifying Table Creation](#5-verifying-table-creation)
* [6. Retrieving Data from Tables](#6-retrieving-data-from-tables)

---

## 1. Database Overview

This project uses a **system-installed MySQL server** (no Docker).  

* **Database Type:** MySQL  
* **Host:** localhost  
* **Root Login:** `mysql -u root -p`  
* **Application User:** `damian-j-piatkowski`  
* **Application Database:** `portfolio-prod-db`  
* **Credentials:** Stored in environment variables (`MYSQL_ROOT_PASSWORD`, `MYSQL_PASSWORD`)

---

## 2. Accessing the Database via Command Line

### Log in as root
```bash
mysql -u root -p
````

You’ll be prompted for the root password (`MYSQL_ROOT_PASSWORD`).

### Log in as your app user

```bash
mysql -u damian-j-piatkowski -p -D portfolio-prod-db
```

You’ll be prompted for the app user password (`MYSQL_PASSWORD`).
This connects you directly to the production database, just like your Flask app does internally.

### Basic commands inside MySQL

```sql
SHOW DATABASES;         -- List all databases
USE portfolio-prod-db;  -- Select your app database
SHOW TABLES;            -- Show tables in the current database
DESCRIBE table_name;    -- Inspect a table’s structure
SELECT * FROM table_name LIMIT 10;  -- View first 10 rows
EXIT;                   -- Leave MySQL
```

---

## 3. Resetting Database Setup

>⚠️ Use these carefully. Resetting may wipe data or schema.

---

### 3.1. Complete Schema Reset

This deletes **all data and schema** and re-initializes migrations.

```bash
# Drop and recreate the database
mysql -u root -p -e "DROP DATABASE IF EXISTS portfolio-prod-db; CREATE DATABASE portfolio-prod-db;"

# Reset migrations
rm -r migrations/*
flask db init
flask db migrate -m "Initial schema"
flask db upgrade
```

---

### 3.2. Data-Only Reset

This clears data while keeping the schema intact.

```bash
# Truncate all tables (example for logs + blog_posts)
mysql -u root -p portfolio-prod-db -e "SET FOREIGN_KEY_CHECKS=0; TRUNCATE TABLE logs; TRUNCATE TABLE blog_posts; SET FOREIGN_KEY_CHECKS=1;"
```

---

### 3.3. Verify Setup

```bash
mysql -u damian-j-piatkowski -p -D portfolio-prod-db
mysql> SHOW TABLES;
mysql> DESCRIBE blog_posts;
```

---

## 4. Database Initialization & Migrations

When setting up the project or after schema changes, run migrations:

1. **Disable logging temporarily** (if needed):

   ```bash
   export LOG_TO_DB=false
   ```

2. **Run migrations:**

   ```bash
   flask db upgrade
   ```

3. **Re-enable logging:**

   ```bash
   export LOG_TO_DB=true
   ```

---

## 5. Verifying Table Creation

After migrations:

```bash
mysql -u damian-j-piatkowski -p -D portfolio-prod-db
mysql> SHOW TABLES;
```

You should see something like:

```
+------------------+
| Tables_in_portfolio-prod-db |
+------------------+
| alembic_version  |
| blog_posts       |
| logs             |
+------------------+
```

---

## 6. Retrieving Data from Tables

Example queries:

```sql
SELECT * FROM logs LIMIT 10;  -- Show first 10 logs
SELECT * FROM logs ORDER BY timestamp DESC LIMIT 10;  -- Latest 10 logs
SELECT id, message, timestamp FROM logs LIMIT 5;      -- Specific columns
SELECT * FROM logs WHERE level = 'ERROR' ORDER BY timestamp DESC LIMIT 5; -- Filtered
```