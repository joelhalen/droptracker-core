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
default_batch_size = int(os.getenv("BATCH_SIZE", 5))

class DropProcessor:
    def __init__(self, batch_size: int = default_batch_size):
        self.batch_size = batch_size
        self.pending_drops: Dict[int, deque] = {}  # player_id -> deque of drops
        self.session = session
    
    async def process_drop(self, embed: interactions.Embed, player_data: Player):
        try:
            player = self.session.merge(player_data)
            
            drop_data = await self._parse_embed(embed)
            if not drop_data:
                return
                
            if player.player_id not in self.pending_drops:
                self.pending_drops[player.player_id] = deque(maxlen=self.batch_size)
            # Convert values and create drop
            try:
                drop = Drop(
                    item_id=int(drop_data['item_id']),
                    value=int(drop_data['value']),
                    quantity=int(drop_data['quantity']),
                    npc_id=int(drop_data['npc_id']),
                    player_id=int(player.player_id),
                    plugin_version=drop_data.get('plugin_version'),
                    partition=get_current_partition(),
                    image_url=embed.image.url if embed.image else None
                )
                print("Drop created:", drop)
                
                self.pending_drops[player.player_id].append(drop)

                if len(self.pending_drops[player.player_id]) >= self.batch_size:
                    await self._process_batch(player.player_id)

            except Exception as e:
                logger.error("process_drop", 
                    f"Drop creation error: {str(e)}. "
                    f"Player ID: {player.player_id} (type: {type(player.player_id)})")
                return

        except Exception as e:
            logger.error("process_drop", f"Error processing drop: {str(e)}")
            self.session.rollback()
    
    async def _parse_embed(self, embed: interactions.Embed) -> Dict:
        """Parse embed fields into drop data"""
        drop_data = {}
        
        
        for field in embed.fields:
            match field.name:
                case "source":
                    npc_name = field.value
                    npc_id = await get_npc_id(npc_name)
                    if not npc_id:
                        logger.error("parse_embed", f"Could not find NPC ID for {npc_name}")
                        return None
                    drop_data['npc_id'] = npc_id
                case "id":
                    drop_data['item_id'] = int(field.value)
                case "value":
                    drop_data['value'] = int(field.value)
                case "quantity":
                    drop_data['quantity'] = int(field.value)
                case "type" if field.value in ["npc", "collection_log", "combat_achievement"]:
                    drop_data['source_type'] = field.value
                case "item":
                    drop_data['item_name'] = field.value
                case "p_v":
                    drop_data['plugin_version'] = field.value
        
        # Validate we have all required fields
        required_fields = ['item_id', 'value', 'quantity', 'npc_id', 'source_type']
        missing_fields = [field for field in required_fields if field not in drop_data]
        
        if missing_fields:
            logger.error("parse_embed", 
                f"Missing required fields: {missing_fields}. "
                f"Parsed data: {drop_data}")
            return None
        
        return drop_data
    
    async def _process_batch(self, player_id: int):
        """Process a batch of drops for a player"""
        if not self.pending_drops.get(player_id):
            return
            
        drops_to_process = list(self.pending_drops[player_id])
        self.pending_drops[player_id].clear()
        
        try:
            self.session.add_all(drops_to_process)
            self.session.commit()
            
        except Exception as e:
            logger.error("process_batch", f"Error processing batch for player {player_id}: {e}")
            self.session.rollback()
    
    async def flush_all(self):
        """Process all remaining drops in the queues"""
        for player_id in list(self.pending_drops.keys()):
            if self.pending_drops[player_id]:
                await self._process_batch(player_id)