import interactions
from interactions import Embed, Button, ButtonStyle, InteractionType, Message, SlashContext

def build_default(title: str, description: str):
    """
        Builds a default embed with the DropTracker logo and footer
    """
    embed = Embed(
        title=title,
        description=description,
        color=0x00FF00
    )
    embed.set_author(
        name="DropTracker",
        icon_url="https://joelhalen.github.io/droptracker-small.gif"
    )
    embed.set_footer("Powered by the DropTracker | https://www.droptracker.io/")
    return embed

