import logging
import os
from landez import MBTilesBuilder

logging.basicConfig(level=logging.DEBUG)
url = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
zoomlevels = [4, 5, 6, 7, 8]
bbox = (-7.818751263994194, 29.932874506926854, 72.01133072878456, 64.56842453507622)
mb = MBTilesBuilder(
    tiles_url=url,
    cache=False,
    filepath="esri-very-highres-2.mbtiles",
)
mb.add_coverage(bbox=bbox,
                zoomlevels=zoomlevels)
tile_tuples = mb.tileslist(bbox, zoomlevels)
print(tile_tuples[:20])
tile_urls = [
    url.format(x=x, y=y, z=z)
    for z, x, y in tile_tuples
]
print(tile_urls[-20:])

import random
import asyncio
from aiohttp import ClientSession

async def fetch(url, session):
    relative = url.split("/tile/")[1]
    os.makedirs("tiles-2/"+ relative.rsplit("/", 1)[0], exist_ok=True)
    async with session.get(url) as response:
        print(f"Reading {url}")
        content = await response.read()
        with open(f"tiles-2/{relative}", "wb") as f:
            f.write(content)


async def bound_fetch(sem, url, session):
    # Getter function with semaphore.
    async with sem:
        await fetch(url, session)


async def run(r):
    url = "http://localhost:8080/{}"
    tasks = []
    # create instance of Semaphore
    sem = asyncio.Semaphore(20)

    # Create client session that will ensure we dont open new connection
    # per each request.
    async with ClientSession() as session:
        for i, url in enumerate(tile_urls):
            # pass Semaphore and session to every GET request
            task = asyncio.ensure_future(bound_fetch(sem, url, session))
            tasks.append(task)

        responses = asyncio.gather(*tasks)
        await responses

number = 10000
loop = asyncio.get_event_loop()

future = asyncio.ensure_future(run(number))
loop.run_until_complete(future)


# mb.run()
