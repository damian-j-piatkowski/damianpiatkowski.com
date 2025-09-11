# Draw.io Diagramming Guide

This guide outlines the best practices and recommended settings for creating and exporting diagrams using Draw\.io (app.diagrams.net) for this project's documentation, particularly for architecture diagrams.

---

## Table of Contents

* [1. Tool and Access](#1-tool-and-access)
* [2. General Diagramming Principles](#2-general-diagramming-principles)
* [3. Recommended Styling Conventions](#3-recommended-styling-conventions)
* [4. Arrow and Connection Styling](#4-arrow-and-connection-styling)
* [5. Export Settings for `README.md`](#5-export-settings-for-readmemd)
* [6. Editing and Updating Diagrams](#6-editing-and-updating-diagrams)

---

## 1. Tool and Access

* **Tool:** Draw\.io (also known as diagrams.net)
* **Access:** [app.diagrams.net](https://app.diagrams.net/) or the desktop application.
* **Source Files:** All editable `.drawio` diagram source files are stored in the `docs/architecture/` directory.

---

## 2. General Diagramming Principles

* **Clarity over Complexity:** Keep diagrams simple and understandable at a glance.
* **Consistent Layout:** Use consistent spacing, alignment, and sizing for related components.
* **Visual Hierarchy:** Use containers to group related systems (e.g., EC2 instance vs external services).

---

## 3. Recommended Styling Conventions

* **Component Coloring:**
  Use consistent colors to distinguish between these groups:

  1. **External Services (Non-Controlled Systems):**

     * Examples: Browser/User Client, Google Authentication, GitHub Actions, Google Drive API, Google SMTP.
     * **Border:** Use a `Dotted` or `Dashed` line to emphasize external ownership.

  2. **AWS EC2 Instance:**

     * The main virtual server hosting your application stack.

  3. **Application Layer (Flask App + Internal Components):**

     * Routes, Controllers, Services, Repositories.
     * Group them under a container labeled “Flask Application.”

  4. **System Services on EC2:**

     * **Nginx (reverse proxy)**
     * **Gunicorn/Flask runtime**
     * **MySQL server**

  5. **Persistent Storage (Database Data):**

     * Logical box representing MySQL’s persisted data.

* **Consistent Sizing:** Same width/height for similar elements (e.g., Controllers, Services).

* **Text/Labels:**

  * Font: `Helvetica`, `Arial`, or `Open Sans`.
  * Larger text for main containers, smaller for internals.
  * Notes: inline text inside a shape with `Shift+Enter` for line breaks.

---

## 4. Arrow and Connection Styling

* **Internal Function Calls (within Flask App):**

  * Unidirectional arrow, labeled `Function Calls`.

* **Data Access Calls (Services → Repositories → MySQL):**

  * Unidirectional arrow, labeled `Data Access Calls`.

* **Database Persistent Storage (MySQL ↔ Data):**

  * **Bidirectional** arrow, labeled `File I/O (Persistent Data)`.

* **External Traffic (Browser → Nginx):**

  * Unidirectional, labeled `HTTP/HTTPS (All App Traffic)`.

* **External API Calls (Flask Services → Google APIs/SMTP):**

  * Unidirectional, labeled `HTTP/S API Calls` or `SMTP Calls`.

* **OAuth Flow (Browser → Google Authentication):**

  * Unidirectional, labeled `OAuth Flow`.

* **CI/CD Deployment (GitHub Actions → EC2 Instance):**

  * Unidirectional arrow, labeled `CI/CD Deployment`.
  * Style: dashed or bold line to distinguish it from runtime data flows.

* **Waypoints:** Use only when needed for clean arrow routing.

---

## 5. Export Settings for `README.md`

When exporting `.drawio` diagrams for embedding in Markdown:

**Save Location & Filename:**

* `docs/architecture/high_level_architecture.svg`

**Export Options (File → Export as → SVG…):**

* **Zoom:** `100%` (SVG scales inherently, so no need to adjust this here).
* **Border Width:** `10` (pixels) - Adds a small, clean white border around your diagram.
* **Transparent Background:** ✅ (Ensures the diagram background is transparent, allowing it to blend with your README).
* **Appearance (Dropdown):** **`Light`** (Crucial for consistent rendering across different previewers and IDEs like PyCharm which might have light backgrounds).
* **Include a copy of my diagram:** ❌ (because the source XML for the diagram is already stored and version-controlled under `docs/architecture/high_level.drawio`).
* **Embed Images:** ✅ (Ensures all visual assets are self-contained).
* **Embed Fonts:** ✅ (Guarantees font consistency across devices).
* **Links (Dropdown):** `Automatic` (This is fine as there are no explicit links in the diagram; it won't create any).

## 6. Editing and Updating Diagrams

1. Open the `.drawio` source file (e.g., `docs/architecture/high_level.drawio`).
2. Make edits in Draw\.io.
3. Save the updated `.drawio` file.
4. Commit the `.drawio` source file to Git.
5. Export a new SVG (see Section 5).
6. Overwrite the existing `high_level_architecture.svg`.
7. Commit the updated `.svg` file.

By following this process, both your editable source diagram and its rendered image in the README will always be up-to-date and in sync.