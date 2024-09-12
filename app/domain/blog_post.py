"""Module for representing and managing blog posts.

This module contains the definition of the `BlogPost` class,
which models a blog post in the system.

The `BlogPost` class includes attributes to store various details of a blog post
such as its title, content, images, and URL slug.

The class-level type hints provide clear indications of the expected data
types for each attribute.

Classes:
- BlogPost: Represents a blog post with attributes for title, content, images,
    and URL.

Example Usage:
    post = BlogPost(
        title='Sample Post',
        content='This is the content of the post.',
        image_small='path/to/small/image.jpg',
        image_medium='path/to/medium/image.jpg',
        image_large='path/to/large/image.jpg',
        url='sample-post'
    )
"""

from datetime import datetime


class BlogPost:
    """Represents a blog post.

    Attributes:
        title: The title of the blog post.
        content: The content of the blog post.
        image_small: URL or path to the small-sized image.
        image_medium: URL or path to the medium-sized image.
        image_large: URL or path to the large-sized image.
        url: The desired URL slug for the blog post.
        created_at: The timestamp when the blog post was created.
    """

    title: str
    content: str
    image_small: str
    image_medium: str
    image_large: str
    url: str
    created_at: datetime

    def __init__(
            self,
            title: str,
            content: str,
            image_small: str,
            image_medium: str,
            image_large: str,
            url: str
    ) -> None:
        """
        Constructs all the necessary attributes for the BlogPost object.

        Args:
            title: The title of the blog post.
            content: The content of the blog post.
            image_small: URL or path to the small-sized image.
            image_medium: URL or path to the medium-sized image.
            image_large: URL or path to the large-sized image.
            url: The desired URL slug for the blog post.
        """
        self.title = title
        self.content = content
        self.image_small = image_small
        self.image_medium = image_medium
        self.image_large = image_large
        self.url = url
        self.created_at = datetime.now()  # Automatically set creation timestamp
