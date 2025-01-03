# models/submissions/drop.py
import asyncio
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean, String
from sqlalchemy.orm import relationship
from sqlalchemy import func, event
from utils.misc import get_current_partition, get_player_cache
from ..base import Base

class Drop(Base):
    """
        :param: item_id
        :param: player_id
        :param: npc_id
        :param: value
        :param: quantity
        :param: image_url (nullable)
    """
    __tablename__ = 'drops'
    drop_id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey('items.item_id'), index=True)
    player_id = Column(Integer, ForeignKey('players.player_id'), index=True, nullable=False)
    date_added = Column(DateTime, index=True, default=func.now())
    npc_id = Column(Integer, ForeignKey('npc_list.npc_id'), index=True)
    date_updated = Column(DateTime, onupdate=func.now(), default=func.now())
    value = Column(Integer)
    quantity = Column(Integer)
    image_url = Column(String(150), nullable=True)
    plugin_version = Column(String(10), nullable=True)
    partition = Column(Integer, default=get_current_partition, index=True)
    
    player = relationship("Player", back_populates="drops")
    notified_drops = relationship("NotifiedSubmission", back_populates="drop")


@event.listens_for(Drop, 'after_insert')
def after_drop_insert(mapper, connection, target):
    from cogs.qualifier import check_drop
    asyncio.create_task(check_drop(target))