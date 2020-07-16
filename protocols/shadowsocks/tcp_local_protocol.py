import asyncio
import socket
import struct
from asyncio import transports
from typing import Optional


class TcpLocalProtocol(asyncio.Protocol):
    def __init__(self, loop):
        self.loop = loop
        self.client_transport = None
        self.remote_transport = None

    def connection_made(self, transport: transports.BaseTransport) -> None:
        self.remote_transport = transport   # server_local 与 server_relay的连接
        pass

    def connection_lost(self, exc: Optional[Exception]) -> None:
        pass

    def data_received(self, data: bytes) -> None:
        if data == b"good":
            # TODO: 获得中继主机连接目的主机成功之后的信息之后, 完成sock5协议的扫尾工作
            hostip, port = self.remote_transport.get_extra_info('sockname')
            host = struct.unpack("!I", socket.inet_aton(hostip))[0]
            self.client_transport.write(
                struct.pack('!BBBBIH', 0x05, 0x00, 0x00, 0x01, host, port))
            pass
        else:
            self.client_transport.write(data)
        pass

    def eof_received(self) -> Optional[bool]:
        pass