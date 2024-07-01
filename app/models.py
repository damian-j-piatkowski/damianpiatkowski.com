from datetime import datetime, timezone


class Log:
    """Represents a log entry.

    Attributes:
        level: The severity level of the log (e.g., 'INFO', 'WARNING', 'ERROR').
        message: The log message.
        timestamp: The UTC timestamp when the log entry was created.
    """

    def __init__(self, level: str, message: str) -> None:
        """
        Constructs all the necessary attributes for the Log object.

        Args:
            level: The severity level of the log.
            message: The log message.
        """
        self.level = level
        self.message = message
        self.timestamp = datetime.now(timezone.utc)


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
