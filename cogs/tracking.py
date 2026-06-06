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
                      max_hp INTEGER,
                      status TEXT)''')
        conn.commit()
        conn.close()

    @commands.command(name='transfer', aliases=['tame'])
    async def transfer_consciousness(self, ctx, dino_type: str, custom_name: str):
        """Transfers your consciousness into a juvenile dinosaur."""
        from cogs.lookup import Lookup
        lookup_cog = self.bot.get_cog('Lookup')
        if not lookup_cog:
            await ctx.send("Expedition systems are offline.")
            return

        dino = next((d for d in lookup_cog.dinosaurs if d['name'].lower() == dino_type.lower()), None)
        if not dino:
            dino = next((d for d in lookup_cog.dinosaurs if dino_type.lower() in d['name'].lower()), None)

        if not dino:
            await ctx.send(f"The Year 2148 archives have no record of a '{dino_type}'.")
            return

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO companions (user_id, dino_name, custom_name, current_hp, max_hp, status) VALUES (?, ?, ?, ?, ?, ?)",
                  (ctx.author.id, dino['name'], custom_name, dino['hp'], dino['hp'], "Transferred Consciousness") )
        conn.commit()
        conn.close()

        await ctx.send(f"**CONSCIOUSNESS LINK ESTABLISHED.** You have successfully merged with a juvenile {dino['name']}. You are now known as **{custom_name}**.")

    @commands.command(name='survive')
    async def survive_human(self, ctx, name: str):
        """Register as a human survivor in the prehistoric world."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        # Humans start with standard stats (e.g., 10 HP)
        c.execute("INSERT INTO companions (user_id, dino_name, custom_name, current_hp, max_hp, status) VALUES (?, ?, ?, ?, ?, ?)",
                  (ctx.author.id, "Human", name, 10, 10, "Human Survivor") )
        conn.commit()
        conn.close()

        await ctx.send(f"**LOGGING EXPEDITION DATA.** You have arrived in the Year 2148 past as a human named **{name}**. Good luck surviving the jungle.")

    @commands.command(name='companions', aliases=['status'])
    async def list_companions(self, ctx):
        """Lists your active identities in the Year 2148."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT id, dino_name, custom_name, current_hp, max_hp, status FROM companions WHERE user_id = ?", (ctx.author.id,))
        rows = c.fetchall()
        conn.close()

        if not rows:
            await ctx.send("You are currently in the Year 2148. Use `!transfer` or `!survive` to begin your journey.")
            return

        embed = discord.Embed(title=f"Expedition Log: {ctx.author.name}", color=discord.Color.blue())
        for row in rows:
            status = row[5] if len(row) > 5 else "Active"
            embed.add_field(name=f"{row[2]} ({row[1]})", value=f"**Status:** {status}\n**HP:** {row[3]}/{row[4]} [ID: {row[0]}]", inline=False)
        
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
