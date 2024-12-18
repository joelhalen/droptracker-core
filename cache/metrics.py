from datetime import datetime, timedelta
import time
from typing import Dict, List, Optional
from cache import redis_client
import json

class MetricsTracker:
    def __init__(self):
        self.start_time = datetime.now()
        self.cache_ttl = 86400  # 24 hours
        
    def _get_cache_keys(self, metric_type: str) -> Dict[str, str]:
        """Get Redis keys for different time scales"""
        current_time = datetime.now()
        current_hour = f"{current_time.year}{current_time.month:02d}{current_time.day:02d}{current_time.hour:02d}"
        current_day = f"{current_time.year}{current_time.month:02d}{current_time.day:02d}"
        current_month = f"{current_time.year}{current_time.month:02d}"
        
        return {
            'total': f"metrics:{metric_type}:total",
            'hourly': f"metrics:{metric_type}:hourly:{current_hour}",
            'daily': f"metrics:{metric_type}:daily:{current_day}",
            'monthly': f"metrics:{metric_type}:monthly:{current_month}",
            'last_hour': f"metrics:{metric_type}:rolling:hour",
            'last_day': f"metrics:{metric_type}:rolling:day"
        }
    
    async def increment(self, metric_type: str) -> None:
        """Increment metrics across all time scales"""
        keys = self._get_cache_keys(metric_type)
        current_time = int(time.time())
        
        pipe = redis_client.pipeline()
        
        # Increment counters
        for key in keys.values():
            pipe.hincrby(key, "count", 1)
            pipe.hset(key, "last_updated", current_time)
        
        # Store timestamp for rolling window calculations
        pipe.lpush(f"metrics:{metric_type}:timestamps", current_time)
        pipe.ltrim(f"metrics:{metric_type}:timestamps", 0, 86400)  # Keep last 24 hours
        
        await pipe.execute()
    
    async def get_metrics(self, metric_type: str) -> Dict:
        """Get comprehensive metrics for all time scales"""
        keys = self._get_cache_keys(metric_type)
        current_time = int(time.time())
        
        # Get all stored metrics
        total = redis_client.hgetall(keys['total'])
        hourly = redis_client.hgetall(keys['hourly'])
        daily = redis_client.hgetall(keys['daily'])
        monthly = redis_client.hgetall(keys['monthly'])
        
        # Get timestamps for rolling calculations
        timestamps = redis_client.lrange(f"metrics:{metric_type}:timestamps", 0, -1)
        timestamps = [int(ts) for ts in timestamps]
        
        # Calculate rolling averages
        last_hour_count = len([ts for ts in timestamps if ts > current_time - 3600])
        last_day_count = len([ts for ts in timestamps if ts > current_time - 86400])
        
        return {
            "total": {
                "count": int(total.get("count", 0)),
                "avg_per_hour": self._calculate_average(int(total.get("count", 0)), self.start_time),
            },
            "current": {
                "hourly": int(hourly.get("count", 0)),
                "daily": int(daily.get("count", 0)),
                "monthly": int(monthly.get("count", 0))
            },
            "rolling": {
                "last_hour": {
                    "count": last_hour_count,
                    "avg_per_minute": last_hour_count / 60
                },
                "last_day": {
                    "count": last_day_count,
                    "avg_per_hour": last_day_count / 24
                }
            }
        }
    
    def _calculate_average(self, count: int, start_time: datetime) -> float:
        """Calculate average per hour since start time"""
        hours = (datetime.now() - start_time).total_seconds() / 3600
        return count / hours if hours > 0 else 0
    
    async def get_all_metrics(self) -> Dict:
        """Get metrics for all tracked types"""
        metric_types = ["drops", "logs", "achievements", "pbs"]
        return {
            metric_type: await self.get_metrics(metric_type)
            for metric_type in metric_types
        } 