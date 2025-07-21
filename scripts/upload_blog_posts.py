"""Script for uploading blog posts to development database from Google Drive.

Usage:
    python -m scripts.upload_blog_posts --file-id "google_drive_file_id" --title "Post Title" --slug "post-slug"

Docker:
    docker-compose exec web python -m scripts.upload_blog_posts --file-id "google_drive_file_id" --title "Post Title" --slug "post-slug"
"""

import argparse
import sys

from app import create_app
from app.config import DevelopmentConfig
from app.controllers.admin_controller import upload_blog_posts_from_drive


def upload_post(file_id: str, title: str, slug: str) -> None:
    """Upload a single blog post to development database.

    Args:
        file_id: Google Drive file ID
        title: Post title
        slug: URL-friendly identifier
    """
    app = create_app(DevelopmentConfig)

    with app.app_context():
        post_data = [{
            "id": file_id,
            "title": title,
            "slug": slug
        }]

        response, status_code = upload_blog_posts_from_drive(post_data)
        response_data = response.get_json()

        print(f"\nStatus Code: {status_code}")

        if "success" in response_data:
            print("\nSuccessfully uploaded:")
            for post in response_data["success"]:
                print(f"- {post['title']} ({post['slug']})")

        if "errors" in response_data and response_data["errors"]:
            print("\nErrors:")
            for error in response_data["errors"]:
                print(f"- File ID {error['file_id']}: {error['error']}")


def main():
    parser = argparse.ArgumentParser(description='Upload blog post from Google Drive to development database')
    parser.add_argument('--file-id', required=True, help='Google Drive file ID')
    parser.add_argument('--title', required=True, help='Post title')
    parser.add_argument('--slug', required=True, help='Post slug')

    args = parser.parse_args()

    try:
        upload_post(args.file_id, args.title, args.slug)
    except Exception as e:
        print(f"Error uploading post: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
