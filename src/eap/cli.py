from __future__ import annotations

import argparse
import json

from .codec import decode_for_human, encode_instruction
from .meter import compare_packet_forms, measure_text
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

    meter_cmd = subparsers.add_parser("meter", help="Estimate text size and token cost.")
    meter_cmd.add_argument("text")
    meter_cmd.add_argument("--label", default="text")
    meter_cmd.add_argument("--rate-per-1k", type=float)

    compare_cmd = subparsers.add_parser("compare", help="Compare EAP packet forms.")
    compare_cmd.add_argument("packet")
    compare_cmd.add_argument("--natural")
    compare_cmd.add_argument("--rate-per-1k", type=float)

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
    elif args.command == "meter":
        result = measure_text(
            args.text,
            label=args.label,
            rate_per_1k_tokens=args.rate_per_1k,
        )
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    elif args.command == "compare":
        packet = parse_packet(args.packet)
        results = compare_packet_forms(
            packet,
            natural=args.natural,
            rate_per_1k_tokens=args.rate_per_1k,
        )
        print(json.dumps([result.to_dict() for result in results], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
