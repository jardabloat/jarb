import os
import discord
import yt_dlp
import json
from dotenv import load_dotenv
from discord.ext import commands
intents = discord.Intents.default()
intents.voice_states = True
intents.message_content = True

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix="!", intents=intents)

options_ytdl = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
}
queues = {}
gen_channels = {}
temp_channel = {}
DATA_FILE = "gen_channels.json"

extractor = yt_dlp.YoutubeDL(options_ytdl)

def load_gen_channels():
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            return {int(k): int(v) for k, v in data.items()}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_gen_channels(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

gen_channels = load_gen_channels()

@bot.event
async def on_voice_state_update(member, before, after):
    gen_channel_id = gen_channels.get(member.guild.id)
    if after.channel is not None and gen_channel_id is not None and after.channel.id == gen_channel_id:
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
async def channel(ctx, id):
    gen_channels[ctx.guild.id] = id
    save_gen_channels(gen_channels)
    await ctx.send(f"Le salon générateur a été défini sur l'ID : {id}")

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