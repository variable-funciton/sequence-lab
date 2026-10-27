"""いろいろな数列の和（級数）の収束・発散。Streamlit に依存しない。

テスト: python -m tests.test_applied
"""

from __future__ import annotations

import math

import numpy as np

EULER_GAMMA = 0.5772156649015329    # オイラー定数 γ
ZETA_HALF = -1.4603545088095868     # ζ(1/2)：1/√1 + … + 1/√N ≈ 2√N + ζ(1/2)

# key: (表示名, 一般項の LaTeX, 項の関数（n の numpy 配列 → 値）, 極限（発散なら None）, 極限の LaTeX)
SERIES = {
    "harmonic": ("1/n（調和級数）", r"\frac{1}{n}", lambda n: 1.0 / n, None, r"\infty"),
    "basel": ("1/n²（バーゼル問題）", r"\frac{1}{n^2}", lambda n: 1.0 / n ** 2, math.pi ** 2 / 6, r"\frac{\pi^2}{6}"),
    "sqrt": ("1/√n", r"\frac{1}{\sqrt{n}}", lambda n: 1.0 / np.sqrt(n), None, r"\infty"),
    "quartic": ("1/n⁴", r"\frac{1}{n^4}", lambda n: 1.0 / n ** 4, math.pi ** 4 / 90, r"\frac{\pi^4}{90}"),
    "telescope": ("1/{n(n+1)}", r"\frac{1}{n(n+1)}", lambda n: 1.0 / (n * (n + 1)), 1.0, "1"),
    "geometric": ("1/2ⁿ（等比数列）", r"\frac{1}{2^n}", lambda n: 0.5 ** n, 1.0, "1"),
    "alternating": ("(−1)ⁿ⁺¹/n（交代級数）", r"\frac{(-1)^{n+1}}{n}", lambda n: np.where(n % 2 == 1, 1.0, -1.0) / n, math.log(2), r"\log_e 2"),
}


def partial_sums(key: str, N: int) -> np.ndarray:
    """S_1, …, S_N"""
    n = np.arange(1, N + 1, dtype=float)
    return np.cumsum(SERIES[key][2](n))


def p_series_partial(p: float, N: int) -> np.ndarray:
    """1/n^p の部分和 S_1, …, S_N"""
    n = np.arange(1, N + 1, dtype=float)
    return np.cumsum(n ** (-p))


def sample_indices(N: int, k: int = 400) -> np.ndarray:
    """1〜N から、対数目盛でほぼ等間隔に k 個（グラフ用）"""
    idx = np.unique(np.round(np.logspace(0, math.log10(N), k)).astype(int))
    return idx[(idx >= 1) & (idx <= N)]


def harmonic_groups(K: int) -> list[tuple[int, int, float]]:
    """調和級数を 1 | 1/2 | 1/3+1/4 | 1/5+…+1/8 | … と分けたときの (始め, 終わり, 和)。2 番目以降の和はすべて 1/2 以上"""
    out = [(1, 1, 1.0)]
    for k in range(K):
        a, b = 2 ** k + 1, 2 ** (k + 1)
        out.append((a, b, sum(1.0 / n for n in range(a, b + 1))))
    return out


def basel_bound(N: int) -> float:
    """1/n² < 1/{n(n−1)} = 1/(n−1) − 1/n（n ≧ 2）を使った上からの評価：S_N < 2 − 1/N"""
    return 2 - 1 / N


def pi_from_basel(S: float) -> float:
    """S ≈ π²/6 から π ≈ √(6S)"""
    return math.sqrt(6 * S)
