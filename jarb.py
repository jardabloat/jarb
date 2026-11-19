import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.voice_states = True
intents.message_content = True

class JarbBot(commands.Bot):
    async def setup_hook(self):
        # Charge tous les fichiers .py présents dans le dossier cogs/
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
                print(f"Cog chargé : {filename[:-3]}")

bot = JarbBot(command_prefix="!", intents=intents)

async def main():
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())