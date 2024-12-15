# models/users/player.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from ..base import Base
from ..associations import user_group_association

class Player(Base):
    """ 
    :param: wom_id: The player's WiseOldMan ID
    :param: player_name: The DISPLAY NAME of the player, exactly as it appears
    :param: user_id: The ID of the associated User object, if one exists
    :param: log_slots: Stored number of collected log slots
    :param: total_level: Account total level based on the last update with WOM.
    """
    __tablename__ = 'players'
    player_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    wom_id = Column(Integer, unique=True)
    account_hash = Column(String(100), nullable=True, unique=True)
    player_name = Column(String(20), index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    log_slots = Column(Integer)
    total_level = Column(Integer)
    date_added = Column(DateTime, default=func.now())
    date_updated = Column(DateTime, onupdate=func.now(), default=func.now())

    pbs = relationship("PersonalBestEntry", back_populates="player")
    cas = relationship("CombatAchievementEntry", back_populates="player")
    clogs = relationship("CollectionLogEntry", back_populates="player")
    user = relationship("User", back_populates="players")
    drops = relationship("Drop", back_populates="player")
    groups = relationship("Group", secondary=user_group_association, back_populates="players")

    def add_group(self, group):
        from ..base import session
        existing_association = session.query(user_group_association).filter_by(
            player_id=self.player_id, group_id=group.group_id).first()
        if self.user:
            tuser = self.user
            tuser.add_group(group)
        if not existing_association:
            self.groups.append(group)
            session.commit()