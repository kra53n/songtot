from os import getcwd, remove
from subprocess import Popen, PIPE

from ytmdl.yt import dw, search, logger
from ytmdl.defaults import DEFAULT


DEFAULT.SONG_TEMP_DIR = getcwd()


async def search_videos_by_query(query_name: str, lim: int):
    return search(query_name, False, False, lim=lim)


async def process_song(song_name: str, ext: str):
    song_name += f'.{ext}'
    cmd = ['ffmpeg', '-i', song_name.replace(' ', '#'), song_name]
    Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True).communicate('y')


async def load_video_to_server(href: str, song_name: str):
    dw(value='https://www.youtube.com' + href, song_name=song_name, no_progress=True)
    logger.info(f'song: {song_name}')
    await process_song(song_name, 'mp3')
    remove(song_name.replace(' ', '#') + '.mp3')
