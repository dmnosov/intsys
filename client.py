import asyncio
import contextlib
import datetime
import logging
import random
import sys


def setup_logger(filename: str = "client.log") -> logging.Logger:
    logger = logging.getLogger("client")
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(filename, encoding="utf-8")
    logger.addHandler(file_handler)

    return logger


def log(
    logger: logging.Logger,
    request_time: str | None = "",
    request_text: str | None = "",
    response_time: str | None = None,
    response_text: str | None = None,
    timeout_time: str | None = None,
) -> None:
    date = datetime.datetime.now(tz=datetime.timezone.utc).date().strftime("%Y-%m-%d")
    if timeout_time:
        logger.info(f"{date};{request_time};{request_text};{timeout_time};(таймаут)")
        return
    logger.info(f"{date};{request_time};{request_text};{response_time};{response_text}")


class Client:
    def __init__(self, logger: logging.Logger, host: str = "127.0.0.1", port: int = 9988) -> None:
        self.logger = logger

        self.host = host
        self.port = port

        self.reader = None
        self.writer = None

        self.request_id = 0
        self.read_queue = asyncio.Queue()

    async def start(self) -> None:
        self.reader, self.writer = await asyncio.open_connection(host=self.host, port=self.port)
        asyncio.create_task(self.read())

        while True:
            await asyncio.sleep(random.uniform(0.3, 3.0))
            message = f"[{self.request_id}] PING"
            request_time = datetime.datetime.now(tz=datetime.timezone.utc).strftime("%H:%M:%S.%f")[:-3]
            self.writer.write((message + "\n").encode("ascii"))
            await self.writer.drain()

            try:
                response, response_time = await asyncio.wait_for(self.read_queue.get(), timeout=2.0)
                log(
                    self.logger,
                    request_time=request_time,
                    request_text=message,
                    response_time=response_time,
                    response_text=response,
                )
            except asyncio.TimeoutError:
                timeout_time = datetime.datetime.now(tz=datetime.timezone.utc).strftime("%H:%M:%S.%f")[:-3]
                log(
                    self.logger,
                    request_time=request_time,
                    request_text=message,
                    timeout_time=timeout_time,
                )
            finally:
                self.request_id += 1

    async def read(self) -> None:
        while True:
            data = await self.reader.readline()
            if not data:
                break
            response = data.decode("ascii").strip()
            response_time = datetime.datetime.now(tz=datetime.timezone.utc).strftime("%H:%M:%S.%f")[:-3]
            if response.endswith("keepalive"):
                log(
                    self.logger,
                    response_time=response_time,
                    response_text=response,
                )
                continue
            await self.read_queue.put((response, response_time))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python client.py <client_id>")  # noqa: T201
        sys.exit(1)
    client_id = int(sys.argv[1])
    with contextlib.suppress(KeyboardInterrupt):
        client = Client(setup_logger(filename=f"client_{client_id}.log"))
        asyncio.run(client.start())
