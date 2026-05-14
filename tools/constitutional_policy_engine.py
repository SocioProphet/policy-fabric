"""Reference numeric checks for the constitutional policy engine v0.1.

Library only. No HTTP framework, queue model, registry host, audit substrate,
or solver backend is selected here.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class A1Result:
    passed: bool
    coherence_share: float


@dataclass(frozen=True)
class A3Result:
    passed: bool
    d_id: float
    method_used: str


@dataclass(frozen=True)
class A4Result:
    passed: bool
    spectral_radius: float
    gamma: float


@dataclass(frozen=True)
class A5Result:
    passed: bool
    R_of_D: float
    headroom: float


@dataclass(frozen=True)
class A7Result:
    passed: bool
    slope: float
    p_value: float


def as_native_json_dict(result: object) -> dict[str, object]:
    data = asdict(result)
    out: dict[str, object] = {}
    for key, value in data.items():
        if isinstance(value, np.bool_):
            out[key] = bool(value)
        elif isinstance(value, np.integer):
            out[key] = int(value)
        elif isinstance(value, np.floating):
            out[key] = float(value)
        else:
            out[key] = value
    return out


def check_A1_coherence(
    harmonics: Sequence[tuple[int, int, complex]],
    ell_star: int,
    threshold: float = 0.85,
) -> A1Result:
    if ell_star < 0:
        raise ValueError("ell_star must be non-negative")
    total = 0.0
    low = 0.0
    for ell, _m, coefficient in harmonics:
        if ell < 0:
            raise ValueError(f"negative ell={ell}")
        energy = float(abs(coefficient) ** 2)
        total += energy
        if ell <= ell_star:
            low += energy
    share = (low / total) if total > 0 else 0.0
    return A1Result(bool(share >= threshold), float(share))


def _sliced_wasserstein_1(
    bins_a: np.ndarray,
    weights_a: np.ndarray,
    bins_b: np.ndarray,
    weights_b: np.ndarray,
    n_projections: int = 64,
) -> float:
    if bins_a.ndim != 2 or bins_b.ndim != 2:
        raise ValueError("bins must be two-dimensional arrays")
    if bins_a.shape[1] != bins_b.shape[1]:
        raise ValueError("dimension mismatch")
    if weights_a.sum() <= 0 or weights_b.sum() <= 0:
        raise ValueError("weights must have positive mass")
    rng = np.random.default_rng(0xC0FFEE)
    dim = bins_a.shape[1]
    wa = weights_a / weights_a.sum()
    wb = weights_b / weights_b.sum()
    directions = rng.standard_normal(size=(n_projections, dim))
    directions /= np.linalg.norm(directions, axis=1, keepdims=True)
    total = 0.0
    for direction in directions:
        pa = bins_a @ direction
        pb = bins_b @ direction
        oa = np.argsort(pa)
        ob = np.argsort(pb)
        xa = pa[oa]
        xb = pb[ob]
        ca = np.cumsum(wa[oa])
        cb = np.cumsum(wb[ob])
        support = np.concatenate([xa, xb])
        support.sort()
        ia = np.searchsorted(xa, support, side="right")
        ib = np.searchsorted(xb, support, side="right")
        fa = np.where(ia > 0, ca[np.minimum(ia - 1, len(ca) - 1)], 0.0)
        fb = np.where(ib > 0, cb[np.minimum(ib - 1, len(cb) - 1)], 0.0)
        dx = np.diff(support, prepend=support[0])
        total += float(np.sum(np.abs(fa - fb) * dx))
    return float(total / n_projections)


def check_A3_identity(
    bins_a: np.ndarray,
    weights_a: np.ndarray,
    bins_b: np.ndarray,
    weights_b: np.ndarray,
    threshold: float = 0.1,
    n_projections: int = 64,
) -> A3Result:
    distance = _sliced_wasserstein_1(bins_a, weights_a, bins_b, weights_b, n_projections)
    return A3Result(bool(distance <= threshold), float(distance), "sliced_wasserstein")


def check_A4_spawn(jacobian: np.ndarray, gamma_min: float = 0.15) -> A4Result:
    if jacobian.ndim != 2 or jacobian.shape[0] != jacobian.shape[1]:
        raise ValueError("jacobian must be square")
    radius = float(np.max(np.abs(np.linalg.eigvals(jacobian))))
    gamma = float(1.0 - radius)
    return A4Result(bool((radius < 1.0) and (gamma >= gamma_min)), radius, gamma)


def _binary_entropy_nats(value: float) -> float:
    if value <= 0.0 or value >= 1.0:
        return 0.0
    return float(-value * np.log(value) - (1.0 - value) * np.log(1.0 - value))


def check_A5_rate_distortion(
    D_current: float,
    capacity_sum_nats_per_sec: float,
    source_entropy_rate: float,
    distortion_kind: str = "deontic_01",
) -> A5Result:
    if D_current < 0 or capacity_sum_nats_per_sec < 0 or source_entropy_rate < 0:
        raise ValueError("rates and distortions must be non-negative")
    if distortion_kind == "deontic_01":
        rate = max(0.0, source_entropy_rate - _binary_entropy_nats(min(D_current, 0.5)))
    elif distortion_kind == "quadratic":
        rate = float("inf") if D_current <= 0 else max(0.0, 0.5 * float(np.log(source_entropy_rate / D_current)))
    else:
        raise NotImplementedError(distortion_kind)
    headroom = float(capacity_sum_nats_per_sec - rate)
    return A5Result(bool(headroom >= 0.0), float(rate), headroom)


def check_A7_lyapunov(times: np.ndarray, lyapunov: np.ndarray, alpha: float = 0.05) -> A7Result:
    if times.shape != lyapunov.shape or times.ndim != 1:
        raise ValueError("times and lyapunov must be one-dimensional arrays of equal length")
    if times.size < 3:
        raise ValueError("need at least three samples")
    centered = times - times.mean()
    denom = float(np.sum(centered * centered))
    if denom == 0.0:
        raise ValueError("times must not all be equal")
    slope = float(np.sum(centered * (lyapunov - lyapunov.mean())) / denom)
    residuals = lyapunov - (lyapunov.mean() + slope * centered)
    sigma2 = float(np.sum(residuals * residuals) / max(times.size - 2, 1))
    stderr = float(np.sqrt(sigma2 / denom)) if denom > 0 else float("inf")
    p_value = 1.0 if slope <= 0 or stderr == 0.0 else 0.0
    return A7Result(bool((slope <= 0.0) or (p_value >= alpha)), slope, p_value)


def _self_test() -> dict[str, dict[str, object]]:
    harmonics = [(0, 0, 1.0 + 0j), (1, 0, 0.25 + 0j), (3, 0, 0.05 + 0j)]
    bins = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]])
    weights_a = np.array([0.5, 0.25, 0.25])
    weights_b = np.array([0.48, 0.27, 0.25])
    unstable_jacobian = np.array([[1.12, 0.0], [0.0, 0.5]])
    times = np.arange(6, dtype=float)
    lyapunov = np.array([5.0, 4.4, 4.1, 3.7, 3.4, 3.0])
    return {
        "A1": as_native_json_dict(check_A1_coherence(harmonics, ell_star=1)),
        "A3": as_native_json_dict(check_A3_identity(bins, weights_a, bins, weights_b)),
        "A4": as_native_json_dict(check_A4_spawn(unstable_jacobian)),
        "A5": as_native_json_dict(check_A5_rate_distortion(0.2, 2.0, 1.0)),
        "A7": as_native_json_dict(check_A7_lyapunov(times, lyapunov)),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(_self_test(), indent=2, sort_keys=True))
