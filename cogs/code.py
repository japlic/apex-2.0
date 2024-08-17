import disnake
from disnake import Embed, TextInputStyle, Color
from disnake.ext import commands
from disnake.ext.commands import Cog
from colorama import Fore, Back, Style

from utils.CONSTANTS import VALID_CODE_LANGUAGES
from utils.http import session
from utils.shortcuts import errorEmb
from utils import checks
dev = checks.is_dev

class CodeCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Base autoresponder command")
    async def eval(self, ctx: disnake.ApplicationCommandInteraction):
        pass

    @eval.sub_command(name="code", description="Run code and get results instantly. Window for code will pop up. [DEV ONLY]")
    async def code(self, inter: disnake.ApplicationCommandInteraction):
        checks.is_dev()
        """
        Run code and get results instantly
        """
        await inter.response.send_modal(modal=CodeModal())


class CodeModal(disnake.ui.Modal):
    def __init__(self):
        # The details of the modal, and its components
        components = [
            disnake.ui.TextInput(
                label="Language",
                placeholder="Language",
                custom_id="language",
                style=TextInputStyle.short,
                max_length=15,
            ),
            disnake.ui.TextInput(
                label="Code",
                placeholder="Write your code here",
                custom_id="code",
                style=TextInputStyle.paragraph,
            ),
        ]
        super().__init__(
            title="Run Code",
            custom_id="run_code",
            components=components,
        )

    # The callback received when the user input is completed.
    async def callback(self, inter: disnake.ModalInteraction):
        language = inter.text_values["language"].strip()
        if not self._check_valid_lang(language):
            embed = disnake.Embed(
                title=f"{language} is not a valid language", colour=Color.red()
            )
            return await inter.send(embed=embed)

        embed = disnake.Embed(title="Running Code")
        embed.add_field(
            name="Language",
            value=language.capitalize(),
            inline=False,
        )
        embed.add_field(
            name="Code",
            value=f"```{language}\n{inter.text_values['code'][:999]}\n```",
            inline=False,
        )
        await inter.send(embed=embed)
        result = await self.run_code(lang=language, code=inter.text_values["code"])
        await self._send_result(inter, result)

    @staticmethod
    async def run_code(*, lang: str, code: str):
        code = await session.post(
            "https://emkc.org/api/v1/piston/execute",
            json={"language": lang, "source": code},
        )
        return await code.json()

    @staticmethod
    async def _send_result(inter, result: dict):
        try:
            output = result["output"]
        except KeyError:
            return await errorEmb(inter, result["message"])

        embed = Embed(title=f"Ran your {result['language']} code", color=0xFFFFFF)
        output = output[:500].strip()
        shortened = len(output) > 500
        lines = output.splitlines()
        shortened = shortened or (len(lines) > 15)
        output = "\n".join(lines[:15])
        output += shortened * "\n\n**Output shortened**"
        embed.add_field(name="Output", value=f"```\n{output}\n```" or "**<No output>**")

        await inter.send(embed=embed)

    @staticmethod
    def _check_valid_lang(param):
        if str(param).casefold() not in VALID_CODE_LANGUAGES:
            return False
        return True


def setup(bot):
    bot.add_cog(CodeCog(bot))
    print(Fore.GREEN + "Code cog loaded")