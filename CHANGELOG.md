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

## [1.1.0] - 2025-09-15
### Added
- **Blog syntax highlighting improvements**
  - Preserved `language-*` classes in `<pre><code>` blocks for client-side highlighters.
  - Introduced lightweight Bash syntax highlighting script:
    - Escapes raw HTML before applying styles for safety.
    - Distinguishes prompt, command, and output via styled `<span>` wrappers.
  - Added automatic language labels above code blocks with pretty overrides per language.
  - Implemented dark “terminal” theme for Bash blocks with styled prompt and output.

### Changed
- **Code block rendering & sanitization**
  - Removed server-side `codehilite` extension to delegate styling fully to client-side.
  - Allowed `class` attributes on `<pre>` and `<code>` tags while maintaining XSS protection.
  - Refactored CSS for code blocks:
    - Unified under `<pre><code class="language-...">`.
    - Moved label placement from `<pre>::before` → `<code>::before` for cleaner semantics.
    - Synced `<pre>` and `<code>` backgrounds to avoid scrollbar color mismatches.
  - Adjusted spacing/padding for readability on desktop, tablet, and mobile.

### Documentation
- Updated docstrings to clarify support for `<pre><code>` attributes (`language-*`) and explain separation of concerns:
  - Markdown provides language hints.
  - Client-side handles syntax highlighting and styling.

---

## [1.0.3] - 2025-09-11
### Changed
- **Infrastructure & deployment**  
  - Removed all Docker dependencies and configs (`docker-compose.*`, `Dockerfile*`, `scripts/wait-for-it.sh`).  
  - Migrated to a dockerless setup using Python `venv` and `systemd` on EC2.  
  - Updated `README.md` with new local setup and deployment workflow.  
  - Refined architecture description to reflect non-containerized MySQL and direct EC2 deployment.  

- **Documentation & diagrams**  
  - Updated `docs/database-guide.md` for non-Docker DB setup.  
  - Adjusted `docs/drawio-guide.md` to align with new diagrams.  
  - Revised `docs/architecture/high_level.drawio` and exported `.svg` to remove Docker layers and clarify direct EC2 deployment flow.  

### Added
- **Responsive improvements for About Hero**  
  - Increased `.about-hero` mobile min-height from 185vh → 200vh.  
  - Added landscape-specific breakpoints for short/wide screens:  
    - `(max-height: 500px) and (orientation: landscape) and (min-width: 751px)` → side-by-side layout with left-aligned text.  
    - `(max-width: 750px) and (orientation: landscape)` → stacked layout with right-shifted text for small phones.  
  - Adjusted `.about-text` sizing/padding across new breakpoints.  
  - Improved `.about-bg img` containment and positioning in wide-but-short screens.

---

## [1.0.2] - 2025-09-10
### Added
- **Responsive support for mobile landscape mode**  
  - Added `<source>` entries in `picture` markup for `(max-height: 500px) and (orientation: landscape)`.  
  - Introduced CSS rules for `.landing-hero` and `.blog-hero` in phone landscape orientation.  
  - Ensures hero layout adapts with side-by-side text and image on wide but short screens.  
  - Updated `.blog-text` styling to align left and avoid auto-centering in landscape mode.

- **Footer version display**  
  Added `v{{ VERSION }}` to footer as muted small text for quick confirmation of deployed build version.

### Fixed
- **Template cache busting**  
  Updated `css_link_bundle` macro to correctly receive and use `VERSION`, ensuring CSS bundles include `?v={{ VERSION }}` query param in production.

### Changed
- **Build process**  
  Replaced `csscompressor` with `rcssmin` for CSS minification, improving reliability and preserving media query syntax and color values.

---

## [1.0.1] - 2025-09-09
### Fixes
- **Environment configuration**  
  Updated `config.py` to load `.env` only when `FLASK_ENV` is not already set, ensuring production systemd service variables are respected.

### Refactors
- **Blog hero image resizer utility**  
  - Replaced hardcoded `landing-hero_source_16x9.jpg` with automatic detection of the first `.jpg`/`.jpeg` file in the target folder.  
  - Standardized output naming to `hero_16x9_<width>w.*`.  
  - Added detailed header with purpose, requirements, usage instructions, and example input/output.  
  - Script now exits gracefully if no source JPG is found.

- **Thumbnail resizer utility**  
  Updated `resize_thumbnails.bat` with structured header and conventions matching the hero image resizer for readability and maintainability.

- **Blog and landing hero styles (index.css)**  
  - Updated `.blog-bg` images to use `object-fit: cover` and `object-position: center bottom` with consistent background color.  
  - Increased `.blog-hero` min-height and `.blog-bg` height on tablets.  
  - Adjusted mobile `.blog-hero` and `.landing-hero` min-heights for better content fit.  
  - Reduced `.contact-form-card.in-view` transition delay from 3.3s to 2.3s.

---

## [1.0.0] - 2025-09-05
### Initial Release

The first production release of damianpiatkowski.com website, launching with:

- **Home Page (`/`)**
- **Privacy Policy (`/privacy`)**
- **About Me (`/about-me`)**
- **Resume (`/resume`)**
- **Blog (`/blog`)**

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
