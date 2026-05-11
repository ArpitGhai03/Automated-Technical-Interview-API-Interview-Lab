"""Create the database schema defined by the SQLAlchemy models.

Run once after starting Postgres:

    python init_db.py
"""

from database import Base, engine
import models  # noqa: F401  -- ensures models are registered with Base.metadata


def main() -> None:
    print(f"Creating tables on {engine.url}...")
    Base.metadata.create_all(bind=engine)
    print("Done. Tables:", ", ".join(sorted(Base.metadata.tables)))


if __name__ == "__main__":
    main()
