import asyncio
import os
import sys


async def _idle_loop():
    while True:
        await asyncio.sleep(60)


def main():
    redis_url = os.getenv("REDIS_URL", "")
    if not redis_url:
        print("REDIS_URL not set — worker idling (no-op)")
        asyncio.run(_idle_loop())
        return

    print(f"REDIS_URL set — starting ARQ worker")
    # Import ARQ only when Redis is configured
    from arq import create_pool
    from arq.worker import Worker as ARQWorker
    from backend.app.worker import WorkerSettings

    # Override the redis_settings at runtime
    WorkerSettings.redis_settings = redis_url
    WorkerSettings.burst = False

    worker = ARQWorker(WorkerSettings)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(worker.run())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
