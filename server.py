import asyncio
import contextlib
import datetime
import logging
import random


def setup_logger() -> logging.Logger:
    logger = logging.getLogger("server")
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler("server.log", encoding="utf-8")
    logger.addHandler(file_handler)

    return logger


def log(
    logger: logging.Logger,
    request_time: str,
    request_text: str,
    response_time: str | None = None,
    response_text: str | None = None,
    ignored: bool = False,
) -> None:
    date = datetime.datetime.now(tz=datetime.timezone.utc).date().strftime("%Y-%m-%d")
    if ignored:
        logger.info(f"{date};{request_time};{request_text};(проигнорировано)")
        return
    logger.info(f"{date};{request_time};{request_text};{response_time};{response_text}")


class Server:
    def __init__(self, logger: logging.Logger, port: int = 9988) -> None:
        self.logger = logger
        self.port = port

        self.clients: set[asyncio.StreamWriter] = set()
        self.response_counter = 0

    async def start(self) -> None:
        server = await asyncio.start_server(self.handle, port=self.port)
        async with server:
            await server.serve_forever()

    async def handle(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        client_id = self._add_client(writer)
        try:
            while True:
                data = await reader.readline()
                if not data:
                    break
                request_time = datetime.datetime.now(tz=datetime.timezone.utc).strftime("%H:%M:%S.%f")[:-3]
                try:
                    request = data.decode("ascii").strip()

                    if random.random() < 0.1:
                        log(self.logger, request_time, request, ignored=True)
                        continue

                    await asyncio.sleep(random.uniform(0.1, 1.0))

                    req_number = request.strip("[]").split()[0]
                    response = f"[{self.response_counter}/{req_number[:-1]}] PONG ({client_id})"
                    self.response_counter += 1

                    response_time = datetime.datetime.now(tz=datetime.timezone.utc).strftime("%H:%M:%S.%f")[:-3]
                    writer.write((response + "\n").encode("ascii"))
                    await writer.drain()

                    log(
                        self.logger,
                        request_time,
                        request,
                        response_time=response_time,
                        response_text=response,
                    )
                except UnicodeDecodeError:
                    pass
        finally:
            self.clients.discard(writer)
            writer.close()
            await writer.wait_closed()

    async def start_broadcast(self) -> None:
        while True:
            for writer in self.clients:
                writer.write((f"[{self.response_counter}] keepalive" + "\n").encode("ascii"))
                await writer.drain()
            await asyncio.sleep(5)

    def _add_client(self, client: asyncio.StreamWriter) -> int:
        self.clients.add(client)
        return len(self.clients)


async def main() -> None:
    server = Server(setup_logger())
    asyncio.create_task(server.start_broadcast())
    await server.start()


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
