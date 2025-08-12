# CHANGELOG

All notable changes to this project will be documented in this file.  
The format follows the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) convention and adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html):

- **Added** – new features
- **Changed** – changes to existing functionality
- **Deprecated** – soon-to-be removed features
- **Removed** – removed features
- **Fixed** – bug fixes
- **Security** – security-related updates

---

## [1.0.0] - 2025-08-14
### Initial Release

The first production release of my personal website, launching with:

- **Home Page (`/`)**  
  Overview of my work, personal brand, and latest updates.

- **Privacy Policy (`/privacy`)**  
  Clear and concise explanation of how visitor data is handled.

- **About Me (`/about-me`)**  
  A personal introduction — focusing on my story, values, and life outside of projects.

- **Resume (`/resume`)**  
  Downloadable CV for professional opportunities.

- **Blog (`/blog`)**  
  Fully functional blogging engine with pagination and individual post pages.  

  **Technical note:**  
  Blog content originates as Google Docs using Markdown conventions.  
  On publish, files are retrieved from Google Drive via the `GoogleDriveService`, sanitized, converted to HTML, and persisted as domain `BlogPost` objects via the `blog_service` and `blog_post_repository`.  
  HTML content is stored in the `blog_posts` table with generated slugs, and the database `created_at` timestamp serves as the single source of truth for publication date.

### Features
- Clean, responsive design for both desktop and mobile.
- SEO-friendly URLs and auto-generated sitemap.
- Structured HTML templates with consistent navigation.
- Backend pipeline for converting Google Drive documents into published posts.
- Production-ready configuration for deployment.

### Test Suite
- Comprehensive automated tests covering controllers, services, repositories, and routes.  
- **Overall coverage:** 80% across 1,173 statements.
