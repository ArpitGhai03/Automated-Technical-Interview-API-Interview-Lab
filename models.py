from sqlalchemy import Column, Integer, Text, String, TIMESTAMP, func, Float, JSON
from database import Base

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(Text, nullable=False)
    language = Column(String(20))
    status = Column(String(20), default="pending")
    output = Column(Text)
    runtime = Column(Float, nullable=True)
    test_passed = Column(Integer, nullable=True)
    test_total = Column(Integer, nullable=True)
    test_results = Column(JSON, nullable=True)  # Array of booleans for each test
    created_at = Column(TIMESTAMP, server_default=func.now())