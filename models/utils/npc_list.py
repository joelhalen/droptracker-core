# models/utils/npc_list.py
from sqlalchemy import Column, Integer, String
from ..base import Base

class NpcList(Base):
    """
    Stores the list of valid NPCs that are 
    being tracked individually for ranking purposes
    :param: npc_id: ID of the NPC based on OSRS Reboxed
    :param: npc_name: Name of the NPC based on OSRS Reboxed
    """
    __tablename__ = 'npc_list'
    npc_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    npc_name = Column(String(60), nullable=False)