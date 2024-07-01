from sqlalchemy.orm import registry
from app.models import Log, BlogPost
from app.schema import logs, blog_posts

def start_mappers():
    mapper_registry = registry()

    mappings = {
        Log: logs,
        BlogPost: blog_posts,
    }

    for model, schema in mappings.items():
        mapper_registry.map_imperatively(model, schema)
