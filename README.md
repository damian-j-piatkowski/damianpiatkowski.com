# Personal Website & Blog – [damianpiatkowski.com](https://damianpiatkowski.com)

A Flask-powered personal website with a blog component, live at [damianpiatkowski.com](https://damianpiatkowski.com). It features a custom-built blog engine that syncs content from Google Drive, sanitizes it, and stores it in a MySQL database. The site also includes a resume, an about page, and an admin interface for managing posts. The entire project is containerized with Docker for easy deployment and local development.

This project is public not just as a portfolio piece, but also to serve as a learning resource for others interested in building a personal website or Flask-based app with CI/CD, Google Drive API integration, and MySQL-backed content management.

---

## Table of Contents

* [Features](#features)
* [Architecture Overview](#architecture-overview)
* [Routes & Admin Panel](#routes--admin-panel)
* [Technology Stack](#technology-stack)
* [Setup & Development](#setup--development)
* [Deployment](#deployment)
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

A visual overview of the system's high-level architecture is provided below in an ASCII art diagram. This text-based representation ensures it's easily viewable across all platforms and keeps the documentation directly editable and version-control friendly.

```
+--------------------------------------------------------------------------------------------------+
|                                        AWS EC2 Instance                                          |
|  +--------------------------------------------------------------------------------------------+  |
|  |                                  Docker (Engine / Host)                                    |  |
|  |                                                                                            |  |
|  |  +-------------------+        +---------------------------------------------------------+  |  |
|  |  |   Nginx Container   |        |                 Flask App Container                   |  |  |
|  |  | (Reverse Proxy)     |        |                                                         |  |  |
|  |  +---------+-----------+        |  +-----------------+      +-----------------+          |  |  |
|  |            |  (Public Traffic)  |  |  Public Routes  |      |  Admin Routes   |<----+    |  |  |
|  |            +------------------->|  +--------+--------+      +--------+--------+      |    |  |  |
|  |            |                    |           |                        |              Token |    |  |
|  |            |  (Admin Traffic)   |           |                        |           Verification|  |  |
|  |            +------------------->|           | Function Calls         | Function Calls|      |  |  |
|  |                                |           V                        V               |      |  |  |
|  |                                |  +-----------------+      +-----------------+      |    |  |  |
|  |                                |  |   Controllers   |      |   Controllers   |<-----+    |  |  |
|  |                                |  +--------+--------+      +--------+--------+          |  |  |
|  |                                |           |                                             |  |  |
|  |                                |           | Function Calls                              |  |  |
|  |                                |           V                                             |  |  |
|  |                                |  +-----------------+                                     |  |  |
|  |                                |  |    Services     |------------------------------------->| (To Google Drive API, SMTP)
|  |                                |  +--------+--------+                                     |  |  |
|  |                                |           |                                             |  |  |
|  |                                |           | Function Calls (Data Access)                |  |  |
|  |                                |           V                                             |  |  |
|  |                                |  +-----------------+                                     |  |  |
|  |                                |  |  Repositories   |-------------------------------------+  |  |
|  |                                |  +-----------------+                                     |  |  |
|  |                                +---------------------------------------------------------+  |  |
|  |                                                                                            |  |
|  |  +-----------------------+                                                                 |  |
|  |  |    MySQL Container    |<---------------------------------------------------------------+  |
|  |  |                       |           (SQL queries)                                          |  |
|  |  +-----------+-----------+                                                                 |  |
|  |              |                                                                             |  |
|  |              | File-based I/O (Persistent Data)                                            |  |
|  |              V                                                                             |  |
|  |  +-----------------------+                                                                 |  |
|  |  |     DB Volume         |                                                                 |  |
|  |  | (Persistent Storage)  |                                                                 |  |
|  |  +-----------------------+                                                                 |  |
|  +--------------------------------------------------------------------------------------------+  |
+--------------------------------------------------------------------------------------------------+
     ^                       ^
     | HTTP/HTTPS            | HTTP/HTTPS
     | (Public Traffic)      | (Admin Login OAuth Flow)
+------------------------------------+
|        Browser/User Client         |
+------------------------------------+
```

***

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

## Setup & Development

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/yourrepo.git
cd yourrepo
```

### 2. Configure Environment

Create a `.env` file for your local environment:

```env
FLASK_ENV=development
MYSQL_DATABASE=your_db
MYSQL_USER=root
MYSQL_PASSWORD=your_password
GOOGLE_DRIVE_FOLDER_ID=your_folder_id
```

Add your Google service account JSON as `google_service_account_details.json` in the root.

### 3. Build & Run via Docker Compose

```bash
docker-compose up --build
```

This starts the app, MySQL (file-based), and Nginx (if configured).

---

## Deployment

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

MIT License © Damian Piatkowski
