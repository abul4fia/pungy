from functools import lru_cache
from pathlib import Path
import random
from typing import Any
from pungy.get_metadata import get_info_from_files

class Singleton(type):
    _instances: dict[Any, Any] = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class DataBase(metaclass=Singleton):
    def __init__(self, path:Path=Path(""), shuffle:bool=False, debug:bool=False):
        self.path = path
        self.files = []
        self.infos = []
        self.artists = []
        self.genres = []
        self.artists_genres = []
        self.last_results = []
        self.index = {}
        self.shuffle = shuffle
        self.debug = debug
        self.populate_database()

    def populate_database(self):
        if self.path.is_dir():
            self.populate_files_from_folder()
        else:
            self.populate_files_from_playlist()
        if self.shuffle:
            random.shuffle(self.files)
        self.infos.extend(get_info_from_files(tuple(self.files)))
        self.artists = sorted(list({m.artist for m in self.infos}), key=lambda x: x.lower())
        self.genres = sorted(list({m.genre for m in self.infos}), key=lambda x: x.lower())
        self.artists_genres = sorted(list({(m.artist, m.genre) for m in self.infos}), key=lambda x: x[0].lower())
        self.last_results = self.infos
        self.index = {m.index: m for m in self.infos}

    def populate_files_from_folder(self):
        self.files.extend(self.path.glob("**/*.m[p4][3a]"))

    def populate_files_from_playlist(self):
        if self.path.suffix != ".m3u":
            raise ValueError("Sólo se soportan listas de reproducción .m3u")
        folder = self.path.parent
        with self.path.open() as f:
            for line in f:
                line = line.strip()
                if line.startswith("#"):
                    continue
                if not line.endswith(".mp3") and not line.endswith(".m4a"):
                    continue
                self.files.append(Path(folder) / Path(line))

    def get(self, index):
        return self.index.get(index)

    @lru_cache
    def artists_filtered(self, filter):
        if not filter:
            return self.artists_genres
        return sorted(list({(m.artist, m.genre) for m in self.infos if filter in m}))

    @lru_cache
    def genres_filtered(self, filter):
        if not filter:
            return self.genres
        return sorted(list({m.genre for m in self.infos if filter in m}))

    @lru_cache
    def filter(self, filter="", artist="", genre=""):
        result = []
        for m in self.infos:
            if artist and artist!=m.artist:
                continue
            if genre and genre!=m.genre:
                continue
            if filter and filter not in m:
                continue
            result.append(m)
        return result

    def updating_filter(self, filter="", artist="", genre=""):
        self.last_results = self.filter(filter, artist, genre)
        return self.last_results


def get_db():
    db = DataBase()
    yield db
