import asyncio
from aiohttp import ClientSession
from common.constants import ROOT_DIR
import random
import base64
import time


loop = asyncio.get_event_loop()

url = 'http://localhost:5000/ping'
counter = 0
time_for_request = []
n = 80

static_folder = ROOT_DIR / 'static'
test_image = static_folder / '2_2.jpg'


async def get(url, session):
    global counter
    start = time.time()
    async with session.get(url) as response:
        counter += response.status == 200
        end = time.time()
        time_for_request.append(end - start)
        return await response.read()


async def fetch(url, session):
    global counter
    with open(test_image, "rb") as imageFile:
        imageStr = base64.b64encode(imageFile.read()).decode('utf-8')
    start = time.time()
    async with session.post(url, json={'photo': imageStr}) as response:
        counter += response.status == 200
        end = time.time()
        time_for_request.append(end - start)
        return await response.read()


async def run(n):
    tasks = []

    async with ClientSession() as session:
        for i in range(n):
            delay = random.randint(0, 2)
            await asyncio.sleep(delay)
            task = asyncio.ensure_future(get(url, session))
            tasks.append(task)

        await asyncio.gather(*tasks)


future = asyncio.ensure_future(run(n))
loop.run_until_complete(future)
print(time_for_request)
print(sum(time_for_request) / n)
assert counter == n
