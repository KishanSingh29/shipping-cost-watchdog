from watchdog.explain import explain_row


def test_unexplained_uses_fixed_template_without_llm():
    text = explain_row({"vs_own_history": "+20.0%", "vs_similar_routes": "+12.0%"})
    assert "unexplained" in text
    assert "no matching note" in text


def test_justified_fallback_mentions_exact_note():
    text = explain_row({"vs_own_history": "+20.0%", "vs_similar_routes": "+12.0%"},
                       "N001", "Heavy flooding caused higher trip costs from Feb 24 to Mar 8.")
    assert "N001" in text
    assert "Feb 24 to Mar 8" in text
