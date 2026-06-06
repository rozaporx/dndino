import discord
import json
import os
import random
from discord.ext import commands

class Encounters(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'dinosaurs.json')
        self.dinosaurs = self.load_data()

    def load_data(self):
        with open(self.data_path, 'r') as f:
            return json.load(f)['dinosaurs']

    @commands.command(name='encounter')
    async def generate_encounter(self, ctx, min_cr: str = "0", max_cr: str = "30"):
        """Generates a random dinosaur encounter within a CR range."""
        try:
            def cr_to_float(cr_str):
                if '/' in cr_str:
                    num, den = cr_str.split('/')
                    return int(num) / int(den)
                return float(cr_str)

            min_cr_val = cr_to_float(min_cr)
            max_cr_val = cr_to_float(max_cr)

            eligible = [d for d in self.dinosaurs if min_cr_val <= cr_to_float(d['cr']) <= max_cr_val]

            if not eligible:
                await ctx.send(f"No dinosaurs found in CR range {min_cr} to {max_cr}.")
                return

            # Randomly pick 1-4 dinosaurs (can be same or different)
            count = random.randint(1, 4)
            selected = random.choices(eligible, k=count)
            
            dino_counts = {}
            for d in selected:
                dino_counts[d['name']] = dino_counts.get(d['name'], 0) + 1

            encounter_list = "\n".join([f"- {count}x {name}" for name, count in dino_counts.items()])
            
            embed = discord.Embed(title="Random Dinosaur Encounter", description=encounter_list, color=discord.Color.orange())
            embed.set_footer(text=f"CR Range: {min_cr} - {max_cr}")
            await ctx.send(embed=embed)

        except ValueError:
            await ctx.send("Invalid CR format. Use numbers or fractions like '1/4'.")

async def setup(bot):
    await bot.add_cog(Encounters(bot))
