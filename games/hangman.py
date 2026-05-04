"""
Hangman — adapted from itspyguru/Python-Games/Hangman
Uses word list extracted from the original words.txt file.
"""
import discord
from discord.ext import commands
import asyncio
import random

# Words extracted from itspyguru/Python-Games/Hangman/words.txt
WORDS = [
    "Revenge", "Tough", "Cost", "Spoil", "Goal", "Praise", "Tolerate",
    "Irritate", "Honest", "Neighbour", "Exception", "Imitate", "Violence",
    "Intention", "Illusion", "Willpower", "Flexible", "Lucky", "Wicked",
    "Enemy", "Effect", "Demand", "Accurate", "Arrogant", "Hesitate",
    "Stubborn", "Rotten", "Ultimate", "Innocent", "Guilty", "Faithful",
    "Blame", "Destroy", "Burden", "Justify", "Wise", "Priority", "Regular",
    "Risky", "Achieve", "Balance", "Curious", "Generous", "Patient",
    "Creative", "Sincere", "Humble", "Courageous", "Ambitious", "Diligent",
    "Resilient", "Persistent", "Optimistic", "Passionate", "Responsible",
    "Determined", "Confident", "Reliable", "Compassionate", "Authentic",
]

HANGMAN_STAGES = [
    # 0 wrong
    "```\n"
    "  +---+\n"
    "  |   |\n"
    "      |\n"
    "      |\n"
    "      |\n"
    "      |\n"
    "=========```",
    # 1 wrong
    "```\n"
    "  +---+\n"
    "  |   |\n"
    "  O   |\n"
    "      |\n"
    "      |\n"
    "      |\n"
    "=========```",
    # 2 wrong
    "```\n"
    "  +---+\n"
    "  |   |\n"
    "  O   |\n"
    "  |   |\n"
    "      |\n"
    "      |\n"
    "=========```",
    # 3 wrong
    "```\n"
    "  +---+\n"
    "  |   |\n"
    "  O   |\n"
    " /|   |\n"
    "      |\n"
    "      |\n"
    "=========```",
    # 4 wrong
    "```\n"
    "  +---+\n"
    "  |   |\n"
    "  O   |\n"
    " /|\\  |\n"
    "      |\n"
    "      |\n"
    "=========```",
    # 5 wrong
    "```\n"
    "  +---+\n"
    "  |   |\n"
    "  O   |\n"
    " /|\\  |\n"
    " /    |\n"
    "      |\n"
    "=========```",
    # 6 wrong — dead
    "```\n"
    "  +---+\n"
    "  |   |\n"
    "  O   |\n"
    " /|\\  |\n"
    " / \\  |\n"
    "      |\n"
    "=========```",
]

MAX_WRONG = 6

class HangmanGame:
    def __init__(self, word: str, player: discord.Member):
        self.word = word.upper()
        self.player = player
        self.guessed: set[str] = set()
        self.wrong: int = 0
        self.over = False

    @property
    def display_word(self):
        return " ".join(c if c in self.guessed else "_" for c in self.word)

    @property
    def won(self):
        return all(c in self.guessed for c in self.word)

    def guess(self, letter: str) -> str:
        letter = letter.upper()
        if letter in self.guessed:
            return "already"
        self.guessed.add(letter)
        if letter not in self.word:
            self.wrong += 1
            return "wrong"
        return "correct"

    def build_embed(self, status: str = None):
        wrong_remaining = MAX_WRONG - self.wrong
        color = 0x57F287 if self.won else (0xED4245 if self.wrong >= MAX_WRONG else 0x5865F2)
        embed = discord.Embed(title="🪢 Hangman", color=color)
        embed.description = HANGMAN_STAGES[self.wrong]
        embed.add_field(name="Word", value=f"`{self.display_word}`", inline=False)
        embed.add_field(
            name="Guessed Letters",
            value=" ".join(sorted(self.guessed)) or "None yet",
            inline=True
        )
        embed.add_field(name="Wrong Guesses", value=f"{self.wrong}/{MAX_WRONG}", inline=True)
        if status:
            embed.add_field(name="Status", value=status, inline=False)
        embed.set_footer(text=f"Player: {self.player.display_name} • Type a letter to guess!")
        return embed

active_hangman: dict[int, HangmanGame] = {}

class Hangman(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="hangman", aliases=["hm"])
    async def hangman(self, ctx):
        if ctx.channel.id in active_hangman:
            return await ctx.send("❌ A Hangman game is already running here! Finish it first.")

        word = random.choice(WORDS)
        game = HangmanGame(word, ctx.author)
        active_hangman[ctx.channel.id] = game

        await ctx.send(embed=game.build_embed("🎮 Game started! Type a single letter to guess."))

        while not game.over:
            def check(m):
                return (
                    m.author == game.player
                    and m.channel == ctx.channel
                    and len(m.content) == 1
                    and m.content.isalpha()
                )

            try:
                msg = await self.bot.wait_for("message", timeout=60.0, check=check)
            except asyncio.TimeoutError:
                game.over = True
                del active_hangman[ctx.channel.id]
                await ctx.send(
                    embed=game.build_embed(f"⏰ Timed out! The word was **{game.word}**."),
                )
                return

            result = game.guess(msg.content)

            if result == "already":
                await ctx.send(f"⚠️ You already guessed `{msg.content.upper()}`!", delete_after=4)
                continue

            if game.won:
                game.over = True
                del active_hangman[ctx.channel.id]
                await ctx.send(embed=game.build_embed(f"🎉 You won! The word was **{game.word}**!"))
                return

            if game.wrong >= MAX_WRONG:
                game.over = True
                del active_hangman[ctx.channel.id]
                await ctx.send(embed=game.build_embed(f"💀 Game over! The word was **{game.word}**."))
                return

            tip = "✅ Correct!" if result == "correct" else "❌ Wrong guess!"
            await ctx.send(embed=game.build_embed(tip))

    @commands.command(name="hangmanstop", aliases=["hmstop"])
    async def hangman_stop(self, ctx):
        if ctx.channel.id not in active_hangman:
            return await ctx.send("No Hangman game running here.")
        game = active_hangman.pop(ctx.channel.id)
        game.over = True
        await ctx.send(f"🛑 Game stopped. The word was **{game.word}**.")

async def setup(bot):
    await bot.add_cog(Hangman(bot))
