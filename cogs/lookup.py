import discord
import json
import os
from discord.ext import commands

class Lookup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'dinosaurs.json')
        self.dinosaurs = self.load_data()

    def load_data(self):
        with open(self.data_path, 'r') as f:
            return json.load(f)['dinosaurs']

    @commands.command(name='dino')
    async def dino_lookup(self, ctx, *, name: str = None):
        """Looks up a dinosaur's stats."""
        if not name:
            names = ", ".join([d['name'] for d in self.dinosaurs])
            await ctx.send(f"**Welcome to the Year 2148 Archives!**\nTo look up a dinosaur, use `!dino <name>`. For example: `!dino T-Rex` or `!dino Triceratops`.\n\n**Available dinosaurs:** {names}")
            return

        # Clean the input to remove punctuation and extra spaces
        clean_input = name.lower().strip()
        
        # 1. Try exact match or fuzzy match on the whole string
        dino = next((d for d in self.dinosaurs if d['name'].lower() in clean_input or clean_input in d['name'].lower()), None)
        
        # 2. If no match, check if any dinosaur name is *contained* within the sentence
        if not dino:
            for d in self.dinosaurs:
                if d['name'].lower() in clean_input:
                    dino = d
                    break

        if not dino:
            # If not found in database, ask the AI to generate/interpret it
            ai_cog = self.bot.get_cog('AI')
            if ai_cog:
                prompt = f"Interpret this potential prehistoric creature name: '{name}'. Generate a D&D 5e stat block summary (AC, HP, CR, and one unique action) and a brief description of what this creature looks like in the Year 2148 expedition."
                await ai_cog.ask_ai(ctx, question=prompt)
                return
            
            # Fallback if AI is offline
            names = ", ".join([d['name'] for d in self.dinosaurs])
            await ctx.send(f"I couldn't find a dinosaur in your message. Did you mean one of these?\n**Available:** {names}")
            return

        embed = discord.Embed(title=dino['name'], description=f"*{dino['size']} {dino['type']}, {dino['alignment']}*", color=discord.Color.green())
        
        # Generate an image using Pollinations.ai
        import urllib.parse
        prompt = f"photorealistic dinosaur, {dino['name']}, prehistoric jungle background, high detail, 8k"
        encoded_prompt = urllib.parse.quote(prompt)
        image_url = f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&seed={random.randint(1, 100000)}&nologo=true"
        embed.set_image(url=image_url)

        embed.add_field(name="Armor Class", value=dino['ac'], inline=True)
        embed.add_field(name="Hit Points", value=f"{dino['hp']} ({dino['hp_formula']})", inline=True)
        embed.add_field(name="Speed", value=dino['speed'], inline=True)
        
        stats = dino['stats']
        stats_str = f"STR: {stats['str']} (+{(stats['str']-10)//2})\n" \
                    f"DEX: {stats['dex']} (+{(stats['dex']-10)//2})\n" \
                    f"CON: {stats['con']} (+{(stats['con']-10)//2})\n" \
                    f"INT: {stats['int']} (+{(stats['int']-10)//2})\n" \
                    f"WIS: {stats['wis']} (+{(stats['wis']-10)//2})\n" \
                    f"CHA: {stats['cha']} (+{(stats['cha']-10)//2})"
        embed.add_field(name="Stats", value=stats_str, inline=False)
        
        if 'skills' in dino:
            embed.add_field(name="Skills", value=dino['skills'], inline=True)
        embed.add_field(name="Challenge", value=f"{dino['cr']} ({dino['xp']} XP)", inline=True)

        if dino['traits']:
            traits_str = "\n".join([f"**{t['name']}**: {t['description']}" for t in dino['traits']])
            embed.add_field(name="Traits", value=traits_str, inline=False)

        for action in dino['actions']:
            embed.add_field(name=action['name'], value=action['description'], inline=False)

        if 'historical_facts' in dino:
            facts_str = "\n".join([f"• {fact}" for fact in dino['historical_facts']])
            embed.add_field(name="Historical Facts", value=facts_str, inline=False)

        await ctx.send(embed=embed)

    @commands.command(name='dinolist')
    async def dino_list(self, ctx):
        """Lists all available dinosaurs."""
        names = [d['name'] for d in self.dinosaurs]
        await ctx.send(f"Available dinosaurs: {', '.join(names)}")

async def setup(bot):
    await bot.add_cog(Lookup(bot))
