from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from peewee import SqliteDatabase, Model, CharField
from pydantic import BaseModel
from hashlib import md5
import argparse
import uvicorn
from starlette.templating import Jinja2Templates


db = SqliteDatabase('shortlinks.db')


class BaseModel(Model):
    class Meta:
        database = db


class ShortLink(BaseModel):
    original_url = CharField(unique=True)
    short_url = CharField(unique=True)


db.connect()
db.create_tables([ShortLink], safe=True)

# FastAPI setup
app = FastAPI()
templates = Jinja2Templates(directory="templates")


class URLItem(BaseModel):
    url: str


def generate_short_link(url: str) -> str:
    return md5(url.encode()).hexdigest()[:6]


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/shorten")
async def create_short_link(url: str = Form(...)):
    short_link = ShortLink.get_or_none(ShortLink.original_url == url)
    if short_link is None:
        short_url = generate_short_link(url)
        short_link = ShortLink.create(original_url=url, short_url=short_url)
    return {"original_url": short_link.original_url, "short_url": short_link.short_url}


@app.get("/{short_url}")
async def redirect_to_url(short_url: str):
    short_link = ShortLink.get_or_none(ShortLink.short_url == short_url)
    if short_link is None:
        raise HTTPException(status_code=404, detail="Short link not found")
    return RedirectResponse(short_link.original_url)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start the FastAPI server.")
    parser.add_argument('-p', '--port', type=int, default=11000, help="Port number to run the FastAPI server on.")
    args = parser.parse_args()
    port = args.port
    uvicorn.run(app, host="0.0.0.0", port=port)
