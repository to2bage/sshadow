import asyncio
from asyncio import transports
from typing import Optional


class BaseProtocol(asyncio.Protocol):
    def __init__(self, loop):
        self.loop = loop
        self.remote_transport = None
        self.client_transport = None

    def connection_made(self, transport: transports.BaseTransport) -> None:
        self.client_transport = transport   # 浏览器的连接
        sock = self.client_transport.get_extra_info("peername")
        print(f"Welcome {sock}")

    def connection_lost(self, exc: Optional[Exception]) -> None:
        if exc is not None:
            self.client_transport.close()
            self.client_transport = None
        pass

    def eof_received(self) -> Optional[bool]:
        self.client_transport.close()
        self.client_transport = None
        pass