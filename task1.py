"""
Задание 1. Синхронно vs Асинхронно.

Объяснение: Синхронный requests.get блокирует поток, пока не скачается
картинка. Асинхронный httpx позволяет скачивать 20 картинок одновременно,
поэтому разница во времени колоссальная.

Замеры времени:
sync : 4.99s
async: 0.39s
"""

import asyncio
import time

import httpx
import requests

URLS = [f"https://picsum.photos/seed/{i}/800/600" for i in range(20)]


def timed(label, fn, *args):
    start = time.perf_counter()
    fn(*args)
    print(f"{label}: {time.perf_counter() - start:.2f}s")


def sync_main():
    for url in URLS:
        requests.get(url)  # по очереди


async def fetch(client: httpx.AsyncClient, url: str) -> int:
    resp = await client.get(url)
    return resp.status_code


async def fast_main():
    async with httpx.AsyncClient(follow_redirects=True) as client:
        tasks = [fetch(client, url) for url in URLS]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    print("Задание 1")
    timed("sync ", sync_main)
    timed("async", lambda: asyncio.run(fast_main()))
