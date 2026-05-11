from sqlalchemy import Column, Integer, Text, String, TIMESTAMP, func
from database import Base

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(Text, nullable=False)
    language = Column(String(20))
    status = Column(String(20), default="pending")
    output = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())