import discord
import random
import re
from discord.ext import commands

class Dice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='roll')
    async def roll(self, ctx, dice: str):
        """Rolls dice in NdN+Mod format."""
        try:
            # Match pattern like 1d20+5 or 2d6
            match = re.match(r'(\d+)d(\d+)([+-]\d+)?', dice.lower())
            if not match:
                await ctx.send("Invalid dice format. Use something like `!roll 1d20+5`.")
                return

            num_dice = int(match.group(1))
            num_sides = int(match.group(2))
            modifier = int(match.group(3)) if match.group(3) else 0

            if num_dice > 100 or num_sides > 1000:
                await ctx.send("That's too many dice or sides! Keep it reasonable (max 100d1000).")
                return

            rolls = [random.randint(1, num_sides) for _ in range(num_dice)]
            total = sum(rolls) + modifier
            
            rolls_str = ', '.join(map(str, rolls))
            mod_str = f" {'+' if modifier >= 0 else ''}{modifier}" if modifier != 0 else ""
            
            if num_dice > 1:
                await ctx.send(f"🎲 Rolling **{dice}**: ({rolls_str}){mod_str} = **{total}**")
            else:
                await ctx.send(f"🎲 Rolling **{dice}**: {total}")

        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

async def setup(bot):
    await bot.add_cog(Dice(bot))
