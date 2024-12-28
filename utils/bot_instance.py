from typing import Optional
from interactions import Client

class BotInstanceManager:
    _instance = None
    _bot: Optional[Client] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BotInstanceManager, cls).__new__(cls)
        return cls._instance

    @classmethod
    def set_bot(cls, bot: Client):
        cls._bot = bot

    @classmethod
    def get_bot(cls) -> Optional[Client]:
        return cls._bot

# Create a singleton instance
bot_manager = BotInstanceManager()