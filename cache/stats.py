import time
from typing import Dict, List


class StatsTracker:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StatsTracker, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.start_time = int(time.time())  # Unix timestamp
        self.drops = 0
        self.logs = 0
        self.achievements = 0
        self.pbs = 0
        self.denied = 0
        
        # Add time window tracking
        self.hourly_stats: Dict = {}
        self.daily_stats: Dict = {}
        self.monthly_stats: Dict = {}
        self.timestamps: Dict[str, List[int]] = {
            "drops": [],
            "logs": [],
            "achievements": [],
            "pbs": [],
            "denied": []
        }
        
        self._initialized = True
    
    def increment(self, stat_type: str) -> None:
        current_time = int(time.time())
        
        # Update total counts
        match stat_type.lower():
            case "drops":
                self.drops += 1
            case "logs":
                self.logs += 1
            case "achievements":
                self.achievements += 1
            case "pbs":
                self.pbs += 1
            case "denied":
                self.denied += 1
        
        # Store timestamp for rolling windows
        self.timestamps[stat_type].append(current_time)
        # Keep only last 24 hours of timestamps
        cutoff = current_time - 86400
        self.timestamps[stat_type] = [ts for ts in self.timestamps[stat_type] if ts > cutoff]
    
    def get_runtime(self) -> int:
        """Return runtime in seconds"""
        return int(time.time()) - self.start_time
    
    def get_stats_report(self) -> str:
        runtime = self.get_runtime()
        minutes = runtime / 60
        hours = minutes / 60
        return ""  # Placeholder for future implementation
