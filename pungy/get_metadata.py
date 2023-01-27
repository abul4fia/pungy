import base64
from functools import lru_cache
from typing import Optional
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4, MP4Cover
from mutagen import File
from pathlib import Path
from dataclasses import dataclass
from datetime import timedelta


@dataclass
class SongInfo:
    """Stores the metadata for a song"""
    title: str
    artist: str
    album: str
    duration: timedelta
    genre: str
    file: str
    format: str
    index: int = -1

    def __contains__(self, txt):
        """This function returns True if the given text appears in any of the
        metadata fields"""
        fields = ("title", "artist", "album", "genre", "file")
        return any(txt.lower() in getattr(self, field).lower() for field in fields)


@dataclass
class CoverData:
    """Stores the album cover for a song"""
    data: str
    mime: str


@lru_cache
def get_info(filename: Path) -> SongInfo:
    if filename.suffix == ".mp3":
        return get_mp3_info(filename)
    elif filename.suffix == ".m4a":
        return get_m4a_info(filename)
    else:
        raise ValueError(f"{filename} is not mp3 or m4a")


@lru_cache
def get_cover(filename: Path) -> CoverData:
    if filename.suffix == ".mp3":
        return get_mp3_cover(filename)
    elif filename.suffix == ".m4a":
        return get_m4a_cover(filename)
    else:
        raise ValueError(f"{filename} is not mp3 or m4a")


def get_mp3_info(filename: Path) -> SongInfo:
    # Default values extracted from filename
    album = str(filename.parent.name)
    artist = str(filename.name).split("-")[0].strip()
    genre = "unknown"
    title = str(filename.name).split("-", maxsplit=1)[-1].strip()

    # Override with metadata extracted by mutagen
    mp3file = MP3(str(filename), ID3=EasyID3)
    album = (mp3file.get("album") or [album])[0]
    artist = (mp3file.get("artist") or [artist])[0]
    genre = (mp3file.get("genre") or [genre])[0]
    title = (mp3file.get("title") or [title])[0]
    duration = timedelta(seconds=mp3file.info.length)  # type: ignore

    return SongInfo(title, artist, album, duration, genre, str(filename), "mp3")


def get_m4a_info(filename: Path) -> SongInfo:
    # Default values extracted from filename
    album = str(filename.parent.name)
    artist = str(filename.name).split("-")[0].strip()
    genre = "unknown"
    title = str(filename.name).split("-", maxsplit=1)[-1].strip()

    # Override with metadata extracted by mutagen
    mp4file = MP4(str(filename))
    album = (mp4file.get("©alb") or [album])[0]
    artist = (mp4file.get("©ART") or [artist])[0]
    genre = (mp4file.get("©gen") or [genre])[0]

    title = (mp4file.get("©nam") or [title])[0]
    duration = timedelta(seconds=mp4file.info.length)  # type: ignore

    return SongInfo(title, artist, album, duration, genre, str(filename), "m4a")


def get_mp3_cover(filename: Path) -> CoverData:
    cover = File(str(filename))
    art = ""
    mime = ""
    data = cover.get("APIC:")
    if data:
        art = base64.b64encode(data.data).decode("ascii")
        mime = data.mime
    return CoverData(art, mime)


def get_m4a_cover(filename: Path) -> CoverData:
    mp4file = MP4(str(filename))
    art = ""
    mime = ""
    data: Optional[MP4Cover] = None
    covers = mp4file.get("covr")
    if covers:
        data = covers[0]
    if data:
        art = base64.b64encode(data).decode("ascii")
        mime = (
            "image/jpeg"
            if data.imageformat == data.FORMAT_JPEG
            else "image/png"
            if data.imageformat == data.FORMAT_PNG
            else ""
        )
    return CoverData(art, mime)


@lru_cache
def get_info_from_files(files:tuple[Path, ...]) -> list[SongInfo]:
    # print(f"get_info_from_files(tuple[{len(files)}])")
    results = []
    i = 0
    for f in files:
        try:
            info = get_info(f)
        except Exception as e:
            print(f"File {f} caused exception '{e}'")
            continue
        info.index = i
        i += 1
        results.append(info)
    return results