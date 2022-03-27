# -*- coding: utf-8 -*-
#  ----------------------------------------------------------------------------
#  MIT License
#
# Copyright (c) 2022 Bluesy
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#  ----------------------------------------------------------------------------
import json
from datetime import datetime, timezone

import discord
from discord import Embed, Color
from discord.ext import commands
from discord.ext.commands import Cog, Context


class Admin(Cog):
    """Admin Cog"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def cog_check(self, ctx: Context) -> bool:
        """Check to run for all cog commands"""
        if ctx.guild is None:
            return False
        return any(
            role.id in (832521484378308660, 832521484378308659, 832521484378308658)
            for role in ctx.author.roles  # type: ignore
        )

    @commands.command()
    async def ping(self, ctx: Context):
        """Ping Command TO Check Bot Is Alive"""
        await ctx.send(f"Pong! Latency: {self.bot.latency * 1000:.2f}ms")

    @commands.Group
    async def slur(self, ctx: Context):
        """Slur command group"""
        if ctx.invoked_subcommand is None:
            await ctx.send(
                "Invoked slur words group - use `add` to add a word, `remove`"
                " to remove a word, or `query` to get all words on the list."
            )

    @slur.command()
    async def add(self, ctx: Context, *, word: str):
        """Adds a word to the slur list"""
        if ctx.guild.id != 832521484340953088:  # type: ignore
            return
        with open("UBCbot.json", encoding="utf8") as json_dict:
            fulldict = json.load(json_dict)
        joinstring = ", "
        if word.lower() not in fulldict["Words"]:
            fulldict["Words"].append(word.lower()).sort()
            with open("UBCbot.json", "w", encoding="utf8") as json_dict:
                json.dump(fulldict, json_dict)
            await ctx.send(
                embed=Embed(
                    title="New list of words defined as slurs",
                    description=f"||{joinstring.join(fulldict['Words'])}||",
                    color=Color.green(),
                    timestamp=datetime.now(tz=timezone.utc),
                )
            )
        else:
            await ctx.send(
                embed=Embed(
                    title="Word already in list of words defined as slurs",
                    description=f"||{joinstring.join(fulldict['Words'])}||",
                    color=Color.blue(),
                    timestamp=datetime.now(tz=timezone.utc),
                )
            )

    @slur.command()
    async def remove(self, ctx: Context, *, word: str):
        """Removes a word from the slur list"""
        if ctx.guild.id != 832521484340953088:  # type: ignore
            return
        with open("UBCbot.json", encoding="utf8") as file:
            fulldict = json.load(file)
        joinstring = ", "
        if word.lower() in fulldict["Words"]:
            fulldict["Words"].remove(word.lower()).sort()
            await ctx.send(
                embed=Embed(
                    title="New list of words defined as slurs",
                    description=f"||{joinstring.join(fulldict['Words'])}||",
                    color=Color.green(),
                    timestamp=datetime.now(tz=timezone.utc),
                )
            )
            with open("UBCbot.json", "w", encoding="utf8") as file:
                json.dump(fulldict, file)
        else:
            await ctx.send(
                embed=Embed(
                    title="Word not in list of words defined as slurs",
                    description=f"||{joinstring.join(fulldict['Words'])}||",
                    color=Color.blue(),
                    timestamp=datetime.now(tz=timezone.utc),
                )
            )

    @slur.command()
    async def query(self, ctx: Context):
        """Queries the slur list"""
        if ctx.guild.id != 832521484340953088:  # type: ignore
            return
        with open("UBCbot.json", encoding="utf8") as json_dict:
            fulldict = json.load(json_dict)
        joinstring = ", "
        await ctx.send(
            embed=Embed(
                title="List of words defined as slurs",
                description=f"||{joinstring.join(fulldict['Words'])}||",
                color=Color.blue(),
                timestamp=datetime.now(tz=timezone.utc),
            )
        )

    @Cog.listener()
    async def on_message(self, message: discord.Message):
        """On_message func"""
        if (
            message.guild.id != 832521484340953088  # type: ignore
            or message.content is None
        ):
            return
        with open("UBCbot.json", encoding="utf8") as file:
            words: list[str] = json.load(file)["Words"]
        content = message.content.lower().split()
        used_slurs = set()
        joinstring = ", "
        for word in content:
            if word in words:
                used_slurs.add(word)
        if used_slurs != set() and not any(
            role.id in [832521484378308660, 832521484378308659, 832521484378308658]
            for role in message.author.roles  # type: ignore
        ):
            await message.delete()
            await message.author.add_roles(  # type: ignore
                discord.Object(id=900612423332028416),
                discord.Object(id=930953847411736598),
                reason="Used a Slur",
            )
            await (
                await self.bot.fetch_channel(832521484828147741)
            ).send(  # type: ignore
                embed=Embed(
                    title=f"[SLUR] {message.author.name}#"
                    f"{message.author.discriminator}",
                    color=Color.red(),
                    timestamp=datetime.now(tz=timezone.utc),
                )
                .add_field(name="User", value=message.author.mention, inline=True)
                .add_field(
                    name="Slurs Used",
                    value=f"||{joinstring.join(used_slurs)}||",
                    inline=True,
                )
                .add_field(
                    name="Channel", value=f"<#{message.channel.id}>", inline=True
                )
                .add_field(name="Message", value=message.content, inline=True)
            )


async def setup(bot: commands.Bot):
    """Loads Plugin"""
    await bot.add_cog(Admin(bot))
