"""
Number Guess — inspired by the score/run mechanic in itspyguru/Python-Games/Dino
Players keep guessing to beat their high score (streak).
"""
import discord
from discord.ext import commands
import asyncio
import random

active_guesses: dict[int, dict] = {}  # channel_id → game state

class NumberGuess(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="numguess", aliases=["guess", "ng"])
    async def numguess(self, ctx, max_num: int = 100):
        max_num = max(10, min(max_num, 10000))

        if ctx.channel.id in active_guesses:
            return await ctx.send("❌ A guessing game is already running here!")

        secret = random.randint(1, max_num)
        attempts = 0
        game = {"secret": secret, "player": ctx.author, "over": False}
        active_guesses[ctx.channel.id] = game

        embed = discord.Embed(
            title="🎲 Number Guess",
            description=f"I'm thinking of a number between **1** and **{max_num}**!\nType your guess in chat.",
            color=0xF1C40F
        )
        embed.set_footer(text=f"Player: {ctx.author.display_name} • Type 'quit' to stop")
        await ctx.send(embed=embed)

        while not game["over"]:
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            try:
                msg = await self.bot.wait_for("message", timeout=60.0, check=check)
            except asyncio.TimeoutError:
                game["over"] = True
                del active_guesses[ctx.channel.id]
                await ctx.send(f"⏰ Timed out! The number was **{secret}**.")
                return

            content = msg.content.strip().lower()

            if content == "quit":
                game["over"] = True
                del active_guesses[ctx.channel.id]
                await ctx.send(f"🛑 Game stopped. The number was **{secret}**.")
                return

            if not content.isdigit():
                await ctx.send("⚠️ Please type a valid number!", delete_after=4)
                continue

            guess = int(content)
            attempts += 1

            if guess < secret:
                await ctx.send(f"📈 **{guess}** is too low! Try higher. _(Attempt {attempts})_")
            elif guess > secret:
                await ctx.send(f"📉 **{guess}** is too high! Try lower. _(Attempt {attempts})_")
            else:
                game["over"] = True
                del active_guesses[ctx.channel.id]
                rating = "🏆 Perfect!" if attempts == 1 else ("🌟 Amazing!" if attempts <= 5 else ("👍 Nice!" if attempts <= 10 else "✅ Got it!"))
                embed = discord.Embed(
                    title="🎉 Correct!",
                    description=f"The number was **{secret}**!\n{rating}",
                    color=0x57F287
                )
                embed.add_field(name="Attempts", value=str(attempts), inline=True)
                embed.add_field(name="Range", value=f"1–{max_num}", inline=True)
                await ctx.send(embed=embed)
                return

async def setup(bot):
    await bot.add_cog(NumberGuess(bot))
