import discord
from discord.ext import commands

class Lore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.story = (
            "**DUNGEONS & DINOSAURS - CORE RULES**\n\n"
            "Dungeons & Dinosaurs is a medieval fantasy roleplaying world where players may choose to play as either a **Human** or a **Dinosaur**. Both paths offer unique challenges, progression systems, and playstyles.\n\n"
            "**Dinosaur Players:**\n"
            "Players who choose to play as a dinosaur begin life as a **Juvenile** and must grow naturally through leveling.\n"
            "- **Levels 1-4: Juvenile** (Small size, reduced stats)\n"
            "- **Levels 5-8: Adolescent** (Increased size, improved combat)\n"
            "- **Levels 9-12: Sub-Adult** (Near full size, traits become pronounced)\n"
            "- **Levels 13-20: Adult** (Fully grown, maximum potential unlocked)\n\n"
            "**Human Players:**\n"
            "Humans begin as inexperienced adventurers and gain stronger equipment and abilities as they level.\n"
            "- **Levels 1-4: Beginner** (Basic weapons/armor)\n"
            "- **Levels 5-8: Advanced** (Improved equipment, professions)\n"
            "- **Levels 9-12: Veteran** (Veteran status, strong armor/weapons)\n"
            "- **Levels 13-20: Elite** (Elite warriors, hunters, or leaders)\n\n"
            "**🦖 DINOSAUR SIZE TIERS 🦖**\n"
            "• **Tier 1 - Tiny**: (Compsognathus, Troodon) - Fastest growth.\n"
            "• **Tier 2 - Small**: (Velociraptor, Oviraptor) - Fast growth.\n"
            "• **Tier 3 - Medium**: (Deinonychus, Dilophosaurus) - Average growth.\n"
            "• **Tier 4 - Large**: (Allosaurus, Stegosaurus) - Slow growth.\n"
            "• **Tier 5 - Huge**: (Triceratops, Spinosaurus) - Very slow growth.\n"
            "• **Tier 6 - Apex**: (T-Rex, Giganotosaurus) - Slowest growth.\n\n"
            "**Gaining Experience:**\n"
            "All players start at Level 1 and earn XP through roleplay, exploration, combat, quests, and survival."
        )

    @commands.command(name='lore', aliases=['rules'])
    async def show_lore(self, ctx):
        """Displays the background story and core rules."""
        embed = discord.Embed(
            title="Dungeons & Dinosaurs - Prehistoric Expedition",
            description=self.story,
            color=discord.Color.dark_red()
        )
        embed.set_footer(text="Choose your path. Survive or Evolve.")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Lore(bot))
