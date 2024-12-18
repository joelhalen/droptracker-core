import asyncio
import interactions
from interactions.api.events import MessageCreate, InteractionCreate, Ready, Startup
from interactions import listen
from dotenv import load_dotenv
import os
from events import on_message_event, on_interaction_event, on_bot_ready
from hypercorn.asyncio import serve
from api.metric_app import app, config

load_dotenv()
intents = (interactions.Intents.ALL)

# Initialize Discord bot
if os.getenv("mode") == "dev":
    bot = interactions.Client(token=os.getenv("DEV_DISCORD_TOKEN"), intents=intents)
else:
    bot = interactions.Client(token=os.getenv("DISCORD_TOKEN"), intents=intents)

## Event Listeners ##
@listen(MessageCreate)
async def on_message_create(event: MessageCreate):
    await on_message_event(event)

@listen(InteractionCreate)
async def on_interaction(event: InteractionCreate):
    await on_interaction_event(event)

@listen(Startup)
async def on_startup(event: Startup):
    await on_bot_ready(event)

async def start_metrics_server():
    """Start the FastAPI server using Hypercorn"""
    await serve(app, config)

async def main():
    """Attempt to run both the Discord bot and API server concurrently in the same process"""
    await asyncio.gather(
        bot.astart(),
        start_metrics_server()
    )

if __name__ == "__main__":
    asyncio.run(main())
