"""
Задание 2. Реальный I/O и обработка ошибок.

Объяснение:
Добавлен таймаут 5 секунд, 3 попытки с экспоненциальным backoff (1с, 2с).
Ошибки перехватываются через return_exceptions=True, поэтому битые URL
не роняют всю программу, а попадают в список ошибок.

Замеры времени:
Общее время: 19.17s
"""

import asyncio
import time

import httpx

URLS = [f"https://picsum.photos/seed/{i}/800/600" for i in range(20)]


def timed(label, fn, *args):
    start = time.perf_counter()
    fn(*args)
    print(f"{label}: {time.perf_counter() - start:.2f}s")


BAD_URLS = ["https://no-such-site.invalid", "https://httpbin.org/delay/10"]
ALL_URLS = URLS + BAD_URLS


async def robust_fetch(client: httpx.AsyncClient, url: str) -> int:
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            resp = await client.get(url, timeout=5.0)
            resp.raise_for_status()
            return resp.status_code
        except (httpx.RequestError, httpx.HTTPStatusError):
            if attempt == max_attempts - 1:
                raise
            wait_time = 2**attempt
            print(f"Ошибка на {url}. Ждем {wait_time}с...")
            await asyncio.sleep(wait_time)


async def robust_main():
    results = []
    errors = []
    async with httpx.AsyncClient(follow_redirects=True) as client:
        tasks = [robust_fetch(client, url) for url in ALL_URLS]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        for url, res in zip(ALL_URLS, responses):
            if isinstance(res, Exception):
                errors.append((url, str(res)))
            else:
                results.append((url, res))
    return results, errors


def run_robust_main():
    start = time.perf_counter()
    results, errors = asyncio.run(robust_main())
    print(f"Успешно скачано: {len(results)}")
    print(f"Ошибок: {len(errors)}")
    for err in errors:
        print(f"  Ошибка: {err[0]} -> {err[1]}")
    print(f"Общее время: {time.perf_counter() - start:.2f}s")


if __name__ == "__main__":
    print("Задание 2")
    timed("robust", run_robust_main)
