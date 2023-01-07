import discord
from pytube import YouTube
from typing import Any
from discord.message import Message
import time
import asyncio

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
        self._songs = []

    def _download_next_song(
            self
    ) -> None:
        """
        Downloads the next song in the list
        :return:
        """
        if len(self._songs) > 0:
            yt = YouTube(self._songs[0])
            self._currVideoLength = yt.length
            t = yt.streams.filter(only_audio=True)
            t[1].download(output_path="temp/", filename="1.mp4")

    def _play_song(
            self,
    ) -> None:
        """
        Plays the song in cache
        :return:
        """
        if len(self._songs) > 0:
            self._songs.pop()
            self._voice.play(discord.FFmpegPCMAudio("temp/1.mp4", executable="ffmpeg/bin/ffmpeg.exe"))
            self._voice.source = discord.PCMVolumeTransformer(self._voice.source)
            self._voice.source.volume = 0.5
            self._startTime = time.time()

    async def on_message(
            self,
            message: Message
    ):
        if message.content[0:5] == '!play':
            self._songs.append(message.content[6:])

            if self._startTime == -1 or \
                    time.time() - self._startTime > (self._currVideoLength + 1):
                self._startTime = -1

                try:
                    channel = message.author.voice.channel
                    self._voice = await channel.connect()
                except:
                    pass

                await message.channel.send(f'downloading...')
                self._download_next_song()

                await message.channel.send(f'playing {self._songs[0]}')
                self._play_song()
            else:
                await message.channel.send(f"Added {self._songs[len(self._songs) - 1]} to the queue")

        elif message.content == '!stop':
            self._voice.stop()
            self._startTime = -1
            await message.channel.send(f'k')

        elif message.content == '!skip':
            self._voice.stop()
            self._download_next_song()
            self._play_song()
            await message.channel.send(f"k")

        elif message.content == "!queue":
            await message.channel.send(f"There's {len(self._songs)} in the queue")

    async def on_ready(
            self
    ) -> None:
        print('Logged on as', self.user)

    async def on_voice_state_update(
            self,
            member,
            before,
            after
    ):
        self._startTime = -1
        print("state updated")


if __name__ == "__main__":
    with open("token.txt", 'r') as f:
        token = f.readline()

    intents = discord.Intents.default()
    intents.message_content = True
    client = MyClient(intents=intents)
    client.run(token)
