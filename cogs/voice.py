from pprint import pprint
import yt_dlp
import discord
import asyncio
import youtube_dl
from discord.ext import commands
from discord.utils import get
import json

servers = {}
youtube_dl.utils.bug_reports_message = lambda: ''


ydl_opts = {
    'format': 'bestaudio',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn',
    'before_options':
    '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
}

ytdl = yt_dlp.YoutubeDL(ydl_opts)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=1):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False, play=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor( None, lambda: ytdl.extract_info(url, download=not stream or play))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


def checkBan(msgAuthorId):
    with open('banlist.json', 'r') as f:
        banlist = json.load(f)
    return True if msgAuthorId in banlist['banlist'] else False


class Voice(commands.Cog):
    def __init__(self, client):
        self.client = client
        cur_song_id = 0
        self.cur_song_id = cur_song_id

    @commands.command(pass_context=True)
    async def join(self, ctx):
        if not ctx.message.author.voice:
            await ctx.send("You are not connected to a voice channel!")
            return

        elif ctx.voice_client and ctx.voice_client.is_connected():
            print('Already connected to voice')
            pass

        else:
            channel = ctx.message.author.voice.channel
            await ctx.send(f'Connected to ``{channel}``')
            await channel.connect()

    @commands.command(pass_context=True, case_insensitive=True, aliases=['p', 'P'])
    async def play(self, ctx, *, url):
        if checkBan(ctx.message.author.id):
            await ctx.send("Madda kudu ra munda")
            return 
        try:
            server_id = ctx.message.guild.id
            async with ctx.typing():
                song = await YTDLSource.from_url(url, loop=self.client.loop, stream=True)
                servers.setdefault(server_id, []).append(song)
                if len(servers[server_id]) > 1:
                    await ctx.send(f'Added **{song.title}** to queue')
                    return    
            self.cur_song_id = 0
            if not ctx.voice_client.is_playing():
                # runs startPlaying synchronously
                await self.startPlaying(ctx, servers[server_id], self.cur_song_id)
                # Uncomment below code to run startPlaying in a separate thread.
                # asyncio.get_event_loop().create_task(
                #     self.startPlaying(ctx, servers[server_id],
                #                         self.cur_song_id))
        except Exception as e:
            print(e)
            await ctx.send("Somenthing went wrong - please try again later!")

    async def startPlaying(self, ctx, queue, number):
        self.cur_song_id = number
        song = queue[number]
        await ctx.send(f'**Now Playing:** {song.title}')
        ctx.voice_client.play(song, after=lambda e: asyncio.run_coroutine_threadsafe(self.startPlaying(ctx, queue, self.cur_song_id + 1), self.client.loop))
        

    @commands.command(pass_context=True, aliases=["pp"], case_insensitive=True)
    async def pause(self, ctx):
        if checkBan(ctx.message.author.id):
            await ctx.send("Madda kudu ra munda")
        else:
            voice = get(self.client.voice_clients, guild=ctx.guild)

            voice.pause()

            user = ctx.message.author.mention
            await ctx.send(f"Bot was paused by {user}")

    @commands.command(pass_context=True, aliases=["r", "res", "rp"], case_insensitive=True)
    async def resume(self, ctx):
        voice = get(self.client.voice_clients, guild=ctx.guild)

        voice.resume()

        user = ctx.message.author.mention
        await ctx.send(f"Bot was resumed by {user}")

    @commands.command(pass_context=True, aliases=["rq"])
    async def remove_queue(self, ctx, number):
        a = ctx.message.guild.id
        b = servers[a]
        del (b[int(number)])
        if len(b) < 1:
            await ctx.send("Your queue is empty now!")
        else:
            await ctx.send(f'Your queue is now {b}')

    @commands.command(pass_context=True, aliases=["cq"], case_insensitive=True)
    async def clear_queue(self, ctx):
        a = ctx.message.guild.id
        del servers[a]
        user = ctx.message.author.mention
        await ctx.send(f"The queue was cleared by {user}")

    @commands.command(pass_context=True, aliases=["q"], case_insensitive=True)
    async def view_queue(self, ctx):
        try:
            queue = servers[ctx.message.guild.id]
            if len(queue) > 0:
                embed = (discord.Embed(title='Your current Queue',
                                       description='```\n\n```'.join(
                                           [song.title for song in queue]),
                                       color=discord.Color.orange()))
                await ctx.send(embed=embed)

                # await ctx.send('\n'.join([song.title for song in queue]))
            else:
                await ctx.send("The queue is empty - nothing to see here!")

        except Exception:
            await ctx.send(f"The queue is empty - nothing to see here!")

    @commands.command(pass_context=True, aliases=["disconnect", "quit", "get out", "stop"], case_insensitive=True)
    async def leave(self, ctx):
        if checkBan(ctx.message.author.id):
            await ctx.send("Madda kudu ra munda")
        else:
            try:
                a = ctx.message.guild.id
                del servers[a]
            except KeyError:
                print(f"{a}'s queue doesn't exist.")
            finally:
                self.cur_song_id = 0
                voice_client = ctx.message.guild.voice_client
                user = ctx.message.author
                await voice_client.disconnect()
                await ctx.send(f'Disconnected from ``{user.voice.channel}``')

    @commands.command(pass_context=True, aliases=["s", "next"], case_insensitive=True)
    async def skip(self, ctx):
        server_id = ctx.message.guild.id
        self.cur_song_id=self.cur_song_id+1
        if self.cur_song_id > len(servers[server_id]) - 1:
            self.cur_song_id = 0
        ctx.voice_client.stop()
        await self.startPlaying(ctx, servers[server_id], self.cur_song_id)

    @commands.command(pass_context=True, aliases=["previous", "back"], case_insensitive=True)
    async def prev(self, ctx):
        server_id = ctx.message.guild.id
        self.cur_song_id=self.cur_song_id-1
        if self.cur_song_id < 0:
            self.cur_song_id = len(servers[server_id])-1
        ctx.voice_client.pause()
        print(self.cur_song_id)
        await self.startPlaying(ctx, servers[server_id], self.cur_song_id)

    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError(
                    "Author not connected to a voice channel.")


async def setup(client):
    await client.add_cog(Voice(client))

