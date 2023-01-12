import asyncio
import discord
import os
import pytube.exceptions
import time
from discord.message import Message
from pytube import YouTube
from typing import Any


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
        self._filename = 0

    def _download_next_song(
            self
    ) -> None:
        """
        Downloads the next song in the list
        :return:
        """
        yt = YouTube(self._songs[0])
        self._currVideoLength = yt.length
        t = yt.streams.filter(only_audio=True)
        t[1].download(output_path="temp/", filename=f"{self._filename}.mp3")
        if self._filename > 10:
            self._filename = 0

    def _play_song(
            self
    ) -> None:
        """
        Plays the song in cache
        :return:
        """
        self._songs.pop()
        self._voice.play(discord.FFmpegPCMAudio(f"temp/{self._filename}.mp3", executable="ffmpeg/bin/ffmpeg.exe"))
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
                    self._voice = await message.author.voice.channel.connect()
                except:
                    pass

                while len(self._songs) > 0:
                    try:
                        await message.channel.send(f'downloading...')
                        self._filename += 1
                        local_file_name = self._filename
                        self._download_next_song()
                        await message.channel.send(f'playing {self._songs[0]}')
                        self._play_song()
                        await asyncio.sleep(self._currVideoLength + 1)
                        os.remove(f"temp/{local_file_name}.mp3")
                    except pytube.exceptions.RegexMatchError:
                        await message.channel.send(f'Cannot find link: {self._songs[0]}')
                        self._songs.pop()
            else:
                await message.channel.send(f"Added {self._songs[len(self._songs) - 1]} to the queue")

        elif message.content == '!stop':
            await message.channel.send(f'k')
            self._voice.stop()
            self._startTime = -1

        elif message.content == '!skip':
            self._voice.stop()
            await message.channel.send(f"k")
            if len(self._songs) > 0:
                await message.channel.send(f'downloading...')
                self._download_next_song()
            if len(self._songs) > 0:
                await message.channel.send(f'playing {self._songs[0]}')
                self._play_song()

        elif message.content == "!queue":
            await message.channel.send(f"There's {len(self._songs)} in the queue")

        elif message.content == "!reset":
            self._startTime = -1
            self._songs = []
            self._voice.stop()
            await message.channel.send(f"Reset")

        elif message.content == "!fuckoff":
            await message.channel.send(f"k")
            self._voice.stop()
            await self._voice.disconnect()

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


if __name__ == "__main__":
    with open("token.txt", 'r') as f:
        token = f.readline()

    intents = discord.Intents.default()
    intents.message_content = True
    client = MyClient(intents=intents)
    client.run(token)
