import interactions
from interactions import Extension, SlashContext, slash_command, check


def is_authed(ctx: SlashContext):
    # TODO: Check if the user is authed for the group they're attempting to 'edit'
    return True


class UserCommands(Extension):
    @slash_command(name="ping", description="Ping the bot")
    async def ping(self, ctx: SlashContext):
        await ctx.send("Pong!")

class GroupCommands(Extension):
    @slash_command(name="group", description="Group commands")
    async def group(self, ctx: SlashContext):
        await ctx.send("Group commands")

    @slash_command(name="delete", description="Delete your primary group from our database entirely.")
    ## An example of how we can check permissions prior to allowing a specific command execution
    @check(is_authed())
    async def delete(self, ctx: SlashContext):
        await ctx.send("Group deleted")
