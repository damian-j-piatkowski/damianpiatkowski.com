from app.domain.blog_post import BlogPost


def test_create_blog_post(session):
    post = BlogPost(
        title='Test Post',
        content='This is a test post content',
        image_small='path/to/small/image.jpg',
        image_medium='path/to/medium/image.jpg',
        image_large='path/to/large/image.jpg'
    )
    session.add(post)
    session.commit()

    # Fetch the blog post from the database
    fetched_post = session.query(BlogPost).first()
    assert fetched_post is not None
    assert fetched_post.title == 'Test Post'
    assert fetched_post.content == 'This is a test post content'
    assert fetched_post.image_small == 'path/to/small/image.jpg'
    assert fetched_post.image_medium == 'path/to/medium/image.jpg'
    assert fetched_post.image_large == 'path/to/large/image.jpg'

def test_update_blog_post(session):
    post = BlogPost(
        title='Original Title',
        content='Original content',
        image_small='path/to/small/image.jpg',
        image_medium='path/to/medium/image.jpg',
        image_large='path/to/large/image.jpg'
    )
    session.add(post)
    session.commit()

    # Update the blog post
    post.title = 'Updated Title'
    post.content = 'Updated content'
    session.commit()

    # Fetch the updated blog post
    fetched_post = session.query(BlogPost).filter_by(title='Updated Title').first()
    assert fetched_post is not None
    assert fetched_post.title == 'Updated Title'
    assert fetched_post.content == 'Updated content'


def test_delete_blog_post(session):
    post = BlogPost(
        title='Post to be deleted',
        content='Content of the post to be deleted',
        image_small='path/to/small/image.jpg',
        image_medium='path/to/medium/image.jpg',
        image_large='path/to/large/image.jpg'
    )
    session.add(post)
    session.commit()

    # Delete the blog post
    session.delete(post)
    session.commit()

    # Verify the blog post has been deleted
    fetched_post = session.query(BlogPost).filter_by(title='Post to be deleted').first()
    assert fetched_post is None


def test_fetch_multiple_blog_posts(session):
    post1 = BlogPost(
        title='Post 1',
        content='Content of post 1',
        image_small='path/to/small/image1.jpg',
        image_medium='path/to/medium/image1.jpg',
        image_large='path/to/large/image1.jpg'
    )
    post2 = BlogPost(
        title='Post 2',
        content='Content of post 2',
        image_small='path/to/small/image2.jpg',
        image_medium='path/to/medium/image2.jpg',
        image_large='path/to/large/image2.jpg'
    )
    session.add(post1)
    session.add(post2)
    session.commit()

    # Fetch all blog posts
    fetched_posts = session.query(BlogPost).all()
    assert len(fetched_posts) == 2
    assert fetched_posts[0].title == 'Post 1'
    assert fetched_posts[1].title == 'Post 2'
