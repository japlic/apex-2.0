import disnake
from disnake.ext import commands
from better_profanity import profanity
import base64
import time
from io import BytesIO
import requests
import typing
from colorama import Fore, Back, Style

class Ai(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.models = {
            "stable-diffusion": "stabilityai/stable-diffusion-xl-base-1.0",
            "waifu-diffusion": "hakurei/waifu-diffusion",
            "nsfw" : "UnfilteredAI/NSFW-gen-v2"
        }

    @commands.slash_command(description="Base autoresponder command")
    async def ai(self, ctx: disnake.ApplicationCommandInteraction):
        pass


    @ai.sub_command(description="Generates AI art")
    async def art(self, inter: disnake.ApplicationCommandInteraction, text: str, model: typing.Literal['stable-diffusion','waifu-diffusion',"nsfw"]):
        """Generates AI art """

        if model not in self.models:
            return await inter.send("Invalid model specified.", ephemeral=True)
        
        channel = inter.channel
        
        # Check if the channel is marked as NSFW
        if model == "nsfw" and not channel.is_nsfw():
            return await inter.send("NSFW requests are only allowed in NSFW channels.", ephemeral=True)

        if profanity.contains_profanity(text) and model != "nsfw":
            return await inter.send("NSFW requests are not allowed in this channel!", ephemeral=True)
        
        if "bot" in channel.name or "command" in channel.name:
            hidden = False
        else:
            hidden = True
        
        ETA = int(time.time() + 15)
        await inter.send(
            f"This might take a bit of time... ETA: <t:{ETA}:R>",
            ephemeral=hidden,
        )
        
        # Make the request using requests
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{self.models[model]}",
            json={"inputs": text},
            headers={"Authorization": f"Bearer GPUPky"}
        )
        
        if response.status_code == 200:
            # Process response data
            try:
                image_data = BytesIO(response.content)
                images = [disnake.File(image_data, "image.png")]
                await inter.edit_original_response(files=images, content="Here you go!")
            except Exception as e:
                await inter.edit_original_response(content=f"Failed to generate AI art. Error: {e}")
        else:
            await inter.edit_original_response(content=f"Failed to generate AI art. Status Code: {response.status_code}")

def setup(bot: commands.Bot):
    bot.add_cog(Ai(bot))
    print(Fore.GREEN + Style.BRIGHT + "Ai cog loaded")

