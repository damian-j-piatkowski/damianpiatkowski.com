from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from app.api_schemas.blog_post_schema import BlogPostSchema
from app.domain.blog_post import BlogPost

blog_bp = Blueprint('blog', __name__)


@blog_bp.route('/api/blog_post', methods=['POST'])
def create_blog_post():
    data = request.get_json()
    schema = BlogPostSchema()

    try:
        validated_data = schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    blog_post = BlogPost(
        title=validated_data['title'],
        content=validated_data['content'],
        image_small=validated_data['image_small'],
        image_medium=validated_data['image_medium'],
        image_large=validated_data['image_large']
    )

    # Save the blog post to the database (using your ORM)
    # ...

    return jsonify(schema.dump(blog_post)), 201


@blog_bp.route('/api/blog_posts', methods=['GET'])
def get_blog_posts():
    # Retrieve blog posts from the database (using your ORM)
    blog_posts = [
        BlogPost(
            title="Sample Post 1",
            content="Content for post 1",
            image_small="/path/to/small1.jpg",
            image_medium="/path/to/medium1.jpg",
            image_large="/path/to/large1.jpg"
        ),
        BlogPost(
            title="Sample Post 2",
            content="Content for post 2",
            image_small="/path/to/small2.jpg",
            image_medium="/path/to/medium2.jpg",
            image_large="/path/to/large2.jpg"
        ),
    ]

    schema = BlogPostSchema(many=True)
    return jsonify(schema.dump(blog_posts)), 200
