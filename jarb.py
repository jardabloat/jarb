import discord
from discord.ext import commands
intents = discord.Intents.default()
intents.voice_states = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

GEN_CHANNEL = 1546869709624971284
temp_channel = {}

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



bot.run('MTU0Njg3MDE0NTMyMDc0NzAyMA.GUqhC6.ooBFGKyHIVhEmfY3QmuQLJAEahy5MTtBjRqKUM')