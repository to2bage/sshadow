import asyncio
import socket
import struct
from asyncio import transports
from typing import Optional

import constants
from protocols.shadowsocks.tcp_local_protocol import TcpLocalProtocol

"""
typing.Optional[Bool]: 表示这个值即可以是Bool, 也可以是None
"""

class ServerLocalProtocol(asyncio.Protocol):
    def __init__(self, loop: asyncio.BaseEventLoop, relay_host, relay_port):
        self.loop = loop
        self.relay_host = relay_host
        self.relay_port = relay_port
        self.client_transport = None
        self.remote_transport = None
        self.state = None

    def connection_made(self, transport: transports.BaseTransport) -> None:
        self.client_transport = transport   # 浏览器的连接
        sock = self.client_transport.get_extra_info("peername")
        print(f"Welcome {sock}")
        self.state = constants.SOCK5_PARSER_STAGE_INIT
        pass

    def connection_lost(self, exc: Optional[Exception]) -> None:
        pass

    def data_received(self, data: bytes) -> None:
        if self.state == constants.SOCK5_PARSER_STAGE_INIT:
            ver, nmethods, _ = struct.unpack("!BBB", data[:3])
            print(ver, "<=>", nmethods)
            self.client_transport.write(struct.pack("!BB", 5, 0))
            self.state = constants.SOCK5_PARSER_STAGE_HOST
            pass
        elif self.state == constants.SOCK5_PARSER_STAGE_HOST:
            ver, cmd, csv, atyp = struct.unpack("!BBBB", data[:4])
            if cmd == 1:
                # tcp
                if atyp == 1:
                    # ipv4
                    remote_host = socket.inet_ntoa(data[4:4+4])
                    remote_port = struct.unpack("!H", data[8:8+2])[0]
                    print(f"目的地址: {remote_host}:{remote_port}")
                    # 连接(remote_host, remote_port)
                    asyncio.create_task(self.connect_to_remote(remote_host, remote_port))
                    pass
                elif atyp == 3:
                    pass
                elif atyp == 4:
                    pass
                pass
            else:
                # ucp
                pass
            pass
        elif self.state == constants.SOCK5_PARSER_STAGE_DATA:
            self.remote_transport.write(data)
            pass
        pass

    def eof_received(self) -> Optional[bool]:
        pass

    # ---------------------------------------------- #
    async def connect_to_remote(self, remote_host, remote_port):
        try:
            remote_transport, tcp_local_protocol \
                = await self.loop.create_connection(lambda: TcpLocalProtocol(self.loop), remote_host, remote_port)
        except Exception as err:
            print(f"serer_local connect {remote_host}:{remote_port} got ERROR: {err}")
        else:
            self.remote_transport = remote_transport
            tcp_local_protocol.client_transport = self.client_transport

            hostip, port = remote_transport.get_extra_info('sockname')
            host = struct.unpack("!I", socket.inet_aton(hostip))[0]
            self.client_transport.write(
                struct.pack('!BBBBIH', 0x05, 0x00, 0x00, 0x01, host, port))
            self.state = constants.SOCK5_PARSER_STAGE_DATA
        pass

    pass