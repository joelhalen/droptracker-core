import asyncio
import interactions
from interactions.api.events import MessageCreate, InteractionCreate, Ready, Startup
from interactions import IntervalTrigger, Task, listen
from dotenv import load_dotenv
import os
from cache.metrics import MetricsTracker
from events import on_message_event, on_interaction_event, on_bot_ready
from hypercorn.asyncio import serve
from api.metric_app import app, config
from utils.message_builder import create_metrics_embed
from utils.num import format_number

load_dotenv()
intents = (interactions.Intents.ALL)

# Initialize Discord bot
if os.getenv("mode") == "dev":
    bot = interactions.Client(token=os.getenv("DEV_DISCORD_TOKEN"), intents=intents)
else:
    bot = interactions.Client(token=os.getenv("DISCORD_TOKEN"), intents=intents)

## Event Listeners ##
@listen(MessageCreate)
async def on_message_create(e: MessageCreate):
    await on_message_event(e)

@listen(InteractionCreate)
async def on_interaction(e: InteractionCreate):
    await on_interaction_event(e)

@listen(Startup)
async def on_startup(e: Startup):
    update_metrics.start()
    await update_metrics()
    await on_bot_ready(e)

async def start_metrics_server():
    """Start the FastAPI server using Hypercorn"""
    await serve(app, config)

## Looped Tasks ##
@Task.create(IntervalTrigger(seconds=60))
async def update_metrics():
    try:
        message_id = 1319702688073650229
        channel = await bot.fetch_channel(1283717633048444968)
        message = await channel.fetch_message(message_id)
        
        metrics = MetricsTracker()
        metrics_data = await metrics.get_all_metrics()
        
        # Create and update embed
        embed = create_metrics_embed(metrics_data)
        await message.edit(embed=embed)
        
    except Exception as e:
        print(f"Error updating metrics message: {e}")


async def main():
    """Attempt to run both the Discord bot and API server concurrently in the same process"""
    await asyncio.gather(
        bot.astart(),
        start_metrics_server()
    )

if __name__ == "__main__":
    asyncio.run(main())
