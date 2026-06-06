import discord
import sqlite3
import os
from discord.ext import commands

class Tracking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'database.sqlite')
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS companions
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER,
                      dino_name TEXT,
                      custom_name TEXT,
                      current_hp INTEGER,
                      max_hp INTEGER)''')
        conn.commit()
        conn.close()

    @commands.command(name='tame')
    async def tame_dino(self, ctx, dino_type: str, custom_name: str):
        """Tames a dinosaur and adds it to your companions."""
        # Find the dino type to get max HP
        from cogs.lookup import Lookup
        lookup_cog = self.bot.get_cog('Lookup')
        if not lookup_cog:
            await ctx.send("Lookup system not available.")
            return

        dino = next((d for d in lookup_cog.dinosaurs if d['name'].lower() == dino_type.lower()), None)
        if not dino:
             # Try fuzzy match
            dino = next((d for d in lookup_cog.dinosaurs if dino_type.lower() in d['name'].lower()), None)

        if not dino:
            await ctx.send(f"Unknown dinosaur type: {dino_type}")
            return

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO companions (user_id, dino_name, custom_name, current_hp, max_hp) VALUES (?, ?, ?, ?, ?)",
                  (ctx.author.id, dino['name'], custom_name, dino['hp'], dino['hp']) )
        conn.commit()
        conn.close()

        await ctx.send(f"You have tamed a {dino['name']} named **{custom_name}**!")

    @commands.command(name='companions')
    async def list_companions(self, ctx):
        """Lists your tamed dinosaurs."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT id, dino_name, custom_name, current_hp, max_hp FROM companions WHERE user_id = ?", (ctx.author.id,))
        rows = c.fetchall()
        conn.close()

        if not rows:
            await ctx.send("You don't have any companions yet. Use `!tame <type> <name>` to get one!")
            return

        embed = discord.Embed(title=f"{ctx.author.name}'s Companions", color=discord.Color.blue())
        for row in rows:
            embed.add_field(name=f"{row[2]} ({row[1]})", value=f"HP: {row[3]}/{row[4]} [ID: {row[0]}]", inline=False)
        
        await ctx.send(embed=embed)

    @commands.command(name='damage')
    async def damage_companion(self, ctx, companion_id: int, amount: int):
        """Applies damage to a companion."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT current_hp, custom_name FROM companions WHERE id = ? AND user_id = ?", (companion_id, ctx.author.id))
        row = c.fetchone()
        
        if not row:
            await ctx.send("Companion not found.")
            conn.close()
            return

        new_hp = max(0, row[0] - amount)
        c.execute("UPDATE companions SET current_hp = ? WHERE id = ?", (new_hp, companion_id))
        conn.commit()
        conn.close()

        await ctx.send(f"**{row[1]}** took {amount} damage! HP is now {new_hp}.")

    @commands.command(name='heal')
    async def heal_companion(self, ctx, companion_id: int, amount: int):
        """Heals a companion."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT current_hp, max_hp, custom_name FROM companions WHERE id = ? AND user_id = ?", (companion_id, ctx.author.id))
        row = c.fetchone()
        
        if not row:
            await ctx.send("Companion not found.")
            conn.close()
            return

        new_hp = min(row[1], row[0] + amount)
        c.execute("UPDATE companions SET current_hp = ? WHERE id = ?", (new_hp, companion_id))
        conn.commit()
        conn.close()

        await ctx.send(f"**{row[1]}** healed for {amount}! HP is now {new_hp}.")

    @commands.command(name='release')
    async def release_companion(self, ctx, companion_id: int):
        """Releases a companion."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("DELETE FROM companions WHERE id = ? AND user_id = ?", (companion_id, ctx.author.id))
        conn.commit()
        conn.close()

        await ctx.send(f"Companion released.")

async def setup(bot):
    await bot.add_cog(Tracking(bot))
