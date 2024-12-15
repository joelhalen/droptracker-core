import re
import interactions
from interactions import listen
from interactions.api.events import MessageCreate, InteractionCreate, Ready, Startup
from interactions import ChannelType
from cogs.general import UserCommands, GroupCommands
from cogs.admin import AdminCommands
import asyncio
from datetime import datetime, timedelta

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
        
        return f"""
Stats Report
-----------
Runtime: {runtime.days}d {runtime.seconds//3600}h {(runtime.seconds//60)%60}m
Total Requests: {self.drops + self.logs + self.achievements + self.pbs}

Drops: {self.drops}
    Per minute: {self.drops/minutes:.2f}
    Per hour: {self.drops/hours:.2f}
    
Logs: {self.logs}
    Per minute: {self.logs/minutes:.2f}
    Per hour: {self.logs/hours:.2f}
    
Achievements: {self.achievements}
    Per minute: {self.achievements/minutes:.2f}
    Per hour: {self.achievements/hours:.2f}
    
Personal Bests: {self.pbs}
    Per minute: {self.pbs/minutes:.2f}
    Per hour: {self.pbs/hours:.2f}
"""

# Create global stats tracker
stats = StatsTracker()

async def on_interaction_event(event: InteractionCreate):
    bot: interactions.Client = event.bot
    print("Interaction created")
    if event.interaction.command.name == "ping":
        await event.interaction.response.send_message("Pong!")
    pass

async def print_stats():
    while True:
        print(stats.get_stats_report())
        await asyncio.sleep(10)  # Print every 5 minutes

async def on_message_event(event: MessageCreate):
    message = event.message
    
    if not message.webhook_id:
        return
        
    if message.channel.parent_id and is_valid(int(message.channel.parent_id)):
        if hasattr(message, 'embeds'):
            embeds = message.embeds
            for embed in embeds:
                if embed.author and embed.author.name == "DropTracker":
                    match embed.title:
                        case title if re.search(r'received some drops', title, re.IGNORECASE):
                            print("Title matches drop")
                            stats.increment("drops")
                        case title if re.search(r'has killed a boss', title, re.IGNORECASE):
                            print("Title matches PB")
                            stats.increment("pbs")
                        case title if re.search(r'has completed a collection log', title, re.IGNORECASE):
                            print("Title matches log")
                            stats.increment("logs")
                        case title if re.search(r'has completed a combat achievement', title, re.IGNORECASE):
                            print("Title matches achievement")
                            stats.increment("achievements")
                        case _:
                            print("Title doesn't match any known submission type")
                            continue

async def on_bot_ready(event: Startup):
    bot: interactions.Client = event.bot
    bot.load_extension("cogs.general")
    bot.load_extension("cogs.admin")
    print("Bot is ready")
    
    # Start the stats printing task
    asyncio.create_task(print_stats())
    return bot

def is_valid(channel_id: int):
    return channel_id in [1211062421591167016, 1107479658267684976]