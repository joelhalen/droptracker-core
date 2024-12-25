# models/submissions/personal_best.py
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean, String
from sqlalchemy.orm import relationship
from ..base import Base

class PersonalBestEntry(Base):
    """
    Stores kill-time data for users
    """
    __tablename__ = 'personal_best'
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey('players.player_id'))
    npc_id = Column(Integer, ForeignKey('npc_list.npc_id'))
    kill_time = Column(Integer, nullable=False)
    personal_best = Column(Integer, nullable=False)
    new_pb = Column(Boolean, default=False)
    plugin_version = Column(String(10), nullable=True)
    image_url = Column(String(150), nullable=True)

    player = relationship("Player", back_populates="pbs")
    notified_pb = relationship("NotifiedSubmission", back_populates="pb")