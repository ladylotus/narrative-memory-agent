"""Unit tests for bias.py — EMA logic, mark decision, alpha selection."""

from __future__ import annotations

import pytest

from app.services.bias import (
    ALPHA_AUTO,
    ALPHA_CHARACTER_DRIVEN,
    ALPHA_GUT_FEELING,
    ALPHA_NONE,
    DIMENSION_KEYS,
    _should_update,
    _get_alpha,
    _ema,
    _scores_to_vector,
    update_preferred_profile,
)


# ── _should_update ─────────────────────────────────────────────


class TestShouldUpdate:
    """When should preferred_profile be updated?"""

    def test_empty_marks_should_update(self) -> None:
        """Empty marks → auto mode → should update."""
        assert _should_update([]) is True

    def test_role_driven_should_update(self) -> None:
        """'role-driven' in marks → should update."""
        assert _should_update(["role-driven"]) is True
        assert _should_update(["role-driven", "plot-driven"]) is True

    def test_gut_feeling_should_update(self) -> None:
        """Only 'gut-feeling' → should update."""
        assert _should_update(["gut-feeling"]) is True

    def test_plot_driven_should_not_update(self) -> None:
        """Only 'plot-driven' → no update."""
        assert _should_update(["plot-driven"]) is False

    def test_experimental_should_not_update(self) -> None:
        """Only 'experimental' → no update."""
        assert _should_update(["experimental"]) is False

    def test_plot_and_experimental_should_not_update(self) -> None:
        """Multiple non-updating marks → no update."""
        assert _should_update(["plot-driven", "experimental"]) is False

    def test_gut_feeling_with_plot_should_not_update(self) -> None:
        """gut-feeling + plot-driven → no update (exact match check fails)."""
        assert _should_update(["gut-feeling", "plot-driven"]) is False


# ── _get_alpha ────────────────────────────────────────────────


class TestGetAlpha:
    """What EMA alpha to use?"""

    def test_empty_marks_auto_alpha(self) -> None:
        assert _get_alpha([]) == ALPHA_AUTO

    def test_role_driven_alpha(self) -> None:
        assert _get_alpha(["role-driven"]) == ALPHA_CHARACTER_DRIVEN

    def test_gut_feeling_alpha(self) -> None:
        assert _get_alpha(["gut-feeling"]) == ALPHA_GUT_FEELING

    def test_plot_driven_alpha(self) -> None:
        assert _get_alpha(["plot-driven"]) == ALPHA_NONE

    def test_experimental_alpha(self) -> None:
        assert _get_alpha(["experimental"]) == ALPHA_NONE

    def test_role_with_plot_alpha(self) -> None:
        """role-driven takes priority over plot-driven."""
        assert _get_alpha(["role-driven", "plot-driven"]) == ALPHA_CHARACTER_DRIVEN

    def test_unknown_mark_alpha(self) -> None:
        """Unknown marks → no update (fallthrough to ALPHA_NONE)."""
        assert _get_alpha(["something-else"]) == ALPHA_NONE


# ── _ema ──────────────────────────────────────────────────────


class TestEMA:
    """Exponential Moving Average calculation."""

    def test_new_profile_from_none(self) -> None:
        """No old profile → return new vector as-is."""
        result = _ema(None, [0.8, 0.7, 0.3, 0.9, 0.1], 0.3)
        assert result == [0.8, 0.7, 0.3, 0.9, 0.1]

    def test_new_profile_wrong_length(self) -> None:
        """Old profile has different length → return new vector."""
        result = _ema([0.5, 0.5], [0.8, 0.7, 0.3, 0.9, 0.1], 0.3)
        assert result == [0.8, 0.7, 0.3, 0.9, 0.1]

    def test_ema_alpha_03(self) -> None:
        """EMA with alpha=0.3: new = 0.3*new + 0.7*old."""
        old = [0.5, 0.5, 0.5, 0.5, 0.5]
        new_vals = [1.0, 1.0, 0.0, 1.0, 0.0]
        result = _ema(old, new_vals, 0.3)
        expected = [0.3 * n + 0.7 * o for o, n in zip(old, new_vals)]
        assert result == pytest.approx(expected, abs=1e-4)

    def test_ema_alpha_01(self) -> None:
        """EMA with alpha=0.1 (slow adaptation)."""
        old = [0.5, 0.5, 0.5, 0.5, 0.5]
        new_vals = [0.9, 0.8, 0.2, 0.7, 0.3]
        result = _ema(old, new_vals, 0.1)
        expected = [0.1 * n + 0.9 * o for o, n in zip(old, new_vals)]
        assert result == pytest.approx(expected, abs=1e-4)

    def test_ema_zero_alpha(self) -> None:
        """Alpha=0 → old unchanged."""
        result = _ema([0.8, 0.7, 0.3, 0.9, 0.1], [1.0, 1.0, 0.0, 1.0, 0.0], 0.0)
        assert result == [0.8, 0.7, 0.3, 0.9, 0.1]

    def test_ema_full_alpha(self) -> None:
        """Alpha=1 → complete replacement."""
        result = _ema([0.5, 0.5, 0.5, 0.5, 0.5], [1.0, 0.0, 1.0, 0.0, 1.0], 1.0)
        assert result == [1.0, 0.0, 1.0, 0.0, 1.0]

    def test_ema_dimension_independence(self) -> None:
        """Each dimension is updated independently."""
        old = [0.1, 0.2, 0.3, 0.4, 0.5]
        new_vals = [1.0, 0.0, 1.0, 0.0, 1.0]
        result = _ema(old, new_vals, 0.5)
        for i in range(5):
            assert result[i] == pytest.approx(0.5 * new_vals[i] + 0.5 * old[i])


