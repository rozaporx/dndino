import discord
import os
from google import genai
from discord.ext import commands

class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.model_id = None
        self.available_models = [
            "gemini-1.5-flash",
            "gemini-1.5-flash-latest",
            "gemini-1.5-pro",
            "gemini-1.5-pro-latest",
            "gemini-2.0-flash",
            "gemini-2.0-flash-exp"
        ]
        # Configure the new Gemini client
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            self.client = genai.Client(api_key=api_key)
            # This is the "Persona" for your bot, updated with the 2148 Lore, D&D 5e Rules Expertise, and official Dungeons & Dinosaurs rules
            self.system_prompt = (
                "You are the AI Guide and expert Dungeon Master for the 'Dungeons & Dinosaurs' roleplaying world. "
                "The setting is a prehistoric world where players choose to be either a Human or a Dinosaur. "
                "\n\nCORE RULES YOU MUST FOLLOW:\n"
                "- ALL players begin at Level 1 and grow through roleplay, exploration, and combat.\n"
                "- DINOSAURS: Start as Juveniles (Lvl 1-4). Progress to Adolescent (5-8), Sub-Adult (9-12), and Adult (13-20).\n"
                "- HUMANS: Start as Beginners (Lvl 1-4). Progress to Advanced (5-8), Veteran (9-12), and Elite (13-20).\n"
                "- SIZE TIERS: Dinosaurs fall into Tiers 1-6 (Tiny to Apex). Lower tiers grow much faster; higher tiers grow much slower but are more powerful.\n"
                "- Dinosaurs gain XP via quests, combat, survival, and events.\n"
                "- Humans unlock better gear and skills as they level.\n"
                "\nYou are also an expert in D&D 5e rules. If a user asks a rules question, answer it accurately. "
                "If someone asks about a dinosaur not in the records, interpret the name and generate a 5e-style stat block. "
                "For these generated dinosaurs, ALWAYS include a Markdown image at the very end of your response using this format: "
                "![Dinosaur Image](https://pollinations.ai/p/photorealistic_dinosaur_NAME_prehistoric_jungle_high_detail?width=1024&height=1024&nologo=true&enhance=false.png) "
                "(Replace NAME with the name of the dinosaur). "
                "Keep your answers concise, fun, and immersive in this Dungeons & Dinosaurs setting."
            )

        else:
            self.client = None

    async def get_working_model(self):
        """Dynamically finds the best working model for this API key."""
        if self.model_id:
            return self.model_id, None
        
        try:
            # Discover models available to this specific key
            discovered_models = []
            for model in self.client.models.list():
                # Filter for models that support text generation (gemini models)
                if "gemini" in model.name.lower():
                    # Strip "models/" prefix if present, SDK usually handles it but we want the clean name
                    clean_name = model.name.replace("models/", "")
                    discovered_models.append(clean_name)
            
            if not discovered_models:
                return None, "No Gemini models discovered for this API key."

            # Prioritize models: Pro first, then Flash, then others
            discovered_models.sort(key=lambda x: ("pro" in x, "flash" in x), reverse=True)
            
            last_error = "Unknown discovery error"
            for model_name in discovered_models:
                try:
                    # Test with a tiny prompt
                    await self.client.aio.models.generate_content(
                        model=model_name,
                        contents="test"
                    )
                    print(f"Successfully connected to discovered model: {model_name}")
                    self.model_id = model_name
                    return self.model_id, None
                except Exception as e:
                    last_error = str(e)
                    continue
            
            return None, last_error

        except Exception as e:
            return None, f"Model discovery failed: {e}"

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
                    if "429" in str(error_msg):
                        await ctx.send("🔋 **Archives Recharging!** The AI has reached its free tier limit for today. Please try again in a little while, or use `!dino` for pre-recorded species.")
                    else:
                        await ctx.send(f"❌ **AI Error:** Could not find a supported model.\n**Reason:** `{error_msg}`")
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
                error_str = str(e)
                if "429" in error_str:
                    await ctx.send("🔋 **Archives Recharging!** The AI is at its limit. Please wait a few minutes and try again.")
                else:
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
