import discord 
from discord.ext import commands
import requests
import os
from dotenv import load_dotenv
import nacl
import yt_dlp
import ffmpeg
import subprocess
import asyncio
import glob
from natsort import natsorted

# TODO 
# 1. Add a way to add a song to the queue
# 2. Add a way to remove a song from the queue
# 3. Add a way to skip a song
# 4. Add a way to pause a song
# 5. Add a way to resume a song
# 6. Add a way to stop a song
# 7. Add a way to shuffle the queue
# 8. Add a way to clear the queue
# 9. Add a way to loop the queue
# 10. Add a way to show the queue
# 11. Add a way to show the current song
# 12. Add a way to show the volume
# 13. Add a way to set the volume
# 14. Add a way to show the queue
# 15. Add a way to show the current song
# 16. Add a way to show the volume

## youtube example
# url queue for playing audio
queue_list = []
# files for playing audio
audio_files = asyncio.Queue()
#index for the queue list
queue_index = 0


#loading environment variables
load_dotenv() 
#with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#  ydl.download([url])

#discord.FFmpegPCMAudio(executable="ffmpeg", source="audio.mp3")

#input_file = "audio.mp3"
#output_file = "audio.pcm"

#command = [
#    "ffmpeg", "-i", input_file,  # Input file
#    "-f", "s16le",  # PCM format: signed 16-bit little-endian
#    "-ar", "48000",  # Sample rate: 48kHz (Discord's preferred format)
#    "-ac", "2",  # Channels: 2 (stereo)
#    output_file  # Output PCM file
#]

#subprocess.run(command)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
  print('We have logged in as {0.user}'.format(bot))


@bot.event
async def on_message(message):
  # prevents the bot from responding to itself
  if message.author == bot.user:
    return
    
  #Just a test command
  if message.content.startswith('!hello'):
    await message.channel.send('Hello!')
    
  #Echo what the user typed to the bot
  if message.content.startswith('!echo '):
    await message.channel.send(message.content[5:])
    
  #Get a random cat picture (Smart fill made this one)
  if message.content.startswith('!cat'):
    response = requests.get('https://api.thecatapi.com/v1/images/search')
    data = response.json()
    await message.channel.send(data[0]['url'])
    
  #Get a random dog picture (Smart fill made this one)
  if message.content.startswith('!dog'):
    response = requests.get('https://dog.ceo/api/breeds/image/random')
    data = response.json()
    await message.channel.send(data['message'])
    
  # allows messages to be processed by bot.commands() if they are not here
  if message.content.startswith('!playaudio '):
    voice_channel = message.author.voice.channel
    if voice_channel:
      yt_URL = message.content[11:]
      #if os.path.exists(Audio_File_Path):
       # os.remove(Audio_File_Path)
      #with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      #  ydl.download(yt_URL)
      await download_audio(yt_URL)
      vc =  discord.utils.get(bot.voice_clients, guild=message.guild)
      if vc is None:
        vc = await voice_channel.connect()
      msg = message.channel
      await MP3_buffer_list(msg)
      await Play_Audio_From_Queue(vc)
      #vc.play(discord.FFmpegPCMAudio(executable = "ffmpeg",source = "audio.mp3"))
      #bot.loop.create_task(Check_If_Audio_is_playing(vc,msg))  
    else:
      await message.channel.send("You are not in a voice channel")
  await bot.process_commands(message)

  if message.content.startswith('download '):
    yt_URL = message.content[9:]
    await download_audio(yt_URL)

#Bot joines the voice channel
@bot.command()
async def join(ctx):
  channel = ctx.author.voice.channel
  await channel.connect()

#bot leaves the voice channel
@bot.command()
async def leave(ctx):
  vc = discord.utils.get(bot.voice_clients, guild=ctx.guild)
  if vc:
    await vc.disconnect()
  else:
    await ctx.send("I'm not in a voice channel.")
    
@bot.command()
async def surprise(ctx):
  await ctx.message.channel.send("||niggaaaa||")

