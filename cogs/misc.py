from disnake.ext import commands
import disnake
from disnake import ui
import datetime
from colorama import Fore, Back, Style

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Base autoresponder command")
    async def server(self, ctx: disnake.ApplicationCommandInteraction):
        pass

    @server.sub_command(name="membercount", description="Get the member count of the server")
    async def count(self, inter):
        """Count the members in the server"""
        member_count = len(inter.guild.members)
        true_member_count = len([m for m in inter.guild.members if not m.bot])
        bot_member_count = len([m for m in inter.guild.members if m.bot])
        guild = inter.guild.name
        embed = disnake.Embed(title="Member count", description=" ", color=0xFFFFFF)
        embed.add_field(
            name="Members of" ,
            value=f" \🌐  All members: **{member_count}**\n \👩‍👩‍👦‍👦 All Humans: **{true_member_count}**\n \🤖  All Bots: **{bot_member_count}**",
            inline=False,
        )
        await inter.send(embed=embed)

def setup(bot: commands.Bot):
    bot.add_cog(Misc(bot))
    print(Fore.GREEN + "Misc cog loaded")