import re
import disnake
import lavalink
from disnake.ext import commands
from lavalink.filters import LowPass
from colorama import Fore, Back, Style
from lavalink.events import TrackStartEvent, QueueEndEvent
from lavalink.errors import ClientError
from lavalink.filters import LowPass
from lavalink.server import LoadType

url_rx = re.compile(r'https?://(?:www\.)?.+')

class LavalinkVoiceClient(disnake.VoiceClient):
    """This is the preferred way to handle external voice sending."""

    def __init__(self, client: disnake.Client, channel: disnake.abc.Connectable):
        self.client = client
        self.channel = channel
        if hasattr(self.client, 'lavalink'):
            self.lavalink = self.client.lavalink
        else:
            self.client.lavalink = lavalink.Client(client.user.id)
            self.client.lavalink.add_node(
                '185.228.1.211',
                8080,
                'youshallnotpass',
                'eu',
                'default-node'
            )
            self.lavalink = self.client.lavalink

    async def on_voice_server_update(self, data):
        lavalink_data = {'t': 'VOICE_SERVER_UPDATE', 'd': data}
        await self.lavalink.voice_update_handler(lavalink_data)

    async def on_voice_state_update(self, data):
        lavalink_data = {'t': 'VOICE_STATE_UPDATE', 'd': data}
        await self.lavalink.voice_update_handler(lavalink_data)

    async def connect(self, *, timeout: float, reconnect: bool, self_deaf: bool = False, self_mute: bool = False) -> None:
        self.lavalink.player_manager.create(guild_id=self.channel.guild.id)
        await self.channel.guild.change_voice_state(channel=self.channel, self_mute=self_mute, self_deaf=self_deaf)

    async def disconnect(self, *, force: bool = False) -> None:
        player = self.lavalink.player_manager.get(self.channel.guild.id)
        if not force and not player.is_connected:
            return
        await self.channel.guild.change_voice_state(channel=None)
        player.channel_id = None
        self.cleanup()

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not hasattr(bot, 'lavalink'):
            bot.lavalink = lavalink.Client(1231703300332716124)
            bot.lavalink.add_node('185.228.1.211', 8080, 'youshallnotpass', 'eu', 'default-node')
        self.lavalink: lavalink.Client = bot.lavalink
        self.lavalink.add_event_hooks(self)

    def cog_unload(self):
        self.bot.lavalink._event_hooks.clear()

    async def cog_before_invoke(self, ctx):
        guild_check = ctx.guild is not None
        if guild_check:
            await self.ensure_voice(ctx)
        return guild_check

    async def cog_before_slash_command_invoke(self, ctx):
        guild_check = ctx.guild is not None
        if guild_check:
            await self.ensure_voice(ctx)
        return guild_check

    async def cog_command_error(self, ctx : disnake.ApplicationCommandInteraction , error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.response.send_message(error.original)

    async def ensure_voice(self, inter: disnake.ApplicationCommandInteraction):
        player = self.bot.lavalink.player_manager.create(inter.guild.id)
        should_connect = inter.application_command.name in ('play',)
        if not inter.author.voice or not inter.author.voice.channel:
            raise commands.CommandInvokeError('Join a voicechannel first.')
        v_client = inter.guild.voice_client
        if not v_client:
            if not should_connect:
                raise commands.CommandInvokeError('Not connected.')
            permissions = inter.author.voice.channel.permissions_for(inter.me)
            if not permissions.connect or not permissions.speak:
                print(Fore.RED+"[ bitch i dont have perms ]")
                raise commands.CommandInvokeError('I need the `CONNECT` and `SPEAK` permissions.')
            player.store('channel', inter.channel.id)
            await inter.author.voice.channel.connect(cls=LavalinkVoiceClient)
        else:
            if v_client.channel.id != inter.author.voice.channel.id:
                raise commands.CommandInvokeError('You need to be in my voicechannel.')

    @lavalink.listener(TrackStartEvent)
    async def on_track_start(self, event: TrackStartEvent):
        player = event.player
        track = event.track
        guild_id = event.player.guild_id
        channel_id = event.player.fetch('channel')
        guild = self.bot.get_guild(guild_id)
        track_info = await player.node.decode_track(track.track)
        track_title = track_info['title']
        track_uri = track_info['uri']



        if not guild:
            return await self.lavalink.player_manager.destroy(guild_id)

        channel = guild.get_channel(channel_id)

        d = disnake.Embed(
                title="Now Playing",
                description=f'[{track_title}]({track_uri})',
                color=disnake.Color.green()
            )


        if channel:
         await channel.send(embed=d)

            
    async def track_hook(self, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            print(Fore.RED+"[ queue ended ]")
            guild_id = event.player.guild_id
            guild = self.bot.get_guild(guild_id)
            await guild.voice_client.disconnect(force=True)
        elif isinstance(event, lavalink.events.TrackStartEvent):
            print(Fore.GREEN+"[ tracked started ]")
            player = event.player
            track = event.track
            track_info = await player.node.decode_track(track.track)
            track_title = track_info['title']
            track_uri = track_info['uri']

            guild = self.bot.get_guild(player.guild_id)
            channel_id = player.fetch('channel')
            channel = guild.get_channel(channel_id)

            now_playing_embed = disnake.Embed(
                title="Now Playing",
                description=f'[{track_title}]({track_uri})',
                color=disnake.Color.green()
            )
            await channel.send(embed=now_playing_embed)

    @commands.slash_command(description="Base autoresponder command")
    async def music(self, ctx: disnake.ApplicationCommandInteraction):
        pass
    @commands.slash_command(description="Base autoresponder command for fliters")
    async def filters(self, ctx: disnake.ApplicationCommandInteraction):
        pass

    @filters.sub_command()
    async def lowpass(self, inter: disnake.ApplicationCommandInteraction, strength: float):
        """Sets the strength of the low pass filter."""
        player = self.bot.lavalink.player_manager.get(inter.guild.id)
        strength = max(0.0, strength)
        strength = min(100, strength)
        embed = disnake.Embed(color=disnake.Color.blurple(), title='Low Pass Filter')
        if strength == 0.0:
            await player.remove_filter('lowpass')
            embed.description = 'Disabled **Low Pass Filter**'
            return await inter.response.send_message(embed=embed)
        low_pass = LowPass()
        low_pass.update(smoothing=strength)
        await player.set_filter(low_pass)
        embed.description = f'Set **Low Pass Filter** strength to {strength}.'
        await inter.response.send_message(embed=embed)

    @music.sub_command()
    async def disconnect(self, inter: disnake.ApplicationCommandInteraction):
        """Disconnects the player from the voice channel and clears its queue."""
        player = self.bot.lavalink.player_manager.get(inter.guild.id)
        if not inter.guild.voice_client:
            return await inter.response.send_message('Not connected.')
        if not inter.author.voice or (player.is_connected and inter.author.voice.channel.id != int(player.channel_id)):
            return await inter.response.send_message('You\'re not in my voicechannel!')
        player.queue.clear()
        await player.stop()
        await inter.guild.voice_client.disconnect(force=True)
        await inter.response.send_message('*⃣ | Disconnected.')

    @music.sub_command()
    async def skip(self, inter: disnake.ApplicationCommandInteraction):
        """Skips the current track."""
        player = self.bot.lavalink.player_manager.get(inter.guild_id)
        
        # Check if the user is in the same voice channel as the bot
        if not inter.author.voice or (player.is_connected and inter.author.voice.channel.id != int(player.channel_id)):
            return await inter.response.send_message('You\'re not in my voicechannel!')

        await player.skip()
        
        # Get information about the new track
        if player.queue:
            next_track = player.queue[0]
            next_track_info = await player.node.decode_track(next_track.track)
            next_track_title = next_track_info['title']
            next_track_uri = next_track_info['uri']
            
            
        else:
            await inter.response.send_message("There are no more tracks in the queue.")

    @music.sub_command()
    async def play(self, inter: disnake.ApplicationCommandInteraction, *, query: str):
        """Searches and plays a song from a given query."""
        player = self.bot.lavalink.player_manager.get(inter.guild.id)
        query = query.strip('<>')

        if not url_rx.match(query):
            query = f'ytsearch:{query}'

        results = await player.node.get_tracks(query)
        if not results or not results['tracks']:
            await inter.response.send_message('Nothing found!')
            return

        if results['load_type'] == "PLAYLIST":
            tracks = results['tracks']
            for track in tracks:
                player.add(requester=inter.user.id, track=track)

            if not player.is_playing:
                await player.play()
                now_playing_embed = disnake.Embed(
                    title="Playlist Started",
                    description=f'Now playing: {tracks[0]["info"]["author"]} - [{tracks[0]["info"]["title"]}]({tracks[0]["info"]["uri"]}) added by [{inter.user.mention}]',
                    color=disnake.Color.green()
                )
                await inter.response.send_message(embed=now_playing_embed)
        else:
            track = results['tracks'][0]

            seconds, track.duration = divmod(track.duration, 1000)
            minutes, seconds = divmod(seconds, 60)

            track = lavalink.AudioTrack(track, inter.user.id, recommended=True)
            player.add(requester=inter.user.id, track=track)
            if not player.is_playing:
                await player.play()
                now_playing_embed = disnake.Embed(
                    title="Now Playing",
                    description=f'[{track.title}]({track.uri})',
                    color=disnake.Color.green()
                )
                await inter.response.send_message(embed=now_playing_embed)
            else:
                queue_embed = disnake.Embed(
                    title="Track Added to Queue",
                    description=f'[{track.title}]({track.uri}) has been added to the queue.',
                    color=disnake.Color.orange()
                )
                await inter.response.send_message(embed=queue_embed)


def setup(bot):
  bot.add_cog(Music(bot))
print(Style.BRIGHT + Fore.GREEN + "Music cog loaded")


