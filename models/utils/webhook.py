# models/utils/webhook.py
from sqlalchemy import Column, Integer, String, DateTime, func
from ..base import Base

class Webhook(Base):
    __tablename__ = 'webhooks'
    webhook_id = Column(Integer, primary_key=True)
    webhook_url = Column(String(255), unique=True)
    date_added = Column(DateTime, default=func.now())
    date_updated = Column(DateTime, onupdate=func.now(), default=func.now())