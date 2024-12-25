from models import Drop, Player, CollectionLogEntry, Group, GroupConfiguration, PersonalBestEntry, CombatAchievementEntry, NotifiedSubmission
import asyncio
from models import Group
from models.base import session

from utils import wiseoldman      

def check_drop(drop: Drop):

    async def check_drop_async(drop: Drop):
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
                    
                    if channel:
                        await channel.send(f"A new drop has been submitted for {player.username} in {group.name}!")
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
