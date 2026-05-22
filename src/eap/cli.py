from __future__ import annotations

import argparse
import json

from .codec import decode_for_human, encode_instruction
from .packet import parse_packet


def main() -> None:
    parser = argparse.ArgumentParser(description="EAP packet tools.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    parse_cmd = subparsers.add_parser("parse", help="Parse an EAP packet as JSON.")
    parse_cmd.add_argument("packet")

    convert_cmd = subparsers.add_parser("convert", help="Convert packet style.")
    convert_cmd.add_argument("packet")
    convert_cmd.add_argument("--style", choices=["ascii", "unicode"], default="ascii")

    encode_cmd = subparsers.add_parser("encode", help="Encode a rough instruction.")
    encode_cmd.add_argument("text")
    encode_cmd.add_argument("--style", choices=["ascii", "unicode"], default="ascii")

    decode_cmd = subparsers.add_parser("decode", help="Decode packet for humans.")
    decode_cmd.add_argument("packet")

    args = parser.parse_args()

    if args.command == "parse":
        packet = parse_packet(args.packet)
        print(
            json.dumps(
                {
                    "direction": packet.direction.value,
                    "domain": packet.domain,
                    "action": packet.action,
                    "target": packet.target,
                    "priority": packet.priority,
                    "data": packet.data,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    elif args.command == "convert":
        packet = parse_packet(args.packet)
        print(packet.to_ascii() if args.style == "ascii" else packet.to_unicode())
    elif args.command == "encode":
        packet = encode_instruction(args.text)
        print(packet.to_ascii() if args.style == "ascii" else packet.to_unicode())
    elif args.command == "decode":
        print(decode_for_human(args.packet))


if __name__ == "__main__":
    main()

