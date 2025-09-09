r"""Script for uploading blog posts to the database from Google Drive.

Usage:
    python -m scripts.upload_blog_posts --env dev --file-id "google_drive_file_id" --slug "post-slug"

For example:
    python -m scripts.upload_blog_posts --env prod --file-id "1ZtTMn_kt08At3BUgWQIa23bv5r6S3SOoBC9JVmN5UOA" --slug "six-essential-object-oriented-design-principles-from-matthias-nobacks-object-design-style-guide"
"""

import argparse
import sys

from app import create_app
from app.config import DevelopmentConfig, ProductionConfig
from app.controllers.admin_controller import upload_blog_posts_from_drive


def upload_post(env: str, file_id: str, slug: str) -> None:
    """Upload a single blog post to the database.

    Args:
        env: Environment (dev or prod)
        file_id: Google Drive file ID
        slug: URL-friendly identifier
    """
    if env == "dev":
        config_class = DevelopmentConfig
    elif env == "prod":
        config_class = ProductionConfig
    else:
        raise ValueError("Invalid env value. Use 'dev' or 'prod'.")

    app = create_app(config_class)

    with app.app_context():
        post_data = [{
            "id": file_id,
            "slug": slug
        }]

        response, status_code = upload_blog_posts_from_drive(post_data)
        response_data = response.get_json()

        print(f"\nStatus Code: {status_code}")

        if "success" in response_data:
            print("\nSuccessfully uploaded:")
            for post in response_data["success"]:
                print(f"- {post['title']} ({post['slug']} {post['categories']})")

        if "errors" in response_data and response_data["errors"]:
            print("\nErrors:")
            for error in response_data["errors"]:
                print(f"- File ID {error['file_id']}: {error['error']}")


def main():
    parser = argparse.ArgumentParser(description="Upload blog post from Google Drive to database")
    parser.add_argument("--env", required=True, choices=["dev", "prod"], help="Target environment")
    parser.add_argument("--file-id", required=True, help="Google Drive file ID")
    parser.add_argument("--slug", required=True, help="Post slug")

    args = parser.parse_args()

    try:
        upload_post(args.env, args.file_id, args.slug)
    except Exception as e:
        print(f"Error uploading post: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
