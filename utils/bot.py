import asyncio
from datetime import datetime

import asyncpg

import disnake
from disnake import ApplicationCommandInteraction, OptionType
from disnake.ext import commands

from utils.CONSTANTS import __VERSION__
from utils.cache import async_cache
from utils.exceptions import UserBlacklisted
from utils.http import HTTPSession
from utils.shortcuts import errorEmb


class OGIROID(commands.InteractionBot):
    def __init__(self, *args, **kwargs):
        super().__init__(
            intents=disnake.Intents.all(),
            command_sync_flags=commands.CommandSyncFlags(sync_commands_debug=True),
            *args,
            **kwargs,
        )
        self._ready_ = False
        self.uptime = datetime.now()
        self.session = HTTPSession(loop=self.loop)
        self.commands_ran = {}
        self.total_commands_ran = {}
        self.db = None
        self.add_app_command_check(
            self.blacklist_check, slash_commands=True, call_once=True
        )

    async def blacklist_check(self, ctx):
        try:
            await self.wait_until_ready()
            if await self.blacklist.blacklisted(ctx.author.id):
                await errorEmb(ctx, "You are blacklisted from using this bot!")
                raise UserBlacklisted
            return True
        except AttributeError:
            pass  # DB hasn't loaded yet

    @async_cache(maxsize=0)
    async def on_slash_command(self, inter: ApplicationCommandInteraction):
        COMMAND_STRUCT = [inter.data]
        do_break = False
        while True:
            COMMAND = COMMAND_STRUCT[-1]
            if not COMMAND.options:
                if inter.data == COMMAND:
                    COMMAND_STRUCT = [inter.data]
                    break
                COMMAND_STRUCT = [inter.data, COMMAND]
                break
            for option in COMMAND.options:
                if option.options:
                    COMMAND_STRUCT.append(option)
                    do_break = False
                elif option.type in [
                    OptionType.sub_command_group,
                    OptionType.sub_command,
                ]:
                    COMMAND_STRUCT.append(option)
                else:
                    do_break = True
                    break
            if do_break:
                break

        COMMAND_NAME = " ".join([command.name for command in COMMAND_STRUCT])

        try:
            self.total_commands_ran[inter.guild.id] += 1
        except KeyError:
            self.total_commands_ran[inter.guild.id] = 1

        if self.commands_ran.get(inter.guild.id) is None:
            self.commands_ran[inter.guild.id] = {}

        try:
            self.commands_ran[inter.guild.id][COMMAND_NAME] += 1
        except KeyError:
            self.commands_ran[inter.guild.id][COMMAND_NAME] = 1