# ── _scores_to_vector ─────────────────────────────────────────


class TestScoresToVector:
    def test_extracts_all_dimensions(self) -> None:
        scores = {"T": 0.9, "B": 0.7, "D": 0.3, "C": 0.8, "P": 0.2}
        result = _scores_to_vector(scores)
        assert result == [0.9, 0.7, 0.3, 0.8, 0.2]

    def test_missing_dimensions_default_to_05(self) -> None:
        scores = {"T": 0.9, "B": 0.7}
        result = _scores_to_vector(scores)
        assert result == [0.9, 0.7, 0.5, 0.5, 0.5]

    def test_wrong_keys_default_to_05(self) -> None:
        scores = {"T": 0.9, "B": 0.7, "X": 99}
        result = _scores_to_vector(scores)
        assert result[2] == 0.5  # D defaults
        assert result[3] == 0.5  # C defaults
        assert result[4] == 0.5  # P defaults

    def test_dimension_order(self) -> None:
        assert DIMENSION_KEYS == ["T", "B", "D", "C", "P"]


# ── update_preferred_profile (integration) ────────────────────


class TestUpdatePreferredProfile:
    """Integration of _should_update + _get_alpha + _ema."""

    def test_full_update_flow_role_driven(self) -> None:
        old = [0.5, 0.5, 0.5, 0.5, 0.5]
        scores = {"T": 0.9, "B": 0.8, "D": 0.2, "C": 0.9, "P": 0.1}
        result = update_preferred_profile(old, scores, ["role-driven"])

        assert result["updated"] is True
        # alpha=0.3: 0.3*new + 0.7*old
        expected = [0.3 * s + 0.7 * o for o, s in zip(old, [0.9, 0.8, 0.2, 0.9, 0.1])]
        assert result["profile"] == pytest.approx(expected, abs=1e-4)

    def test_no_update_plot_driven(self) -> None:
        old = [0.5, 0.5, 0.5, 0.5, 0.5]
        result = update_preferred_profile(old, {"T": 0.9}, ["plot-driven"])
        assert result["updated"] is False
        assert result["profile"] == old

    def test_no_update_experimental(self) -> None:
        result = update_preferred_profile(None, {"T": 0.9}, ["experimental"])
        assert result["updated"] is False
        assert result["profile"] is None

    def test_auto_mode_empty_marks(self) -> None:
        result = update_preferred_profile(None, {"T": 0.9, "B": 0.8, "D": 0.2, "C": 0.9, "P": 0.1}, [])
        assert result["updated"] is True
        assert result["profile"] == [0.9, 0.8, 0.2, 0.9, 0.1]  # alpha=0.15, but None old → full replace

    def test_gut_feeling_slow_update(self) -> None:
        old = [0.5, 0.5, 0.5, 0.5, 0.5]
        scores = {"T": 1.0, "B": 1.0, "D": 0.0, "C": 1.0, "P": 0.0}
        result = update_preferred_profile(old, scores, ["gut-feeling"])
        assert result["updated"] is True
        # alpha=0.1: very slow adaptation
        new_vec = [1.0, 1.0, 0.0, 1.0, 0.0]
        expected = [0.1 * n + 0.9 * o for o, n in zip(old, new_vec)]
        assert result["profile"] == pytest.approx(expected, abs=1e-4)

    def test_multiple_updates_convergence(self) -> None:
        """Repeated updates should converge the profile toward user preference."""
        profile = None
        # Simulate 3 role-driven updates, all preferring high T/B/C, low D/P
        for _ in range(3):
            result = update_preferred_profile(
                profile,
                {"T": 0.9, "B": 0.8, "D": 0.2, "C": 0.85, "P": 0.15},
                ["role-driven"],
            )
            profile = result["profile"]

        assert profile is not None
        # After 3 updates with alpha=0.3:
        # update 1: 0.3*new + 0.7*None → new (full replace since old=None)
        # update 2: 0.3*new + 0.7*profile1
        # update 3: 0.3*new + 0.7*profile2
        assert profile[0] > 0.7  # T should be pulled toward 0.9
        assert profile[3] > 0.7  # C should be pulled toward 0.85
        assert profile[4] < 0.4  # P should be pulled toward 0.15

    def test_both_marks_available_but_only_role_counts(self) -> None:
        """role-driven + plot-driven → treats as role-driven (update)."""
        old = [0.5] * 5
        scores = {k: 0.8 for k in DIMENSION_KEYS}
        result = update_preferred_profile(old, scores, ["role-driven", "plot-driven"])
        assert result["updated"] is True
