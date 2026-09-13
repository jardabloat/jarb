import os
import discord
import yt_dlp
from dotenv import load_dotenv
from discord.ext import commands
intents = discord.Intents.default()
intents.voice_states = True
intents.message_content = True

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix="!", intents=intents)

GEN_CHANNEL = 1546869709624971284
temp_channel = {}

options_ytdl = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
}
queues = {}

extractor = yt_dlp.YoutubeDL(options_ytdl)

@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel is not None and after.channel.id == GEN_CHANNEL:
        server = after.channel.guild
        cat = after.channel.category

        new_channel = await server.create_voice_channel(
            name=f"Salon de {member.display_name}", 
            category=cat
        )

        await member.move_to(new_channel)
        temp_channel[new_channel] = member

    if before.channel is not None and before.channel in temp_channel and len(before.channel.members) == 0:
        await before.channel.delete()
        del temp_channel[before.channel]

@bot.command()
async def new_name(ctx, *, new_name):
    if ctx.author.voice is not None and ctx.author.voice.channel is not None and ctx.author.voice.channel in temp_channel and ctx.author == temp_channel[ctx.author.voice.channel]:
        await ctx.author.voice.channel.edit(name=new_name)
        await ctx.send(f"Nom modifié pour "+new_name)

@bot.command()
async def user_limit(ctx, number):
    if ctx.author.voice is not None and ctx.author.voice.channel is not None and ctx.author.voice.channel in temp_channel and ctx.author == temp_channel[ctx.author.voice.channel]:
        await ctx.author.voice.channel.edit(user_limit=int(number))
        await ctx.send(f"Limite d'utilisateur mise à jour à "+number)

@bot.command()
async def music(ctx, link):
    if ctx.author.voice is not None and ctx.author.voice.channel is not None:
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
        voice_client = ctx.voice_client

        if ctx.guild.id not in queues:
            queues[ctx.guild.id] = []

        queues[ctx.guild.id].append(link)

        if voice_client.is_playing():
            pass
        else:
            play_next(ctx, ctx.guild.id, voice_client)



def play_next(ctx, guild, voice_client):
    if guild in queues and len(queues[guild]) > 0:
        link = queues[guild].pop(0)
        info = extractor.extract_info(link, download=False)
        url = info['url']

        voice_client.play(
            discord.FFmpegPCMAudio(
            url, 
            executable="C:/FFmpeg/bin/ffmpeg.exe", 
            before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
        ), 
        after=lambda erreur: play_next(ctx, guild, voice_client)
)

@bot.command()
async def quit(ctx):
    if ctx.voice_client is not None:
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()
        if ctx.guild.id in queues:
            del queues[ctx.guild.id]


# .\.venv\Scripts\activate
bot.run(TOKEN)