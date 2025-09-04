# Draw.io Diagramming Guide

This guide outlines the best practices and recommended settings for creating and exporting diagrams using Draw.io (app.diagrams.net) for this project's documentation, particularly for architecture diagrams.

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

* **Tool:** Draw.io (also known as diagrams.net)
* **Access:** [app.diagrams.net](https://app.diagrams.net/) or integrated desktop application.
* **Source Files:** All editable `.drawio` diagram source files are stored in the `docs/architecture/` directory.

## 2. General Diagramming Principles

* **Clarity over Complexity:** Aim for diagrams that are easy to understand at a glance.
* **Consistent Layout:** Maintain consistent spacing, alignment, and sizing of similar components.
* **Visual Hierarchy:** Use container shapes effectively to show containment and relationships.

## 3. Recommended Styling Conventions

* **Component Coloring:**
    The key principle for coloring is **consistency and clear differentiation**. Use a distinct color for each of the following groups to visually separate them, ensuring that elements within a group share the same color.

    1.  **External Services (Non-Controlled Systems):**
        * **Purpose:** Systems outside of your direct AWS EC2 instance, not managed by you (e.g., Browser/User Client, Google Authentication, GitHub Actions, Google Drive API, Google SMTP).
        * **Border:** Use a `Dotted` or `Dashed` line style to emphasize external ownership/boundary.

    2.  **AWS EC2 Instance:**
        * **Purpose:** The main cloud virtual server hosting your application.

    3.  **Docker (Engine / Host):**
        * **Purpose:** The container runtime environment within your EC2 instance.

    4.  **Flask App Container and Internal Components:**
        * **Purpose:** The Flask application container and all its internal layers (Routes, Controllers, Services, Repositories). These logically belong together as part of "your application code."

    5.  **MySQL Container:**
        * **Purpose:** The database server software.

    6.  **Persistent Storage (DB Volume):**
        * **Purpose:** The physical storage volume for your database.

* **Consistent Sizing:** Maintain consistent sizing for similar components (e.g., Width: 160, Height: 30 for Repositories, Services, Controllers).
* **Text/Labels:**
    * **Font:** Stick to a readable sans-serif font (e.g., `Helvetica`, `Arial`, `Open Sans`).
    * **Font Size:** Use larger for main containers, smaller for internal components and arrow labels.
    * **Internal Notes:** For contextual notes within a shape (e.g., Admin Routes), embed text directly and use `Shift + Enter` for line breaks.

## 4. Arrow and Connection Styling

* **Internal Function Calls (within Flask App):**
    * Arrow: Unidirectional
    * Label: `Function Calls` (e.g., Routes to Controllers, Controllers to Services)
* **Internal Data Access Calls (Services to Repositories):**
    * Arrow: Unidirectional
    * Label: `Data Access Calls`
* **Database Persistent Storage (MySQL Container to DB Volume):**
    * Arrow: **Bidirectional**
    * Label: `File I/O (Persistent Data)`
* **External Traffic (Browser to Nginx Waypoint):**
    * Arrow: Unidirectional
    * Label: `HTTP/HTTPS (All App Traffic)`
* **External API Calls (Services to Google Drive API, Google SMTP):**
    * Arrow: Unidirectional
    * Labels: `HTTP/S API Calls`, `SMTP Calls`
* **OAuth Flow Initiation (Browser to Google Authentication):**
    * Arrow: Unidirectional
    * Label: `HTTP/HTTPS (Admin Login OAuth Flow)`
* **CI/CD Deployment (GitHub Actions to Docker):**
    * Arrow: Unidirectional
    * Label: `CI/CD Pipeline / Deployment`
    * *Optional:* Consider making this arrow a dashed or thicker line to visually distinguish it from data flows.
* **Waypoints:** Use sparingly for clean bends, avoid sharp angles.

## 5. Export Settings for `README.md`

When exporting your `.drawio` diagram for embedding in `README.md` (or other Markdown files), use the following settings for optimal display on desktop and mobile.

**Save Location & Filename:**
* Save the exported SVG file as: `docs/architecture/high_level_architecture.svg`

**Export Options (File > Export as > SVG...):**

* **Zoom:** `100%` (SVG scales inherently, so no need to adjust this here).
* **Border Width:** `10` (pixels) - Adds a small, clean white border around your diagram.
* **Transparent Background:** **CHECKED** (Ensures the diagram background is transparent, allowing it to blend with your README).
* **Appearance (Dropdown):** **`Light`** (Crucial for consistent rendering across different previewers and IDEs like PyCharm which might have light backgrounds).
* **Include a copy of my diagram:** **UNCHECKED** (because the source XML for the diagram is already stored and version-controlled under `docs/architecture/high_level.drawio`).
* **Embed Images:** **CHECKED** (Ensures all visual assets are self-contained).
* **Embed Fonts:** **CHECKED** (Guarantees font consistency across devices).
* **Links (Dropdown):** `Automatic` (This is fine as there are no explicit links in the diagram; it won't create any).

## 6. Editing and Updating Diagrams

To make changes to an existing diagram:

1.  **Open the Source File:** Open the `.drawio` source file (e.g., `docs/architecture/high_level.drawio`) directly in Draw.io (either online at `app.diagrams.net` or using the desktop application).
2.  **Make Your Changes:** Edit the diagram as needed.
3.  **Save the Source:** **Save the `.drawio` file** in Draw.io. This is crucial for version control.
4.  **Version Control:** Commit the updated `.drawio` file to your Git repository.
5.  **Re-Export SVG:** Follow the **"5. Export Settings for `README.md`"** steps above to re-export the diagram as an SVG file.
6.  **Replace Existing SVG:** Save the new SVG file, overwriting the old one (e.g., `docs/architecture/high_level_architecture.svg`).
7.  **Commit Updated SVG:** Commit the newly exported `.svg` file to your Git repository.

By following this process, both your editable source diagram and its rendered image in the README will always be up-to-date and in sync.