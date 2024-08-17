import disnake
from disnake.ext import commands, tasks
import platform
import asyncio


if platform.system() == "Windows":
    bot = commands.Bot(command_prefix='?')
else:
    bot = commands.Bot(command_prefix='?')


def load_cogs():
    cogs = ["cogs.mod", "cogs.poll", "cogs.ai", "cogs.help", "cogs.music", "cogs.fun","cogs.misc", "cogs.code","cogs.user"]
    for cog in cogs:
        try:
            bot.load_extension(cog)
        except Exception as e:
            print(f"Failed to load cog {cog}: {e}")




def unload_cogs():
    cogs = ["cogs.mod", "cogs.poll", "cogs.ai", "cogs.help", "cogs.music", "cogs.fun","cogs.misc", "cogs.code","cogs.user"]
    for cog in cogs:
        try:
            bot.unload_extension(cog)
        except Exception as e:
            print(f"Failed to unload cog {cog}: {e}")


load_cogs()


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")
    # update_server_list.start()
    await status_task()


async def status_task():
    activities = [
        disnake.Activity(type=disnake.ActivityType.playing, name="fortnite"),
        disnake.Activity(type=disnake.ActivityType.playing, name="with electricity ⚡"),
        disnake.Activity(type=disnake.ActivityType.listening, name="/cmd help"),
        disnake.Activity(type=disnake.ActivityType.watching, name=f"watching {len(bot.guilds)} servers")
    ]

    while True:
        for activity in activities:
            await bot.change_presence(status=disnake.Status.dnd, activity=activity)
            await asyncio.sleep(20)


@bot.command()
async def reload(ctx):
    authorized_users = [318414198663282689, 1045011821838475334]
    if ctx.author.id in authorized_users:
        unload_cogs()
        load_cogs()
        await ctx.reply("Reloaded")
        print("\n\n\nReloaded\n\n\n")
    else:
        await ctx.reply("No Permissions")


##@tasks.loop(seconds=10)
#async def update_server_list():
# guild = await bot.fetch_guild(1111730220521758720)
# vc_lock_channel = await guild.fetch_channel(1114859296908382208)
# await vc_lock_channel.edit(name=f"In {len(bot.guilds)} guilds")

bot.run("MTEwODUxMDY1NzQ3ODkzNDYwOA.GYoKkI.MGeFl6wiIy0l_lNBdkHagN4mJl1XNFK8r6APkc")