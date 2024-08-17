import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction
import requests
import aiohttp
from colorama import Fore, Back, Style

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Base autoresponder command")
    async def fun(self, ctx: ApplicationCommandInteraction):
        pass

    @fun.sub_command(description="get a catfact")
    async def catfact(self, interaction: disnake.ApplicationCommandInteraction):
        """Gets a catfact"""

        async with aiohttp.ClientSession() as session:
            async with session.get("https://catfact.ninja/fact") as response:
                fact = (await response.json())["fact"]
                length = (await response.json())["length"]
                embed = disnake.Embed(title=f'Random Cat Fact Number: **{length}**', description=f'Cat Fact: {fact}', colour=0x400080)
                embed.set_footer(text="")
                await interaction.response.send_message(embed=embed)

    @fun.sub_command(description="get a minecraft avatar")
    async def minecraft_avatar(self, inter:disnake.ApplicationCommandInteraction, username:str):
        """Gets the mc avatar of the given username"""

        api_url = f'https://minotar.net/skin/{username}.png'
        embed = disnake.Embed(title=f"Minecraft Avatar - {username}")
        embed.set_image(url=api_url)
        embed.set_footer(text="Right-click the image and select 'Save Image As' to download.")
        await inter.response.send_message(embed=embed)

    @fun.sub_command(description="gives you a joke")
    async def joke(self, inter:disnake.ApplicationCommandInteraction):
        """Gets a random joke """

        response = requests.get("https://official-joke-api.appspot.com/jokes/random")
        joke_data = response.json()
        setup = joke_data['setup']
        punchline = joke_data['punchline']

        embed = disnake.Embed(title="Random Joke", color=0xFFD700)
        embed.add_field(name="Setup", value=setup)
        embed.add_field(name="Punchline", value=punchline)
        embed.set_footer(text="Enjoy the joke!")

        await inter.response.send_message(embed=embed)

def setup(bot: commands.Bot):
    bot.add_cog(Fun(bot))
    print(Fore.GREEN + "Fun cog loaded")