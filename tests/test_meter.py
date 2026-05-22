from eap import compare_packet_forms, estimate_tokens, measure_text, parse_packet


def test_estimate_tokens_counts_ascii_chunks_compactly() -> None:
    assert estimate_tokens(">SEC:XSS #ctx4 !9") < estimate_tokens(
        "Please check context 4 for XSS with high priority."
    )


def test_measure_text_includes_cost_when_rate_is_given() -> None:
    result = measure_text(">SEC:XSS #ctx4 !9", rate_per_1k_tokens=0.5)

    assert result.chars == 17
    assert result.utf8_bytes == 17
    assert result.heuristic_tokens > 0
    assert result.estimated_cost is not None


def test_compare_packet_forms_includes_natural_ascii_unicode_json() -> None:
    packet = parse_packet("◤SEC::XSS ➔ 📦[#ctx4] ⚡9")
    results = compare_packet_forms(packet, natural="過去ログ4番のXSSを超ガチで見て")
    labels = [result.label for result in results]

    assert labels == ["natural", "ascii_eap", "unicode_eap", "json"]
    assert results[1].text == ">SEC:XSS #ctx4 !9"
    assert results[2].text == "◤SEC::XSS ➔ 📦[#ctx4] ⚡9"

