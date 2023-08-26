import json
import os
import discord
from discord.ext import commands
# from keep_alive import keep_alive
import asyncio
import subprocess

def get_prefix(client, message):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)
    return prefixes[str(message.guild.id)]


client = commands.Bot(command_prefix=get_prefix, intents=discord.Intents.all())


@client.event
async def on_guild_join(guild):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)
    prefixes[str(guild.id)] = '-'

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)


@client.event
async def on_guild_remove(guild):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)
    prefixes.pop[str(guild.id)]

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)


@client.command()
async def changeprefix(ctx, prefix):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)
        prefixes[str(ctx.guild.id)] = prefix

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

    await ctx.send(f'Prefix has been changed to {prefix}')


@client.command()
async def load(ctx, extension):
    await client.load_extension(f'cogs.{extension}')


@client.command()
async def unload(ctx, extension):
    await client.unload_extension(f'cogs.{extension}')


@client.command()
async def reload(ctx, extension):
    await client.unload_extension(f'cogs.{extension}')
    await client.load_extension(f'cogs.{extension}')


async def load_extensions():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await client.load_extension(f'cogs.{filename[:-3]}')


@commands.Cog.listener()
async def on_ready(self):
    print(f'Logged in as {self.client.name}'.format(self.client.name))


async def main():
    async with client:
        await load_extensions()
        try:
            # await client.start(os.environ.get('token'))
            await client.start('ODg4MjM4OTY4NzI0OTIyNDAx.GYclTO.6GzmHK0yXB0WV5WGAkcyuUpKXkoiNBkqz98db8')
        except discord.errors.HTTPException as e:
            print('executing kill 1')
            print(e)
            # p = subprocess.run(("kill", "1"))
            # p.wait()


# keep_alive()
asyncio.run(main(debug=True))

# try:
#     client.run(os.environ['token'])
# except:
#     print('executing kill 1')
#     os.system.execute('kill 1')
