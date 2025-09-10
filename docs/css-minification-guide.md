# CSS Minification and Bundling Guide

This guide documents the CSS bundling and minification strategy for the project.
It explains how styles are organized, how the Python-based minification script works,
and how templates dynamically load styles in development and production environments.

## Purpose
- Ensures optimal CSS delivery in production through minification and bundling
- Maintains easy debugging in development by serving unminified individual files
- Provides a consistent, cache-busted way to load styles in templates

## Key Features
- **Python-based bundling** using `csscompressor`
- **CSS_BUNDLES** definition maps bundles to their component files
- **Environment-aware loading** via Jinja macro:
  - Development → individual `.css` files
  - Production → single minified `.min.css` bundle
- **Cache-busting** with version query parameter
- **Simple CLI script** for building bundles: `python scripts/minify_css.py`

---

## Table of Contents
1. [Bundle Definitions](#bundle-definitions)
2. [Minification Script](#minification-script)
3. [Template Integration](#template-integration)
4. [Development Workflow](#development-workflow)
5. [Production Workflow](#production-workflow)

---

## Bundle Definitions

CSS bundles are defined in the `CSS_BUNDLES` dictionary:

```python
CSS_BUNDLES = {
    "global.min.css": [
        "app/static/css/variables.css",
        "app/static/css/base.css",
    ],
    "index.min.css": [
        "app/static/css/index.css",
    ],
    # ...additional bundles...
}
````

Each key corresponds to the name of the output file, while the value is a list of source files.

---

## Minification Script

Located at `scripts/minify_css.py`, the script:

1. Iterates through each bundle in `CSS_BUNDLES`
2. Concatenates the input CSS files
3. Minifies the combined CSS with `csscompressor`
4. Writes the result into `app/static/dist/css`

Run manually with:

```bash
python scripts/minify_css.py
```

Output example:

```
Built global.min.css
Built index.min.css
```

---

## Template Integration

The Jinja macro `css_link_bundle` in `macros/css_loader.html` decides which CSS to load:

* **Development (`ENV=development`)**
  Loads individual CSS files for easier debugging:

  ```html
  <link rel="stylesheet" href="/static/css/base.css">
  ```

* **Production (`ENV=production`)**
  Loads the corresponding minified bundle with versioning:

  ```html
  <link rel="stylesheet" href="/static/dist/css/index.min.css?v=12345">
  ```

Usage in a template:

```jinja
{{ css_link_bundle("index", ENV=ENV, VERSION=VERSION) }}
```

> **Note**
> Even though `ENV` is globally available in templates (via the context processor in `app/__init__.py`), you still need to pass it explicitly as an argument to the macro.
> This is because Jinja macros don’t automatically inherit global variables; they only receive the parameters you pass in.

---

## Development Workflow

* Edit CSS in `app/static/css/`
* Refresh the page → individual files are loaded directly
* No build step required

---

## Production Workflow

* Run the minification script:

  ```bash
  python scripts/minify_css.py
  ```
* Deploy the contents of `app/static/dist/css` to the server
* Templates automatically load the `.min.css` bundles

---

## Notes

* All CSS files should live under `app/static/css/`
* Add new pages by defining a bundle in `CSS_BUNDLES` and updating templates
* Version tags are controlled via the `VERSION` config variable.  
  This value comes from the `app/__version__.py` file, which serves as the single source of truth for your application’s version