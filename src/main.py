import asyncio
import logging
import traceback

import os
import redis

from discord.ext import commands
from discord.utils import get

import discord

from misc.misc import MiscCommandCog
from races.races_common import RacesCommon
from races.races import Races
from races.async_races import AsyncRaces
from roles import Roles
from voting.polls import Polls

import constants


# format logging
logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

description = "FFR discord bot"

bot = commands.Bot(
    command_prefix="?", description=description, case_insensitive=True, intents=intents
)

redis_pool = redis.ConnectionPool(
    host=os.environ.get("REDIS_HOST", "localhost"),
    port=int(os.environ.get("REDIS_PORT", "6379")),
    decode_responses=False,
)

redis_races = redis.StrictRedis(connection_pool=redis_pool)
redis_polls = redis.StrictRedis(connection_pool=redis_pool)


@bot.event
async def on_ready():
    logging.info("discord.py version: %s",discord.__version__)
    logging.info("Logged in as")
    logging.info(bot.user.name)
    logging.info(bot.user.id)
    logging.info("------")


def is_admin(ctx):
    user = ctx.author
    return (any(role.name in constants.ADMINS for role in user.roles)) or (
        user.id == int(140605120579764226)
    )


def allow_seed_rolling(ctx):
    return (ctx.channel.name == constants.call_for_races_channel) or (
        ctx.channel.category_id == get(ctx.guild.categories, name="races").id
    )


@bot.event
async def on_command_error(ctx, error):
    poor_soul = bot.get_user(478735647449022482)
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        raise error
    error_msg = "".join(traceback.TracebackException.from_exception(error).format())
    await poor_soul.send(" ".join(["Error in FFRBot!!\n", error_msg]))
    raise error


# used to clear channels for testing purposes

# @bot.command(pass_context = True)
# async def purge(ctx):
#     channel = ctx.message.channel
#     await bot.purge_from(channel, limit=100000)

def handle_exit(client, loop):
    # taken from https://stackoverflow.com/a/50981577
    loop.run_until_complete(client.logout())
    for t in asyncio.Task.all_tasks(loop=loop):
        if t.done():
            t.exception()
            continue
        t.cancel()
        try:
            loop.run_until_complete(asyncio.wait_for(t, 5, loop=loop))
            t.exception()
        except asyncio.InvalidStateError:
            pass
        except asyncio.TimeoutError:
            pass
        except asyncio.CancelledError:
            pass


async def main(client, token):
    await bot.add_cog(MiscCommandCog(bot))
    races = Races(bot, redis_races)
    async_races = AsyncRaces(bot, redis_races)
    await bot.add_cog(RacesCommon(bot, races, async_races))
    await bot.add_cog(races)
    await bot.add_cog(async_races)
    await bot.add_cog(Roles(bot))
    await bot.add_cog(Polls(bot, redis_polls))

    async with client:
        await client.start(token)


with open("token.txt", "r") as f:
    token = f.read()
token = token.strip()

asyncio.run(main(bot, token))
