"""
Snake — adapted from itspyguru/Python-Games/Snake
Discord text-based version: players collect food on a mini ASCII grid,
scored by how many they collect before hitting a wall or themselves.
Persistent leaderboard stored in a JSON file.
"""
import discord
from discord.ext import commands
import asyncio
import random
import json
import os

LEADERBOARD_FILE = "snake_scores.json"

UP = "⬆️"
DOWN = "⬇️"
LEFT = "⬅️"
RIGHT = "➡️"
DIRECTIONS = [UP, DOWN, LEFT, RIGHT]

DIR_MAP = {
    UP: (0, -1),
    DOWN: (0, 1),
    LEFT: (-1, 0),
    RIGHT: (1, 0),
}
OPPOSITE = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}

SNAKE_HEAD = "🟢"
SNAKE_BODY = "🟩"
FOOD = "🍎"
EMPTY = "⬛"

GRID_W = 7
GRID_H = 6

def load_scores() -> dict:
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE) as f:
            return json.load(f)
    return {}

def save_scores(scores: dict):
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(scores, f)

def get_leaderboard():
    scores = load_scores()
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)

class SnakeGame:
    def __init__(self):
        cx, cy = GRID_W // 2, GRID_H // 2
        self.snake = [(cx, cy), (cx - 1, cy)]  # head first
        self.direction = RIGHT
        self.score = 0
        self.over = False
        self.food = self._spawn_food()

    def _spawn_food(self):
        free = [
            (x, y)
            for x in range(GRID_W)
            for y in range(GRID_H)
            if (x, y) not in self.snake
        ]
        return random.choice(free) if free else None

    def move(self, direction: str) -> bool:
        if direction == OPPOSITE[self.direction]:
            direction = self.direction  # ignore reverse
        self.direction = direction

        dx, dy = DIR_MAP[self.direction]
        hx, hy = self.snake[0]
        nx, ny = hx + dx, hy + dy

        if not (0 <= nx < GRID_W and 0 <= ny < GRID_H):
            self.over = True
            return False
        if (nx, ny) in self.snake:
            self.over = True
            return False

        self.snake.insert(0, (nx, ny))
        if (nx, ny) == self.food:
            self.score += 1
            self.food = self._spawn_food()
            if self.food is None:
                self.over = True  # board full — you win!
                return True
        else:
            self.snake.pop()
        return True

    def render(self) -> str:
        grid = [[EMPTY] * GRID_W for _ in range(GRID_H)]
        if self.food:
            fx, fy = self.food
            grid[fy][fx] = FOOD
        for i, (x, y) in enumerate(self.snake):
            grid[y][x] = SNAKE_HEAD if i == 0 else SNAKE_BODY
        return "\n".join("".join(row) for row in grid)

    def build_embed(self, status: str = None):
        color = 0x57F287 if not self.over else 0xED4245
        embed = discord.Embed(title="🐍 Snake", color=color)
        embed.description = self.render()
        embed.add_field(name="Score", value=str(self.score), inline=True)
        embed.add_field(name="Length", value=str(len(self.snake)), inline=True)
        if status:
            embed.add_field(name="Status", value=status, inline=False)
        else:
            embed.set_footer(text="React with arrows to move! You have 10s per turn.")
        return embed

active_snake: dict[int, SnakeGame] = {}

class Snake(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="snake")
    async def snake(self, ctx):
        if ctx.channel.id in active_snake:
            return await ctx.send("❌ A Snake game is already running here!")

        game = SnakeGame()
        active_snake[ctx.channel.id] = game

        msg = await ctx.send(embed=game.build_embed("🎮 Use arrows below to move!"))
        for emoji in DIRECTIONS:
            await msg.add_reaction(emoji)

        while not game.over:
            def check(reaction, user):
                return (
                    user == ctx.author
                    and str(reaction.emoji) in DIRECTIONS
                    and reaction.message.id == msg.id
                )

            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=15.0, check=check)
            except asyncio.TimeoutError:
                game.over = True
                break

            game.move(str(reaction.emoji))
            try:
                await msg.remove_reaction(reaction.emoji, user)
            except Exception:
                pass
            await msg.edit(embed=game.build_embed())

        # Game over
        del active_snake[ctx.channel.id]
        await msg.clear_reactions()

        # Update leaderboard
        scores = load_scores()
        uid = str(ctx.author.id)
        player_name = ctx.author.display_name
        old_score = scores.get(uid, {}).get("score", 0) if isinstance(scores.get(uid), dict) else scores.get(uid, 0)

        # Flatten to simple name:score
        flat = {}
        for k, v in scores.items():
            flat[k] = v if isinstance(v, int) else v.get("score", 0)

        is_pb = game.score > flat.get(uid, 0)
        flat[uid] = max(game.score, flat.get(uid, 0))
        # store display name alongside
        flat[f"name_{uid}"] = player_name
        save_scores(flat)

        pb_str = " 🏆 **New personal best!**" if is_pb else ""
        await msg.edit(
            embed=game.build_embed(f"💀 Game over! Score: **{game.score}**{pb_str}\nUse `!leaderboard` to see rankings.")
        )

async def setup(bot):
    await bot.add_cog(Snake(bot))
