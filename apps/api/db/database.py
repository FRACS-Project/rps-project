"""Database engine and sessions.

Builds the PostgreSQL engine from `DATABASE_URL` and provides the
per-request session dependency. Tables are created with `create_all`
(no migrations yet).
"""

import os
from sqlalchemy import event
from sqlmodel import SQLModel, create_engine, Session

# DATABASE WITH SQLITE
#
# sqlite_file_name = "rps_db.db"
# sqlite_url = f"sqlite:///{sqlite_file_name}"

# connect_args = {"check_same_thread": False}
# engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


# @event.listens_for(engine, "connect")
# def _set_sqlite_pragma(dbapi_connection, connection_record):
#     cursor = dbapi_connection.cursor()
#     cursor.execute("PRAGMA foreign_keys=ON")
#     cursor.close()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(DATABASE_URL, echo=True, pool_pre_ping=True)

def create_db_and_tables():
    """Create all tables that do not exist yet. Does not alter existing ones."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """FastAPI dependency: yield a database session for one request."""
    with Session(engine) as session:
        yield session
