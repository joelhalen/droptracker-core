import interactions
from models import Player, Drop
from models.base import session
from typing import List, Dict
from collections import deque
from utils.misc import get_current_partition, get_player_cache
from utils.num import get_npc_id
from utils.logger import Logger
from cache.player_stats import PlayerStatsCache
import os
from dotenv import load_dotenv

load_dotenv()

logger = Logger()
default_batch_size = os.getenv("BATCH_SIZE", 5)

class DropProcessor:
    def __init__(self, batch_size: int = default_batch_size):
        self.batch_size = batch_size
        self.pending_drops: Dict[int, deque] = {}  # player_id -> deque of drops
    
    async def process_drop(self, embed: interactions.Embed, player_data: Player):
        """Process a single drop and add it to the batch queue"""
        logger.info("process_drop", f"Processing drop for player {player_data.player_id}")
        try:
            logger.info("process_drop", f"Parsing embed for player {player_data.player_id}")
            drop_data = await self._parse_embed(embed)
            if not drop_data:
                logger.error("process_drop", f"Failed to parse embed for player {player_data.player_id}")
                return
                
            # Initialize queue for this player if it doesn't exist
            if player_data.player_id not in self.pending_drops:
                self.pending_drops[player_data.player_id] = deque(maxlen=self.batch_size)
                logger.info("process_drop", f"Initialized queue for player {player_data.player_id}")

            # Add drop to queue
            drop = Drop(
                item_id=drop_data['item_id'],
                value=drop_data['value'],
                quantity=drop_data['quantity'],
                npc_id=drop_data['npc_id'],
                player_id=player_data.player_id,
                source_type=drop_data['source_type'],
                authed=True,
                partition=get_current_partition(),
            )
            
            self.pending_drops[player_data.player_id].append(drop)
            logger.info("process_drop", f"Added drop to queue for player {player_data.player_id}")
            # Process batch if we've reached batch size
            if len(self.pending_drops[player_data.player_id]) >= self.batch_size:
                await self._process_batch(player_data.player_id)
                logger.info("process_drop", f"Processed batch for player {player_data.player_id}")
        except Exception as e:
            logger.error("process_drop", f"Error processing drop: {e}")
    
    async def _parse_embed(self, embed: interactions.Embed) -> Dict:
        """Parse embed fields into drop data"""
        drop_data = {}
        
        for field in embed.fields:
            if field.name == "source":
                npc_name = field.value
                npc_id = await get_npc_id(npc_name)
                if not npc_id:
                    return None
                drop_data['npc_id'] = npc_id
            elif field.name == "id":
                drop_data['item_id'] = field.value
            elif field.name == "value":
                drop_data['value'] = field.value
            elif field.name == "quantity":
                drop_data['quantity'] = field.value
            elif field.name == "type":
                drop_data['source_type'] = field.value
            elif field.name == "item":
                drop_data['item_name'] = field.value
        print("returning", drop_data)
        return drop_data
    
    async def _process_batch(self, player_id: int):
        """Process a batch of drops for a player"""
        if not self.pending_drops.get(player_id):
            return
            
        drops_to_process = list(self.pending_drops[player_id])
        self.pending_drops[player_id].clear()
        
        try:
            session.add_all(drops_to_process)
            session.commit()
            
            # Update player cache after successful batch insert
            player_cache = get_player_cache(player_id)
            await player_cache.rebuild_cache_sync()
            
            logger.info("process_batch", 
                       f"Successfully processed batch of {len(drops_to_process)} drops for player {player_id}")
            
        except Exception as e:
            logger.error("process_batch", f"Error processing batch for player {player_id}: {e}")
            session.rollback()
    
    async def flush_all(self):
        """Process all remaining drops in the queues"""
        for player_id in list(self.pending_drops.keys()):
            if self.pending_drops[player_id]:
                await self._process_batch(player_id)