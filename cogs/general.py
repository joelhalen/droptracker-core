import interactions
from interactions import Extension, SlashContext, slash_command, check
from models import Player, Group, User
from models.base import session
from utils.message_builder import build_default
from utils.misc import get_command_id

def is_authed():
    # TODO: Check if the user is authed for the group they're attempting to 'edit'
    return True

def is_registered(ctx: SlashContext):
    try:
        user: interactions.Member = ctx.author
    except:
        print("Context author is null")
        return False
    user = session.query(User).filter(User.user_id == user.id).first()
    if not user:
        return False
    return True

class UserCommands(Extension):
    @slash_command(name="ping", description="Ping the bot")
    async def ping(self, ctx: SlashContext):
        await ctx.send("Pong!")

    @slash_command(name="register", description="Register your account in the DropTracker database")
    async def register(self, ctx: SlashContext):
        if is_registered(ctx):
            embed = build_default(":warning: Error :warning:", f"Your account is already registered in the DropTracker database.")
            return await ctx.send(embed=embed)
        user = User(user_id=ctx.author.id)
        session.add(user)
        session.commit()
        embed = build_default(":tada: Account Registered :tada:", f"Your account has been registered successfully!")
        return await ctx.send(embed=embed)

class GroupCommands(Extension):
    @slash_command(name="group", description="Group commands")
    async def group(self, ctx: SlashContext):
        await ctx.send("Group commands")

    @slash_command(name="create-group", description="Register your group in the DropTracker database (requires a WOM ID)",
                   default_member_permissions=interactions.Permissions.ADMINISTRATOR)
    async def create_group(self, ctx: SlashContext, group_name: str, wom_id: int):
        if not is_registered(ctx):
            embed = build_default(":warning: Error :warning:", f"You must first be <{get_command_id(ctx.bot, 'register')}>ed in order to create a group.")
            embed.add_field(name="",value=f"If you believe this is a mistake, please [reach out in our Discord](https://droptracker.io/).",inline=False)
            return await ctx.send(embed=embed)
        group = session.query(Group).filter(Group.guild_id == ctx.guild_id, Group.wom_id == wom_id).first()
        if group:
            embed = build_default(":warning: Error :warning:", f"A group associated to this discord server ({ctx.guild_id}) or Wise Old Man ID ({wom_id}) already exists, named `{group.group_name}`.")
            return await ctx.send(embed=embed)
        try:
            guild_id = str(ctx.guild_id)
            group = Group(group_name=group_name, wom_id=wom_id, guild_id=guild_id)
            session.add(group)
            session.commit()
        except Exception as e:
            print(f"Error creating group: {e}")
            embed = build_default(":warning: Error :warning:", f"An error occurred while creating your group. Please try again later.")
            return await ctx.send(embed=embed)
        embed = build_default(":tada: Group Created :tada:", f"Your group has been created successfully!")
        embed.add_field(name="",value=f"You can use the <{get_command_id(ctx.bot, 'group-edit')}> command to make changes to your configuration.", inline=False)
        embed.add_field(name="Group Information",value=f"Name: {group_name}\n"  +
                        f"Wise Old Man Group ID: {wom_id}\n" +
                        f"DropTracker Group ID: {group.group_id}\n" +
                        f"Discord Guild ID: {guild_id}\n",inline=False)
        return await ctx.send(embed=embed)

    @slash_command(name="delete", description="Delete your primary group from our database entirely.",
                   default_member_permissions=interactions.Permissions.ADMINISTRATOR)
    async def delete(self, ctx: SlashContext):
        await ctx.send("Group deleted")
