# models/submissions/combat_achievement.py
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from sqlalchemy import func
from ..base import Base

class CombatAchievementEntry(Base):
    """
    :param: player_id: Player ID who received this achievement
    :param: task_name: The name of the task they completed
    """
    __tablename__ = 'combat_achievement'
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey('players.player_id'))
    task_name = Column(String(255), nullable=False)
    image_url = Column(String(255), nullable=True)
    plugin_version = Column(String(10), nullable=True)
    date_added = Column(DateTime, index=True, default=func.now())

    player = relationship("Player", back_populates="cas")
    notified_ca = relationship("NotifiedSubmission", back_populates="ca")