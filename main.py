import asyncio
from datetime import datetime
import interactions
from interactions.api.events import MessageCreate, InteractionCreate, Ready, Startup
from interactions import IntervalTrigger, Task, listen
from dotenv import load_dotenv
import os
from cache.metrics import MetricsTracker
from events import on_message_event, on_interaction_event, on_bot_ready
from utils.message_builder import create_metrics_embed, generate_lootboard_embed
import multiprocessing
from hypercorn.asyncio import serve
from cogs.images import lootboard
from utils.bot_instance import bot_manager


load_dotenv()
intents = (interactions.Intents.ALL)

def run_discord_bot():
    """Initialize and run the Discord bot"""
    if os.getenv("mode") == "dev":
        bot = interactions.Client(token=os.getenv("DEV_DISCORD_TOKEN"), intents=intents)
    else:
        bot = interactions.Client(token=os.getenv("DISCORD_TOKEN"), intents=intents)

    bot_manager.set_bot(bot)

    @bot.listen(MessageCreate)
    async def on_message_create(e: MessageCreate):
        await on_message_event(e)

    @bot.listen(InteractionCreate)
    async def on_interaction(e: InteractionCreate):
        await on_interaction_event(e)

    @bot.listen(Startup)
    async def on_startup(e: Startup):
        update_metrics.start()
        await update_metrics()
        await on_bot_ready(e)
        await update_lootboard()

    @Task.create(IntervalTrigger(seconds=60))
    async def update_metrics():
        try:
            message_id = 1319702688073650229
            channel = await bot.fetch_channel(1283717633048444968)
            message = await channel.fetch_message(message_id)
            
            metrics = MetricsTracker()
            metrics_data = await metrics.get_all_metrics()
            
            embed = create_metrics_embed(metrics_data)
            await message.edit(embed=embed)
            
        except Exception as e:
            print(f"Error updating metrics message: {e}")

    async def update_lootboard():
        image_path, total_players = await lootboard.board_generator(1)
        channel = await bot.fetch_channel(1210765311498788865)
        embed = await generate_lootboard_embed(total_players)
        await channel.send("Lootboard test", file=image_path, embed=embed)

    bot.start()

if __name__ == "__main__":
    print("---------------------------------")
    print("-----  DropTracker.io Core  -----")
    print("---------------------------------")
    print("- Version: " + os.getenv("VERSION"))
    print("- Startup time: " + datetime.now().strftime("%H:%M"))
    print("---------------------------------")
    print("----------- @joelhalen ----------")
    print("---------------------------------")
    run_discord_bot()
    print("--- Ready to process incoming events... ")
