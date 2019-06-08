import aiohttp
import discord
from redbot.core import commands

__author__="kennnyshiwa and Beryju"

class ARKCog(commands.Cog):
    """ARK lookup Cog"""

    special_queries = {
        '@everyone': "Hah. Nice try. Being very funny. Cheeky cunt.",
        '@here': "You thought this would work too, very funny",
        ':(){ :|: & };: -': "This is a python bot, not a bash bot you nimwit."
    }

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)

    @staticmethod
    async def do_lookup(query: str) -> dict:
        """Run the actual ARK lookup"""
        base_url = ("https://odata.intel.com/API/v1_0/Products/Processors()?&$filter="
                    "substringof(%%27%s%%27,ProductName)&$format=json")

        async with aiohttp.ClientSession() as session:
            async with session.get(base_url % query) as r:
                data = await r.json()
                if not data.get("d"):
                    return None
                return data.get("d")[0]

    def escape_query(self, query) -> str:
        """Escape mentions from queries"""
        return query.replace('`', "'")

    @commands.bot_has_permissions(embed_links=True)
    @commands.command()
    async def ark(self, ctx, *, query):
        """
            Search for `query` on Intel's ARK. By default shows the following attributes:

                - ProductName
                - ClockSpeed
                - ClockSpeedMax
                - CoreCount
                - ThreadCount
                - VTD
                - AESTech
                -MemoryTypes
                -ECCMemory
                -MaxMem

            Reference of fields can be found here: https://odata.intel.com/
        """
        author = ctx.author.mention
        async with ctx.typing():
            query = self.escape_query(''.join(query))
            # Check special queries first
            if query in self.special_queries:
                await ctx.send(self.special_queries[query])
                return
            if query == author:
                await ctx.send("Go to google if you want to search yourself")
                return
            cpu_data = await self.do_lookup(query)
            if not cpu_data:
                await ctx.send("I couldn't find anything matching `%s`" % query)
                return
            fields = ['ProductName', 'ClockSpeed', 'ClockSpeedMax',
                    'CoreCount', 'ThreadCount', 'VTD', 'AESTech',
                    'MemoryTypes', 'ECCMemory', 'MaxMem']

         # Create embedded message
            embed = discord.Embed(
                title="ARK Search Result",
                description="Query was `%s`" % query,
                color=await ctx.embed_color()
            )
            for field in fields:
                if not cpu_data[field]:
                    embed.add_field(name=field, value="Not Available", inline=True)
                else:
                    embed.add_field(name=field, value=cpu_data[field], inline=True)
            await ctx.send(embed=embed)

    def cog_unload(self):
        self.bot.loop.create_task(self.session.close())