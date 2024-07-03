import random
import discord
from discord.ext import commands
import asyncio
import yt_dlp
import os
import spotipy
import unicodedata
import re
from dotenv import load_dotenv

TOKEN = os.getenv("TOKEN")
#playing music from spotify work in progress
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_SECRET_KEY = os.getenv('SPOTIFY_SECRET_KEY')


"""Variables"""
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.voice_states = True
spotify = spotipy.Spotify()
images = ['images/blackMan.png', 'images/mario.png' , 'images/oldTwitch.png',"images/panda.png", "images/spongebob.png"]
sounds = ['sounds/gameStart.mp3' , 'sounds/succes.mp3' , 'sounds/twitchLaugh.mp3']
ffmpegPath = "ffmpeg-master-latest-win64-gpl/ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe";
ffmpegOptions = {'before_options': '-reconnect 1 -reconnected_streamed 1 -reconnect_delay_max 5'}
ydl_options = {
       'format': 'bestaudio/best',
       'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
       'ffmpeg_location' : "ffmpeg-master-latest-win64-gpl/ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe",
       'ffprobe_location' : "ffmpeg-master-latest-win64-gpl/ffmpeg-master-latest-win64-gpl/bin/ffprobe.exe"
       }
ffmpegOptions1 = {'options' : '-vn'}

ytdl = yt_dlp.YoutubeDL(ydl_options)

client = commands.Bot(command_prefix="!",intents=intents)


@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')

@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to my Discord server!'
    )

"""Basic response"""
@client.command(name='response' ,help="Sends random quote to your dm")
async def response_command(ctx):

    brooklyn_99_quotes = [
        "“Be yourself; everyone else is already taken.” ― Oscar Wilde",
        "“Two things are infinite: the universe and human stupidity; and I'm not sure about the universe.” ― Albert Einstein",
        "“A room without books is like a body without a soul.” ― Marcus Tullius Cicero",
        "“In three words I can sum up everything I've learned about life: it goes on.” ― Robert Frost"

    ]
    response = random.choice(brooklyn_99_quotes)
    await ctx.send(response)
    
"Jd"
@client.command(name='JD', help= "Sends JD quote on text channel or to your dm")
async def jd_command(ctx):
        await ctx.send("Jest Dobrze!!!")

"""Mutes all"""
@client.command(name='muteall' , help="Mutes all users from voice channel")
async def muteall(ctx):
    if ctx.author.voice is None:
         await ctx.send("There is nobody on voice channel")
         return
    else:
        voice_channel = ctx.author.voice.channel

        for members, voice_state in voice_channel.voice_states.items():
            member = ctx.guild.get_member(members)
            if member:
                await member.edit(mute=True)
        await ctx.send("all members were muted!!!")

"""Unmutes all"""
@client.command(name='unmuteall' , help="Unmutes all users from voice channel")
async def muteall(ctx):
    if ctx.author.voice is None:
         await ctx.send("There is nobody on voice channel")
         return
    else:
        voice_channel = ctx.author.voice.channel

        for members, voice_state in voice_channel.voice_states.items():
            member = ctx.guild.get_member(members)
            if member:
                await member.edit(mute=False)
        await ctx.send("all members were unmuted Sad!!!")

@client.command(name='puke' , help="write !puke @user; Moves deafened user to random voice channels until he undefean himself")
async def on_voice_state_update(ctx):
    if ctx.author.voice and ctx.author.voice.self_deaf:
        guild = ctx.guild
        channels = guild.voice_channels
        channel_names = [channel.name for channel in channels]
        try:
            while True:
                for i in range(3):
                    await ctx.author.move_to(channels[i])   
                    await asyncio.sleep(2)
            
            
            
            
        except discord.HTTPException as e:
            pass
    else:
        print("member is not connected")
           # while member.voice.self_deaf:

"""sends images priv"""
@client.command(name="sendPic" , help='type !sendPic @user; Sends random images to mentioned user.')
async def sendNudes(ctx, member:discord.Member):
    file = discord.File(random.choice(images))
    try:
        await member.send(file=file)
        await ctx.send(f"Sended image to {member.name}.")
    except commands.errors.MissingRequiredArgument:
        await ctx.send("please use @username to send the picture.")

"""Plays sounds"""
@client.command(name="sound" , help="You have to be on voice channel; Plays random sound")
async def playVoice(ctx):
    if ctx.voice_client is None:
        channel = ctx.author.voice.channel
        await channel.connect()
    else:
        channel = ctx.author.voice.channel
    voice_channel = ctx.voice_client
    voice_channel.play(discord.FFmpegPCMAudio(random.choice(sounds), executable=ffmpegPath))
    await ctx.send("Playing random sound.")
    await asyncio.sleep(3)
    await ctx.voice_client.disconnect()


async def playSong(url, voiceClient):
    player = discord.FFmpegPCMAudio(url, **ffmpegOptions1, executable=ffmpegPath)
    voiceClient.play(player)
    while voiceClient.is_playing():
            await asyncio.sleep(1)
    for i in range(30):
        if voiceClient.is_playing():
            break
        await asyncio.sleep(1)    

        if not voiceClient.is_playing():
            voiceClient.stop()
            await voiceClient.disconnect()

"""adding playlist"""
songPlaylist = []
@client.command(name='addyt', help="Type !addyt linkToYtsong; adds song to your playlist")
async def addSong(ctx , url):
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
    song_url = data['url']
    songPlaylist.append(song_url)
    await ctx.send(f'Added song to your playlist')

"""Yt song request"""
voice_clients = {}
@client.command(name='playt', help="Type !playt linkToYtsong; plays a song or added earlier playlist on voice channel")
async def ytPlay(ctx,msg):
    firstSong = True
    try:
        if firstSong:
            if not ctx.author.voice:
                await ctx.send('You need to be on voice channel!!!')
                return
            voice_client = await ctx.author.voice.channel.connect()
            voice_clients[voice_client.guild.id] = voice_client

            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(msg, download=False))
            song_url = data['url']
            await playSong(song_url,voice_client)
            firstSong = False

        if len(songPlaylist) > 0:
            while len(songPlaylist) >0:
                song_url= songPlaylist.pop(0)
                await playSong(song_url,voice_client)

    except Exception as err:
        print(f'Error: {err}')    

"""Skip music"""
@client.command(name='skip')
async def skip(ctx):
    voice_client = ctx.guild.voice_client
    if voice_client and voice_client.is_connected():
        if voice_client.is_playing() and len(songPlaylist) >0:
            voice_client.stop()
            song_url = songPlaylist.pop(0)
            await playSong(song_url,voice_client)
            await ctx.send("Skipping currently playing music")



@client.command(name='stop', help='Stops currently playing music and disconnects bot.')
async def stop(ctx):
    voice_channel = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice_channel.is_playing() and voice_channel and voice_channel.is_connected():
        voice_channel.stop()
    await voice_channel.disconnect()
    await ctx.send("Disconnecting bot from the channel.")

@client.command(name='removeRole' , help="Removes role of mentioned member")
async def remove_role(ctx, role_name: str, member_name: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    
    if role:
        #member = discord.utils.get(ctx.guild.members , display_name=member_name)
        if member_name:
            try:
                await member_name.remove_roles(role)
                await ctx.send(f'Removed the {role.name} role from {member_name.display_name}.')
            except discord.Forbidden:
                await ctx.send('I do not have permission to manage roles.')
            except discord.HTTPException:
                await ctx.send('Failed')
        else:
            await ctx.send(f'Member "{member_name}" not found.')
    else:
        await ctx.send(f'Role "{role_name}" not found.')

load_dotenv()

client.run(TOKEN)
