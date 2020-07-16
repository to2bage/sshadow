import asyncio
import socket
import struct
from asyncio import transports

import constants
from protocols.shadowsocks.tcp_relay_protocol import TcpRelayProtocol
from protocols.shadowsocks.base_protocol import BaseProtocol

class ServerRelayProtocol(BaseProtocol):
    def __init__(self, loop):
        super().__init__(loop)
        self.state = None

    def connection_made(self, transport: transports.BaseTransport) -> None:
        super().connection_made(transport)
        self.state = constants.RELAY_SERVER_STAGE_CONNED
        pass


    def data_received(self, data: bytes) -> None:
        if self.state == constants.RELAY_SERVER_STAGE_CONNED:
            remote_host = socket.inet_ntoa(data[:4])
            remote_port = struct.unpack("!H", data[4:4+2])[0]
            print(f"GET {remote_host}:{remote_port}")
            # TODO: 连接{remote_host, remote_port}
            asyncio.create_task(self.connect_to_remote(remote_host, remote_port))
            pass
        elif self.state == constants.RELAY_SERVER_STAGE_CONNING:
            self.remote_transport.write(data)
            pass
        pass


    # -------------------------- 连接到目的主机 ------------------------------ #
    async def connect_to_remote(self, remote_host, remote_port):
        try:
            remote_transport, tcp_relay_protocol \
                = await self.loop.create_connection(lambda: TcpRelayProtocol(self.loop), remote_host, remote_port)
        except Exception as err:
            print(f"serer_local connect {remote_host}:{remote_port} got ERROR: {err}")
            self.remote_transport.close()
            self.remote_transport = None
            self.client_transport.close()
            self.client_transport = None
        else:
            self.remote_transport = remote_transport
            tcp_relay_protocol.client_transport = self.client_transport
            self.state = constants.RELAY_SERVER_STAGE_CONNING
            # TODO: 返回一个成功信号
            self.client_transport.write(b"good")
    pass