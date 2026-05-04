"""
Tic Tac Toe — adapted from itspyguru/Python-Games/Tic Tac Toe
2-player Discord version with reaction-based board.
"""
import discord
from discord.ext import commands
import asyncio

EMPTY = "⬜"
X = "❌"
O = "⭕"
NUMBER_EMOJIS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]

WIN_COMBOS = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
    [0, 3, 6], [1, 4, 7], [2, 5, 8],  # cols
    [0, 4, 8], [2, 4, 6]               # diags
]

class TicTacToeGame:
    def __init__(self, player1: discord.Member, player2: discord.Member):
        self.board = [EMPTY] * 9
        self.players = [player1, player2]
        self.symbols = [X, O]
        self.turn = 0
        self.over = False

    @property
    def current_player(self):
        return self.players[self.turn % 2]

    @property
    def current_symbol(self):
        return self.symbols[self.turn % 2]

    def make_move(self, pos: int) -> bool:
        if self.board[pos] != EMPTY:
            return False
        self.board[pos] = self.current_symbol
        self.turn += 1
        return True

    def check_winner(self):
        for combo in WIN_COMBOS:
            vals = [self.board[i] for i in combo]
            if vals[0] != EMPTY and len(set(vals)) == 1:
                return vals[0]
        if EMPTY not in self.board:
            return "draw"
        return None

    def render_board(self):
        rows = []
        for r in range(3):
            row = ""
            for c in range(3):
                idx = r * 3 + c
                cell = self.board[idx]
                row += cell if cell != EMPTY else NUMBER_EMOJIS[idx]
            rows.append(row)
        return "\n".join(rows)

    def build_embed(self, status: str = None):
        embed = discord.Embed(
            title="❌ Tic Tac Toe ⭕",
            color=0x5865F2
        )
        embed.description = self.render_board()
        if status:
            embed.add_field(name="Result", value=status, inline=False)
        else:
            embed.add_field(
                name="Turn",
                value=f"{self.current_symbol} {self.current_player.mention}",
                inline=False
            )
        embed.add_field(
            name="Players",
            value=f"{X} {self.players[0].mention}  vs  {O} {self.players[1].mention}",
            inline=False
        )
        embed.set_footer(text="React with a number to place your mark!")
        return embed

# Active games: channel_id → game
active_games: dict[int, TicTacToeGame] = {}

class TicTacToe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ttt", aliases=["tictactoe"])
    async def ttt(self, ctx, opponent: discord.Member = None):
        if opponent is None:
            return await ctx.send("❌ Usage: `!ttt @opponent`")
        if opponent.bot:
            return await ctx.send("❌ You can't play against a bot!")
        if opponent == ctx.author:
            return await ctx.send("❌ You can't play against yourself!")
        if ctx.channel.id in active_games:
            return await ctx.send("❌ A game is already running in this channel!")

        # Challenge confirmation
        challenge = await ctx.send(
            f"{opponent.mention}, {ctx.author.mention} challenges you to Tic Tac Toe! React ✅ to accept or ❌ to decline."
        )
        await challenge.add_reaction("✅")
        await challenge.add_reaction("❌")

        def check_accept(reaction, user):
            return user == opponent and str(reaction.emoji) in ["✅", "❌"] and reaction.message.id == challenge.id

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=30.0, check=check_accept)
        except asyncio.TimeoutError:
            await challenge.edit(content="⏰ Challenge timed out.")
            return

        if str(reaction.emoji) == "❌":
            return await challenge.edit(content=f"❌ {opponent.display_name} declined the challenge.")

        await challenge.delete()

        game = TicTacToeGame(ctx.author, opponent)
        active_games[ctx.channel.id] = game

        msg = await ctx.send(embed=game.build_embed())
        for emoji in NUMBER_EMOJIS:
            await msg.add_reaction(emoji)

        while not game.over:
            def check_move(reaction, user):
                return (
                    user == game.current_player
                    and str(reaction.emoji) in NUMBER_EMOJIS
                    and reaction.message.id == msg.id
                )

            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check_move)
            except asyncio.TimeoutError:
                game.over = True
                del active_games[ctx.channel.id]
                await msg.edit(embed=game.build_embed(f"⏰ {game.current_player.display_name} timed out! Game over."))
                return

            pos = NUMBER_EMOJIS.index(str(reaction.emoji))

            if not game.make_move(pos):
                # Cell taken — remove their reaction silently
                try:
                    await msg.remove_reaction(reaction.emoji, user)
                except Exception:
                    pass
                continue

            winner_sym = game.check_winner()
            if winner_sym:
                game.over = True
                del active_games[ctx.channel.id]
                if winner_sym == "draw":
                    status = "🤝 It's a draw!"
                else:
                    winner = game.players[game.symbols.index(winner_sym)]
                    status = f"🎉 {winner_sym} **{winner.display_name}** wins!"
                await msg.edit(embed=game.build_embed(status))
                await msg.clear_reactions()
                return

            await msg.edit(embed=game.build_embed())
            try:
                await msg.remove_reaction(reaction.emoji, user)
            except Exception:
                pass

async def setup(bot):
    await bot.add_cog(TicTacToe(bot))
