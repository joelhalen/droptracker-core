from datetime import datetime
import time
from sqlalchemy import func
from cache import redis_client
from models.base import session
from models.submissions import Drop
from typing import Dict, Optional, List
import json

class PlayerStatsCache:
    def __init__(self):
        self.cache_ttl = 3600  # 1 hour cache TTL
    
    def _get_cache_keys(self, player_id: int, partition_date: Optional[datetime] = None) -> Dict[str, str]:
        """Return all related cache keys for a player, optionally for a specific partition"""
        base_keys = {
            'total': f"player:{player_id}:total",  # Overall totals
            'stats': f"player:{player_id}:stats",
            'items': f"player:{player_id}:items",
            'bosses': f"player:{player_id}:bosses",
        }
        
        if partition_date:
            partition = f"{partition_date.year}:{partition_date.month:02d}"
            return {
                'total': base_keys['total'],  # Keep total key unchanged
                'stats': f"{base_keys['stats']}:{partition}",
                'items': f"{base_keys['items']}:{partition}",
                'bosses': f"{base_keys['bosses']}:{partition}",
            }
        return base_keys
    
    async def update_player_stats(self, drop: Drop) -> None:
        """Update all player stats in Redis when a new drop is received"""
        # Get both total and partition-specific keys
        total_keys = self._get_cache_keys(drop.player_id)
        partition_keys = self._get_cache_keys(drop.player_id, drop.date_added)
        current_time = int(time.time())
        
        pipe = redis_client.pipeline()
        
        # Update total stats
        pipe.hincrby(total_keys['total'], "total_value", drop.value)
        pipe.hincrby(total_keys['total'], "total_drops", 1)
        pipe.hset(total_keys['total'], "last_updated", current_time)
        
        # Update partition-specific general stats
        pipe.hincrby(partition_keys['stats'], "total_value", drop.value)
        pipe.hincrby(partition_keys['stats'], "total_drops", 1)
        pipe.hset(partition_keys['stats'], "last_updated", current_time)
        
        # Update partition-specific item stats
        item_key = f"{drop.item_id}"
        pipe.hincrby(partition_keys['items'], f"{item_key}:quantity", drop.quantity)
        pipe.hincrby(partition_keys['items'], f"{item_key}:value", drop.value)
        
        # Update partition-specific boss stats
        if drop.npc_id:
            boss_key = f"{drop.npc_id}"
            pipe.hincrby(partition_keys['bosses'], f"{boss_key}:drops", 1)
            pipe.hincrby(partition_keys['bosses'], f"{boss_key}:value", drop.value)
        
        # Set TTL for all keys
        for key in [*total_keys.values(), *partition_keys.values()]:
            pipe.expire(key, self.cache_ttl)
        
        await pipe.execute()
    
    async def remove_drop(self, drop: Drop) -> None:
        """Remove a specific drop from both total and partition-specific cache"""
        total_keys = self._get_cache_keys(drop.player_id)
        partition_keys = self._get_cache_keys(drop.player_id, drop.date_added)
        
        pipe = redis_client.pipeline()
        
        # Remove from total stats
        pipe.hincrby(total_keys['total'], "total_value", -drop.value)
        pipe.hincrby(total_keys['total'], "total_drops", -1)
        
        # Remove from partition-specific general stats
        pipe.hincrby(partition_keys['stats'], "total_value", -drop.value)
        pipe.hincrby(partition_keys['stats'], "total_drops", -1)
        
        # Remove from partition-specific item stats
        item_key = f"{drop.item_id}"
        pipe.hincrby(partition_keys['items'], f"{item_key}:quantity", -drop.quantity)
        pipe.hincrby(partition_keys['items'], f"{item_key}:value", -drop.value)
        
        # Remove from partition-specific boss stats
        if drop.npc_id:
            boss_key = f"{drop.npc_id}"
            pipe.hincrby(partition_keys['bosses'], f"{boss_key}:drops", -1)
            pipe.hincrby(partition_keys['bosses'], f"{boss_key}:value", -drop.value)
        
        await pipe.execute()
    
    async def invalidate_cache(self, player_id: int) -> None:
        """Completely remove all cached data for a player"""
        keys = self._get_cache_keys(player_id)
        await redis_client.delete(*keys.values())
    
    async def rebuild_cache(self, player_id: int) -> None:
        """Rebuild all cache data from the database, including partitioned data"""
        await self.invalidate_cache(player_id)
        
        # Fetch all drops for the player
        drops = session.query(Drop).filter(Drop.player_id == player_id).all()
        
        # Initialize tracking dictionaries
        total_stats = {"value": 0, "drops": 0}
        partitioned_stats = {}
        
        for drop in drops:
            # Update total stats
            total_stats["value"] += drop.value
            total_stats["drops"] += 1
            
            # Get partition key
            partition = f"{drop.date_added.year}:{drop.date_added.month:02d}"
            
            # Initialize partition if needed
            if partition not in partitioned_stats:
                partitioned_stats[partition] = {
                    "stats": {"value": 0, "drops": 0},
                    "items": {},
                    "bosses": {}
                }
            
            # Update partition stats
            part_stats = partitioned_stats[partition]
            part_stats["stats"]["value"] += drop.value
            part_stats["stats"]["drops"] += 1
            
            # Update item stats
            if drop.item_id not in part_stats["items"]:
                part_stats["items"][drop.item_id] = {"quantity": 0, "value": 0}
            part_stats["items"][drop.item_id]["quantity"] += drop.quantity
            part_stats["items"][drop.item_id]["value"] += drop.value
            
            # Update boss stats
            if drop.npc_id:
                if drop.npc_id not in part_stats["bosses"]:
                    part_stats["bosses"][drop.npc_id] = {"drops": 0, "value": 0}
                part_stats["bosses"][drop.npc_id]["drops"] += 1
                part_stats["bosses"][drop.npc_id]["value"] += drop.value
        
        # Store everything in Redis
        pipe = redis_client.pipeline()
        
        # Store total stats
        total_keys = self._get_cache_keys(player_id)
        pipe.hset(total_keys['total'], mapping={
            "total_value": total_stats["value"],
            "total_drops": total_stats["drops"],
            "last_updated": int(time.time())
        })
        
        # Store partitioned stats
        for partition, stats in partitioned_stats.items():
            year, month = partition.split(":")
            partition_date = datetime(int(year), int(month), 1)
            partition_keys = self._get_cache_keys(player_id, partition_date)
            
            # Store partition general stats
            pipe.hset(partition_keys['stats'], mapping={
                "total_value": stats["stats"]["value"],
                "total_drops": stats["stats"]["drops"],
                "last_updated": int(time.time())
            })
            
            # Store partition item stats
            for item_id, item_stats in stats["items"].items():
                pipe.hset(partition_keys['items'], f"{item_id}:quantity", item_stats["quantity"])
                pipe.hset(partition_keys['items'], f"{item_id}:value", item_stats["value"])
            
            # Store partition boss stats
            for npc_id, boss_stats in stats["bosses"].items():
                pipe.hset(partition_keys['bosses'], f"{npc_id}:drops", boss_stats["drops"])
                pipe.hset(partition_keys['bosses'], f"{npc_id}:value", boss_stats["value"])
            
            # Set TTL for partition keys
            for key in partition_keys.values():
                pipe.expire(key, self.cache_ttl)
        
        # Set TTL for total keys
        for key in total_keys.values():
            pipe.expire(key, self.cache_ttl)
        
        await pipe.execute()
    
    async def get_player_stats(self, player_id: int, partition_date: Optional[datetime] = None) -> Optional[Dict]:
        """Get complete player stats from cache or compute from database"""
        keys = self._get_cache_keys(player_id, partition_date)
        
        # Try cache first
        cached_total = redis_client.hgetall(keys['total'])
        cached_stats = redis_client.hgetall(keys['stats'])
        cached_items = redis_client.hgetall(keys['items'])
        cached_bosses = redis_client.hgetall(keys['bosses'])
        
        if cached_total:  # Only check total as it's always present
            result = {
                "total": {
                    "total_value": int(cached_total["total_value"]),
                    "total_drops": int(cached_total["total_drops"]),
                    "last_updated": int(cached_total["last_updated"])
                }
            }
            
            if partition_date:
                result["partition"] = {
                    "general": {
                        "total_value": int(cached_stats.get("total_value", 0)),
                        "total_drops": int(cached_stats.get("total_drops", 0)),
                        "last_updated": int(cached_stats.get("last_updated", 0))
                    },
                    "items": self._parse_cached_items(cached_items),
                    "bosses": self._parse_cached_bosses(cached_bosses)
                }
            
            return result
        
        # Cache miss - rebuild cache and return
        await self.rebuild_cache(player_id)
        return await self.get_player_stats(player_id, partition_date)
    
    def _parse_cached_items(self, cached_items: Dict) -> Dict:
        """Parse raw cached item data into structured format"""
        items = {}
        for key, value in cached_items.items():
            item_id, stat_type = key.split(':')
            if item_id not in items:
                items[item_id] = {}
            items[item_id][stat_type] = int(value)
        return items
    
    def _parse_cached_bosses(self, cached_bosses: Dict) -> Dict:
        """Parse raw cached boss data into structured format"""
        bosses = {}
        for key, value in cached_bosses.items():
            npc_id, stat_type = key.split(':')
            if npc_id not in bosses:
                bosses[npc_id] = {}
            bosses[npc_id][stat_type] = int(value)
        return bosses