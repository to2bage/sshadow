import asyncio
from asyncio import transports
from typing import Optional


class TcpRelayProtocol(asyncio.Protocol):
    def __init__(self, loop):
        self.loop = loop
        self.client_transport = None
        self.remote_transport = None

    def connection_made(self, transport: transports.BaseTransport) -> None:
        self.remote_transport = transport   # server_relay 与 remote的连接
        pass

    def connection_lost(self, exc: Optional[Exception]) -> None:
        pass

    def data_received(self, data: bytes) -> None:
        self.client_transport.write(data)
        pass

    def eof_received(self) -> Optional[bool]:
        pass