import os
import re
import interactions
from interactions import BaseTrigger, IntervalTrigger, Task, listen
from interactions.api.events import MessageCreate, InteractionCreate, Ready, Startup
from interactions import ChannelType
from cache.metrics import MetricsTracker
from cache.stats import StatsTracker
from cogs.commands.general import UserCommands, GroupCommands
from cogs.commands.admin import AdminCommands
import asyncio
from datetime import datetime, timedelta
import time

from utils.ip_update import CloudflareIPUpdater

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
    return

async def on_message_event(event: MessageCreate):
    """
        Gets called every time a message is created in any guild the bot is a member of.
        All incoming submissions are received through messages in Discord, using webhooks.
    """
    message = event.message
    
    if not message.webhook_id:
        ## We only need to look for messages with attached webhook ids.
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
    bot.load_extension("cogs.commands.general")
    bot.load_extension("cogs.commands.admin")
    print("Bot is ready")
    metrics = MetricsTracker()
    await metrics.initialize()
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