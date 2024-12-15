import asyncio
import interactions
from interactions.api.events import MessageCreate, InteractionCreate, Ready, Startup
from interactions import listen
from dotenv import load_dotenv
import os
from events import on_message_event, on_interaction_event, on_bot_ready

load_dotenv()
intents = (interactions.Intents.ALL)

bot = interactions.Client(token=os.getenv("DISCORD_TOKEN"), intents=intents)

## Event Listeners ##
@listen(MessageCreate)
async def on_message_create(event: MessageCreate):
    # Debug the event before passing it
    
    # Pass the event directly instead of wrapping it
    await on_message_event(event)

@listen(InteractionCreate)
async def on_interaction(event: InteractionCreate):
    await on_interaction_event(event)

@listen(Startup)
async def on_startup(event: Startup):
    await on_bot_ready(event)


async def main():
    await bot.astart()
    

if __name__ == "__main__":
    asyncio.run(main())
