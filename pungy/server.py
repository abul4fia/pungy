from typing import Optional
from fastapi import FastAPI, Request, HTTPException, Form, Depends
import asyncio
import aiofiles
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, Response, FileResponse, RedirectResponse
from pathlib import Path
import uvicorn
from pydantic import BaseModel
import typer
from pungy.get_metadata import get_cover, get_info_from_files
from pungy.database import DataBase, get_db


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    return RedirectResponse("/static/index.html")


@app.post("/getSongs")
async def get_songs(
    filter: str = Form(""), artist: str = Form(""), genre: str = Form(""),
    db: DataBase =Depends(get_db)
):
    musics = []
    for m in db.filter(filter, artist, genre):
        musics.append({
            "file": m.file,
            "title": m.title,
            "artist": m.artist,
            "album": m.album,
            "genre": m.genre,
            "index": m.index
        })
    return {"files": musics}


@app.post("/getInfos")
async def get_info(
    index: int = Form(),
    db: DataBase =Depends(get_db)
):
    song = db.get(index)
    if not song:
        raise HTTPException(404, detail=f"Song with {index=} not found")
    cover = get_cover(Path(song.file))
    response = {
        'file': song.file, 
        'infos': {
            "artist": song.artist,
            "genre": song.genre,
            "album": song.album,
            "title": song.title
        },
        "art": cover.data, 
        "mime": cover.mime
        }
    return response


@app.get('/getGenres')
def getGenres(filter: str = "", db: DataBase=Depends(get_db)):
    if filter:
        return db.genres_filtered(filter)
    return db.genres

@app.get('/getArtists')
def getGenres(filter: str= "", db: DataBase=Depends(get_db)):
    if filter:
        return db.artists_filtered(filter)
    return db.artists_genres

@app.get('/file/')
def getFile(path: str):
    print(path)
    return FileResponse(Path(path), headers={"Accept-ranges": "bytes"})

def main(
    path: str = typer.Option("/mnt/media/Musica", "--path", "-P"),
    port: int = typer.Option(8000, "--port", "-p"),
):
    database = DataBase(Path(path))    
    print(f"Detectados {len(database.files)} ficheros")
    uvicorn.run("pungy.server:app", host="0.0.0.0", port=port, workers=1)


if __name__ == "__main__":
    typer.run(main)
