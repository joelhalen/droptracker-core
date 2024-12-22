from datetime import datetime, timedelta
import time
from typing import Dict, List, Optional
from cache import redis_client
from sqlalchemy import Column, Integer, BigInteger
from models.base import Base
import json
import psutil
import os
from functools import lru_cache
from cache.stats import StatsTracker
from models.metrics import MetricSnapshot
from models.base import session
import asyncio

stats = StatsTracker()

class MetricsTracker:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MetricsTracker, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.start_time = stats.start_time
        self.cache_ttl = 86400
        self.process = psutil.Process(os.getpid())
        self._pending_snapshots = []
        self._snapshot_lock = asyncio.Lock()
        self._last_snapshot = 0
        self._last_metrics = {
            'drops': 0,
            'collections': 0,
            'pbs': 0,
            'achievements': 0,
            'missed': 0,
            'total': 0
        }
        self.snapshot_interval = 5
        self._initialized = True
    
    async def _snapshot_loop(self):
        """Periodically save snapshots to database with delta values"""
        while True:
            try:
                current_time = int(time.time())
                if current_time - self._last_snapshot >= self.snapshot_interval:
                    # Calculate deltas
                    current_metrics = {
                        'drops': stats.drops,
                        'collections': stats.logs,
                        'pbs': stats.pbs,
                        'achievements': stats.achievements,
                        'missed': stats.denied,
                        'total': stats.drops + stats.logs + stats.pbs + stats.achievements
                    }
                    
                    deltas = {
                        key: current_metrics[key] - self._last_metrics[key]
                        for key in current_metrics
                    }
                    
                    snapshot = MetricSnapshot(
                        drops=deltas['drops'],
                        collections=deltas['collections'],
                        pbs=deltas['pbs'],
                        achievements=deltas['achievements'],
                        missed=deltas['missed'],
                        total=deltas['total'],
                        timestamp=current_time
                    )
                    
                    session.add(snapshot)
                    try:
                        session.commit()
                        self._last_snapshot = current_time
                        self._last_metrics = current_metrics  # Update last metrics after successful commit
                    except Exception as e:
                        print(f"Error committing snapshot: {e}")
                        session.rollback()
                        
            except Exception as e:
                print(f"Error in snapshot loop: {e}")
            await asyncio.sleep(1)
    
    async def initialize(self):
        """Initialize async components"""
        if not hasattr(self, '_snapshot_task'):
            self._snapshot_task = asyncio.create_task(self._snapshot_loop())
    
    async def _create_snapshot(self):
        """Create a new snapshot of current metrics"""
        try:
            current_time = int(time.time())
            
            snapshot = MetricSnapshot(
                drops=stats.drops,
                collections=stats.logs,
                pbs=stats.pbs,
                achievements=stats.achievements,
                missed=stats.denied,
                total=stats.drops + stats.logs + stats.pbs + stats.achievements,
                timestamp=current_time
            )
            
            async with self._snapshot_lock:
                self._pending_snapshots.append(snapshot)
        except Exception as e:
            print(f"Error creating snapshot: {e}")
    
    async def _save_pending_snapshots(self):
        """Save all pending snapshots to database"""
        async with self._snapshot_lock:
            if not self._pending_snapshots:
                return
                
            try:
                session.bulk_save_objects(self._pending_snapshots)
                session.commit()
                self._pending_snapshots.clear()
            except Exception as e:
                print(f"Error saving snapshots: {e}")
                session.rollback()
    
    async def get_historical_data(self, hours: int = 24) -> Dict[str, List[int]]:
        """Get historical data from database"""
        cutoff = int(time.time()) - (hours * 3600)
        snapshots = session.query(MetricSnapshot)\
            .filter(MetricSnapshot.timestamp >= cutoff)\
            .order_by(MetricSnapshot.timestamp.asc())\
            .all()
        
        return {
            'drops': [s.drops for s in snapshots],
            'logs': [s.collections for s in snapshots],
            'achievements': [s.achievements for s in snapshots],
            'pbs': [s.pbs for s in snapshots],
            'missed': [s.missed for s in snapshots],
            'total': [s.total for s in snapshots],
            'timestamps': [s.timestamp for s in snapshots]
        }
    
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
        """Increment metrics and create snapshot"""
        keys = self._get_cache_keys(metric_type)
        current_time = int(time.time())
        
        pipe = redis_client.pipeline()
        
        # Increment counters
        for key in keys.values():
            pipe.hincrby(key, "count", 1)
            pipe.hset(key, "last_updated", current_time)
        
        # Store timestamp for rolling window calculations
        pipe.lpush(f"metrics:{metric_type}:timestamps", current_time)
        pipe.ltrim(f"metrics:{metric_type}:timestamps", 0, 86400)
        
        await pipe.execute()
        await self._create_snapshot()
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage statistics"""
        memory_info = self.process.memory_info()
        
        return {
            "rss": memory_info.rss / 1024 / 1024,  # RSS in MB
            "vms": memory_info.vms / 1024 / 1024,  # VMS in MB
            "percent": self.process.memory_percent(),
            "cpu_percent": self.process.cpu_percent(),
            "threads": len(self.process.threads()),
            "open_files": len(self.process.open_files()),
            "connections": len(self.process.connections()),
        }
    
    @lru_cache(maxsize=1)  
    def get_system_metrics(self) -> Dict[str, float]:
        """Get system-wide metrics"""
        return {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "swap_percent": psutil.swap_memory().percent,
        }
    
    async def get_metrics(self, metric_type: str) -> Dict:
        """Get comprehensive metrics with Redis caching"""
        current_time = int(time.time())
        cache_key = f"metrics:{metric_type}:cached_data"
        
        # Try to get cached data first
        cached_data = redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
        
        # Calculate metrics if not cached
        minutes_in_hour = min(60, (current_time - stats.start_time) / 60)
        hours_in_day = min(24, (current_time - stats.start_time) / 3600)
        
        # Get counts from StatsTracker timestamps for accuracy
        hourly_count = len([ts for ts in stats.timestamps[metric_type] 
                           if ts >= current_time - 3600])
        daily_count = len([ts for ts in stats.timestamps[metric_type] 
                          if ts >= current_time - 86400])
        
        # Get historical data with a single query
        cutoff = current_time - (24 * 3600)
        snapshots = session.query(MetricSnapshot)\
            .filter(MetricSnapshot.timestamp >= cutoff)\
            .order_by(MetricSnapshot.timestamp.desc())\
            .all()
        
        # Process historical data
        hour_buckets = [0] * 24
        for snapshot in snapshots:
            hour_index = (current_time - snapshot.timestamp) // 3600
            if hour_index < 24:
                match metric_type:
                    case 'drops': count = snapshot.drops
                    case 'logs': count = snapshot.collections
                    case 'achievements': count = snapshot.achievements
                    case 'pbs': count = snapshot.pbs
                    case 'denied': count = snapshot.missed
                    case _: count = 0
                hour_buckets[hour_index] += count
        
        metrics_data = {
            "total": {
                "count": getattr(stats, metric_type, 0),
                "avg_per_hour": daily_count / hours_in_day if hours_in_day > 0 else 0,
            },
            "current": {
                "hourly": hourly_count,
                "daily": daily_count,
                "monthly": getattr(stats, metric_type, 0)
            },
            "rolling": {
                "last_hour": {
                    "count": hourly_count,
                    "avg_per_minute": hourly_count / minutes_in_hour if minutes_in_hour > 0 else 0
                },
                "last_day": {
                    "count": daily_count,
                    "avg_per_hour": daily_count / hours_in_day if hours_in_day > 0 else 0
                }
            },
            "historical": {
                "hourly": list(reversed(hour_buckets))
            }
        }
        
        # Cache the result for 1 minute
        redis_client.setex(cache_key, 60, json.dumps(metrics_data))
        return metrics_data
    
    def _calculate_average(self, count: int, start_time: datetime) -> float:
        """Calculate average per hour since start time"""
        hours = (datetime.now() - start_time) / 3600
        return count / hours if hours > 0 else 0
    
    async def get_all_metrics(self) -> Dict:
        """Get metrics for all tracked types including system metrics"""
        metric_types = ["drops", "logs", "achievements", "pbs"]
        
        metrics_data = {
            metric_type: await self.get_metrics(metric_type)
            for metric_type in metric_types
        }
        
        # Add system metrics
        metrics_data["system"] = {
            "memory": self.get_memory_usage(),
            "system": self.get_system_metrics(),
            "uptime": {
                "start_time": stats.start_time,  # Unix timestamp
                "seconds": int(time.time()) - stats.start_time,
                "formatted": str(timedelta(seconds=int(time.time()) - stats.start_time))
            }
        }
        
        return metrics_data 
    
    def get_hourly_data(self, metric_type: str, hours: int = 24) -> List[int]:
        """Get hourly counts from database snapshots with optimized querying"""
        current_time = int(time.time())
        cutoff = current_time - (hours * 3600)
        
        # Get snapshots for the last 24 hours with a single optimized query
        snapshots = session.query(MetricSnapshot)\
            .filter(MetricSnapshot.timestamp >= cutoff)\
            .order_by(MetricSnapshot.timestamp.desc())\
            .all()
        
        # Initialize buckets for each hour
        hour_buckets = [0] * hours
        
        # Group snapshots by hour
        for snapshot in snapshots:
            hour_index = (current_time - snapshot.timestamp) // 3600
            if hour_index < hours:
                match metric_type:
                    case 'drops': count = snapshot.drops
                    case 'logs': count = snapshot.collections
                    case 'achievements': count = snapshot.achievements
                    case 'pbs': count = snapshot.pbs
                    case 'denied': count = snapshot.missed
                    case _: count = 0
                hour_buckets[hour_index] += count
        
        return list(reversed(hour_buckets))
    
