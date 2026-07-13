"""SQLAlchemy Core schema definition for the users table.

This module models the relational layer for administrative identity records,
safeguarding unique system handles and cryptographic validation metrics
for single-user environment security boundaries.

Columns:
    id (Integer): Primary key with automatic incrementation.
    username (String): Unique canonical system identification handle.
    password_hash (String): The cryptographically hashed password digest string
        (e.g., bcrypt/scrypt variant outputs).

Data Lifecycle Schema Examples:

    1. Required Insertion Payload:
       {
           "username": "admin_damian",
           "password_hash": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Bw59G..."
       }

    2. Resulting Complete Database Record:
       {
           "id": 1,
           "username": "admin_damian",
           "password_hash": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Bw59G..."
       }
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Table
)

from app.models.base import metadata

users = Table(
    'users', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column(
        'username',
        String(50),
        nullable=False,
        unique=True
    ),
    Column(
        'password_hash',
        String(255),
        nullable=False
    )
)
