import disnake
from disnake.ext import commands
from colorama import just_fix_windows_console, Fore, Style

# Initialize colorama for Windows
just_fix_windows_console()

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_slash_command_error(self, inter: disnake.ApplicationCommandInteraction, error):
        """
        The event triggered when an error is raised while invoking a slash command.
        :param inter: Interaction
        :param error: Exception
        """
        # Embed to send to the user
        embed = disnake.Embed(
            title="Error",
            color=disnake.Color.red()
        )

        # Add details to the embed based on the error type
        if isinstance(error, commands.CommandNotFound):
            embed.description = "Command not found."
        elif isinstance(error, commands.MissingRequiredArgument):
            embed.description = "Missing required argument."
        elif isinstance(error, commands.CommandInvokeError):
            embed.description = f"An error occurred: ```{error.original}```"
        else:
            embed.description = f"An unexpected error occurred: ```{str(error)}```"

        await inter.response.send_message(embed=embed, ephemeral=True)

        # Print the error in the console with block code formatting
        print(f"{Fore.RED}Error: {Style.BRIGHT}```{str(error)}```{Style.RESET_ALL}")

    @commands.slash_command()
    async def error_test(self, inter: disnake.ApplicationCommandInteraction, arg: str):
        """
        Command to trigger an error for testing purposes.
        """

def setup(bot):
    bot.add_cog(ErrorHandler(bot))
