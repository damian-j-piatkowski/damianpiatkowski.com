"""Integration tests for the convert_markdown_to_html function in the FormattingService module.

This test retrieves a markdown file from Google Drive, converts it to HTML using
the FormattingService, and verifies that the output matches the expected HTML.

Tests included:
    - test_convert_markdown_to_html_with_google_drive_file: Retrieves markdown content
      from Google Drive, converts it to HTML, and verifies the conversion.
"""

import pytest

from app import exceptions
from app.services.formatting_service import convert_markdown_to_html
from app.services.google_drive_service import GoogleDriveService

TEST_MARKDOWN_FILE_ID = '1zZM1zY6qmOIuXh2Fb-6oQ3lZ_ETRvEnlnl75Pw3WecE'


def test_convert_markdown_to_html_with_google_drive_file(
        google_drive_service_fixture: GoogleDriveService
) -> None:
    """Tests converting markdown content from a Google Drive file to HTML."""
    try:
        # Retrieve markdown content from Google Drive
        markdown_content = google_drive_service_fixture.read_file(TEST_MARKDOWN_FILE_ID)

        # Convert markdown to HTML
        html_content = convert_markdown_to_html(markdown_content)

        # Expected HTML output
        expected_html = """<h1>Six Essential Object-Oriented Design Principles from Matthias Noback's “Object Design Style Guide”</h1>
<p>The concept of transferable skills is one that I hold dear, particularly in the realm of programming. Good object design is not exclusive to Python, PHP, or any other specific language; it's a universal philosophy. While the implementation details may differ from one technology to another, the underlying principles remain the same.</p>
<p>Limiting yourself to resources that focus exclusively on one language, like searching for 'design books in Python' can restrict your access to a broader pool of valuable insights. Embracing general concepts, even when presented in unfamiliar languages, can significantly broaden your understanding and improve your adaptability.</p>
<p>This is why 'Object Design Style Guide' is a book worth your time, regardless of your current toolbox. It delves deeply into these universal concepts of object-oriented design, offering insights that transcend specific programming languages. Whether you're working with C++, R, or any other object-oriented language, the principles covered in this book will provide you with valuable knowledge and skills that can enhance your programming practice.</p>
<p>In this blog post, I aim to distill some core ideas from Noback's well-regarded book, which you can incorporate into your everyday decision-making framework when designing objects in your programs. If you find Python easier to read than, say, Java, you're in luck, as I will be illustrating the concepts in that language.</p>
<h2>Principle No. 1: Favor Composition Over Inheritance</h2>
<p>In the early days of object-oriented programming, inheritance was often seen as a cornerstone feature. Many developers relied heavily on inheritance to promote code reuse and establish relationships between classes. However, over time, it became apparent that excessive use of inheritance could lead to rigid and confusing designs.</p>
<blockquote>
<p>"In this book, inheritance plays a small role, even though it’s supposed to be a very important feature of object-oriented programming. In practice, using inheritance mostly leads to a confusing design."</p>
</blockquote>
<p>Noback's perspective aligns with modern software design principles. In Python, inheritance is often reserved for defining interfaces and creating hierarchies, such as custom exceptions, using abstract base classes (ABCs). <br />
However, for most other purposes, composition is favored over inheritance. Composition allows for greater flexibility and encapsulation, enabling developers to build complex systems by combining simpler, more modular components. This approach not only makes the code more manageable and understandable but also reduces the tight coupling that deep inheritance hierarchies tend to create.<br />
Let's illustrate composition, but instead of cars and engines that almost every tutorial has, I'll use games, because games are fun:</p>
<pre class="codehilite"><code class="language-python">class Game:
    def __init__(self, title: str, play_time: int = 0) -&gt; None:
        self.title: str = title
        self.play_time: int = play_time


    def add_play_time(self, hours: int) -&gt; None:
        self.play_time += hours
        print(f&quot;Added {hours} hours to {self.title}. Total play time is now {self.play_time} hours.&quot;)


    def __str__(self) -&gt; str:
        return f&quot;{self.title} ({self.play_time} hours played)&quot;


class GamerAccount:
    def __init__(self, username: str) -&gt; None:
        self.username: str = username
        self.games: list[Game] = []


    def add_game(self, game: Game) -&gt; None:
        self.games.append(game)
        print(f&quot;Added game: {game.title} to {self.username}'s account.&quot;)


    def get_total_play_time(self) -&gt; int:
        total_play_time: int = sum(game.play_time for game in self.games)
        print(f&quot;{self.username}'s total play time across all games is {total_play_time} hours.&quot;)
        return total_play_time


    def list_games(self) -&gt; None:
        print(f&quot;{self.username}'s owned games:&quot;)
        for game in self.games:
            print(game)


# Usage
gamer = GamerAccount(username=&quot;PlayerOne&quot;)
game1 = Game(title=&quot;Game A&quot;, play_time=10)
game2 = Game(title=&quot;Game B&quot;, play_time=5)


gamer.add_game(game1)
gamer.add_game(game2)


gamer.list_games()
gamer.get_total_play_time()


game1.add_play_time(2)
gamer.get_total_play_time()
</code></pre>

<p>In this example, the GamerAccount class uses composition to manage instances of the Game class. This allows the GamerAccount to keep track of owned games and total play times without inheriting from the Game class, promoting better modularity and encapsulation.</p>"""  # noqa: E501

        # Assert the HTML content matches expected HTML
        assert html_content == expected_html, \
            "The HTML output does not match the expected HTML structure."

    except exceptions.GoogleDriveFileNotFoundError:
        pytest.fail("Google Drive file not found; ensure the file ID is correct.")
    except exceptions.GoogleDrivePermissionError:
        pytest.fail("Insufficient permissions to access the Google Drive file.")
    except exceptions.GoogleDriveAPIError as e:
        pytest.fail(f"An unexpected API error occurred: {str(e)}")