#bot sends a picture using the cat API but this time it is under a spoiler
@bot.command()
async def yeet(ctx):
  response = requests.get('https://api.thecatapi.com/v1/images/search')
  data = response.json()
  picture = data[0]['url']
  await ctx.message.channel.send(f"|| {picture} ||")


@bot.command()
async def stop_audio(ctx):
  vc = discord.utils.get(bot.voice_clients, guild=ctx.guild)
  if vc and vc.is_playing():
    vc.stop()
    await ctx.send("Audio stopped and disconnected.")
    
@bot.command()
async def Queue(ctx):
  if len(queue_list) != 0:
    for i in range(len(queue_list)):
      await ctx.send(f"{i+1}. {queue_list[i]}")
  else:
   await ctx.send("Queue is empty.")
  
@bot.command()
async def skip(ctx):
  vc = discord.utils.get(bot.voice_clients, guild=ctx.guild)
  if vc and vc.is_playing():
    vc.stop()
    await ctx.send("skipped the audio ")
  else:
    await ctx.send("No audio is playing.")

    
###helper functions###

async def MP3_buffer_list(msg):
  files = glob.glob('audio*.mp3')
  files = natsorted(files)
  await msg.send(files)
  for file in files:
    await audio_files.put(file)
 
#checking if audio is playing from bot
async def Check_If_Audio_is_playing(vc,msg):
  while vc.is_playing():
    await asyncio.sleep(1)
  await vc.disconnect()
  await msg.send("addios nibba :smiling_imp:")

#creating a queue for URLs
async def Add_To_Queue(URL):
  global queue_index
  queue_list.append(URL)

#playing audio from the queue
async def Play_Audio_From_Queue(vc):
  while not audio_files.empty():
    audio = await audio_files.get()
    vc.play(discord.FFmpegPCMAudio(executable="ffmpeg", source=audio))
    while vc.is_playing():
      await asyncio.sleep(1)
    if not vc.not_playing():
      os.remove(audio)
  #once the audio_files queue is done then the queue i cleared
#  await clear_queue()

#clear Queue this needs futher implementation
async def clear_queue():
  global queue_index
  #clear the queue
  queue_list.clear()
  print(queue_list)
  #resets the queue
  queue_index = 0
  #clear the audio files once the queue is done 
  for file in glob.glob("audio*.mp3"):
    os.remove(file)
 

  audio_files = asyncio.Queue()
  #index for the queue list
  queue_index = 0


#TODO the while loop is causing all downloads to happen first before playing audio 
async def download_audio(URL):
  global queue_index
  await Add_To_Queue(URL)
  ydl_opts = {
      'format': 'bestaudio/best',
      'outtmpl': 'audio%(autonumber)02d.%(ext)s',
      'postprocessors':[{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '48',
      }],
      #'force-overwrites': True,
  }
  while queue_index < len(queue_list):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      ydl.download(queue_list)
    queue_index += 1
  #if not queue_list.empty():
  # yt_link = await queue_list.get()
  #  with yt_dlp.YoutubeDL(ydl_opts) as ydl:
  #    ydl.download(yt_link)


bot.run(os.getenv("DISCORD_TOKEN"))

#  if message.content.startswith('!playaudio '):
#  voice_channel = message.author.voice.channel
#  if voice_channel:
#    yt_URL = message.content[11:]
#    await Add_To_Queue(yt_URL)
#    for index in range(len(queue_list)):
#      if index > 1:
#       await message.channel.send(f"Added {queue_list[index]} to the queue")
#      if os.path.exists(Audio_File_Path):
#        os.remove(Audio_File_Path)
#      with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#        ydl.download([queue_list[index]])
#      vc = await voice_channel.connect()
#      vc.play(discord.FFmpegPCMAudio(executable = "ffmpeg",source = "audio.mp3"))
#     bot.loop.create_task(Check_If_Audio_is_playing(vc))
#      await message.channel.send('addios nibba :smiling_imp:')
#    else:
#      await message.channel.send("You are not in a voice channel")