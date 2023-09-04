import asyncio


class TCPClient:
    def __init__(self, host: str, port: int):
        self._host = host
        self._port = port
        self._reader = None
        self._writer = None
        self._task = None

    async def start(self):
        self._reader, self._writer = await asyncio.open_connection(self._host, self._port)
        asyncio.create_task(self._listen())

    async def stop(self):
        self._task.cancel()
        self._writer.close()
        await self._writer.wait_closed()

    async def _listen(self):
        while True:
            data = await self._reader.read(1000)
            await asyncio.sleep(0)

    async def write(self, message: bytes):
        self._writer.write(message)
        await self._writer.drain()
