"""テントマップ x_{n+1} = f(x_n)（f(x) = 2x (x ≦ 1/2)、2 − 2x (x > 1/2)）。Streamlit に依存しない。

テスト: python -m tests.test_applied
"""

from __future__ import annotations

import math
from fractions import Fraction


def tent(x):
    """Fraction でも float でも使える"""
    return 2 * x if x <= Fraction(1, 2) else 2 - 2 * x


def orbit(x0, N: int) -> list:
    out = [x0]
    for _ in range(N):
        out.append(tent(out[-1]))
    return out


def parse_x0(s: str) -> Fraction:
    """「1/7」「0.3」「3/10」などを分数に（0 以上 1 以下）"""
    s = s.strip().replace("／", "/").replace(" ", "")
    x = Fraction(s)
    if not 0 <= x <= 1:
        raise ValueError("0 以上 1 以下の数を入れてください")
    return x


def eventual_period(x0: Fraction, limit: int = 100000) -> tuple[int, int] | None:
    """分数の初期値の軌道が「何回目から」「周期いくつ」でくり返すか (前の部分の長さ, 周期)"""
    seen = {}
    x = x0
    for n in range(limit):
        if x in seen:
            return seen[x], n - seen[x]
        seen[x] = n
        x = tent(x)
    return None


def binary_digits(x: Fraction, k: int) -> str:
    """0 ≦ x ≦ 1 の 2 進数の小数部分 k 桁（x = 1 は 0.111… として表す）"""
    if x == 1:
        return "1" * k
    out = []
    for _ in range(k):
        x *= 2
        if x >= 1:
            out.append("1"); x -= 1
        else:
            out.append("0")
    return "".join(out)


def float_collapse_step(x0: float, limit: int = 200) -> int | None:
    """float で計算すると何回目に 0 になってしまうか"""
    x = x0
    for n in range(1, limit + 1):
        x = 2 * x if x <= 0.5 else 2 - 2 * x
        if x == 0:
            return n
    return None


def to_logistic(y):
    """テントマップの値 y → ロジスティック写像（a = 4）の値 x = sin²(πy/2)"""
    return math.sin(math.pi * float(y) / 2) ** 2
