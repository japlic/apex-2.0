import disnake
from disnake.ext import commands
from utils.pagination import CreatePaginator
from colorama import Fore, Back, Style

color_list = [0x3498db, 0xe74c3c, 0x2ecc71, 0xf1c40f, 0x9b59b6, 0xe67e22, 0x1abc9c, 0xe74c3c, 0x34495e, 0x2ecc71]
class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Base autoresponder command")
    async def cmd(self, ctx: disnake.ApplicationCommandInteraction):
        pass

    @cmd.sub_command(name="help", description="Lists all commands")
    async def help(self, inter):
        """Lists all commands"""
        embeds = []

        cogs = self.bot.cogs.items()
        for cog_name, cog in cogs:
            embed = disnake.Embed(title=cog.qualified_name, colour=0x00ff00)
            if cog is None:
                continue
            cmds = cog.get_slash_commands()
            name = cog.qualified_name

            value = ""
            for cmd in cmds:
                value += f"`/{cmd.qualified_name}` - {cmd.description}\n"
                if cmd.children:
                    for children, sub_command in cmd.children.items():
                        try:
                            value += f"`/{sub_command.qualified_name}` - {sub_command.description}\n"
                        except AttributeError:
                            pass

            if value == "":
                continue

            embed.description = f"{cog.description}\n\n{value}"
            embeds.append(embed)

        paginator = CreatePaginator(embeds, inter.author.id, timeout=300.0)
        await inter.send(embed=embeds[0], view=paginator)


def setup(bot: commands.Bot):
    bot.add_cog(Help(bot))
print(Fore.GREEN + "Help cog loaded")