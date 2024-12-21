""" This file is an example of how to create a new embed. """

from interactions import Embed
from datetime import datetime

async def example_embed():
    embed = Embed(
        title="Example Embed",
        description="This is an example embed",
        color=0x00FF00
    )
    embed.add_field(
        name="Field 1",
        value="Value 1",
        inline=False
    )
    embed.set_thumbnail(url="https://i.imgur.com/1234567890.png")
    embed.set_image(url="https://i.imgur.com/1234567890.png")
    embed.set_footer(text="Footer Text", icon_url="https://i.imgur.com/1234567890.png")
    embed.set_author(name="Author Name", icon_url="https://i.imgur.com/1234567890.png")
    embed.set_timestamp(datetime.now())

    return embed