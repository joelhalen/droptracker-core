from models.base import session
from models import NpcList
from utils.logger import Logger

logger = Logger()

async def get_npc_id(npc_name: str) -> int:
    """Get the NPC ID for the passed NPC name"""
    try:
        npc = session.query(NpcList).filter(NpcList.npc_name == npc_name).first()
        return npc.npc_id if npc else None
    except Exception as e:
        logger.error(f"get_npc_id", "No stored NPC ID found for {npc_name}", e)
        return None

def format_number(num: float) -> str:   
    """Format numbers with K/M/B suffixes"""
    if num >= 1_000_000_000:
        return f"{num/1_000_000_000:.1f}B"
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    if num >= 1_000:
        return f"{num/1_000:.1f}K"
    return f"{num:.1f}"