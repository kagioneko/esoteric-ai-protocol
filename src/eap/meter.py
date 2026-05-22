from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import re
from typing import Optional

from .packet import EapPacket


@dataclass(frozen=True)
class TextMeter:
    label: str
    text: str
    chars: int
    utf8_bytes: int
    heuristic_tokens: int
    estimated_cost: Optional[float] = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def measure_text(
    text: str,
    *,
    label: str = "text",
    rate_per_1k_tokens: Optional[float] = None,
) -> TextMeter:
    tokens = estimate_tokens(text)
    cost = None
    if rate_per_1k_tokens is not None:
        cost = tokens * rate_per_1k_tokens / 1000
    return TextMeter(
        label=label,
        text=text,
        chars=len(text),
        utf8_bytes=len(text.encode("utf-8")),
        heuristic_tokens=tokens,
        estimated_cost=cost,
    )


def compare_packet_forms(
    packet: EapPacket,
    *,
    natural: Optional[str] = None,
    rate_per_1k_tokens: Optional[float] = None,
) -> list[TextMeter]:
    forms: list[tuple[str, str]] = []
    if natural is not None:
        forms.append(("natural", natural))
    forms.extend(
        [
            ("ascii_eap", packet.to_ascii()),
            ("unicode_eap", packet.to_unicode()),
            ("json", _packet_json(packet)),
        ]
    )
    return [
        measure_text(text, label=label, rate_per_1k_tokens=rate_per_1k_tokens)
        for label, text in forms
    ]


def estimate_tokens(text: str) -> int:
    if not text:
        return 0

    tokens = 0
    for chunk in re.findall(r"[A-Za-z0-9_]+|[^\sA-Za-z0-9_]", text):
        if re.fullmatch(r"[A-Za-z0-9_]+", chunk):
            tokens += max(1, (len(chunk) + 3) // 4)
        else:
            tokens += _symbol_weight(chunk)
    return tokens


def _symbol_weight(symbol: str) -> int:
    codepoint = ord(symbol)
    if codepoint <= 0x7F:
        return 1
    if codepoint <= 0xFFFF:
        return 1
    return 2


def _packet_json(packet: EapPacket) -> str:
    payload = {
        "d": packet.direction.value,
        "dom": packet.domain,
        "act": packet.action,
        "t": packet.target,
    }
    if packet.priority is not None:
        payload["p"] = packet.priority
    if packet.data:
        payload["data"] = packet.data
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))

