import asyncio
from typing import List, Optional
from datetime import datetime
from models.base import session
from models import Player
from utils.misc import get_player_cache

async def get_global_rankings(partition_date: Optional[datetime] = None) -> List[int]:
    """Get global rankings of all players based on their total loot value"""
    if partition_date is None:
        partition_date = datetime.now()
        
    players = session.query(Player.player_id).all()
    player_totals = []
    
    async def get_player_total(player_id: int):
        cache = get_player_cache(player_id)
        stats = await cache.get_player_stats(partition_date)
        if stats and "total" in stats:
            return (player_id, stats["total"]["total_value"])
        return (player_id, 0)
    
    tasks = [get_player_total(player[0]) for player in players]
    player_totals = await asyncio.gather(*tasks)
    
    rankings = sorted(player_totals, key=lambda x: x[1], reverse=True)
    return [player_id for player_id, _ in rankings] 