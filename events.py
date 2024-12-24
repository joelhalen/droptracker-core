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
from models.base import Session, session
from models import Player, Log
from submissions.processor import DropProcessor
from utils.logger import Logger

from utils.ip_update import CloudflareIPUpdater
from utils.misc import get_player_cache, normalize_username
from utils.wiseoldman import check_user_by_username
from sqlalchemy import or_

# Create global stats tracker
stats = StatsTracker()
logger = Logger()
drop_processor = DropProcessor()

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
    submitted_rsn = None
    submitted_acc_hash = None
    submitted_plugin_version = None
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
                        if field.name == "player":
                            submitted_rsn = field.value
                        if field.name == "acc_hash":
                            submitted_acc_hash = field.value
                        if field.name == "player_name" and not submitted_rsn:
                            submitted_rsn = field.value
                        if field.name == "p_v_hash":
                            submitted_plugin_version = field.value
                    if not submitted_plugin_version:
                        ## TODO: Once the plugin updates are approved,
                        ## we can log submissions lacking a version and ignore them.
                        pass
                    if not submitted_rsn or not submitted_acc_hash:
                        new_log = Log(
                            level="ERROR",
                            source="on_message_event",
                            message="No player or acc_hash found in embed",
                            details=f"jump_url: {message.jump_url}"
                        )
                        session.add(new_log)
                        session.commit()
                        return
                    if submitted_rsn.lower() == "maybe l die":
                        print("Message url:", message.jump_url)
                    player_updated = await check_player(submitted_rsn, submitted_acc_hash)
                    if not player_updated:
                        ## If the player update fails, ignore the entire submission.
                        return
                    for field in embed.fields:
                        if field.name == "type":  # Look for a field named "type"
                            match field.value:
                                case "drop":
                                    stats.increment("drops")
                                    await drop_processor.process_drop(embed, player_updated)
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
    logger.info("on_bot_ready", f"{bot.user.username} is ready with ID {bot.user.id}")
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



async def check_player(rsn: str, acc_hash: str) -> bool:
    """
    Check if a player exists and verify their account hash.
    If they don't exist, create them. If they do exist, verify hash.
    """
    local_session = Session()
    try:
        normalized_rsn = normalize_username(rsn)
        # First check if player exists by account hash
        existing_player = local_session.query(Player).filter(
            Player.account_hash == acc_hash
        ).first()
        
        if existing_player:
            stored_name = normalize_username(existing_player.player_name)
            if stored_name != normalized_rsn:
                logger.error(
                    "check_player",
                    f"Authentication failed: Hash {acc_hash} belongs to different player. "
                    f"Expected player: {existing_player.player_name}, Got: {rsn}"
                )
                return None
            
            # Update player name if case/format changed
            if existing_player.player_name != rsn:
                logger.info("check_player", 
                    f"Updating player name format from {existing_player.player_name} to {rsn}")
                existing_player.player_name = rsn
                existing_player.date_updated = datetime.now()
                local_session.commit()
            return existing_player
            
        # Check WOM for player data
        wom_player, wom_name, wom_id = await check_user_by_username(normalized_rsn)
        if not wom_player or not wom_id:
            logger.error("check_player", f"Could not find WOM data for {rsn}")
            return None
            
        new_player = Player(
            wom_id=wom_id,
            player_name=rsn,  # Store original name
            account_hash=acc_hash,
            date_updated=datetime.now(),
            date_added=datetime.now()
        )
        local_session.add(new_player)
        local_session.commit()
        logger.info("check_player", f"New player {rsn} added to database")
        return new_player
        
    except Exception as e:
        local_session.rollback()
        logger.error("check_player", f"Error processing player {rsn}", error=e)
        return None
    finally:
        local_session.close()