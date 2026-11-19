import discord
from discord.ext import commands
import yt_dlp

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}
        self.extractor = yt_dlp.YoutubeDL({
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
        })

    def play_next(self, ctx, guild_id, voice_client):
        if guild_id in self.queues and len(self.queues[guild_id]) > 0:
            link = self.queues[guild_id].pop(0)
            info = self.extractor.extract_info(link, download=False)
            url = info['url']

            voice_client.play(
                discord.FFmpegPCMAudio(
                    url,
                    executable="C:/FFmpeg/bin/ffmpeg.exe",  # Ou "ffmpeg" sous Linux
                    before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
                ),
                after=lambda error: self.play_next(ctx, guild_id, voice_client)
            )

    @commands.command()
    async def music(self, ctx, link: str):
        if ctx.author.voice and ctx.author.voice.channel:
            voice_channel = ctx.author.voice.channel
            if ctx.voice_client is None:
                await voice_channel.connect()
            voice_client = ctx.voice_client

            if ctx.guild.id not in self.queues:
                self.queues[ctx.guild.id] = []

            self.queues[ctx.guild.id].append(link)

            if not voice_client.is_playing():
                self.play_next(ctx, ctx.guild.id, voice_client)
        else:
            await ctx.send("Vous devez être dans un salon vocal !")

    @commands.command()
    async def quit(self, ctx):
        if ctx.voice_client is not None:
            ctx.voice_client.stop()
            await ctx.voice_client.disconnect()
            if ctx.guild.id in self.queues:
                del self.queues[ctx.guild.id]
            await ctx.send("Déconnecté et file d'attente vidée.")

async def setup(bot):
    await bot.add_cog(Music(bot))