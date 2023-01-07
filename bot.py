import discord
from pytube import YouTube
from typing import Any
from discord.message import Message
import time

file_path = "temp/file_example_MP3_700KB.mp3"


class MyClient(discord.Client):
    def __init__(
            self,
            *,
            intents,
            **options: Any):

        super().__init__(intents=intents, **options)
        self._voice = None
        self._currVideoLength = 0
        self._startTime = -1

    async def on_ready(
            self
    ) -> None:
        print('Logged on as', self.user)

    async def on_message(
            self,
            message: Message
    ):
        if message.content[0:5] == '!play':
            if self._startTime == -1 or \
                    time.time() - self._startTime > (self._currVideoLength + 1):
                self._startTime = -1

                url = message.content[6:]
                await message.channel.send(f'downloading...')
                yt = YouTube(url)
                self._currVideoLength = yt.length
                t = yt.streams.filter(only_audio=True)
                t[1].download(output_path="temp/", filename="1.mp4")

                await message.channel.send(f'playing {url}')

                channel = message.author.voice.channel

                try:
                    self._voice = await channel.connect()
                except:
                    pass

                self._voice.play(discord.FFmpegPCMAudio("temp/1.mp4", executable="ffmpeg/bin/ffmpeg.exe"))
                self._voice.source = discord.PCMVolumeTransformer(self._voice.source)
                self._voice.source.volume = 0.5
                self._startTime = time.time()
            else:
                await message.channel.send(f"I'm too retarded to play more than one song at a time right now")


if __name__ == "__main__":
    with open("token.txt", 'r') as f:
        token = f.readline()

    intents = discord.Intents.default()
    intents.message_content = True
    client = MyClient(intents=intents)
    client.run(token)
