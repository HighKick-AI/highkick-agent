import asyncio
from typing import Any, Awaitable, Callable, Optional, Tuple

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Callable, Coroutine

from fastapi import FastAPI

TaskFn = Callable[..., Awaitable[Any]]
CoroutineType = Callable[[], Coroutine]

class AsyncTaskPool:
    """
    A FIFO async task pool with bounded concurrency.
    - add_task(fn, *args, **kwargs) enqueues a coroutine function call.
    - The first added tasks are the first to start executing (up to `pool_size` in parallel).
    - Each add_task() returns an awaitable Future for that task's result.
    - Use `await pool.aclose()` (or async context manager) for graceful shutdown.
    """
    def __init__(self, pool_size: int):
        if pool_size < 1:
            raise ValueError("pool_size must be >= 1")
        self._pool_size = pool_size
        self._queue: asyncio.Queue[
            Tuple[TaskFn, tuple, dict, asyncio.Future]
        ] = asyncio.Queue()
        self._workers: list[asyncio.Task] = []
        self._closed = False
        self._start_workers()
        print("AsyncTaskPool created")

    def _start_workers(self) -> None:
        self._workers = [asyncio.create_task(self._worker(i)) for i in range(self._pool_size)]

    async def _worker(self, wid: int) -> None:
        try:
            while True:
                fn, args, kwargs, fut = await self._queue.get()
                if fut.cancelled():
                    self._queue.task_done()
                    continue
                try:
                    # Run the user coroutine
                    result = await fn(*args, **kwargs)
                except Exception as exc:
                    if not fut.done():
                        fut.set_exception(exc)
                else:
                    if not fut.done():
                        fut.set_result(result)
                finally:
                    self._queue.task_done()
        except asyncio.CancelledError:
            # Drain: if canceled, just exit
            pass

    def add_task(self, fn: TaskFn, *args, **kwargs) -> "asyncio.Future[Any]":
        """
        Enqueue a coroutine function (not a coroutine object).
        Returns a Future that resolves/rejects with the task's result/exception.
        """
        if self._closed:
            raise RuntimeError("Pool is closed; cannot add new tasks.")
        fut: asyncio.Future = asyncio.get_event_loop().create_future()
        # FIFO: asyncio.Queue preserves put() order; workers consume in that order
        self._queue.put_nowait((fn, args, kwargs, fut))
        return fut

    async def join(self) -> None:
        """Wait until all currently enqueued tasks are processed."""
        await self._queue.join()

    async def aclose(self) -> None:
        """
        Gracefully stop the pool after all queued tasks finish.
        Further add_task() calls will fail.
        """
        if self._closed:
            return
        print("AsyncTaskPool stopping...")
        self._closed = True
        # Wait for queue to drain
        await self._queue.join()
        # Cancel workers and wait for them to finish
        for w in self._workers:
            w.cancel()
        await asyncio.gather(*self._workers, return_exceptions=True)
        print("AsyncTaskPool stopped")

    # Async context manager convenience
    async def __aenter__(self) -> "AsyncTaskPool":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()


def init_task_pool(app: FastAPI) -> CoroutineType:
    async def _init() -> None:
        pool = AsyncTaskPool(1)
        app.state.task_pool = pool

    return _init


def close_task_pool(app: FastAPI) -> CoroutineType:
    async def _close() -> None:
        if hasattr(app.state, "task_pool"):
            await app.state.task_pool.aclose()

    return _close