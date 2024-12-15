# models/utils/item_list.py
from sqlalchemy import Column, Integer, String, Boolean
from ..base import Base

class ItemList(Base):
    __tablename__ = 'items'
    item_id = Column(Integer, primary_key=True, nullable=False, index=True)
    item_name = Column(String(125), index=True)
    noted = Column(Boolean, nullable=False)