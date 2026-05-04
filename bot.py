import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# Load all game cogs
COGS = [
    "games.tictactoe",
    "games.hangman",
    "games.rockpaperscissors",
    "games.minesweeper",
    "games.numguess",
    "games.snake",
]

@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online and ready!")
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name="!help | Python Games"
        )
    )

@bot.command(name="help")
async def help_cmd(ctx):
    embed = discord.Embed(
        title="🎮 Python Games Bot",
        description="Inspired by [itspyguru/Python-Games](https://github.com/itspyguru/Python-Games)\nAll games adapted for Discord!",
        color=0x5865F2
    )
    embed.add_field(
        name="🎯 Games",
        value=(
            "`!ttt @opponent` — Tic Tac Toe (2-player)\n"
            "`!hangman` — Hangman word game\n"
            "`!rps <rock|paper|scissors>` — Rock Paper Scissors vs Bot\n"
            "`!minesweeper [rows] [cols] [mines]` — Minesweeper grid\n"
            "`!numguess [max]` — Guess the number\n"
            "`!snake` — Snake high-score leaderboard game\n"
        ),
        inline=False
    )
    embed.add_field(
        name="📊 Stats",
        value="`!leaderboard` — View top scores",
        inline=False
    )
    embed.set_footer(text="Python Games Bot • Railway Hosted")
    await ctx.send(embed=embed)

@bot.command(name="leaderboard", aliases=["lb", "scores"])
async def leaderboard(ctx):
    from games.snake import load_scores
    raw = load_scores()
    # build list of (display_name, score)
    entries = []
    for k, v in raw.items():
        if k.startswith("name_"):
            continue
        if isinstance(v, int):
            uid = k
            name = raw.get(f"name_{uid}", f"<@{uid}>")
            entries.append((name, v))
    entries.sort(key=lambda x: x[1], reverse=True)
    if not entries:
        return await ctx.send("No scores yet! Play `!snake` to get on the board.")
    embed = discord.Embed(title="🏆 Snake Leaderboard", color=0xF1C40F)
    medals = ["🥇", "🥈", "🥉"]
    desc = ""
    for i, (name, score) in enumerate(entries[:10]):
        medal = medals[i] if i < 3 else f"`{i+1}.`"
        desc += f"{medal} **{name}** — {score} pts\n"
    embed.description = desc
    await ctx.send(embed=embed)

async def main():
    async with bot:
        for cog in COGS:
            await bot.load_extension(cog)
        await bot.start(TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
