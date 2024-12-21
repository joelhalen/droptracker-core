from sqlalchemy import Column, Integer, BigInteger
from models.base import Base


class MetricSnapshot(Base):
    """Model for storing metric snapshots"""
    __tablename__ = 'metric_snapshots'
    
    id = Column(Integer, primary_key=True)
    drops = Column(Integer, default=0)
    collections = Column(Integer, default=0)
    pbs = Column(Integer, default=0)
    achievements = Column(Integer, default=0)
    missed = Column(Integer, default=0)
    total = Column(Integer, default=0)
    timestamp = Column(BigInteger, index=True)

    def __repr__(self):
        return f"<MetricSnapshot(id={self.id}, timestamp={self.timestamp}, total={self.total})>"