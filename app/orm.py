"""Classical / Imperative ORM Mapper Registration.

This module is responsible for bridging the pure business domain models with the 
relational database schemas, maintaining a strict Clean Architecture boundary.

Why this module exists (Dependency Inversion):
--------------------------------------------
In typical Active Record patterns (like SQLAlchemy's Declarative Base), domain classes 
are forced to inherit from database-specific classes, coupling business logic tightly 
to the persistence framework.

By using Imperative (or "Classical") Mappings via SQLAlchemy's `registry`, our 
domain models (e.g., DictionaryWord, User) remain completely pure:
- They do not import SQLAlchemy or any other framework.
- They have no knowledge of database types, foreign keys, or tables.
- They can be tested in pure Python without mocking database dependencies.

This module acts as the "glue" that binds them together at application startup.

How Mappings are Structured:
----------------------------
1. Simple/Independent Mappings: Models without relationships are mapped in a simple
   loop to minimize boilerplate code.
2. Relational Mappings: Models containing foreign keys or multi-table relationships
   must be mapped explicitly. We declare relationship behaviors (cascades, lazy loading,
   and secondary association tables) here to bridge the database logic to clean Python 
   collections.
"""

from sqlalchemy.orm import registry, relationship

# --- Domain Models ---
from app.domain.blog_post import BlogPost
from app.domain.dictionary_example import DictionaryExample
from app.domain.dictionary_source import DictionarySource
from app.domain.dictionary_word import DictionaryWord
from app.domain.han_viet_root import HanVietRoot
from app.domain.user import User
# --- Table Schemas ---
from app.models.tables.blog_post import blog_posts
from app.models.tables.dictionary_example import dictionary_examples
from app.models.tables.dictionary_source import dictionary_sources
from app.models.tables.dictionary_word import dictionary_words
from app.models.tables.han_viet_root import han_viet_roots
from app.models.tables.user import users
from app.models.tables.word_han_viet_association import word_han_viet_association

# Initialize the registry to track classical model mappings
mapper_registry = registry()


def start_mappers(app):
    """Imperatively maps all domain entities to physical database tables.

    This function is executed during application initialization. It guards
    against duplicate initialization by checking the 'MAPPERS_INITIALIZED' flag.
    """
    if not app.config.get('MAPPERS_INITIALIZED', False):

        # 1. Loop-mapped simple entities (Zero relationships / foreign keys)
        simple_mappings = {
            BlogPost: blog_posts,
            User: users,
            HanVietRoot: han_viet_roots,
            DictionarySource: dictionary_sources,
        }

        for model, schema in simple_mappings.items():
            mapper_registry.map_imperatively(model, schema)

        # 2. Explicitly-mapped relational entities

        # Map DictionaryExample (Many-to-One relationship to DictionarySource)
        mapper_registry.map_imperatively(
            DictionaryExample,
            dictionary_examples,
            properties={
                'source': relationship(
                    DictionarySource,
                    lazy='joined',
                    uselist=False
                )
            }
        )

        # Map DictionaryWord (One-to-Many to Examples, Many-to-Many to Roots)
        mapper_registry.map_imperatively(
            DictionaryWord,
            dictionary_words,
            properties={
                # Delete related examples from DB when the parent Word is removed
                'examples': relationship(
                    DictionaryExample,
                    cascade='all, delete-orphan',
                    lazy='select',
                    order_by=dictionary_examples.c.created_at.asc()
                ),
                # Many-to-Many mapping routed through the secondary association table
                'han_viet_roots': relationship(
                    HanVietRoot,
                    secondary=word_han_viet_association,
                    lazy='select'
                )
            }
        )

        app.config['MAPPERS_INITIALIZED'] = True
