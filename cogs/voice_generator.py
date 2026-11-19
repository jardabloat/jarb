import json
import discord
from discord.ext import commands

DATA_FILE = "gen_channels.json"

class VoiceGenerator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.temp_channel = {}
        self.gen_channels = self.load_gen_channels()

    def load_gen_channels(self):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                return {int(k): int(v) for k, v in data.items()}
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_gen_channels(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.gen_channels, f, indent=4)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        gen_channel_id = self.gen_channels.get(member.guild.id)
        if after.channel is not None and gen_channel_id is not None and after.channel.id == gen_channel_id:
            server = after.channel.guild
            cat = after.channel.category

            new_channel = await server.create_voice_channel(
                name=f"Salon de {member.display_name}", 
                category=cat
            )
            await member.move_to(new_channel)
            self.temp_channel[new_channel] = member

        if before.channel is not None and before.channel in self.temp_channel and len(before.channel.members) == 0:
            await before.channel.delete()
            del self.temp_channel[before.channel]

    @commands.command()
    async def new_name(self, ctx, *, new_name):
        if (ctx.author.voice and ctx.author.voice.channel in self.temp_channel 
                and ctx.author == self.temp_channel[ctx.author.voice.channel]):
            await ctx.author.voice.channel.edit(name=new_name)
            await ctx.send(f"Nom modifié pour {new_name}")

    @commands.command()
    async def user_limit(self, ctx, number: int):
        if (ctx.author.voice and ctx.author.voice.channel in self.temp_channel 
                and ctx.author == self.temp_channel[ctx.author.voice.channel]):
            await ctx.author.voice.channel.edit(user_limit=number)
            await ctx.send(f"Limite d'utilisateur mise à jour à {number}")

    @commands.command()
    async def channel(self, ctx, channel_id: int):
        self.gen_channels[ctx.guild.id] = channel_id
        self.save_gen_channels()
        await ctx.send(f"Le salon générateur a été défini sur l'ID : {channel_id}")

# Fonction obligatoire pour enregistrer le Cog
async def setup(bot):
    await bot.add_cog(VoiceGenerator(bot))