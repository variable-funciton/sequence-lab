"""数列の内積と畳み込み。Streamlit に依存しない。

テスト: python -m tests.test_applied
"""

from __future__ import annotations

from fractions import Fraction


def parse_seq(s: str) -> list[Fraction]:
    """「1, 2, 3」「1/6 1/6」などを分数の数列に"""
    s = s.replace("、", ",").replace("，", ",").replace("／", "/").replace(" ", ",")
    out = [Fraction(t) for t in s.split(",") if t.strip()]
    if not out:
        raise ValueError("数を 1 つ以上入れてください")
    return out


def dot(a, b):
    """内積 a_1 b_1 + a_2 b_2 + … （長さは短いほうに合わせる）"""
    return sum(x * y for x, y in zip(a, b))


def convolve(a, b) -> list:
    """畳み込み c_n = Σ_k a_k b_{n−k}（n = 0, 1, …, len(a) + len(b) − 2。番号は 0 から）"""
    if not a or not b:
        return []
    c = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            c[i + j] += x * y
    return c


def conv_terms(a, b, n: int) -> list[tuple[int, object, object]]:
    """c_n を作る項 [(k, a_k, b_{n−k})]"""
    return [(k, a[k], b[n - k]) for k in range(len(a)) if 0 <= n - k < len(b)]


def dice_dist(n: int, faces: int = 6) -> list[Fraction]:
    """n 個のさいころの目の和の確率（和 = n, n+1, …, faces·n）"""
    one = [Fraction(1, faces)] * faces
    d = one
    for _ in range(n - 1):
        d = convolve(d, one)
    return d


def pascal(n: int) -> list[list[int]]:
    """(1 + x)^k の係数（k = 0, …, n）：[1, 1] を k 回畳み込む"""
    rows = [[1]]
    for _ in range(n):
        rows.append(convolve(rows[-1], [1, 1]))
    return rows


def moving_average(x: list[float], w: int) -> list[float]:
    """幅 w の移動平均 = [1/w, …, 1/w] との畳み込み（両端の不完全な所は除く）"""
    k = [1 / w] * w
    c = convolve(x, k)
    return c[w - 1:len(x)]


def multiply_digits(x: int, y: int) -> tuple[list[int], list[int], int]:
    """掛け算の筆算 = 各けたの数字の畳み込み + くり上がり。
    戻り値 (くり上がり前の各けた（1 の位から）, くり上がり後の各けた, 積)"""
    a = [int(d) for d in reversed(str(x))]
    b = [int(d) for d in reversed(str(y))]
    c = convolve(a, b)
    digits, carry = [], 0
    for v in c:
        v += carry
        digits.append(v % 10)
        carry = v // 10
    while carry:
        digits.append(carry % 10)
        carry //= 10
    return c, digits, int("".join(map(str, reversed(digits))))
