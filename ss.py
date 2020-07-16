import asyncio

import constants
import util
from protocols.shadowsocks.server_local_protocol import ServerLocalProtocol
from protocols.shadowsocks.server_relay_protocol import ServerRelayProtocol


"""
python3 ss.py local --host "0.0.0.0" --port 9002 --relayhost "127.0.0.1" --relayport 9006
python3 ss.py relay --host "0.0.0.0" --port 9006
"""

async def main(loop):
    ns = util.parse_args_new()

    if ns.mode == constants.SOCK5_SERVER_MODE_LOCAL:
        fn = lambda : ServerLocalProtocol(loop, ns.relayhost, ns.relayport)
    elif ns.mode == constants.SOCK5_SERVER_MODE_RELAY:
        fn = lambda : ServerRelayProtocol(loop)

    server: asyncio.Server = await loop.create_server(fn, ns.host, ns.port)
    print(f"Serving on {ns.host}:{ns.port}")

    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(main(loop))
    except Exception as err:
        print(err)
    finally:
        loop.close()