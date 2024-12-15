import interactions
from interactions import Extension, SlashContext

class AdminCommands(Extension):
    @interactions.slash_command(name="admin", description="Admin commands")
    async def admin(self, ctx: interactions.SlashContext):
        await ctx.send("Admin commands")