from fastapi import FastAPI
from fastapi.responses import FileResponse

import urllib.request
from bs4 import BeautifulSoup
from datetime import date
import time
import json

from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    item_id: int

def getLatutiedot():
    data = []
    ajodata = {}
    req = urllib.request.Request(
        "http://www.seinajoki.fi/kulttuurijaliikunta/liikuntapalvelut/ulkoilureitistotjahiihtoladut_0/hiihtoladut.html"
    )
    response = urllib.request.urlopen(req)
    the_page = response.read()
    soup = BeautifulSoup(the_page, features="lxml")

    today = date.today()
    timestamp = time.time()
    table = soup.table.tr

    for row in soup.table.find_all("tr"):
        cols = row.find_all("td")
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele])  # Get rid of empty values

    ajodata["timestamp"] = timestamp
    for item in data:
        try:
            pvm = item[len(item) - 1].split(".")
            ajettu = date(today.year, int(pvm[1]), int(pvm[0]))
            erotus = today - ajettu
            ajodata[item[0]] = {"driven": str(ajettu), "delta": erotus.days}  # erotus.days
        except:
            if len(item) > 0:
                ajodata[item[0]] = {"driven": None, "delta": None}
    return ajodata


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse('favicon.ico')


@app.get("/item/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}


@app.get("/items/")
async def list_items():
    return [{"item_id": 1, "name": "Foo"}, {"item_id": 2, "name": "Bar"}]


@app.post("/items/")
async def create_item(item: Item):
    return item


@app.get("/hiihtoladut")
async def hiihtoladut():
    return getLatutiedot()