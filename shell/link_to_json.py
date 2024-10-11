import sys
sys.path.insert(0, '..')
import v2ray.v2ray2json as v2ray2json
from pprint import pprint
import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description = "v2ray2json convert vmess, vless, trojan, ... link to client json config."
    )
    parser.add_argument(
        "config",
        nargs = "?",
        help = "A vmess://, vless://, trojan://, ... link.",
    )



    option = parser.parse_args()
    config = option.config

    pprint(v2ray2json.generate_json(config))