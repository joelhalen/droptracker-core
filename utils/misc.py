



import interactions


async def get_command_id(bot: interactions.Client, command_name: str):
    """
        Attempts to return the Discord ID for the passed 
        command name based on the context of the bot being used,
        incase the client is changed which would result in new command IDs
    """
    try:
        commands = bot.application_commands
        if commands:
            for command in commands:
                cmd_name = command.get_localised_name("en")
                if cmd_name == command_name:
                    return command.cmd_id[0]
        return "`command not yet added`"
    except Exception as e:
        print("Couldn't retrieve the ID for the command")
        print("Exception:", e)