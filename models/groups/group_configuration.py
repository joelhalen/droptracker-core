# models/groups/group_configuration.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import LONGTEXT
from ..base import Base

class GroupConfiguration(Base):
    __tablename__ = 'group_configurations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey('groups.group_id'), nullable=False)
    config_key = Column(String(60), nullable=False)
    config_value = Column(String(255), nullable=False)
    long_value = Column(LONGTEXT, nullable=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    group = relationship("Group", back_populates="configurations")