from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Text
from sqlalchemy.sql import func
import time
from models.base import Base

class Log(Base):
    """Model for storing application logs"""
    __tablename__ = 'logs'
    
    id = Column(Integer, primary_key=True)
    level = Column(String(10), nullable=False)  # INFO, WARNING, ERROR, DEBUG
    source = Column(String(50), nullable=False)  # Which part of the application
    message = Column(Text, nullable=False)
    details = Column(Text, nullable=True)  # For storing stack traces or additional data
    timestamp = Column(BigInteger, index=True, default=lambda: int(time.time()))
    
    def __repr__(self):
        return f"<Log(id={self.id}, level={self.level}, source={self.source}, timestamp={self.timestamp})>" 