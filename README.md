# Personal Website & Blog – [damianpiatkowski.com](https://damianpiatkowski.com)

A Flask-powered personal website with a blog component, live at [damianpiatkowski.com](https://damianpiatkowski.com). It features a custom-built blog engine that syncs content from Google Drive, sanitizes it, and stores it in a MySQL database. The site also includes a resume, an about page, and an admin interface for managing posts. The entire project is containerized with Docker for easy deployment and local development.

This project is public not just as a portfolio piece, but also to serve as a learning resource for others interested in building a personal website or Flask-based app with CI/CD, Google Drive API integration, and MySQL-backed content management.

***

**For database setup and management details, refer to [Database Management Guide](docs/DATABASE.md).**
**For detailed information on project diagrams, refer to [Draw.io Diagramming Guide](docs/DRAWIO_GUIDE.md).**

---

## Table of Contents

* [Features](#features)
* [Architecture Overview](#architecture-overview)
    * [Layered Architecture](#layered-architecture)
    * [High-level Architecture Diagram](#high-level-architecture-diagram)
    * [Diagram Explanation](#diagram-explanation)
* [Technology Stack](#technology-stack)
* [Containerization Setup](#containerization-setup)
    * [Docker Installation & Setup](#docker-installation--setup)
        * [Linux](#linux)
            * [Troubleshooting Docker Permissions on Linux](#troubleshooting-docker-permissions-on-linux)
        * [Windows](#windows)
    * [Running the Docker Containers](#running-the-docker-containers)
        * [Prepare your Environment File](#prepare-your-environment-file)
        * [Navigate to the Project Directory](#navigate-to-the-project-directory)
        * [Start the Containers](#start-the-containers)
        * [Verify Running Containers](#verify-running-containers)
        * [Access Your Application](#access-your-application)
    * [Troubleshooting: Application Not Accessible (Web Container Exited)](#troubleshooting-application-not-accessible-web-container-exited)
        * [How to Diagnose](#how-to-diagnose)
        * [Rebuilding Containers from Scratch](#rebuilding-containers-from-scratch)
        * [How to Fix](#how-to-fix)
* [Deployment](#deployment)
    * [Strategy](#strategy)
    * [CI/CD (GitHub Actions)](#cicd-github-actions)
* [License](#license)

---

## Features

* 📄 Blog with paginated posts and individual article pages
* ✍️ Admin interface with AJAX-powered upload and delete operations
* 📂 Google Drive API integration to sync blog drafts
* 🧼 Content normalization and sanitization before database insertion
* 📁 Static pages: About Me, Resume, and Privacy Policy
* 📬 Contact form with backend processing and flash messaging
* 🐋 Dockerized setup with GitHub Actions for CI/CD deployment
* 🐬 File-based MySQL database for blog post storage

---

## Architecture Overview

This project is a personal website and blog engine powered by Flask, deployed with Docker on an EC2 instance, and uses GitHub Actions for CI/CD. Blog content is sourced from Google Drive and persisted into a file-based MySQL database.

***

### Layered Architecture

The Flask application follows a layered architecture inspired by the book *Architecture Patterns with Python: Enabling Test-Driven Development, Domain-Driven Design, and Event-Driven Microservices* by Bob Gregory and Harry Percival. This approach promotes clear separation of concerns, making the system easier to test, maintain, and extend.

```
Flask App
├── Routes
│   └── Handles incoming HTTP requests and maps them to controllers
├── Controllers
│   └── Orchestrate request handling, call services
├── Services
│   └── Contain business logic, call repositories or external APIs (e.g. Google Drive)
├── Repositories
│   └── Interact with the MySQL database using SQLAlchemy
```

***

### High-level Architecture Diagram

A visual overview of the system's high-level architecture is provided below. This diagram offers a clear, scalable representation of the application's components and their interactions, designed to be easily viewable across all platforms.

![High-level Architecture Diagram](docs/architecture/high_level_architecture.svg)

---

### Diagram Explanation

This diagram illustrates the main components and data flows within the system:

* **User Interaction**: The **Browser/User Client** initiates all requests. Standard website traffic routes through **Nginx** to the **Public Routes** in the Flask app. Access to the administrative panel also goes via Nginx, but specifically targets the **Admin Routes**.
* **Authentication**: The **Admin Routes** are uniquely responsible for handling the **Google OAuth flow**, connecting with **Google Authentication** to verify your identity. Public routes don't require any authentication.
* **Internal Flask Flow**: Both **Public Routes** and **Admin Routes** delegate logic to **Controllers**, which then orchestrate requests by interacting with **Services**. Services encapsulate the core business logic.
* **Data Persistence**: **Services** communicate with **Repositories** for all data access operations. The Repositories then interact with the **MySQL Container** by sending SQL queries.
* **Persistent Storage**: The **MySQL Container** stores its data persistently on a dedicated **DB Volume** (a file-based volume on the EC2 instance).
* **External APIs**: **Services** also manage interactions with external APIs, such as the **Google Drive API** (for fetching blog content) and an **SMTP Server** (e.g., Gmail) for sending emails.
* **Deployment & CI/CD**: **GitHub Actions** handles the continuous integration and deployment process, securely pushing updates to the **AWS EC2 Instance**.

---

## Technology Stack

* **Python / Flask** – Main backend framework
* **Jinja2** – Template rendering
* **MySQL (File-based)** – Lightweight DB for storing blog posts
* **Google Drive API** – Blog post draft source
* **Docker / Docker Compose** – Container orchestration
* **GitHub Actions** – CI/CD
* **EC2** – Deployment host

---

## Containerization Setup

This project leverages Docker for containerization, which offers significant benefits for both development and deployment.

**What is Docker?** Docker is a platform that allows you to automate the deployment, scaling, and management of applications using containers. Containers are lightweight, standalone, executable packages of software that include everything needed to run an application: code, runtime, system tools, system libraries, and settings.

**Why use Docker?**
* **Environment Consistency:** Ensures that the development, testing, and production environments are identical, eliminating "it works on my machine" issues.
* **Isolation:** Applications and their dependencies are isolated from each other and from the host system, preventing conflicts.
* **Easy Setup:** Simplifies the process of setting up a development environment, as all dependencies are pre-packaged.
* **Portability:** Containers can run consistently across different operating systems and cloud providers.

***

### Docker Installation & Setup

Before running the project, ensure Docker Desktop (for Windows/macOS) or Docker Engine (for Linux) is installed and running on your machine.

***

#### Linux

If you're on a Linux system, Docker runs as a service. You'll need `sudo` privileges to manage it.

1.  **Check Docker Status:**
    First, verify if the Docker daemon is running:
    ```bash
    sudo systemctl status docker
    ```
    You should see `Active: active (running)`. If it's not running, or if you get an error, proceed to the next step.

2.  **Start Docker (if needed):**
    If Docker is not running, start the service:
    ```bash
    sudo systemctl start docker
    ```

3.  **Enable Docker on Boot (Recommended):**
    To ensure Docker starts automatically every time your system boots, enable the service:
    ```bash
    sudo systemctl enable docker
    ```

***

##### Troubleshooting Docker Permissions on Linux

If you encounter "permission denied" errors when trying to run Docker commands (e.g., `unable to connect to the Docker daemon socket`), this is almost always because your user is not part of the `docker` Linux group.

1.  **Add your user to the `docker` group:**
    Open a terminal and run:
    ```bash
    sudo usermod -aG docker $USER
    ```
    * `sudo`: Grants temporary root privileges.
    * `usermod`: User modification utility.
    * `-aG`: Appends (`-a`) the user to the specified supplementary group (`-G`).
    * `docker`: The group that has permissions to interact with the Docker daemon socket.
    * `$USER`: Automatically substitutes your current username.

2.  **Crucial Step: Apply the group change.**
    Simply running the `usermod` command isn't enough. Your current session won't immediately recognize the new group membership. **You must reboot your machine** to ensure a fresh login with updated group information.

3.  **Verify your group membership (optional):**
    After rebooting, open a terminal and run:
    ```bash
    groups $USER
    ```
    You should now see `docker` listed among your groups (e.g., `damian : damian adm cdrom sudo dip plugdev lpadmin lxd sambashare **docker**`).

***

#### Windows

*(This section is a placeholder. Add detailed steps for installing Docker Desktop on Windows here, including enabling WSL2 if necessary, and ensuring it's running.)*

---

### Running the Docker Containers

Once Docker is installed and running, you can start the project's services (your Flask application and MySQL database) using Docker Compose.

1.  **Prepare your Environment File:**
    Ensure you have a `.env` file in the same directory as your `docker-compose.yml` file. This file will contain crucial environment variables for your database and application. An example `.env` file looks like this:
    ```
    # === General ===
    FLASK_ENV=development
    # Flask secret key for sessions and CSRF
    SECRET_KEY=example
    
    # === Admin Panel Google OAuth (frontend-based OAuth login for the admin panel) ===
    ADMIN_PANEL_ALLOWED_USERS=example
    ADMIN_PANEL_GOOGLE_CLIENT_ID=example
    ADMIN_PANEL_GOOGLE_CLIENT_SECRET=example
    ADMIN_PANEL_GOOGLE_REDIRECT_URI=http://localhost:5000/login/authorized
    
    # === Google Drive API ===
    DRIVE_BLOG_POSTS_FOLDER_ID=example
    DRIVE_BLOG_POSTS_FOLDER_ID_TEST=example
    ```
    *Replace the placeholder values with your desired credentials.*

2.  **Navigate to the Project Directory:**
    Open your terminal or command prompt and navigate to the root directory of this project, where the `docker-compose.yml` file is located.

    ```bash
    cd /path/to/your/flask_project
    ```
    *(Replace `/path/to/your/flask_project` with the actual path to your project.)*

3.  **Start the Containers:**
    Execute the following command to build (if necessary) and start all services defined in your `docker-compose.yml` file in detached mode (meaning they will run in the background).

    ```bash
    docker compose up -d
    ```

    **Explanation of the command:**
    * `docker compose`: This is the main command for interacting with Docker Compose projects.
    * `up`: This subcommand builds, (re)creates, starts, and attaches to containers for a service.
    * `-d`: This flag stands for "detached mode." It starts the containers in the background, allowing you to continue using your terminal. If you omit `-d`, the logs from your containers will be displayed in your terminal, and you'll need to press `Ctrl+C` to stop them (which will also stop the containers).

4.  **Verify Running Containers:**
    To confirm that your containers are running correctly, you can use the `docker ps` command:

    ```bash
    docker ps
    ```
    You should see output listing containers for your `web` (Flask app) and `db` (MySQL) services, with a `Status` of `Up`.

5.  **Access Your Application:**
    Once the containers are up and running, your Flask application should be accessible in your web browser at:

    `http://localhost:5000`

    *(Note: If you changed `FLASK_RUN_PORT` in your `.env` file, use that port instead of 5000.)*

***

### Troubleshooting: Application Not Accessible (Web Container Exited)

If you run `docker compose up -d` and then find that your application is not accessible at `http://localhost:5000`, a common reason is that the `web` container started but then immediately exited.

**How to Diagnose:**

1.  **Check Container Status:**
    Use `docker ps -a` to list all Docker containers, including those that have exited.
    ```bash
    docker ps -a
    ```
    Look for your `damianpiatkowskicom-web-1` container in the output. If its `STATUS` is `Exited (...)` (e.g., `Exited (126) 11 seconds ago`), while your `db` container is `Up`, it indicates a problem with your web service's startup command.

    **Example of problematic output:**
    ```
    CONTAINER ID   IMAGE                     COMMAND                   CREATED         STATUS                     PORTS          NAMES
    cadc9cd40472   damianpiatkowskicom-web   "sh -c 'mkdir -p /lo…"   12 seconds ago  Exited (126) 11 seconds ago                  damianpiatkowskicom-web-1
    590a923cbe46   mysql:latest              "docker-entrypoint.s…"   12 seconds ago  Up 12 seconds              0.0.0.0:3306->3306/tcp   damianpiatkowskicom-db-1
    ```
    The `Exited (126)` status for the `web` container is the key indicator. This often means the command Docker tried to execute inside the container was not found or lacked necessary permissions.

2.  **Getting Detailed Container Logs:**
    The most crucial step to debug an exited container is to inspect its logs. Docker collects all `stdout` and `stderr` output from the running processes inside the container.

    * **View logs for a specific service:**
        To see the output that your `web` container printed before it exited, use the `docker compose logs` command, specifying the service name:
        ```bash
        docker compose logs web
        ```
        This will display all the historical logs from your `damianpiatkowskicom-web-1` container. Look for error messages, stack traces, or any output that indicates why your Flask application or its startup script (`wait-for-it.sh`) failed.

    * **View only the most recent logs (useful for verbose outputs):**
        If the logs are very long, you can limit the output to the last N lines:
        ```bash
        docker compose logs web --tail 50
        ```
        (Replace `50` with any number of lines you want to see from the end.)

      * **Run the service in foreground (for real-time debugging):**
          If you want to see the logs as they happen and interact directly with the container's startup, you can run `docker compose up` without the `-d` (detached) flag, focusing on the service that's failing.

          First, ensure your services are stopped:
          ```bash
          docker compose down
          ```
          Then, bring up only the `web` service (and its dependencies, like `db`, will also start) in the foreground:
          ```bash
          docker compose up web
          ```
          The output will stream directly to your terminal. This is often the quickest way to catch the exact error message that causes the container to exit. Once you see the error and diagnose it, you can press `Ctrl+C` to stop the foreground process (which will also stop the containers), then resolve the issue, and finally run `docker compose up -d --build` again.

    By examining the logs, you'll get detailed information about why your Flask application container (`web`) is exiting with status code 1, allowing you to pinpoint the specific error or misconfiguration.

3. **Rebuilding Containers from Scratch:**
   If you suspect the issue is related to package installation or cached layers:

    * **Clean rebuild of a specific service:**
        ```bash
        docker compose down
        docker compose build --no-cache web
        docker compose up
        ```
      This forces Docker to rebuild the container without using cached layers, ensuring fresh installation of all dependencies.

    * **If you need to rebuild everything:**
        ```bash
        docker compose down
        docker compose build --no-cache
        docker compose up
        ```

   This is particularly useful when:
    - Dependencies aren't being installed correctly
    - You've updated requirements.txt

***

**How to Fix:**

The most common cause for `Exited (126)` in this setup is that the `wait-for-it.sh` script (or another script executed by your `command`) does not have executable permissions inside the container.

1.  **Stop and remove the currently running containers:**
    ```bash
    docker compose down
    ```

2.  **Make the script executable on your host machine:**
    Navigate to your project's root directory and run:
    ```bash
    chmod +x scripts/wait-for-it.sh
    ```
    This command adds execute permissions to the script.

3.  **Rebuild the `web` image and start all services:**
    Since the file permissions change needs to be incorporated into the Docker image itself, you must force a rebuild of the `web` service's image.
    ```bash
    docker compose up -d --build
    ```
    This will stop any containers, rebuild your `web` image (incorporating the new permissions), and then start all services again.

4.  **Verify Running Containers (Again):**
    After running the `--build` command, use `docker ps` again:
    ```bash
    docker ps
    ```
    Both `damianpiatkowskicom-web-1` and `damianpiatkowskicom-db-1` should now show `Status: Up ...`. Your application should now be accessible.

---

## Deployment

**to be completed later**

### Strategy

* **Dual-Stage Deploy**: `staging` & `production`
* **Deployed to EC2 via GitHub Actions**
* Secrets (e.g., SSH keys, ENV variables) stored in GitHub Secrets

### CI/CD (GitHub Actions)

* On push to `main` or PR merge, actions will:

  * Build and test the container
  * SSH into EC2
  * Pull the latest image
  * Restart the containers

---

## License

This project is open-sourced and distributed under the terms of the **[MIT License](LICENSE)**.

Copyright © 2024-Present Damian Piatkowski.
