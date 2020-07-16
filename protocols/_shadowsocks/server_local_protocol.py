import asyncio
import socket
import struct
from asyncio import transports

import constants
from protocols.shadowsocks.tcp_local_protocol import TcpLocalProtocol
from protocols.shadowsocks.base_protocol import BaseProtocol

"""
typing.Optional[Bool]: 表示这个值即可以是Bool, 也可以是None
"""

class ServerLocalProtocol(BaseProtocol):
    def __init__(self, loop: asyncio.BaseEventLoop, relay_host, relay_port):
        super().__init__(loop)
        self.relay_host = relay_host
        self.relay_port = relay_port
        self.state = None

    def connection_made(self, transport: transports.BaseTransport) -> None:
        super().connection_made(transport)
        self.state = constants.SOCK5_PARSER_STAGE_INIT
        pass


    def data_received(self, data: bytes) -> None:
        if self.state == constants.SOCK5_PARSER_STAGE_INIT:
            ver, nmethods, _ = struct.unpack("!BBB", data[:3])
            # print(ver, "<=>", nmethods)
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
                    # print(f"目的地址: {remote_host}:{remote_port}")
                    # 连接(remote_host, remote_port)
                    # asyncio.create_task(self.connect_to_remote(remote_host, remote_port))
                    # TODO: 连接中继主机(self.relay_host, self.relay_port)
                    asyncio.create_task(self.connect_to_relay(self.relay_host, self.relay_port, remote_host, remote_port))
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

    # ---------------------- 连接目的主机 ------------------------ #
    async def connect_to_remote(self, remote_host, remote_port):
        try:
            remote_transport, tcp_local_protocol \
                = await self.loop.create_connection(lambda: TcpLocalProtocol(self.loop), remote_host, remote_port)
        except Exception as err:
            print(f"serer_local connect {remote_host}:{remote_port} got ERROR: {err}")
            self.remote_transport.close()
            self.remote_transport = None
            self.client_transport.close()
            self.client_transport = None
        else:
            self.remote_transport = remote_transport
            tcp_local_protocol.client_transport = self.client_transport

            hostip, port = remote_transport.get_extra_info('sockname')
            host = struct.unpack("!I", socket.inet_aton(hostip))[0]
            self.client_transport.write(
                struct.pack('!BBBBIH', 0x05, 0x00, 0x00, 0x01, host, port))
            self.state = constants.SOCK5_PARSER_STAGE_DATA
        pass

    # ---------------------- 连接中继主机 ------------------------ #
    async def connect_to_relay(self, relay_host, relay_port, remote_host, remote_port):
        try:
            remote_transport, tcp_local_protocol \
                = await self.loop.create_connection(lambda: TcpLocalProtocol(self.loop), relay_host, relay_port)
        except Exception as err:
            print(f"serer_local connect {relay_host}:{relay_port} got ERROR: {err}")
            self.remote_transport.close()
            self.remote_transport = None
            self.client_transport.close()
            self.client_transport = None
        else:
            self.remote_transport = remote_transport
            tcp_local_protocol.client_transport = self.client_transport
            self.state = constants.SOCK5_PARSER_STAGE_DATA      # todo: 修改了状态为constants.SOCK5_PARSER_STAGE_DATA
            # TODO: 发送{remote_host, remote_port}到中继主机
            host = struct.unpack("!I", socket.inet_aton(remote_host))[0]
            self.remote_transport.write(
                struct.pack('!IH', host, remote_port))
        pass

    pass