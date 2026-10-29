"""
Задание 3 (*). Вынос CPU-bound-вычислений.

Объяснение:
1. При прямом вызове heavy() внутри корутины (use_pool=False) event loop
блокируется, и тикер (точки) замирает, так как CPU-bound задача занимает поток.
2. При использовании ProcessPoolExecutor и loop.run_in_executor()
тяжелые вычисления выносятся в отдельный процесс, освобождая event loop.
Точки продолжают бежать.

Замеры времени:
cpu: 0.47s
"""

import asyncio
import hashlib
import os
import time
from concurrent.futures import ProcessPoolExecutor

import httpx

URLS = [f"https://picsum.photos/seed/{i}/800/600" for i in range(20)]


def timed(label, fn, *args):
    start = time.perf_counter()
    fn(*args)
    print(f"{label}: {time.perf_counter() - start:.2f}s")


def heavy(body: bytes) -> str:
    return hashlib.sha256(body * 1000).hexdigest()


async def ticker():
    while True:
        print(".", end="", flush=True)
        await asyncio.sleep(0.1)


async def cpu_main(use_pool: bool):
    async with httpx.AsyncClient(follow_redirects=True) as client:
        print(f"\nСкачиваем картинку (Процессы: {use_pool})...")
        resp = await client.get(URLS[0])
        body = resp.content

        print("Начинаем вычисления (смотрите на точки):")
        ticker_task = asyncio.create_task(ticker())

        if use_pool:
            loop = asyncio.get_running_loop()
            with ProcessPoolExecutor(max_workers=os.cpu_count()) as pool:
                result = await loop.run_in_executor(pool, heavy, body)
        else:
            # БЛОКИРУЮЩИЙ вызов: цикл замрет
            result = heavy(body)

        ticker_task.cancel()
        print(f"\nХеш готов: {result[:15]}...")


def run_pool():
    asyncio.run(cpu_main(use_pool=True))


if __name__ == "__main__":
    print("Задание 3")
    # Сначала демонстрируем проблему (раскомментируйте, если хотите увидеть, как все замирает):
    # print("\n--- Демонстрация БЕЗ процессов (loop заблокирован) ---")
    # asyncio.run(cpu_main(use_pool=False))

    print("\n--- Демонстрация С процессами (loop свободен) ---")
    timed("cpu", run_pool)
