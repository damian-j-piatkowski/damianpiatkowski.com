"""Script to manually seed blog posts in the development database.

Usage:
    python -m scripts.seed_blog_posts --posts 25
    python -m scripts.seed_blog_posts --posts 10 --content "Custom content"

Docker:
    docker-compose exec web python -m scripts.seed_blog_posts --posts 2
"""

import argparse
import sys
from datetime import datetime

from app import create_app
from app.config import DevelopmentConfig
from app.extensions import db
from app.models.tables.blog_post import blog_posts


def generate_lorem_ipsum(paragraphs: int = 3) -> str:
    """Generates Lorem Ipsum HTML content with a specified number of paragraphs."""
    lorem_text = """
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor 
    incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud 
    exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
    """

    paragraphs_html = ''.join([f"<p>{lorem_text}</p>" for _ in range(paragraphs)])
    return f"""
    <article>
        <div class="content">
            {paragraphs_html}
        </div>
    </article>
    """


def seed_posts(num_posts: int, base_content: str = None) -> None:
    """Seeds the database with a specified number of blog posts."""
    app = create_app(DevelopmentConfig)

    with app.app_context():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Define category sets - each post will get 2 categories from one of these sets
        category_sets = [
            ["Python", "Web Development"],      # Set 1 - posts 1, 4, 7, 10, ...
            ["JavaScript", "Frontend"],         # Set 2 - posts 2, 5, 8, 11, ...
            ["DevOps", "Cloud Computing"]       # Set 3 - posts 3, 6, 9, 12, ...
        ]

        for i in range(num_posts):
            post_number = i + 1
            unique_id = f"{timestamp}_{post_number}"

            # Generate content - either custom or lorem ipsum
            if base_content:
                content = f"{base_content} (Post {unique_id})"
            else:
                content = generate_lorem_ipsum()

            # Get categories using modulo to cycle through the sets
            categories = category_sets[i % len(category_sets)]

            # Insert the post with timestamp-based unique identifiers and categories
            db.session.execute(blog_posts.insert().values(
                title=f"Development Test Post {unique_id}",
                slug=f"dev-test-post-{unique_id}",
                html_content=content,
                drive_file_id=f"dev-test-file-{unique_id}",
                categories=categories
            ))

            print(f"Created post {post_number}/{num_posts} with categories: {categories}")

        db.session.commit()
        print(f"\nSuccessfully created {num_posts} blog posts")


def main():
    parser = argparse.ArgumentParser(description='Seed development database with test blog posts')
    parser.add_argument('--posts', type=int, required=True, help='Number of posts to generate')
    parser.add_argument('--content', type=str, help='Custom content template (optional)')

    args = parser.parse_args()

    try:
        seed_posts(args.posts, args.content)
    except Exception as e:
        print(f"Error seeding posts: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
