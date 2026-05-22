from eap import decode_for_human, encode_instruction


def test_encode_japanese_xss_instruction() -> None:
    packet = encode_instruction("過去ログ4番のXSSを超ガチで見て")

    assert packet.to_ascii() == ">SEC:XSS #ctx4 !9"


def test_encode_summary_instruction() -> None:
    packet = encode_instruction("ctx12 を軽く要約して")

    assert packet.to_ascii() == ">DAT:SUM #ctx12 !1"


def test_decode_for_human() -> None:
    text = decode_for_human("<SEC:VUL #ctx4 | line=42 fixed=false")

    assert "応答" in text
    assert "SEC::VUL" in text
    assert "line=42" in text

