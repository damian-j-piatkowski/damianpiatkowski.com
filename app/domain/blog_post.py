class BlogPost:
    """Represents a blog post.

    Attributes:
        title: The title of the blog post.
        content: The content of the blog post.
        image_small: URL or path to the small-sized image.
        image_medium: URL or path to the medium-sized image.
        image_large: URL or path to the large-sized image.
    """

    def __init__(
            self,
            title: str,
            content: str,
            image_small: str,
            image_medium: str,
            image_large: str
    ) -> None:
        """
        Constructs all the necessary attributes for the BlogPost object.

        Args:
            title: The title of the blog post.
            content: The content of the blog post.
            image_small: URL or path to the small-sized image.
            image_medium: URL or path to the medium-sized image.
            image_large: URL or path to the large-sized image.
        """
        self.title = title
        self.content = content
        self.image_small = image_small
        self.image_medium = image_medium
        self.image_large = image_large
