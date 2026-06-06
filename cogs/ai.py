import discord
import os
import google.generativeai as genai
from discord.ext import commands

class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Configure Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            # Use 1.5-flash if available, fallback to gemini-pro
            try:
                self.model = genai.GenerativeModel('gemini-1.5-flash')
            except:
                self.model = genai.GenerativeModel('gemini-pro')
            self.chat_history = []
            # This is the "Persona" for your bot
            self.system_prompt = (
                "You are a helpful and knowledgeable D&D 5e Dinosaur Expert. "
                "You know everything about prehistoric creatures and how they fit into a fantasy RPG. "
                "Keep your answers concise, fun, and occasionally use dinosaur puns. "
                "If someone asks about stats, remind them they can use the !dino command."
            )
        else:
            self.model = None

    @commands.command(name='ask')
    async def ask_ai(self, ctx, *, question: str):
        """Asks the AI a question about dinosaurs or D&D."""
        if not self.model:
            await ctx.send("AI is not configured. Please add GEMINI_API_KEY to the environment variables.")
            return

        async with ctx.typing():
            try:
                prompt = f"{self.system_prompt}\n\nUser Question: {question}"
                response = self.model.generate_content(prompt)
                
                # Discord has a 2000 character limit per message
                answer = response.text
                if len(answer) > 1900:
                    answer = answer[:1900] + "..."
                
                await ctx.reply(answer)
            except Exception as e:
                await ctx.send(f"Sorry, I had a brain freeze! Error: {e}")

    @commands.Cog.listener()
    async def on_message(self, message):
        # Don't respond to other bots or ourselves
        if message.author.bot:
            return

        # If the bot is mentioned, respond using AI
        if self.bot.user.mentioned_in(message) and not message.mention_everyone:
            question = message.content.replace(f'<@!{self.bot.user.id}>', '').replace(f'<@{self.bot.user.id}>', '').strip()
            if not question:
                await message.channel.send("Roar! (You mentioned me? Use `!ask <question>` or type a message after mentioning me!)")
                return
            
            ctx = await self.bot.get_context(message)
            await self.ask_ai(ctx, question=question)

async def setup(bot):
    await bot.add_cog(AI(bot))
