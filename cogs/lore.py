import discord
from discord.ext import commands

class Lore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.story = (
            "**THE YEAR 2148**\n"
            "Humanity achieved what generations believed was impossible: **Time Travel.**\n\n"
            "For decades, scientists experimented with sending information through time. Eventually, they succeeded in "
            "sending living consciousnesses into the distant past—over 65 million years ago, when dinosaurs ruled the Earth.\n\n"
            "**The Mission:** Observe. Study. Learn.\n"
            "But humans did what humans always do: they immediately started using it for their own purposes.\n\n"
            "**The Discovery:** Adult dinosaur brains were too developed to safely accept a human consciousness. "
            "However, **Juvenile dinosaurs** were different. Their developing brains could successfully merge with a human mind.\n\n"
            "**The Choice:**\n"
            "- **The Survivors:** Some volunteers chose to remain human, arriving with nothing but primitive tools and their determination. "
            "They built camps, hunted, and became legends among other survivors.\n"
            "- **The Transferred:** Others abandoned their human bodies entirely. Their consciousnesses were transferred into "
            "juvenile dinosaurs, allowing them to live as the creatures they studied. Some became swift raptors; others, "
            "towering Triceratops. A few dream of becoming the apex predator—the Tyrannosaurus Rex.\n\n"
            "**A New Society:** Humans fight to survive. Dinosaurs fight to grow. Both compete for territory, resources, and glory. "
            "Some dinosaurs remember being human. Others forget the future they came from entirely."
        )

    @commands.command(name='lore')
    async def show_lore(self, ctx):
        """Displays the background story of the year 2148."""
        embed = discord.Embed(
            title="Prehistoric Expedition: Project 2148",
            description=self.story,
            color=discord.Color.dark_red()
        )
        embed.set_footer(text="Choose your path. Survive or Evolve.")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Lore(bot))
