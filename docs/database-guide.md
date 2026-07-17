Awesome! It's satisfying when the terminal cuts through the noise and just works.

Here is your updated, production-grade `database-guide.md` with **Section 3** refactored to focus on the reliable command-line setup process. It also adds a dedicated troubleshooting section for DBeaver users—specifically addressing the caching traps and the `public key retrieval` error.

---

```markdown
# Database Management Guide

This guide provides essential information and commands for managing the MySQL database used by this project, including accessing it via the command line, establishing isolated testing environments, and performing common tasks like verifying table creation.

---

## Table of Contents

* [1. Database Overview](#1-database-overview)
* [2. Accessing the Database via Command Line](#2-accessing-the-database-via-command-line)
* [3. Setup of Isolated Testing Environment (Pristine TDD Sandbox)](#3-setup-of-isolated-testing-environment-pristine-tdd-sandbox)
    * [3.1. DB Security Profiles](#31-db-security-profiles)
    * [3.2. Setup via Terminal (Recommended)](#32-setup-via-terminal-recommended)
    * [3.3. Verify Permissions](#33-verify-permissions)
    * [3.4. GUI Integration Troubleshooting (DBeaver)](#34-gui-integration-troubleshooting-dbeaver)
* [4. Resetting Database Setup](#4-resetting-database-setup)
    * [4.1. Complete Schema Reset](#41-complete-schema-reset)
    * [4.2. Data-Only Reset](#42-data-only-reset)
    * [4.3. Verify Setup](#43-verify-setup)
* [5. Database Initialization & Migrations](#5-database-initialization--migrations)
* [6. Verifying Table Creation](#6-verifying-table-creation)
* [7. Retrieving Data from Tables](#7-retrieving-data-from-tables)

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

```

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

## 3. Setup of Isolated Testing Environment (Pristine TDD Sandbox)

To prevent automated integration tests from trashing or corrupting your active development database, tests utilize a completely isolated logical database schema and a restricted database user credentials profile.

### 3.1. DB Security Profiles

* **Test Database Name:** `damian-piatkowski-com-test-db`
* **Test Runner Username:** `damian-test-runner`
* **Target Privileges:** Restrictive access **only** to the test database schema (strictly forbidden from reading or mutating the production/development schema).

### 3.2. Setup via Terminal (Recommended)

Running the configuration scripts directly inside a native command-line session ensures that queries bypass any local GUI caching or active transaction limits.

1. **Log in as your root administrator:**
```bash
mysql -u root -p

```


2. **Execute the sandboxing query blocks:**
```sql
-- Create the dedicated testing database schema
CREATE DATABASE IF NOT EXISTS `damian-piatkowski-com-test-db` 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- Create the test-specific runner account
-- (Replace 'your_actual_secure_password' with the credential configured in your local .env)
CREATE USER IF NOT EXISTS 'damian-test-runner'@'localhost' 
IDENTIFIED BY 'your_actual_secure_password';

-- Restrict privileges: Grant access ONLY to the test database
GRANT ALL PRIVILEGES ON `damian-piatkowski-com-test-db`.* TO 'damian-test-runner'@'localhost';

-- Flush privileges to apply changes immediately
FLUSH PRIVILEGES;

```


3. **Exit root and verify the new sandbox login:**
```bash
exit

# Try logging in as the restricted test runner
mysql -u damian-test-runner -p -D damian-piatkowski-com-test-db

```



### 3.3. Verify Permissions

Ensure the security sandbox configuration has locked the user strictly to the test path:

```sql
SHOW GRANTS FOR 'damian-test-runner'@'localhost';

```

### 3.4. GUI Integration Troubleshooting (DBeaver)

If you plan to monitor the testing sandbox visually inside DBeaver, you may need to address a couple of common driver and caching behaviors:

#### Fixing the 'Public Key Retrieval Not Allowed' Error

If DBeaver fails to open a connection because of a secure RSA plugin constraint, configure the driver parameters:

1. Right-click your connection in the **Database Navigator** -> select **Edit Connection**.
2. Navigate to the **Driver properties** tab.
3. Locate `allowPublicKeyRetrieval` and switch it to **`TRUE`**.
4. Locate `useSSL` and switch it to **`FALSE`** (for local development only).
5. Apply, save, and reconnect.

#### Revealing Hidden Databases (Caching/Filter Trap)

If DBeaver does not list your new database in the explorer tree after creation:

* **The Filter Trap:** Right-click your connection -> **Edit Connection** -> next to the *Database* input box, ensure **`Show all databases`** is explicitly checked.
* **The Cache Trap:** Select your connection in the Navigator panel and press **`F5`** (or right-click and select **Refresh**) to force DBeaver to rebuild its database navigation tree.

---

## 4. Resetting Database Setup

> ⚠️ Use these carefully. Resetting may wipe data or schema.

---

### 4.1. Complete Schema Reset

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

### 4.2. Data-Only Reset

This clears data while keeping the schema intact.

```bash
# Truncate all tables (example for blog_posts + dictionary_words)
mysql -u root -p portfolio-prod-db -e "SET FOREIGN_KEY_CHECKS=0; TRUNCATE TABLE blog_posts; TRUNCATE TABLE dictionary_words; SET FOREIGN_KEY_CHECKS=1;"

```

---

### 4.3. Verify Setup

```bash
mysql -u damian-j-piatkowski -p -D portfolio-prod-db
mysql> SHOW TABLES;
mysql> DESCRIBE blog_posts;

```

---

## 5. Database Initialization & Migrations

When setting up the project or after schema changes, apply the compiled migrations to update your local database structure:

```bash
flask db upgrade

```

---

## 6. Verifying Table Creation

After migrations:

```bash
mysql -u damian-j-piatkowski -p -D portfolio-prod-db
mysql> SHOW TABLES;

```

You should see:

```
+-----------------------------------+
| Tables_in_portfolio-prod-db       |
+-----------------------------------+
| alembic_version                   |
| blog_posts                        |
| dictionary_examples               |
| dictionary_sources                |
| dictionary_words                  |
| han_viet_roots                    |
| users                             |
| word_han_viet_association         |
+-----------------------------------+

```

---

## 7. Retrieving Data from Tables

Example queries for vocabulary database analysis:

```sql
SELECT * FROM dictionary_words LIMIT 10;  -- Show first 10 dictionary entries
SELECT viet_word, english_translation FROM dictionary_words ORDER BY created_at DESC LIMIT 5;  -- Latest 5 added words
SELECT * FROM han_viet_roots WHERE root = 'học'; -- Check a specific Sino-Vietnamese semantic particle