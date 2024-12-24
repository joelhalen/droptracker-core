import time
import interactions
from datetime import datetime
from typing import Optional, Tuple
from utils.logger import Logger

logger = Logger()

def get_player_cache(player_id: int):
    """
    Lazy import to get PlayerStatsCache instance for a player
    
    Args:
        player_id: The ID of the player to get cache for
        
    Returns:
        PlayerStatsCache instance for the specified player
    """
    from cache.player_stats import PlayerStatsCache
    return PlayerStatsCache.get_instance(player_id)

def get_partition(date: Optional[datetime] = None) -> Tuple[int, str]:
    if not date:
        date = datetime.now()
        
    numeric_partition = date.year * 100 + date.month
    formatted_partition = f"{date.year}:{date.month:02d}"
    
    return numeric_partition, formatted_partition

def get_current_partition() -> int:
    numeric_partition, _ = get_partition()
    print("Returning numeric partition:", numeric_partition)
    return numeric_partition

async def get_command_id(bot: interactions.Client, command_name: str):
    try:
        commands = bot.application_commands
        if commands:
            for command in commands:
                cmd_name = command.get_localised_name("en")
                if cmd_name == command_name:
                    return command.cmd_id[0]
        return "`command not yet added`"
    except Exception as e:
        logger.error("get_command_id", f"Couldn't retrieve the ID for the command: {e}")

def normalize_username(username: str) -> str:
    """
    Normalize RuneScape username by:
    1. Replacing hyphens with spaces
    2. Converting to lowercase
    3. Removing extra whitespace
    4. Removing special characters
    
    Args:
        username: The username to normalize
        
    Returns:
        Normalized username string
    """
    # Convert to lowercase and replace hyphens/underscores with spaces
    normalized = username.lower().replace('-', ' ').replace('_', ' ')
    
    # Remove extra whitespace and strip
    normalized = ' '.join(normalized.split())
    
    return normalized

def are_names_equivalent(name1: str, name2: str) -> bool:
    """
    Checks if two player names are equivalent by:
    - Comparing exact matches first
    - Then comparing normalized versions (spaces/underscores)
    Returns True if names are considered equivalent
    """
    if not name1 or not name2:
        return False
        
    # First check exact match
    if name1 == name2:
        return True
        
    # Then check with normalized special characters
    norm1 = name1.replace('_', ' ').replace('-', ' ')
    norm2 = name2.replace('_', ' ').replace('-', ' ')
    
    return norm1.strip() == norm2.strip()