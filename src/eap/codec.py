from __future__ import annotations

import re

from .packet import Direction, EapPacket, parse_packet


def encode_instruction(text: str) -> EapPacket:
    lowered = text.lower()
    domain = "GEN"
    action = "DO"
    priority = 5
    target = _extract_target(text)

    if any(word in lowered for word in ["xss", "脆弱", "security", "セキュリティ"]):
        domain = "SEC"
        action = "XSS" if "xss" in lowered else "AUDIT"
    elif any(word in lowered for word in ["要約", "summary", "summarize"]):
        domain = "DAT"
        action = "SUM"
    elif any(word in lowered for word in ["refactor", "リファクタ"]):
        domain = "SYS"
        action = "REF"

    if any(word in lowered for word in ["超ガチ", "deep", "徹底", "最高"]):
        priority = 9
    elif any(word in lowered for word in ["軽く", "quick", "最速"]):
        priority = 1

    return EapPacket.request(domain, action, target, priority=priority)


def decode_for_human(raw_packet: str) -> str:
    packet = parse_packet(raw_packet)
    direction = {
        Direction.REQUEST: "要求",
        Direction.RESPONSE: "応答",
        Direction.SYNC: "同期",
    }[packet.direction]
    data = ""
    if packet.data:
        pairs = ", ".join(f"{key}={value}" for key, value in packet.data.items())
        data = f" データ: {pairs}."
    priority = f" 優先度: {packet.priority}." if packet.priority is not None else ""
    return (
        f"{direction}: {packet.domain}::{packet.action} を {packet.target} に対して実行します."
        f"{priority}{data}"
    )


def _extract_target(text: str) -> str:
    ctx_match = re.search(r"(?:ctx|context|ログ|過去ログ)\s*#?(\d+)", text, re.IGNORECASE)
    if ctx_match:
        return f"#ctx{ctx_match.group(1)}"

    number_match = re.search(r"(\d+)\s*番", text)
    if number_match:
        return f"#ctx{number_match.group(1)}"

    return "#ctx0"

