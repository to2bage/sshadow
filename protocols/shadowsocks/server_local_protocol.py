import asyncio
import socket
import struct
from functools import partial
from asyncio import transports

import constants
from protocols.shadowsocks.tcp_local_protocol import TcpLocalProtocol
from protocols.shadowsocks.base_protocol import BaseProtocol
from protocols.sock5.sock5_processer import Sock5Processer

"""
typing.Optional[Bool]: 表示这个值即可以是Bool, 也可以是None
"""

class ServerLocalProtocol(BaseProtocol):
    def __init__(self, loop: asyncio.BaseEventLoop, relay_host, relay_port):
        super().__init__(loop)
        self.relay_host = relay_host
        self.relay_port = relay_port
        self.state = None
        self.sock5_processer = None

    def connection_made(self, transport: transports.BaseTransport) -> None:
        super().connection_made(transport)
        self.state = constants.SOCK5_PARSER_STAGE_INIT
        self.sock5_processer = Sock5Processer(self.relay_host, self.relay_port,
                                        partial(self.connect_to_relay),
                                        partial(self.answer_sock5_connect))
        pass


    def data_received(self, data: bytes) -> None:
        if self.is_shake_with_sock5():
            self.sock5_processer.process(data)
            pass
        elif self.is_tcp_transport():
            self.remote_transport.write(data)
            pass
        pass

    def is_shake_with_sock5(self):
        return self.state in [constants.SOCK5_PARSER_STAGE_INIT, constants.SOCK5_PARSER_STAGE_HOST]

    def is_tcp_transport(self):
        return self.state not in [constants.SOCK5_PARSER_STAGE_INIT, constants.SOCK5_PARSER_STAGE_HOST]

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

    # ---------------------------- 处理socks5应答数据 ------------------------------ #
    def answer_sock5_connect(self, data):
        if self.state == constants.SOCK5_PARSER_STAGE_INIT:
            self.client_transport.write(struct.pack("!BB", 5, 0))
            pass
        elif self.state == constants.SOCK5_PARSER_STAGE_DATA:
            self.remote_transport.write(data)
            pass

    pass