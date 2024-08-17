import disnake
import disnake
from disnake import *
from disnake.ext import commands
from better_profanity import profanity
import base64
import time
from io import BytesIO
from disnake.ext import commands
from colorama import Fore, Back, Style

class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Base autoresponder command")
    async def user(self, ctx: disnake.ApplicationCommandInteraction):
     pass

    @user.sub_command(description="Fetches user info")
    async def fetch(self, ctx: disnake.ApplicationCommandInteraction, user: disnake.Member = None):
        """Fetches user information"""

        if user is None:
            user = ctx.author

        embed = disnake.Embed(title="User Info", color=0x800080)  # Set a fantasy-inspired color

        # User information
        embed.set_thumbnail(url=user.avatar.url)  # Set the user's avatar as the thumbnail
        embed.add_field(name="Name", value=f"*{user.display_name}*", inline=True)  # Use italic formatting
        embed.add_field(name="ID", value=f"`{user.id}`", inline=True)  # Use monospace formatting
        embed.add_field(name="Joined Server", value=user.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
        embed.add_field(name="Joined Discord", value=user.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)

        # Roles
        roles = [role.name for role in user.roles[1:]]  # Exclude the everyone role
        roles_str = ', '.join(roles) if roles else "None"
        embed.add_field(name="Roles", value=f"```{roles_str}```", inline=False)  # Use code block formatting

        # Permissions
        permissions = user.guild_permissions
        perms_str = ', '.join([perm.replace("_", " ").title() for perm, value in permissions if value])
        embed.add_field(name="Permissions", value=f"```{perms_str}```", inline=False)  # Use code block formatting

        await ctx.send(embed=embed)

def setup(bot: commands.Bot):
    bot.add_cog(User(bot))
    print(Fore.GREEN + "User cog loaded")