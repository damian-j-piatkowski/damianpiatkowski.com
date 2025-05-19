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

![App Architecture](docs/architecture/app_architecture_flow.png)

### Components

* **Nginx** as a reverse proxy
* **Flask** app container
* **MySQL** file-based container
* **Google Drive** for syncing drafts
* **GitHub Actions** for CI/CD
* **EC2** instance running everything via Docker Compose

---

## Routes & Admin Panel

### Home

* `GET /` → `index.html`
* `POST /submit-contact` → Handles form submission
* `GET /privacy` → `privacy.html`

### Resume

* `GET /resume` → `resume.html`

### About Me

* `GET /about-me` → `about-me.html`
* Route: `routes/about_me.about_me`

### Blog

* `GET /blog` → Paginated blog posts (`blog.html`)
* `GET /blog/<slug>` → Individual post (`single_blog_post.html`)

### Admin Panel

#### Published Posts

* `GET /admin/published-posts` → `admin_published_posts.html`

  * Renders all DB blog posts
  * AJAX deletion via:
* `DELETE /admin/delete-blog-posts`

  * JSON-based batch deletion by slug

#### Unpublished Posts

* `GET /admin/unpublished-posts` → `admin_posts.html`

  * Fetches unposted Google Drive docs
  * Compares normalized slugs to DB
* `POST /admin/upload-blog-posts`

  * Batch upload to DB
  * HTML is sanitized, slugs normalized, and posts inserted

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
