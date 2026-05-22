import pytest

from eap import EapPacket, PacketParseError, parse_packet
from eap.packet import Direction


def test_parse_unicode_request() -> None:
    packet = parse_packet('◤SEC::XSS ➔ 📦[#ctx4] ⚡9 ⁝ payload="<script>"')

    assert packet.direction == Direction.REQUEST
    assert packet.domain == "SEC"
    assert packet.action == "XSS"
    assert packet.target == "#ctx4"
    assert packet.priority == 9
    assert packet.data == {"payload": "<script>"}


def test_parse_ascii_response() -> None:
    packet = parse_packet("<SEC:VUL #ctx4 | line=42 fixed=false")

    assert packet.direction == Direction.RESPONSE
    assert packet.priority is None
    assert packet.data == {"line": 42, "fixed": False}


def test_convert_between_styles() -> None:
    packet = parse_packet(">SEC:XSS #ctx4 !9")

    assert packet.to_unicode() == "◤SEC::XSS ➔ 📦[#ctx4] ⚡9"
    assert parse_packet(packet.to_unicode()).to_ascii() == ">SEC:XSS #ctx4 !9"


def test_response_builder() -> None:
    packet = EapPacket.response(
        domain="sec",
        action="vul",
        target="#ctx4",
        data={"line": 42, "fixed": False},
    )

    assert packet.to_ascii() == "<SEC:VUL #ctx4 | line=42 fixed=false"


def test_invalid_packet_fails() -> None:
    with pytest.raises(PacketParseError):
        parse_packet("please check ctx4 for xss")

