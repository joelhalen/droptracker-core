import asyncio
from datetime import datetime
import random
import interactions
from interactions import Embed, Extension, GuildText, OptionType, Permissions, SlashCommandOption, SlashContext, is_owner, slash_command, check
from utils.message_builder import create_log_embed
from utils.num import format_number

from models import Webhook, Log
from models.base import session

class AdminCommands(Extension):
    

    @slash_command(name="new_webhook",
                   description="Generate a new webhook, adding it to the database and the GitHub list.")
    async def new_webhook_generator(self, ctx: SlashContext):
        servers = ["main", "alt"]
        server = random.choice(servers)
        if server == "main":
            parent_id = 1211062421591167016
        else:
            parent_id = 1107479658267684976
        try:
            parent_channel = await ctx.bot.fetch_channel(parent_id)
            num = 35
            channel_name = f"drops-{num}"
            while channel_name in [channel.name for channel in parent_channel.channels]:
                num += 1
                channel_name = f"drops-{num}"
            new_channel: GuildText = await parent_channel.create_text_channel(channel_name)
            logo_path = '/store/droptracker/disc/static/assets/img/droptracker-small.gif'
            avatar = interactions.File(logo_path)
            webhook: interactions.Webhook = await new_channel.create_webhook(name=f"DropTracker Webhooks ({num})", avatar=avatar)
            webhook_url = webhook.url
            db_webhook = Webhook(webhook_url=str(webhook_url))
            session.add(db_webhook)
            session.commit()
            await ctx.send(f"A new webhook has been generated in <#{new_channel.id}> ({server}) with ID `{webhook.id}` (`{db_webhook.webhook_id}`)",ephemeral=True)
        except Exception as e:
            await ctx.send(f"Couldn't create a new webhook:{e}",ephemeral=True)
        pass

    @slash_command(name="logs", description="Filter logs by source and level",
                   options=[
                       SlashCommandOption(
                           name="source",
                           description="The source func",
                           type=OptionType.STRING,
                           required=False
                       ),
                       SlashCommandOption(
                           name="level",
                           description="Log level to view (ERROR, INFO, DEBUG)",
                           type=OptionType.STRING,
                           required=False
                       )
                   ],
                   default_member_permissions=Permissions.ADMINISTRATOR)
    async def log_filter(self, ctx: SlashContext, source: str = None, level: str = None):
        query = session.query(Log)
        if source:
            query = query.filter(Log.source == source)
        if level:
            query = query.filter(Log.level == level)
        logs = query.all()
        embeds = await create_log_embed(logs, source, level)
        return await ctx.send(embeds=embeds)

