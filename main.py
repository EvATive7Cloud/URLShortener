from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import RedirectResponse, HTMLResponse
from peewee import SqliteDatabase, Model, CharField
from pydantic import BaseModel as PydanticModel
import argparse
import os
import random
import string
import sys
from pathlib import Path

import uvicorn


db = SqliteDatabase("shortlinks.db")


class DBModel(Model):
    class Meta:
        database = db


class ShortLink(DBModel):
    original_url = CharField(unique=True)
    short_url = CharField(unique=True)


db.connect()
db.create_tables([ShortLink], safe=True)

# FastAPI setup
app = FastAPI()


class URLItem(PydanticModel):
    url: str


def generate_short_link(url: str) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(random.choices(alphabet, k=10))


def get_resource_path(*relative_parts: str) -> Path:
    """
    Resolve a resource path that works both in development and when
    bundled with PyInstaller (using the _MEIPASS temporary folder).
    """
    if hasattr(sys, "_MEIPASS"):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parent
    return base_path.joinpath(*relative_parts)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    index_path = get_resource_path("templates", "index.html")
    if not index_path.is_file():
        raise HTTPException(status_code=500, detail="Frontend file not found")
    content = index_path.read_text(encoding="utf-8")
    return HTMLResponse(content=content)


@app.post("/shorten")
async def create_short_link(item: URLItem):
    url = item.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    # If URL already exists, return the existing short link
    short_link = ShortLink.get_or_none(ShortLink.original_url == url)
    if short_link is None:
        # Generate a unique random short URL
        max_attempts = 10000
        for _ in range(max_attempts):
            candidate = generate_short_link(url)
            if not ShortLink.get_or_none(ShortLink.short_url == candidate):
                short_link = ShortLink.create(
                    original_url=url,
                    short_url=candidate,
                )
                break
        else:
            raise HTTPException(
                status_code=500, detail="Failed to generate unique short URL"
            )

    return {"original_url": short_link.original_url, "short_url": short_link.short_url}


@app.get("/{short_url}")
async def redirect_to_url(short_url: str):
    short_link = ShortLink.get_or_none(ShortLink.short_url == short_url)
    if short_link is None:
        return Response(status_code=404, content="Not Found")
    return RedirectResponse(short_link.original_url)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start the FastAPI server.")
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=11000,
        help="Port number to run the FastAPI server on.",
    )
    args = parser.parse_args()
    port = args.port
    uvicorn.run(app, host="0.0.0.0", port=port)
