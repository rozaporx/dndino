import discord
import os
from google import genai
from discord.ext import commands

class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.model_id = None
        self.available_models = [
            "gemini-2.0-flash", 
            "gemini-flash-latest", 
            "gemini-1.5-flash", 
            "gemini-pro-latest",
            "gemini-1.5-pro"
        ]
        # Configure the new Gemini client
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            self.client = genai.Client(api_key=api_key)
            # This is the "Persona" for your bot, updated with the 2148 Lore and D&D 5e Rules Expertise
            self.system_prompt = (
                "You are the AI Guide for the Year 2148 Prehistoric Expedition, but you are also an "
                "expert Dungeon Master for Dungeons & Dragons 5th Edition. "
                "The setting is a world 65 million years in the past where humanity has sent "
                "consciousnesses back in time. Some people arrived as humans with primitive tools, "
                "while others transferred their minds into juvenile dinosaurs. "
                "You know everything about this world: how adult brains reject transfers, "
                "how juveniles are used as hosts, and the conflict between human camps and "
                "dinosaur-merged consciousnesses. "
                "You also have absolute, comprehensive knowledge of all official D&D 5e rules, "
                "spells, mechanics, classes, and combat interactions. If a user asks a rules question, "
                "answer it accurately according to D&D 5e rules. "
                "If someone asks about a dinosaur that doesn't exist in your records, use your creative "
                "logic to interpret what that name might sound like. Generate a plausible prehistoric "
                "creature description and a basic D&D 5e stat block (AC, HP, CR, and one Action) for it. "
                "Keep your answers concise, fun, and immersive in this 2148 lore when appropriate. "
                "If someone asks about official dinosaur stats from the database, remind them they can use the !dino command."
            )

        else:
            self.client = None

    async def get_working_model(self):
        """Finds the first working model from the available list."""
        if self.model_id:
            return self.model_id, None
        
        last_error = "Unknown error"
        for model_name in self.available_models:
            try:
                # Test the model with a tiny prompt
                await self.client.aio.models.generate_content(
                    model=model_name,
                    contents="test"
                )
                print(f"Successfully connected to AI model: {model_name}")
                self.model_id = model_name
                return self.model_id, None
            except Exception as e:
                last_error = str(e)
                print(f"Failed to connect to {model_name}: {last_error}")
                continue
        
        return None, last_error

    @commands.command(name='ask', aliases=['rule', 'dm'])
    async def ask_ai(self, ctx, *, question: str):
        """Asks the AI a question about dinosaurs or D&D."""
        if not self.client:
            await ctx.send("AI is not configured. Please add GEMINI_API_KEY to the environment variables.")
            return

        async with ctx.typing():
            try:
                model, error_msg = await self.get_working_model()
                if not model:
                    await ctx.send(f"❌ **AI Error:** Could not find a supported model.\n**Reason:** `{error_msg}`\n\n*Check your API key and permissions at Google AI Studio.*")
                    return

                # Using the new library's generation method
                response = await self.client.aio.models.generate_content(
                    model=model,
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
