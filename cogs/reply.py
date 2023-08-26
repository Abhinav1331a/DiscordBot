import datetime
from discord.ext import commands
import json

currentTime = datetime.datetime.now()
currentTime.hour


class reply(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'Pong {round(self.client.latency * 1000)} ms')

    @commands.command(pass_context=True, aliases=["hello", "alfred", "namaste", "good morning", "greetings", "good evening"], case_insensitive=True)
    async def hi(self, ctx):
        await ctx.send('How can I be of service today, Master?')

    @commands.command(pass_context=True, aliases=["buhbye", "tata", "good night"], case_insensitive=True)
    async def bye(self, ctx):
        if currentTime.hour < 18:
            await ctx.send('Very well! See you later Master!')

        if currentTime.hour > 18:
            await ctx.send('Good Night Master!')

    @commands.command()
    async def ban(self, ctx, user):
        user = user.replace('@', '')
        user = user.replace('<', '')
        user = user.replace('>', '')
        with open('banlist.json', 'r') as f:
            banlist = json.load(f)
        if int(user) == 535867927375642654:
            await ctx.send('Asha ki hadhu, gudha ki siggu undali. Erri puvva')
        if int(user) not in banlist['banlist']:
            banlist['banlist'].append(int(user))
        with open('banlist.json', 'w') as f:
            json.dump(banlist, f, indent=4)
        await ctx.send(f'Banned {await self.client.fetch_user(int(user))}')
            
    @commands.command()
    async def unban(self, ctx, user):
        user = user.replace('@', '')
        user = user.replace('<', '')
        user = user.replace('>', '')
        with open('banlist.json', 'r') as f:
            banlist = json.load(f)
        try:
            banlist['banlist'].remove(int(user))
            with open('banlist.json', 'w') as f:
                json.dump(banlist, f, indent=4)
            await ctx.send(
                f'Unbanned {await self.client.fetch_user(int(user))}')
        except ValueError:
            await ctx.send('User not in ban list')

async def setup(client):
    await client.add_cog(reply(client))
