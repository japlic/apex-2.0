from disnake.ext import commands
import disnake
from colorama import Fore, Back, Style


class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Base autoresponder command")
    async def mod(self, ctx: disnake.ApplicationCommandInteraction):
        pass

    @mod.sub_command(description="Kick a user")
    async def kick(self, ctx: disnake.ApplicationCommandInteraction, user: disnake.Member, reason: str = "No reason provided"):
        """Kicks a user from the server"""

        if not ctx.author.guild_permissions.kick_members:
            await ctx.response.send_message("You don't have permission to kick members.", ephemeral=True)
            return

        if user.top_role >= ctx.author.top_role:
            await ctx.response.send_message("You don't have permission to kick this user.", ephemeral=True)
            return

        try:
            await user.kick(reason=reason)
            await ctx.response.send_message(f"{user.display_name} has been kicked.", ephemeral=True)
        except disnake.errors.Forbidden:
            await ctx.response.send_message("I don't have permission to kick this user.", ephemeral=True)

    @mod.sub_command(description="Ban a user")
    async def ban(self, ctx: disnake.ApplicationCommandInteraction, user: disnake.Member, reason: str = "No reason provided"):
        """Bans a user from the server"""

        if not ctx.author.guild_permissions.ban_members:
            await ctx.response.send_message("You don't have permission to ban members.", ephemeral=True)
            return

        if user.top_role >= ctx.author.top_role:
            await ctx.response.send_message("You don't have permission to ban this user.", ephemeral=True)
            return

        try:
            await user.ban(reason=reason)
            await ctx.response.send_message(f"{user.display_name} has been banned.", ephemeral=True)
        except disnake.errors.Forbidden:
            await ctx.response.send_message("I don't have permission to ban this user.", ephemeral=True)

def setup(bot):
    bot.add_cog(Mod(bot))
print(Fore.GREEN + Style.BRIGHT + "Mod cog loaded")