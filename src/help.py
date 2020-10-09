import discord
from discord.ext import commands


class CustomHelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__()

    def command_not_found(self, string):
        return "Command `{0}` not found".format(string)

    def subcommand_not_found(self, command, string):
        if (isinstance(command, commands.Group) and
                len(command.all_commands) > 0):

            return "Command `{0}` has no subcommand `{1}`.".format(
                command.qualified_name,
                string
            )

        return "Command `{0}` has no subcommands.".format(
            command.qualified_name
        )

    def command_formatting(self, command):
        return discord.Embed(
            title=command.name,
            description=command.help
        )

    async def send_bot_help(self, mapping):
        embed = discord.Embed(
            title="Help"
        )
        mapping = mapping[None]
        for command in mapping:
            embed.add_field(
                name=command.name,
                value=command.help,
                inline=False
            )

        return await self.context.send(embed=embed)

    async def send_command_help(self, command):
        embed = self.command_formatting(command)
        await self.context.send(embed=embed)
