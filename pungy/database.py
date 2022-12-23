from functools import lru_cache
from typing import Any
from pungy.get_metadata import get_info_from_files

class Singleton(type):
    _instances: dict[Any, Any] = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class DataBase(metaclass=Singleton):
    def __init__(self, path=""):
        self.path = path
        self.files = []
        self.infos = []
        self.artists = []
        self.genres = []
        self.artists_genres = []
        self.last_results = []
        self.index = {}
        if path:
            self.populate_database()

    def populate_database(self):
        self.files.extend(self.path.glob("**/*.m[p4][3a]"))
        self.infos.extend(get_info_from_files(tuple(self.files)))
        self.artists = sorted(list({m.artist for m in self.infos}), key=lambda x: x.lower())
        self.genres = sorted(list({m.genre for m in self.infos}), key=lambda x: x.lower())
        self.artists_genres = sorted(list({(m.artist, m.genre) for m in self.infos}), key=lambda x: x[0].lower())
        self.last_results = self.infos
        self.index = {m.index: m for m in self.infos}

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
