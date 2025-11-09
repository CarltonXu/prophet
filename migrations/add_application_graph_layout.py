"""Add graph_layout column to applications table."""

from sqlalchemy import inspect
from sqlalchemy import text

from db import db


def upgrade():
    engine = db.engine
    inspector = inspect(engine)

    with engine.connect() as connection:
        columns = [column['name'] for column in inspector.get_columns('applications')]
        if 'graph_layout' not in columns:
            connection.execute(text('ALTER TABLE applications ADD COLUMN graph_layout JSON'))


def downgrade():
    # SQLite does not support dropping columns easily; no-op downgrade.
    pass

