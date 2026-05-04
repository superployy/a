"""
Rock Paper Scissors — adapted from itspyguru/Python-Games/Rock Paper Scissor
Discord single-command version vs the bot.
"""
import discord
from discord.ext import commands
import random

CHOICES = {"rock": "🪨", "paper": "📄", "scissors": "✂️"}
BEATS = {"rock": "scissors", "paper": "rock", "scissors": "paper"}

class RockPaperScissors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="rps")
    async def rps(self, ctx, choice: str = None):
        choice = (choice or "").lower()
        if choice not in CHOICES:
            return await ctx.send(
                f"❌ Invalid choice! Use: `!rps rock`, `!rps paper`, or `!rps scissors`"
            )

        bot_choice = random.choice(list(CHOICES.keys()))

        player_emoji = CHOICES[choice]
        bot_emoji = CHOICES[bot_choice]

        if choice == bot_choice:
            result = "🤝 It's a tie!"
            color = 0xFEE75C
        elif BEATS[choice] == bot_choice:
            result = "🎉 You win!"
            color = 0x57F287
        else:
            result = "💀 Bot wins!"
            color = 0xED4245

        embed = discord.Embed(title="🪨 Rock Paper Scissors ✂️", color=color)
        embed.add_field(name=f"You", value=f"{player_emoji} {choice.capitalize()}", inline=True)
        embed.add_field(name="vs", value="⚔️", inline=True)
        embed.add_field(name="Bot", value=f"{bot_emoji} {bot_choice.capitalize()}", inline=True)
        embed.add_field(name="Result", value=result, inline=False)
        embed.set_footer(text="Play again with !rps <rock|paper|scissors>")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(RockPaperScissors(bot))
