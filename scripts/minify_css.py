import os
from csscompressor import compress

CSS_BUNDLES = {
    "global.min.css": [
        "app/static/css/variables.css",
        "app/static/css/base.css",
    ],
    "index.min.css": [
        "app/static/css/index.css",
    ],
    "about-me.min.css": [
        "app/static/css/about-me.css",
    ],
    "resume.min.css": [
        "app/static/css/resume.css",
    ],
    "privacy.min.css": [
        "app/static/css/privacy.css",
    ],
    "blog.min.css": [
        "app/static/css/blog/categories.css",
        "app/static/css/blog/post_list_layout.css",
        "app/static/css/blog/post_metadata.css",
    ],
    "single_blog_post.min.css": [
        "app/static/css/blog/single_post_layout.css",
        "app/static/css/blog/post_metadata.css",
        "app/static/css/blog/post_body.css",
        "app/static/css/blog/categories.css",
    ],
}

OUTPUT_DIR = "app/static/dist/css"

def minify_bundle(output_file, input_files):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    combined_css = ""
    for path in input_files:
        with open(path, "r", encoding="utf-8") as f:
            combined_css += f.read() + "\n"
    minified = compress(combined_css)
    with open(os.path.join(OUTPUT_DIR, output_file), "w", encoding="utf-8") as f:
        f.write(minified)
    print(f"Built {output_file}")

if __name__ == "__main__":
    for out_file, in_files in CSS_BUNDLES.items():
        minify_bundle(out_file, in_files)