# 🎮 Discord Python Games Bot

A Discord bot hosting text-based adaptations of games from
[itspyguru/Python-Games](https://github.com/itspyguru/Python-Games),
deployed on Railway.

## Games Included

| Command | Game | Origin |
|---------|------|--------|
| `!ttt @user` | Tic Tac Toe (2-player) | Tic Tac Toe |
| `!hangman` | Hangman (with original word list) | Hangman |
| `!rps rock\|paper\|scissors` | Rock Paper Scissors vs Bot | Rock Paper Scissor |
| `!minesweeper [r] [c] [mines]` | Minesweeper spoiler grid | MineSweeper |
| `!numguess [max]` | Guess the number | Dino (score mechanic) |
| `!snake` | Snake with leaderboard | Snake |
| `!leaderboard` | Top Snake scores | — |

---

## 🚀 Setup

### 1. Create a Discord Bot

1. Go to [discord.com/developers/applications](https://discord.com/developers/applications)
2. Click **New Application** → name it → go to **Bot** tab
3. Click **Reset Token** → copy your token
4. Enable these **Privileged Gateway Intents**:
   - ✅ Message Content Intent
5. Go to **OAuth2 → URL Generator**:
   - Scopes: `bot`
   - Bot Permissions: `Send Messages`, `Read Message History`, `Add Reactions`, `Embed Links`, `Manage Messages`
6. Copy the generated URL and invite the bot to your server

### 2. Local Setup

```bash
git clone <your-repo>
cd discord-games-bot
pip install -r requirements.txt
cp .env.example .env
# Edit .env and paste your DISCORD_TOKEN
python bot.py
```

### 3. Deploy to Railway

1. Push this project to a GitHub repository
2. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**
3. Select your repository
4. Go to your service → **Variables** tab → Add:
   ```
   DISCORD_TOKEN = your_token_here
   ```
5. Railway will auto-detect `Procfile` and deploy! ✅

> **Tip:** Railway gives you 500 free hours/month on the Hobby plan.
> Set the service type to **Worker** (no web server needed).

---

## 📁 Project Structure

```
discord-games-bot/
├── bot.py                  # Main bot entry point
├── games/
│   ├── tictactoe.py        # Tic Tac Toe (reaction-based)
│   ├── hangman.py          # Hangman (original word list)
│   ├── rockpaperscissors.py
│   ├── minesweeper.py      # Discord spoiler cells
│   ├── numguess.py         # Number guessing game
│   └── snake.py            # Snake + leaderboard
├── requirements.txt
├── Procfile                # Railway process definition
├── railway.toml            # Railway config
└── .env.example
```

---

## Adding More Games

Each game is a self-contained Discord.py **Cog**. To add a new game:

1. Create `games/mygame.py` with a `setup(bot)` function
2. Add `"games.mygame"` to the `COGS` list in `bot.py`

---

Built with ❤️ using [discord.py](https://discordpy.readthedocs.io/) and hosted on [Railway](https://railway.app).
