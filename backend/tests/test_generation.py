"""Unit tests for GenerationService — parsing and fallback."""

from __future__ import annotations

from app.services.generation import GenerationService, _fallback_options


# ── _parse_options ────────────────────────────────────────────

class TestParseOptions:
    """_parse_options extracts generation options from LLM JSON responses."""

    def test_parse_valid_options(self) -> None:
        raw = (
            '{"options": ['
            '  {"label": "A", "title": "Safe Path", "voice": "I would approach this carefully."},'
            '  {"label": "B", "title": "Bold Move", "voice": "I would challenge them directly."}'
            "]}"
        )
        result = GenerationService._parse_options(raw)
        assert len(result) == 2
        assert result[0]["label"] == "A"
        assert result[0]["title"] == "Safe Path"
        assert result[1]["voice"] == "I would challenge them directly."

    def test_parse_non_json_fallback(self) -> None:
        """Non-JSON output falls back to a single wrapped option."""
        result = GenerationService._parse_options("I don't know what to say here.")
        assert len(result) == 1
        assert result[0]["label"] == "A"
        assert result[0]["title"] == "Response"
        assert "I don't know what to say here." in result[0]["voice"]

    def test_parse_empty_json(self) -> None:
        """Empty JSON object falls back."""
        result = GenerationService._parse_options("{}")
        assert len(result) == 1
        assert result[0]["label"] == "A"

    def test_parse_missing_options_key(self) -> None:
        """JSON without 'options' key falls back."""
        result = GenerationService._parse_options('{"not_options": []}')
        assert len(result) == 1

    def test_parse_empty_options_list(self) -> None:
        """Empty options list falls back."""
        result = GenerationService._parse_options('{"options": []}')
        assert len(result) == 1

    def test_parse_json_in_code_block(self) -> None:
        """JSON inside ```json block should still be extracted."""
        raw = (
            "Here are three possible responses:\n\n"
            "```json\n"
            '{"options": [\n'
            '  {"label": "A", "title": "Careful", "voice": "I would think twice."},\n'
            '  {"label": "B", "title": "Reckless", "voice": "I would go for it."}\n'
            "]}\n"
            "```"
        )
        result = GenerationService._parse_options(raw)
        assert len(result) == 2

    def test_parse_invalid_json_recovery(self) -> None:
        """Malformed JSON falls back."""
        raw = '{"options": [{"label": "A", "title": "Broken" (missing brace)'
        result = GenerationService._parse_options(raw)
        assert len(result) == 1

    def test_parse_voice_fallback_from_text(self) -> None:
        """If 'voice' key is missing but 'text' exists, use 'text'."""
        raw = '{"options": [{"label": "A", "title": "Test", "text": "spoken version"}]}'
        result = GenerationService._parse_options(raw)
        assert len(result) == 1
        assert result[0]["voice"] == "spoken version"

    def test_parse_auto_label_generation(self) -> None:
        """Missing labels auto-generate as A, B, C..."""
        raw = (
            '{"options": ['
            '  {"title": "First", "voice": "One"},'
            '  {"title": "Second", "voice": "Two"},'
            '  {"title": "Third", "voice": "Three"}'
            "]}"
        )
        result = GenerationService._parse_options(raw)
        assert result[0]["label"] == "A"
        assert result[1]["label"] == "B"
        assert result[2]["label"] == "C"


# ── fallback ──────────────────────────────────────────────────

class TestFallbackOptions:
    def test_fallback_wraps_raw(self) -> None:
        result = _fallback_options("LLM gave a weird response but here it is")
        assert len(result) == 1
        assert result[0]["label"] == "A"
        assert result[0]["title"] == "Response"
        assert "LLM gave a weird response" in result[0]["voice"]

    def test_fallback_truncates_long_response(self) -> None:
        long_text = "x" * 1000
        result = _fallback_options(long_text)
        assert len(result[0]["voice"]) <= 500
