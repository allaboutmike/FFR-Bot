import random
from urllib.parse import parse_qs, urlparse

from discord.ext import commands

from races.races import Races, is_race_room
from races.async_races import AsyncRaces
import constants

class RacesCommon(commands.Cog):
    """
    Class to manage races, and coordinate common commands    
    """

    def __init__(self, bot, races, async_races):
        self.bot = bot
        # Races manager will also create and hold onto the two other races
        self.races = races
        self.async_races = async_races


    @commands.command(aliases=["s", "spec"])
    async def spectate(self, ctx):
        if is_race_room(ctx):
            await self.races.spectate(ctx, -1)
            return
        await self.async_races.spectate(ctx)

    @commands.command(aliases=["ff"])
    async def forfeit(self, ctx):
        if is_race_room(ctx):
            await self.races.forfeit(ctx)
            return
        await self.async_races.forfeit(ctx)

    @commands.command(
        aliases=["ff1url", "ff1roll", "ffrroll", "rollseedurl", "roll_ffr_url_seed"]
    )
    async def ffrurl(self, ctx, url):
        if not ctx.channel.name in constants.call_for_race_channels and not is_race_room(ctx):
            return

        user = ctx.author
        if url is None:
            await user.send("You need to supply the url to roll a seed for.")
            return

        parsed = urlparse(url)
        flags = parse_qs(parsed.query)["f"][0]

        msg = await ctx.channel.send(
            self.flagseedgen(
                flags,
                parsed.hostname,
            )
        )
        await msg.pin()

    def flagseedgen(self, flags, site):
        seed = random.randint(0, 4294967295)
        url = "<https://" + site

        url += "/Randomize?s=" + ("{0:-0{1}x}".format(seed, 8)) + "&f=" + flags

        url += ">"
        return url

    @commands.command()
    async def ff1seed(self, ctx):
        if not ctx.channel.name in constants.call_for_race_channels and not is_race_room(ctx):
            return

        await ctx.channel.send("{0:-0{1}x}".format(random.randint(0, 4294967295), 8))
