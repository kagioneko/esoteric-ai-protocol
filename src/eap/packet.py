from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import re
from typing import Optional


class PacketParseError(ValueError):
    pass


class Direction(str, Enum):
    REQUEST = "request"
    RESPONSE = "response"
    SYNC = "sync"


UNICODE_DIRECTION = {
    "◤": Direction.REQUEST,
    "◢": Direction.RESPONSE,
    "▰": Direction.SYNC,
}
ASCII_DIRECTION = {
    ">": Direction.REQUEST,
    "<": Direction.RESPONSE,
    "=": Direction.SYNC,
}
UNICODE_DIRECTION_OUT = {value: key for key, value in UNICODE_DIRECTION.items()}
ASCII_DIRECTION_OUT = {value: key for key, value in ASCII_DIRECTION.items()}

UNICODE_RE = re.compile(
    r"^\s*(?P<dir>[◤◢▰])(?P<domain>[A-Z0-9]{2,8})::(?P<action>[A-Z0-9_]{2,16})"
    r"\s*➔\s*📦\[(?P<target>[^\]]+)\]"
    r"(?:\s*⚡(?P<priority>[1-9]))?"
    r"(?:\s*⁝\s*(?P<data>.*))?\s*$"
)
ASCII_RE = re.compile(
    r"^\s*(?P<dir>[><=])(?P<domain>[A-Z0-9]{2,8}):(?P<action>[A-Z0-9_]{2,16})"
    r"\s+(?P<target>#[A-Za-z0-9_.:-]+)"
    r"(?:\s+!(?P<priority>[1-9]))?"
    r"(?:\s+\|\s*(?P<data>.*))?\s*$"
)


@dataclass(frozen=True)
class EapPacket:
    direction: Direction
    domain: str
    action: str
    target: str
    priority: Optional[int] = None
    data: dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        domain = self.domain.upper()
        action = self.action.upper()
        if not re.fullmatch(r"[A-Z0-9]{2,8}", domain):
            raise ValueError("domain must be 2-8 uppercase letters or digits")
        if not re.fullmatch(r"[A-Z0-9_]{2,16}", action):
            raise ValueError("action must be 2-16 uppercase letters, digits, or underscores")
        if not self.target.startswith("#"):
            raise ValueError("target must start with #")
        if self.priority is not None and not 1 <= self.priority <= 9:
            raise ValueError("priority must be between 1 and 9")
        object.__setattr__(self, "domain", domain)
        object.__setattr__(self, "action", action)

    @classmethod
    def request(
        cls,
        domain: str,
        action: str,
        target: str,
        *,
        priority: int = 5,
        data: Optional[dict[str, object]] = None,
    ) -> "EapPacket":
        return cls(Direction.REQUEST, domain, action, target, priority, data or {})

    @classmethod
    def response(
        cls,
        domain: str,
        action: str,
        target: str,
        *,
        data: Optional[dict[str, object]] = None,
    ) -> "EapPacket":
        return cls(Direction.RESPONSE, domain, action, target, None, data or {})

    def to_unicode(self) -> str:
        packet = (
            f"{UNICODE_DIRECTION_OUT[self.direction]}{self.domain}::{self.action}"
            f" ➔ 📦[{self.target}]"
        )
        if self.priority is not None:
            packet += f" ⚡{self.priority}"
        if self.data:
            packet += f" ⁝ {_format_data(self.data)}"
        return packet

    def to_ascii(self) -> str:
        packet = f"{ASCII_DIRECTION_OUT[self.direction]}{self.domain}:{self.action} {self.target}"
        if self.priority is not None:
            packet += f" !{self.priority}"
        if self.data:
            packet += f" | {_format_data(self.data)}"
        return packet


def parse_packet(raw: str) -> EapPacket:
    match = UNICODE_RE.match(raw)
    if match:
        groups = match.groupdict()
        return EapPacket(
            direction=UNICODE_DIRECTION[groups["dir"]],
            domain=groups["domain"],
            action=groups["action"],
            target=groups["target"],
            priority=_parse_priority(groups.get("priority")),
            data=_parse_data(groups.get("data")),
        )

    match = ASCII_RE.match(raw)
    if match:
        groups = match.groupdict()
        return EapPacket(
            direction=ASCII_DIRECTION[groups["dir"]],
            domain=groups["domain"],
            action=groups["action"],
            target=groups["target"],
            priority=_parse_priority(groups.get("priority")),
            data=_parse_data(groups.get("data")),
        )

    raise PacketParseError(f"invalid EAP packet: {raw}")


def _parse_priority(value: Optional[str]) -> Optional[int]:
    if value is None:
        return None
    return int(value)


def _parse_data(raw: Optional[str]) -> dict[str, object]:
    if raw is None or raw.strip() == "":
        return {}

    data: dict[str, object] = {}
    for token in _split_data(raw):
        if "=" not in token:
            data[token] = True
            continue
        key, value = token.split("=", 1)
        data[key.strip()] = _coerce_value(value.strip())
    return data


def _split_data(raw: str) -> list[str]:
    tokens: list[str] = []
    current: list[str] = []
    quote: Optional[str] = None

    for char in raw:
        if char in {"'", '"'}:
            if quote == char:
                quote = None
            elif quote is None:
                quote = char
            current.append(char)
        elif char.isspace() and quote is None:
            if current:
                tokens.append("".join(current))
                current = []
        else:
            current.append(char)

    if current:
        tokens.append("".join(current))
    return tokens


def _coerce_value(raw: str) -> object:
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in {"'", '"'}:
        return raw[1:-1]
    lowered = raw.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    try:
        return int(raw)
    except ValueError:
        return raw


def _format_data(data: dict[str, object]) -> str:
    return " ".join(f"{key}={_format_value(value)}" for key, value in data.items())


def _format_value(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    text = str(value)
    if re.fullmatch(r"[A-Za-z0-9_.:/#-]+", text):
        return text
    escaped = text.replace('"', '\\"')
    return f'"{escaped}"'

