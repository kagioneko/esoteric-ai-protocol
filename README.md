# Esoteric AI Protocol (EAP)

> A compact packet grammar for agent-to-agent communication.

EAP is an experimental protocol for compressing multi-agent messages into
small, structured packets. It removes human filler, separates intent from
payload, and keeps context references as pointers instead of replaying long
conversation history.

## Design Notes

The original visual grammar uses dense Unicode markers:

```text
◤SEC::XSS ➔ 📦[#ctx4] ⚡9 ⁝ payload="<script>"
◢SEC::VUL ➔ 📦[#ctx4] ⁝ line=42 fixed=false
```

That is great for dashboards and logs, but token cost is tokenizer-dependent.
Some models split emoji and symbols into multiple tokens. For real cost control,
EAP also supports an ASCII transport:

```text
>SEC:XSS #ctx4 !9 | payload="<script>"
<SEC:VUL #ctx4 | line=42 fixed=false
```

The protocol therefore has two layers:

- **Display layer:** cinematic Unicode packets for human-visible logs.
- **Transport layer:** compact ASCII packets for cheaper, more predictable LLM I/O.

## Packet Model

Every packet has:

- `direction`: request, response, or sync
- `domain`: short uppercase namespace, such as `SEC`, `DAT`, `SYS`
- `action`: operation or status, such as `XSS`, `SUM`, `OK`, `ERR`
- `target`: context pointer, such as `#ctx4`
- `priority`: optional `1..9`
- `data`: optional key-value payload

## Unicode Grammar

```text
[dir][DOMAIN]::[ACTION] ➔ 📦[target] [⚡priority] [⁝ data]
```

Directions:

- `◤`: request
- `◢`: response
- `▰`: sync

Example:

```text
◤SEC::XSS ➔ 📦[#ctx4] ⚡9 ⁝ payload="<script>"
```

## ASCII Grammar

```text
[dir][DOMAIN]:[ACTION] [target] [!priority] [| data]
```

Directions:

- `>`: request
- `<`: response
- `=`: sync

Example:

```text
>SEC:XSS #ctx4 !9 | payload="<script>"
```

## Install

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
```

## CLI

Parse a packet:

```bash
eap parse '◤SEC::XSS ➔ 📦[#ctx4] ⚡9 ⁝ payload="<script>"'
```

Convert Unicode to ASCII:

```bash
eap convert '◤SEC::XSS ➔ 📦[#ctx4] ⚡9 ⁝ payload="<script>"' --style ascii
```

Encode a rough natural-language instruction:

```bash
eap encode "過去ログ4番のXSSを超ガチで見て"
```

Decode a packet for humans:

```bash
eap decode '<SEC:VUL #ctx4 | line=42 fixed=false'
```

## Python API

```python
from eap import EapPacket, parse_packet

packet = parse_packet("◤SEC::XSS ➔ 📦[#ctx4] ⚡9")
print(packet.to_ascii())

response = EapPacket.response(
    domain="SEC",
    action="VUL",
    target="#ctx4",
    data={"line": 42, "fixed": False},
)
print(response.to_unicode())
```

## System Prompt Template

```text
You are an EAP-native agent.
Output only valid EAP packets.
Do not use greetings, explanations, or natural-language filler.
Prefer ASCII transport unless Unicode display mode is requested.

Request:  >DOMAIN:ACTION #target !priority | data
Response: <DOMAIN:STATUS #target | data
Sync:     =DOMAIN:STATUS #target | data
```

## Practical Positioning

EAP is strongest as a constrained intermediate representation for agent logs,
handoffs, status updates, and tool-routing. It should not pretend that symbol
choice alone guarantees token savings. The reliable savings come from:

- fixed grammar
- short domain/action codes
- context pointers instead of copied context
- key-value payloads instead of prose
- strict rejection of conversational filler

## License

MIT

