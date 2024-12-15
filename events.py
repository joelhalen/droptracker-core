import os
import re
import interactions
from interactions import listen
from interactions.api.events import MessageCreate, InteractionCreate, Ready, Startup
from interactions import ChannelType
from cogs.general import UserCommands, GroupCommands
from cogs.admin import AdminCommands
import asyncio
from datetime import datetime, timedelta

from utils.ip_update import CloudflareIPUpdater

class StatsTracker:
    def __init__(self):
        self.start_time = datetime.now()
        self.drops = 0
        self.logs = 0
        self.achievements = 0
        self.pbs = 0
        
    def increment(self, stat_type: str):
        match stat_type.lower():
            case "drops":
                self.drops += 1
            case "logs":
                self.logs += 1
            case "achievements":
                self.achievements += 1
            case "pbs":
                self.pbs += 1
    
    def get_runtime(self) -> timedelta:
        return datetime.now() - self.start_time
    
    def get_stats_report(self) -> str:
        runtime = self.get_runtime()
        minutes = runtime.total_seconds() / 60
        hours = minutes / 60
        
        # Move cursor up 7 lines, return to start, and clear each line
        return f"\033[7F\r" + f"""Status Report\033[K
Runtime: {runtime.days}d {runtime.seconds//3600}h {(runtime.seconds//60)%60}m {runtime.seconds%60}s\033[K
Total Requests: {self.drops + self.logs + self.achievements + self.pbs}\033[K
Drops: {self.drops} ({self.drops/minutes:.2f}/min, {self.drops/hours:.2f}/hr)\033[K
Logs: {self.logs} ({self.logs/minutes:.2f}/min, {self.logs/hours:.2f}/hr)\033[K
Achievements: {self.achievements} ({self.achievements/minutes:.2f}/min, {self.achievements/hours:.2f}/hr)\033[K
Personal Bests: {self.pbs} ({self.pbs/minutes:.2f}/min, {self.pbs/hours:.2f}/hr)\033[K"""

# Create global stats tracker
stats = StatsTracker()

async def on_interaction_event(event: InteractionCreate):
    bot: interactions.Client = event.bot
    print("Interaction created")
    if event.interaction.command.name == "ping":
        await event.interaction.response.send_message("Pong!")
    pass

async def print_stats():
    # Print initial empty lines
    print("\n" * 6)
    while True:
        print(stats.get_stats_report(), end='', flush=True)
        await asyncio.sleep(0.05)

async def on_message_event(event: MessageCreate):
    message = event.message
    
    if not message.webhook_id:
        return
        
    if message.channel.parent_id and is_valid(int(message.channel.parent_id)):
        if hasattr(message, 'embeds'):
            embeds = message.embeds
            for embed in embeds:
                if embed.author and embed.author.name == "DropTracker":
                    # Check each field in the embed
                    for field in embed.fields:
                        if field.name == "type":  # Look for a field named "type"
                            match field.value:
                                case "drop":
                                    stats.increment("drops")
                                case "collection_log":
                                    stats.increment("logs")
                                case "combat_achievement":
                                    stats.increment("achievements")
                                case "npc_kill":
                                    stats.increment("pbs")
                                case _:
                                    continue

async def on_bot_ready(event: Startup):
    bot: interactions.Client = event.bot
    bot.load_extension("cogs.general")
    bot.load_extension("cogs.admin")
    print("Bot is ready")
    
    # Start the stats printing task
    asyncio.create_task(print_stats())
    if is_prod(): 
        updater = CloudflareIPUpdater()
        updater.start_monitoring(interval_seconds=300)
    return bot

def is_valid(channel_id: int):
    return channel_id in [1211062421591167016, 1107479658267684976]

def is_prod():
    return os.getenv("MODE") == "prod"