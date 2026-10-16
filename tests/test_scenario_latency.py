"""Scenario-runner latency export: timings leave the harness as JSON."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import TYPE_CHECKING

from gameplay_agent import executor
from gameplay_agent.scenario_runner import ScenarioResult, run_scenario_async

if TYPE_CHECKING:
    import pytest

_FIXTURE = (
    Path(__file__).resolve().parents[1]
    / "apps/agent/src/scenarios/production/castle_imperial_army.yaml"
)


def _run(*, collect_latency: bool) -> ScenarioResult:
    return asyncio.run(run_scenario_async(_FIXTURE, collect_latency=collect_latency))


def test_collect_latency_exports_every_loop_that_ran(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(executor, "RESCAN_SETTLE_DELAY", 0.0)
    monkeypatch.setattr(executor.config, "action_delay", 0.0)
    result = _run(collect_latency=True)
    assert result.passed, result.failures
    assert result.latency is not None
    assert "perceive" in result.latency
    assert "act" in result.latency
    perceive = result.latency["perceive"]
    assert isinstance(perceive, dict)
    p50 = perceive["p50_ms"]
    assert isinstance(p50, float) and p50 >= 0.0
    phases = perceive["phase_p50_ms"]
    assert isinstance(phases, dict)
    assert "capture" in phases


def test_latency_is_absent_without_the_flag(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(executor, "RESCAN_SETTLE_DELAY", 0.0)
    monkeypatch.setattr(executor.config, "action_delay", 0.0)
    result = _run(collect_latency=False)
    assert result.passed, result.failures
    assert result.latency is None
