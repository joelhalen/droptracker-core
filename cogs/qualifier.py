import asyncio
from models.base import session
from typing import TYPE_CHECKING
from utils import wiseoldman
from utils.bot_instance import bot_manager
from utils.message_builder import generate_drop_embed

if TYPE_CHECKING:
    from models import Drop, Player, CollectionLogEntry, Group, GroupConfiguration, PersonalBestEntry, CombatAchievementEntry, NotifiedSubmission



def check_drop(drop: Drop):

    async def check_drop_async(drop: Drop):
        bot = bot_manager.get_bot()
        if not bot:
            return
            
        player: Player = drop.player
        player_wom_id = player.wom_id
        groups = await wiseoldman.fetch_player_groups(player_wom_id)
        for group_id in groups:
            group = session.query(Group).filter(Group.group_id == group_id).first()
            if group:
                group_settings = session.query(GroupConfiguration).filter(GroupConfiguration.group_id == group_id).all()
                min_value_raw = [setting for setting in group_settings if setting.config_key == 'minimum_value_to_notify']
                min_value_raw = min_value_raw[0]
                min_value = min_value_raw.config_value
                if drop.value >= min_value:
                    """
                        Send a notification to the group Discord channel
                    """
                    channel_id_raw = [setting for setting in group_settings if setting.config_key == 'channel_id_to_send_drops']
                    channel_id_raw = channel_id_raw[0]
                    channel_id = channel_id_raw.config_value
                    
                    channel = await bot.fetch_channel(channel_id)
                    embed = generate_drop_embed(group_id, drop)
                    if channel:
                        await channel.send(embed=embed)
        if drop.value >= 1000:
            """
                Send a global notification to the Discord server
            """
            channel = await bot.fetch_channel(1217463930805293139)
            embed = generate_drop_embed(group_id, drop)
            if channel:
                await channel.send(embed=embed) 
        pass

    asyncio.run(check_drop_async(drop))

def check_collection(clog: CollectionLogEntry):
    async def check_clog_async(clog: CollectionLogEntry):
        # Your async code here
        pass

    asyncio.run(check_clog_async(clog))

def check_personal_best(pb: PersonalBestEntry):
    async def check_pb_async(pb: PersonalBestEntry):
        # Your async code here
        pass

    asyncio.run(check_pb_async(pb))

def check_combat_achievement(ca: CombatAchievementEntry):
    async def check_ca_async(ca: CombatAchievementEntry):
        # Your async code here
        pass

    asyncio.run(check_ca_async(ca))
