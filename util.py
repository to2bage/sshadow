import argparse

import constants

def parse_args_new():
    parser = argparse.ArgumentParser()
    sub_parser = parser.add_subparsers()

    local_parser = sub_parser.add_parser(constants.SOCK5_SERVER_MODE_LOCAL)
    local_parser.add_argument("--host", dest="host", type=str)
    local_parser.add_argument("--port", dest="port", type=int)
    local_parser.add_argument("--relayhost", dest="relayhost", type=str)
    local_parser.add_argument("--relayport", dest="relayport", type=int)
    local_parser.add_argument("--mode", dest="mode", type=str, default=constants.SOCK5_SERVER_MODE_LOCAL)

    relay_parser = sub_parser.add_parser(constants.SOCK5_SERVER_MODE_RELAY)
    relay_parser.add_argument("--host", dest="host", type=str)
    relay_parser.add_argument("--port", dest="port", type=int)
    relay_parser.add_argument("--mode", dest="mode", type=str, default=constants.SOCK5_SERVER_MODE_RELAY)

    args = parser.parse_args()
    return args
    pass