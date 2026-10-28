"""2 つの状態（晴れ・雨）のマルコフ連鎖。Streamlit に依存しない。

a = P(晴れ → 晴れ)、b = P(雨 → 晴れ)。n 回目が晴れの確率 p_n は p_{n+1} = a p_n + b(1 − p_n) = (a − b)p_n + b。
テスト: python -m tests.test_applied
"""

from __future__ import annotations

import random


def probs(a: float, b: float, p1: float, N: int) -> list[float]:
    """p_1, …, p_N（漸化式で）"""
    out = [p1]
    for _ in range(N - 1):
        p = out[-1]
        out.append(a * p + b * (1 - p))
    return out


def limit(a: float, b: float) -> float | None:
    """極限 b / (1 − a + b)（a − b = 1、つまり a = 1, b = 0 のときは決まらない）"""
    d = 1 - a + b
    return None if d == 0 else b / d


def closed_form(a: float, b: float, p1: float, n: int) -> float:
    """一般項 p_n = α + (a − b)^{n−1}(p_1 − α)"""
    al = limit(a, b)
    if al is None:
        return p1
    return al + (a - b) ** (n - 1) * (p1 - al)


def generate(a: float, b: float, p1: float, N: int, rng: random.Random) -> list[int]:
    """1 = 晴れ、0 = 雨 の列を N 個"""
    s = [1 if rng.random() < p1 else 0]
    for _ in range(N - 1):
        s.append(1 if rng.random() < (a if s[-1] == 1 else b) else 0)
    return s


def estimate(seq: list[int]) -> tuple[dict, float | None, float | None]:
    """記録から遷移の回数を数えて a = P(晴→晴)、b = P(雨→晴) を推定する（学習）"""
    cnt = {(1, 1): 0, (1, 0): 0, (0, 1): 0, (0, 0): 0}
    for x, y in zip(seq, seq[1:]):
        cnt[(x, y)] += 1
    from_sun, from_rain = cnt[(1, 1)] + cnt[(1, 0)], cnt[(0, 1)] + cnt[(0, 0)]
    a = cnt[(1, 1)] / from_sun if from_sun else None
    b = cnt[(0, 1)] / from_rain if from_rain else None
    return cnt, a, b


def parse_weather(text: str) -> list[int]:
    """「晴晴雨晴」「☀☀☂」「SSRS」「晴れ 雨 晴れ」などを 1/0 の列に"""
    t = text.replace("晴れ", "晴").replace("くもり", "").replace("曇", "")
    out = []
    for ch in t:
        if ch in "晴☀SsHh○":
            out.append(1)
        elif ch in "雨☂☔Rr●":
            out.append(0)
    return out


def temperature(p: float, T: float) -> float:
    """2 択の確率 (p, 1 − p) を「温度」T で変える：p^(1/T) / (p^(1/T) + (1 − p)^(1/T))。
    T < 1 で確率の高いほうに偏り、T > 1 で半々に近づく"""
    if p <= 0 or p >= 1:
        return p
    x, y = p ** (1 / T), (1 - p) ** (1 / T)
    return x / (x + y)


def run_lengths(seq: list[int], state: int = 1) -> list[int]:
    """同じ状態が続いた長さの一覧"""
    out, n = [], 0
    for s in seq:
        if s == state:
            n += 1
        elif n:
            out.append(n); n = 0
    if n:
        out.append(n)
    return out
