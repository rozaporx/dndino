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
                      status TEXT,
                      level INTEGER DEFAULT 1,
                      xp INTEGER DEFAULT 0,
                      inventory TEXT DEFAULT '',
                      abilities TEXT DEFAULT '')''')
        # Check if columns exist for existing databases
        c.execute("PRAGMA table_info(companions)")
        columns = [column[1] for column in c.fetchall()]
        for col in ['level', 'xp', 'inventory', 'abilities']:
            if col not in columns:
                c.execute(f"ALTER TABLE companions ADD COLUMN {col} {'INTEGER DEFAULT 0' if col == 'xp' else ('INTEGER DEFAULT 1' if col == 'level' else 'TEXT DEFAULT \"\"')}")
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
        c.execute("INSERT INTO companions (user_id, dino_name, custom_name, current_hp, max_hp, status, level, xp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                  (ctx.author.id, dino['name'], custom_name, dino['hp'], dino['hp'], "Transferred Consciousness", 1, 0) )
        conn.commit()
        conn.close()

        await ctx.send(f"**CONSCIOUSNESS LINK ESTABLISHED.** You have successfully merged with a juvenile {dino['name']}. You are now known as **{custom_name}**. Progress is being saved automatically.")

    @commands.command(name='survive')
    async def survive_human(self, ctx, name: str):
        """Register as a human survivor in the prehistoric world."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        # Humans start with standard stats (e.g., 10 HP)
        c.execute("INSERT INTO companions (user_id, dino_name, custom_name, current_hp, max_hp, status, level, xp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                  (ctx.author.id, "Human", name, 10, 10, "Human Survivor", 1, 0) )
        conn.commit()
        conn.close()

        await ctx.send(f"**LOGGING EXPEDITION DATA.** You have arrived in the Year 2148 past as a human named **{name}**. Progress is being saved automatically.")

    @commands.command(name='train')
    async def train_companion(self, ctx, companion_id: int):
        """Trains your companion to gain XP and level up."""
        import random
        from cogs.lookup import Lookup
        lookup_cog = self.bot.get_cog('Lookup')
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT dino_name, custom_name, level, xp, max_hp FROM companions WHERE id = ? AND user_id = ?", (companion_id, ctx.author.id))
        row = c.fetchone()
        
        if not row:
            await ctx.send("Companion not found.")
            conn.close()
            return

        dino_name, custom_name, level, xp, max_hp = row
        
        # Determine growth multiplier based on Tier
        multiplier = 1.0
        if lookup_cog:
            dino_data = next((d for d in lookup_cog.dinosaurs if d['name'].lower() == dino_name.lower()), None)
            if dino_data and 'tier' in dino_data:
                tier = dino_data['tier']
                multipliers = {1: 2.0, 2: 1.5, 3: 1.0, 4: 0.8, 5: 0.6, 6: 0.4}
                multiplier = multipliers.get(tier, 1.0)

        gain = int(random.randint(15, 30) * multiplier)
        if gain < 1: gain = 1 
        
        new_xp = xp + gain
        xp_needed = level * 100
        leveled_up = False
        new_level = level
        new_max_hp = max_hp

        if new_xp >= xp_needed:
            new_level += 1
            new_xp -= xp_needed
            leveled_up = True
            new_max_hp = int(max_hp * 1.1) + 5

        c.execute("UPDATE companions SET xp = ?, level = ?, max_hp = ?, current_hp = ? WHERE id = ?", 
                  (new_xp, new_level, new_max_hp, new_max_hp, companion_id))
        conn.commit()
        conn.close()

        if leveled_up:
            growth_stage = "Juvenile"
            unlock_msg = ""
            if dino_name == "Human":
                if new_level == 5: unlock_msg = "\n🔓 **Unlocked:** Improved Weapons & Professions."
                elif new_level == 9: unlock_msg = "\n🔓 **Unlocked:** Veteran Armor & Status."
                elif new_level == 13: unlock_msg = "\n🔓 **Unlocked:** Elite Warrior Equipment."
                
                if new_level >= 13: growth_stage = "Elite"
                elif new_level >= 9: growth_stage = "Veteran"
                elif new_level >= 5: growth_stage = "Advanced"
                else: growth_stage = "Beginner"
            else:
                if new_level == 5: unlock_msg = "\n🔓 **Unlocked:** Adolescent Combat Capabilities."
                elif new_level == 9: unlock_msg = "\n🔓 **Unlocked:** Pronounced Species Traits."
                elif new_level == 13: unlock_msg = "\n🔓 **Unlocked:** Maximum Species Potential."

                if new_level >= 13: growth_stage = "Adult"
                elif new_level >= 9: growth_stage = "Sub-Adult"
                elif new_level >= 5: growth_stage = "Adolescent"
            
            await ctx.send(f"🎊 **LEVEL UP!** **{custom_name}** is now **Level {new_level}** ({growth_stage})!{unlock_msg}\n*Progress saved to the Archives.*")
        else:
            await ctx.send(f"📖 **Training Complete.** **{custom_name}** gained {gain} XP. ({new_xp}/{xp_needed})")

    @commands.command(name='companions', aliases=['status'])
    async def list_companions(self, ctx):
        """Lists your active identities and saved progress."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT id, dino_name, custom_name, current_hp, max_hp, status, level, xp, inventory, abilities FROM companions WHERE user_id = ?", (ctx.author.id,))
        rows = c.fetchall()
        conn.close()

        if not rows:
            await ctx.send("No saved progress found. Use `!transfer` or `!survive` to begin.")
            return

        embed = discord.Embed(title=f"Expedition Log: {ctx.author.name}", color=discord.Color.blue())
        for row in rows:
            dino_name, custom_name, level = row[1], row[2], row[6]
            
            # Determine stage and unlocks based on Core Rules
            growth_stage = "Juvenile"
            unlocks = "Basic Gear"
            if dino_name == "Human":
                if level >= 13: growth_stage, unlocks = "Elite", "Elite Warrior Equipment, Legendary Status"
                elif level >= 9: growth_stage, unlocks = "Veteran", "Strong Armor & Weapons, High Reputation"
                elif level >= 5: growth_stage, unlocks = "Advanced", "Improved Weaponry, Advanced Professions"
                else: growth_stage, unlocks = "Beginner", "Basic Weapons, Survival Tools"
            else:
                if level >= 13: growth_stage, unlocks = "Adult", "All Species Abilities, Max Potential"
                elif level >= 9: growth_stage, unlocks = "Sub-Adult", "Pronounced Species Traits, Near-Full Size"
                elif level >= 5: growth_stage, unlocks = "Adolescent", "Access to Additional Abilities, Improved Combat"
                else: growth_stage, unlocks = "Juvenile", "Limited Abilities, Reduced Stats"

            xp_needed = level * 100
            embed.add_field(
                name=f"{custom_name} (Lvl {level} {growth_stage} {dino_name})", 
                value=f"**HP:** {row[3]}/{row[4]} | **XP:** {row[7]}/{xp_needed}\n**Unlocks:** {unlocks}\n**ID:** `{row[0]}`", 
                inline=False
            )
        
        embed.set_footer(text="Your progress is automatically saved to the Year 2148 database.")
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
