from disnake.ext import commands
import disnake
from disnake import ui
from colorama import Fore, Back, Style


class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    active_polls = {}

    class PollView(ui.View):
        def __init__(self, poll_question: str):
            super().__init__()
            self.poll_question = poll_question
            self.vote_count = {"Yes": 0, "No": 0}
            self.voted_users = set()

        @ui.button(label="Yes", style=disnake.ButtonStyle.primary, custom_id="choice1")
        async def choice1_button(self, button: ui.Button, interaction: disnake.MessageInteraction):
            if interaction.user.id in self.voted_users:
                await interaction.response.send_message("You have already voted and cannot vote again.", ephemeral=True)
            else:
                self.vote_count["Yes"] += 1
                self.voted_users.add(interaction.user.id)
                await interaction.response.send_message("You voted for 'Yes'.", ephemeral=True)
                await self.update_poll_message(interaction)

        @ui.button(label="No", style=disnake.ButtonStyle.primary, custom_id="choice2")
        async def choice2_button(self, button: ui.Button, interaction: disnake.MessageInteraction):
            if interaction.user.id in self.voted_users:
                await interaction.response.send_message("You have already voted and cannot vote again.", ephemeral=True)
            else:
                self.vote_count["No"] += 1
                self.voted_users.add(interaction.user.id)
                await interaction.response.send_message("You voted for 'No'.", ephemeral=True)
                await self.update_poll_message(interaction)

        async def update_poll_message(self, interaction: disnake.MessageInteraction):
            poll_message = f"**{self.poll_question}**\n\n"
            poll_message += f"Yes - Votes: {self.vote_count['Yes']}\n"
            poll_message += f"No - Votes: {self.vote_count['No']}"

            embed = disnake.Embed(title="Poll", description=poll_message, color=0x00ff00)

            await interaction.message.edit(embed=embed)

        async def interaction_check(self, interaction: disnake.Interaction) -> bool:
            return interaction.user.id != interaction.message.author.id
    
    @commands.slash_command(description="Base autoresponder command")
    async def poll(self, ctx: disnake.ApplicationCommandInteraction):
        pass

    @poll.sub_command(description="Start a poll")
    async def start(self, ctx: disnake.ApplicationCommandInteraction, question: str):
        """Starts a poll in the current channel"""

        if not ctx.author.guild_permissions.kick_members:
            await ctx.response.send_message("You don't have permission to start a poll.", ephemeral=True)
            return

        poll_message = f"**{question}**\n\nYes - Votes: 0\nNo - Votes: 0"

        embed = disnake.Embed(title="Poll", description=poll_message, color=0x00ff00)
        try:
            poll_msg = await ctx.send(embed=embed, view=self.PollView(question))
            self.active_polls[ctx.channel.id] = poll_msg

        except disnake.HTTPException as e:
            await ctx.send("An error occurred while creating the poll. Please try again later.")

def setup(bot):
    bot.add_cog(Poll(bot))
print(Fore.GREEN+"Poll cog loaded")
