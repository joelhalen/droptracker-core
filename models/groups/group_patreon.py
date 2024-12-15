# models/groups/group_patreon.py
from sqlalchemy import Column, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from ..base import Base

class GroupPatreon(Base):
    __tablename__ = 'group_patreon'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    group_id = Column(Integer, ForeignKey('groups.group_id'), nullable=True)
    patreon_tier = Column(Integer, nullable=False)  # A user needs to be tier 2 
    date_added = Column(DateTime, default=func.now())
    date_updated = Column(DateTime, onupdate=func.now(), default=func.now())

    user = relationship("User", back_populates="group_patreon")
    group = relationship("Group", back_populates="group_patreon")