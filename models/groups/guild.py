# models/groups/guild.py
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship
from ..base import Base

class Guild(Base):
    """
    :param: guild_id: Discord guild_id, string-formatted.
    :param: group_id: Respective group_id, if one already exists
    :param: date_added: Time the guild was generated
    :param: initialized: Status of the guild's registration
    """
    __tablename__ = 'guilds'
    guild_id = Column(String(255), primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.group_id'), nullable=True)
    date_added = Column(DateTime, default=func.now())
    date_updated = Column(DateTime, onupdate=func.now(), default=func.now())
    initialized = Column(Boolean, default=False)

    group = relationship("Group", back_populates="guild", single_parent=True, uselist=False)