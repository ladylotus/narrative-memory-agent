"""Unit tests for bias_prompt.py — threshold descriptions for each dimension."""

from __future__ import annotations

import pytest

from app.services.bias_prompt import profile_to_bias_prompt, _describe


# ── _describe ──────────────────────────────────────────────────


class TestDescribe:
    """_describe converts (value, high_desc, low_desc) → natural language."""

    def test_high_threshold(self) -> None:
        result = _describe("T", 0.85, "stay close to core", "bend traits")
        assert "strongly" in result
        assert "stay close to core" in result

    def test_mid_high_threshold(self) -> None:
        result = _describe("B", 0.60, "follow patterns", "break patterns")
        assert "moderately" in result
        # 0.6 >= 0.55 → uses high_desc
        assert "follow patterns" in result

    def test_mid_low_threshold(self) -> None:
        result = _describe("C", 0.45, "stay coherent", "contradiction is fine")
        assert "moderately" in result
        # 0.45 < 0.55 → uses low_desc
        assert "contradiction is fine" in result

    def test_low_threshold(self) -> None:
        result = _describe("P", 0.2, "surprise welcome", "stay predictable")
        assert "slightly" in result
        assert "stay predictable" in result

    def test_boundary_07(self) -> None:
        """0.70 exactly → strongly."""
        result = _describe("T", 0.70, "high", "low")
        assert "strongly" in result

    def test_boundary_069(self) -> None:
        """0.69 → moderately (below 0.7 threshold)."""
        result = _describe("T", 0.69, "high", "low")
        assert "slightly" not in result
        assert "moderately" in result

    def test_boundary_04(self) -> None:
        """0.40 exactly → moderately."""
        result = _describe("D", 0.40, "stay close", "shift tone")
        assert "moderately" in result

    def test_boundary_039(self) -> None:
        """0.39 → slightly."""
        result = _describe("D", 0.39, "stay close", "shift tone")
        assert "slightly" in result


# ── profile_to_bias_prompt ────────────────────────────────────


class TestProfileToBiasPrompt:
    """Convert 5-dim vector to natural language bias instructions."""

    def test_empty_profile(self) -> None:
        assert profile_to_bias_prompt([]) == ""
        assert profile_to_bias_prompt(None) == ""  # type: ignore[arg-type]

    def test_short_profile(self) -> None:
        assert profile_to_bias_prompt([0.5]) == ""

    def test_high_values(self) -> None:
        """High trait/behaviour/self-consistency, low distance/surprise → stay close to character."""
        result = profile_to_bias_prompt([0.9, 0.8, 0.2, 0.9, 0.1])
        assert "Based on your previous responses" in result
        assert "stay very close to your core traits" in result  # T high
        assert "Follow patterns" in result  # B high
        assert "Stay close to your usual way" in result  # D low
        assert "internally consistent" in result  # C high
        assert "safe, expected directions" in result  # P low

    def test_low_values(self) -> None:
        """Low trait/behaviour/self-consistency, high distance/surprise → open to OOC."""
        result = profile_to_bias_prompt([0.2, 0.3, 0.8, 0.2, 0.9])
        assert "may seem out of character" in result  # T low
        assert "break away from your usual patterns" in result  # B low
        assert "quite different" in result  # D high
        assert "uncertainty and internal conflict" in result  # C low
        assert "bold or unexpected" in result  # P high

    def test_mid_values(self) -> None:
        """All values in mid-range → moderate language."""
        result = profile_to_bias_prompt([0.5, 0.5, 0.5, 0.5, 0.5])
        assert "bend" in result  # T mid
        assert "occasionally" in result  # B mid
        assert "shift your tone" in result  # D mid
        assert "A little contradiction" in result  # C mid
        assert "Balanced" in result  # P mid

    def test_describe_d_boundary_low_semantic(self) -> None:
        """D dimension semantics are inverted: lower D = closer = stay close."""
        result = profile_to_bias_prompt([0.5, 0.5, 0.2, 0.5, 0.5])
        assert "Stay close to your usual way" in result

    def test_describe_d_boundary_high_semantic(self) -> None:
        """Higher D = farther = shift tone."""
        result = profile_to_bias_prompt([0.5, 0.5, 0.7, 0.5, 0.5])
        assert "quite different" in result
