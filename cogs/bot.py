import disnake
from disnake.ext import commands
from disnake import Embed

class BotCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(BotCog(bot))