"""
Minesweeper — adapted from itspyguru/Python-Games/MineSweeper
Uses Discord spoiler tags so cells are hidden until clicked.
"""
import discord
from discord.ext import commands
import random

MINE = "💣"
NUMBERS = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣"]

class Minesweeper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="minesweeper", aliases=["ms"])
    async def minesweeper(self, ctx, rows: int = 8, cols: int = 8, mines: int = 10):
        rows = max(4, min(rows, 12))
        cols = max(4, min(cols, 10))
        mines = max(1, min(mines, rows * cols - 1))

        # Place mines
        all_cells = [(r, c) for r in range(rows) for c in range(cols)]
        mine_cells = set(map(tuple, random.sample(all_cells, mines)))

        def count_adj(r, c):
            count = 0
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    if (r + dr, c + dc) in mine_cells:
                        count += 1
            return count

        # Build board string using Discord spoiler tags ||emoji||
        lines = []
        for r in range(rows):
            row = ""
            for c in range(cols):
                if (r, c) in mine_cells:
                    cell = MINE
                else:
                    n = count_adj(r, c)
                    cell = NUMBERS[n]
                row += f"||{cell}||"
            lines.append(row)

        board_str = "\n".join(lines)

        # Check message length — Discord limit 2000 chars
        if len(board_str) > 1900:
            return await ctx.send("❌ Board too large! Try smaller dimensions.")

        embed = discord.Embed(
            title="💣 Minesweeper",
            description=board_str,
            color=0xEB459E
        )
        embed.add_field(name="Grid", value=f"{rows}×{cols}", inline=True)
        embed.add_field(name="Mines", value=str(mines), inline=True)
        embed.set_footer(text="Tap the spoiler cells to reveal them! Avoid the 💣")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Minesweeper(bot))
