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
        
        # Add any columns missing from an existing submissions table.
        if 'submissions' in inspector.get_table_names():
            columns = [c['name'] for c in inspector.get_columns('submissions')]
            missing = {
                'runtime': "ALTER TABLE submissions ADD COLUMN runtime DOUBLE PRECISION",
                'test_passed': "ALTER TABLE submissions ADD COLUMN test_passed INTEGER",
                'test_total': "ALTER TABLE submissions ADD COLUMN test_total INTEGER",
                'test_results': "ALTER TABLE submissions ADD COLUMN test_results JSON",
                'problem_id': "ALTER TABLE submissions ADD COLUMN problem_id VARCHAR(64)",
            }
            for column, ddl in missing.items():
                if column not in columns:
                    print(f"Adding missing {column} column...")
                    conn.execute(text(ddl))
                    conn.commit()
                    print(f"Column {column} added successfully")


if __name__ == "__main__":
    main()
