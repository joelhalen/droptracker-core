
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship
from models.base import Base


class NotifiedSubmission(Base):
    """
    Drops that have exceeded the necessary threshold to have a notification
    sent to a Discord channel are stored in this table to allow modifications
    to be made to the message, drop, etc.
    """
    __tablename__ = 'notified'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    channel_id = Column(String(35), nullable=False)
    message_id = Column(String(35))
    group_id = Column(Integer, ForeignKey('groups.group_id'), nullable=False)
    status = Column(String(15))  # 'sent', 'removed', or 'pending'
    date_added = Column(DateTime, index=True, default=func.now())
    date_updated = Column(DateTime, onupdate=func.now(), default=func.now())
    edited_by = Column(Integer, ForeignKey('users.user_id'), nullable=True)
    
    # Nullable foreign keys to allow only one relationship to be defined
    drop_id = Column(Integer, ForeignKey('drops.drop_id'), nullable=True)
    clog_id = Column(Integer, ForeignKey('collection.log_id'), nullable=True)
    ca_id = Column(Integer, ForeignKey('combat_achievement.id'), nullable=True)
    pb_id = Column(Integer, ForeignKey('personal_best.id'), nullable=True)

    # Relationships
    drop = relationship("Drop", back_populates="notified_drops")
    clog = relationship("CollectionLogEntry", back_populates="notified_clog")
    ca = relationship("CombatAchievementEntry", back_populates="notified_ca")
    pb = relationship("PersonalBestEntry", back_populates="notified_pb")

    def __init__(self, channel_id: str, 
                 message_id: str, 
                 group_id: int,
                 status: str, 
                 drop=None, 
                 clog=None, 
                 ca=None, 
                 pb=None):
        """
        Ensure that only one of drop, clog, ca, or pb can be defined.
        """
        if sum([bool(drop), bool(clog), bool(ca), bool(pb)]) > 1:
            raise ValueError("Only a single association can be provided to a NotifiedSubmission.")
        self.channel_id = channel_id
        self.message_id = message_id
        self.group_id = group_id
        self.status = status
        self.drop = drop
        self.clog = clog
        self.ca = ca
        self.pb = pb

