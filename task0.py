"""

Задание 0. Разминка-ловушка.

Объяснение: В slow_main используется await внутри цикла for. Программа
ждет завершения каждого запроса по очереди (последовательно).
Исправление: В fast_main используется asyncio.gather, который запускает
все задачи конкурентно (одновременно).

Замеры времени:
slow : 0.65s
fast : 0.34s
"""

import asyncio
import time

import httpx

URLS = [f"https://picsum.photos/seed/{i}/800/600" for i in range(20)]


def timed(label, fn, *args):
    start = time.perf_counter()
    fn(*args)
    print(f"{label}: {time.perf_counter() - start:.2f}s")


async def fetch(client: httpx.AsyncClient, url: str) -> int:
    resp = await client.get(url)
    return resp.status_code


async def slow_main():
    async with httpx.AsyncClient(follow_redirects=True) as client:
        for url in URLS:
            await fetch(client, url)  # <-- ЛОВУШКА


async def fast_main():
    async with httpx.AsyncClient(follow_redirects=True) as client:
        tasks = [fetch(client, url) for url in URLS]
        await asyncio.gather(*tasks)  # <-- ИСПРАВЛЕНИЕ


if __name__ == "__main__":
    print("Задание 0")
    timed("slow ", lambda: asyncio.run(slow_main()))
    timed("fast ", lambda: asyncio.run(fast_main()))
