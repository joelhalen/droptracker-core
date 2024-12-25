# models/submissions/collection_log.py
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from sqlalchemy import func
from ..base import Base

class CollectionLogEntry(Base):
    """ 
    :param: item_id: The item ID for the item the user received
    :param: source: The NPC or source name that the drop was received from
    :param: player_id: The ID of the player who received the drop
    :param: reported_slots: The total log slots the user had when the submission arrived
    """
    __tablename__ = 'collection'
    log_id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, index=True, nullable=False)
    npc_id = Column(Integer, ForeignKey('npc_list.npc_id'), nullable=False)
    player_id = Column(Integer, ForeignKey('players.player_id'), index=True, nullable=False)
    reported_slots = Column(Integer)
    image_url = Column(String(255), nullable=True)
    date_added = Column(DateTime, index=True, default=func.now())
    plugin_version = Column(String(10), nullable=True)
    date_updated = Column(DateTime, onupdate=func.now(), default=func.now())

    player = relationship("Player", back_populates="clogs")
    notified_clog = relationship("NotifiedSubmission", back_populates="clog")