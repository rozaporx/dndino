# D&D Dinosaur Discord Bot

A Discord bot for D&D 5e dinosaur enthusiasts.

## Features
- **!dino <name>**: Look up dinosaur stats.
- **!dinolist**: List all available dinosaurs.
- **!roll <dice>**: Roll dice (e.g., `!roll 1d20+5`).
- **!encounter <min_cr> <max_cr>**: Generate a random dinosaur encounter.
- **!tame <type> <name>**: Tame a dinosaur companion.
- **!companions**: List your tamed companions.
- **!damage <id> <amount>**: Damage a companion.
- **!heal <id> <amount>**: Heal a companion.
- **!release <id>**: Release a companion.

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create a `.env` file from `.env.example` and add your Discord bot token.
3. Run the bot:
   ```bash
   python main.py
   ```
