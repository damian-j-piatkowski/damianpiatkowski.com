from sqlalchemy.orm import registry

from app.domain.blog_post import BlogPost
from app.models.tables.blog_post import blog_posts

mapper_registry = registry()


def start_mappers(app):
    if not app.config.get('MAPPERS_INITIALIZED', False):
        mappings = {
            BlogPost: blog_posts,
        }

        for model, schema in mappings.items():
            mapper_registry.map_imperatively(model, schema)

        app.config['MAPPERS_INITIALIZED'] = True
