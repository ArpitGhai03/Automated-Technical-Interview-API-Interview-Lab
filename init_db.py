"""Create the database schema defined by the SQLAlchemy models.

Run once after starting Postgres:

    python init_db.py
"""

from database import Base, engine
import models  # noqa: F401  -- ensures models are registered with Base.metadata
from sqlalchemy import text, inspect


def main() -> None:
    print(f"Creating tables on {engine.url}...")
    Base.metadata.create_all(bind=engine)
    print("Done. Tables:", ", ".join(sorted(Base.metadata.tables)))
    
    # Add missing columns to existing tables (schema migration)
    with engine.connect() as conn:
        inspector = inspect(engine)
        
        # Check if test_results column exists in submissions table
        if 'submissions' in inspector.get_table_names():
            columns = [c['name'] for c in inspector.get_columns('submissions')]
            if 'test_results' not in columns:
                print("Adding missing test_results column...")
                conn.execute(text(
                    "ALTER TABLE submissions ADD COLUMN test_results JSON"
                ))
                conn.commit()
                print("Column test_results added successfully")


if __name__ == "__main__":
    main()
