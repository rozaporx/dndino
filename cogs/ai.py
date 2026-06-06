import discord
import os
from google import genai
from discord.ext import commands

class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Configure the new Gemini client
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            self.client = genai.Client(api_key=api_key)
            self.model_id = "gemini-1.5-flash"
            # This is the "Persona" for your bot
            self.system_prompt = (
                "You are a helpful and knowledgeable D&D 5e Dinosaur Expert. "
                "You know everything about prehistoric creatures and how they fit into a fantasy RPG. "
                "Keep your answers concise, fun, and occasionally use dinosaur puns. "
                "If someone asks about stats, remind them they can use the !dino command."
            )
        else:
            self.client = None

    @commands.command(name='ask')
    async def ask_ai(self, ctx, *, question: str):
        """Asks the AI a question about dinosaurs or D&D."""
        if not self.client:
            await ctx.send("AI is not configured. Please add GEMINI_API_KEY to the environment variables.")
            return

        async with ctx.typing():
            try:
                # Using the new library's generation method
                response = self.client.models.generate_content(
                    model=self.model_id,
                    config={"system_instruction": self.system_prompt},
                    contents=question
                )
                
                answer = response.text
                if len(answer) > 1900:
                    answer = answer[:1900] + "..."
                
                await ctx.reply(answer)
            except Exception as e:
                await ctx.send(f"Sorry, I had a brain freeze! Error: {e}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if self.bot.user.mentioned_in(message) and not message.mention_everyone:
            question = message.content.replace(f'<@!{self.bot.user.id}>', '').replace(f'<@{self.bot.user.id}>', '').strip()
            if not question:
                await message.channel.send("Roar! (You mentioned me? Use `!ask <question>` or type a message after mentioning me!)")
                return
            
            ctx = await self.bot.get_context(message)
            await self.ask_ai(ctx, question=question)

async def setup(bot):
    await bot.add_cog(AI(bot))
