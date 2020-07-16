import asyncio
import socket
import struct

import constants

class Sock5Processer(object):
    def __init__(self, relay_host, relay_port, tcp_connect_coro, tcp_reply):
        self.relay_host = relay_host
        self.relay_port = relay_port
        self.tcp_connect_coro = tcp_connect_coro
        self.tcp_reply = tcp_reply
        self.state = constants.SOCK5_PARSER_STAGE_INIT
        pass

    def process(self, data):
        if self.state == constants.SOCK5_PARSER_STAGE_INIT:
            ver, nmethods, _ = struct.unpack("!BBB", data[:3])
            # print(ver, "<=>", nmethods)
            # self.client_transport.write(struct.pack("!BB", 5, 0))
            self.tcp_reply(struct.pack("!BB", 5, 0))
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
                    asyncio.create_task(self.tcp_connect_coro(self.relay_host, self.relay_port, remote_host, remote_port))
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
            # self.remote_transport.write(data)
            self.tcp_reply(data)
            pass
        pass

    pass