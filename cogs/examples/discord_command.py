""" The DropTracker uses interactions.py (v5) to interact with Discord's API.

This file is an example of how to create a new command.

Notes:
- In order for the new command to be registered in Discord's API, the function msut be part of a properly-imported cog (see events.py)
- Even after being imported through a cog, you may need to re-log or restart your Discord client to see the new command yourself.
"""

import interactions
from interactions import SlashCommand, SlashContext, slash_command, SlashCommandOption, OptionType

# We use the slash_command decorator to create a new command.
@slash_command(
    name="example",
    description="An example command",
    options=[
        # Options can be provided to allow input on various parameters.
    SlashCommandOption(
        name="number",
        type=OptionType.INTEGER,
        description="A number",
        required=True
    ),
    SlashCommandOption(
        name="string",
        type=OptionType.STRING,
        description="A string",
        required=True
    ),
    SlashCommandOption(
        name="boolean",
        type=OptionType.BOOLEAN,
        description="A boolean",
        required=True
    )
]
)
## We then define a function that correlates to the slash_command decorator
async def example_command(ctx: SlashContext, number: int, string: str, boolean: bool):
    await ctx.send(f"Number: {number}, String: {string}, Boolean: {boolean}")

