import interactions
from interactions.api.events import MessageCreate, InteractionCreate, Ready, Startup
from cogs.general import UserCommands, GroupCommands
from cogs.admin import AdminCommands

async def on_message_event(event: MessageCreate):
    ## All submissions are received through message events on Discord's API.
    ## This means they pass through this method EVERY. SINGLE. TIME.
    bot: interactions.Client = event.bot
    print("Message created")

async def on_interaction_event(event: InteractionCreate):
    ## "interactions" are received through button-presses and a few other ways.
    ## We primarily use them for configurating groups, but they have various use cases.
    bot: interactions.Client = event.bot
    print("Interaction received")

async def on_bot_ready(event: Startup):
    ## Tasks that need to be completed whenever the bot initialially connects to Discord's API.
    bot: interactions.Client = event.bot
    bot.load_extension("cogs.general")
    bot.load_extension("cogs.admin")
    print("Bot is ready")
    return bot