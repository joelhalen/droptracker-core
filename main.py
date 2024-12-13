import interactions
from interactions.api.events import MessageCreate, InteractionCreate, Ready
from interactions import listen
from dotenv import load_dotenv
import os
from events import on_message_create, on_interaction, on_ready

load_dotenv()

bot = interactions.Client(token=os.getenv("DISCORD_TOKEN"))

## Event Listeners ##
@listen(MessageCreate)
async def on_message_create(event: MessageCreate):
    await on_message_create(event)

@listen(InteractionCreate)
async def on_interaction(event: InteractionCreate):
    await on_interaction(event)

@listen(Ready)
async def on_ready(event: Ready):
    await on_ready(event)


if __name__ == "__main__":
    print("Starting up...")
    bot.start()
