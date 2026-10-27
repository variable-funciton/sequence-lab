"""数列の計算ロジック（Streamlit に依存しない純粋な関数）。

お金の計算は Fraction で厳密に行い、表示のときだけ丸める。
（課題の数値 3,310,000 円・年利 10% などがぴったり再現できるようにするため）
"""

from __future__ import annotations

import math
from fractions import Fraction


def to_frac(x) -> Fraction:
    """float を含む入力を Fraction に（0.1 -> 1/10 のように 10 進表記どおりに変換）"""
    if isinstance(x, Fraction):
        return x
    if isinstance(x, int):
        return Fraction(x)
    return Fraction(str(x))


# =====================================================================
# 漸化式 a_{n+1} = (1 + r) a_n − P （ローンの返済残高）
# =====================================================================
def loan_balances(a0, r, P, N: int) -> list[Fraction]:
    """a_0, a_1, …, a_N を返す。"""
    a0, r, P = to_frac(a0), to_frac(r), to_frac(P)
    out = [a0]
    for _ in range(N):
        out.append((1 + r) * out[-1] - P)
    return out


def payment_for_target(a0, r, N: int, aN=0) -> Fraction:
    """N 年後の残高が aN になる毎年の返済額 P。

    一般項 a_N = (1+r)^N a_0 − P{(1+r)^N − 1}/r より
        P = r{(1+r)^N a_0 − a_N} / {(1+r)^N − 1}     (r ≠ 0)
        P = (a_0 − a_N) / N                          (r = 0)
    """
    a0, r, aN = to_frac(a0), to_frac(r), to_frac(aN)
    if N <= 0:
        raise ValueError("N must be positive")
    if r == 0:
        return (a0 - aN) / N
    g = (1 + r) ** N
    return r * (g * a0 - aN) / (g - 1)


def fixed_point(r, P):
    """特性方程式 α = (1+r)α − P の解 α = P / r（r = 0 なら None）"""
    r, P = to_frac(r), to_frac(P)
    return None if r == 0 else P / r


def closed_form(a0, r, P, n: int) -> Fraction:
    """一般項 a_n = α + (1+r)^n (a_0 − α)"""
    a0, r, P = to_frac(a0), to_frac(r), to_frac(P)
    if r == 0:
        return a0 - n * P
    alpha = P / r
    return alpha + (1 + r) ** n * (a0 - alpha)


def loan_trend(a0, r, P) -> str:
    """残高の振る舞い: 'decrease'（いずれ完済）, 'constant', 'increase'（借金が増える）"""
    a0, r, P = to_frac(a0), to_frac(r), to_frac(P)
    interest = r * a0
    if P > interest:
        return "decrease"
    if P == interest:
        return "constant"
    return "increase"


def years_to_payoff(a0, r, P, limit: int = 1000):
    """残高が初めて 0 以下になる年（返済が利息以下なら None）"""
    if loan_trend(a0, r, P) != "decrease":
        return None
    a = to_frac(a0)
    r, P = to_frac(r), to_frac(P)
    for n in range(1, limit + 1):
        a = (1 + r) * a - P
        if a <= 0:
            return n
    return None


# =====================================================================
# 単利（等差数列）と複利（等比数列）
# =====================================================================
def simple_interest(a0, r, N: int) -> list[Fraction]:
    """単利の元利合計 a_n = a_0 (1 + n r) 　… 公差 a_0 r の等差数列"""
    a0, r = to_frac(a0), to_frac(r)
    return [a0 * (1 + n * r) for n in range(N + 1)]


def compound_interest(a0, r, N: int) -> list[Fraction]:
    """複利の元利合計 a_n = a_0 (1 + r)^n 　… 公比 1 + r の等比数列"""
    a0, r = to_frac(a0), to_frac(r)
    return [a0 * (1 + r) ** n for n in range(N + 1)]


def doubling_years(r):
    """複利で元本が 2 倍になるまでの年数（実数）。r <= 0 なら None"""
    r = float(r)
    return None if r <= 0 else math.log(2) / math.log(1 + r)


# =====================================================================
# 等差数列
# =====================================================================
def arithmetic_terms(a, d, N: int) -> list[Fraction]:
    a, d = to_frac(a), to_frac(d)
    return [a + (n - 1) * d for n in range(1, N + 1)]


def arithmetic_sums(a, d, N: int) -> list[Fraction]:
    """S_1, …, S_N  （S_n = n{2a + (n−1)d}/2）"""
    a, d = to_frac(a), to_frac(d)
    return [Fraction(n, 2) * (2 * a + (n - 1) * d) for n in range(1, N + 1)]


def first_negative_index(a, d):
    """a_n < 0 となる最小の n（ならないなら None）"""
    a, d = to_frac(a), to_frac(d)
    if a < 0:
        return 1
    if d >= 0:
        return None
    # a + (n−1)d < 0  ⇔  n > 1 + a/(−d)
    return math.floor(1 + a / (-d)) + 1


def max_sum(a, d):
    """S_n が最大となる n のリストと最大値（d < 0 かつ a > 0 のとき）。それ以外は None"""
    a, d = to_frac(a), to_frac(d)
    if d >= 0 or a <= 0:
        return None
    # 正または 0 の項を全部足したときが最大。a_n = 0 となる項があれば n が 2 つ
    last_nonneg = math.floor(1 + a / (-d))
    sums = arithmetic_sums(a, d, last_nonneg)
    best = sums[-1]
    ns = [n for n, s in enumerate(sums, start=1) if s == best]
    return ns, best


def fmt_yen(x) -> str:
    """円表示（整数ならそのまま、端数があれば小数第1位まで）"""
    x = to_frac(x)
    if x.denominator == 1:
        return f"{x.numerator:,} 円"
    return f"{float(x):,.1f} 円"


def fmt_num(x) -> str:
    """一般の数（整数・分数・小数を見やすく）"""
    x = to_frac(x)
    if abs(x) >= 10**12:
        return f"{float(x):.4g}".replace("-", "−")
    if x.denominator == 1:
        return f"{x.numerator:,}"
    if x.denominator <= 12:
        sign = "−" if x < 0 else ""
        return f"{sign}{abs(x.numerator)}/{x.denominator}"
    return f"{float(x):,.4g}"


# =====================================================================
# 等比数列
# =====================================================================
def geometric_terms(a, r, N: int) -> list[Fraction]:
    """a_1, …, a_N  （a_n = a r^(n−1)）"""
    a, r = to_frac(a), to_frac(r)
    return [a * r ** (n - 1) for n in range(1, N + 1)]


def geometric_sums(a, r, N: int) -> list[Fraction]:
    """S_1, …, S_N を公式で計算（r = 1 のときは S_n = n a）"""
    a, r = to_frac(a), to_frac(r)
    if r == 1:
        return [n * a for n in range(1, N + 1)]
    return [a * (1 - r ** n) / (1 - r) for n in range(1, N + 1)]


def geometric_limit(a, r):
    """|r| < 1 のときの和の極限 a / (1 − r)。それ以外は None"""
    a, r = to_frac(a), to_frac(r)
    return a / (1 - r) if abs(r) < 1 else None


# 公比の 6 つの場合（表示順）
RATIO_CASES = ["0<r<1", "r=1", "r>1", "-1<r<0", "r=-1", "r<-1"]


def ratio_case(r) -> str:
    """公比 r が 6 つの場合のどれにあたるか（r = 0 は ValueError）"""
    r = to_frac(r)
    if r == 0:
        raise ValueError("r = 0 は扱わない")
    if r == 1:
        return "r=1"
    if r == -1:
        return "r=-1"
    if r > 1:
        return "r>1"
    if r > 0:
        return "0<r<1"
    if r > -1:
        return "-1<r<0"
    return "r<-1"


def latex_num(x, digits: int = 4) -> str:
    """LaTeX 用の数。整数は桁区切り、分母の小さい分数は \\frac、それ以外は小数（大きければ指数表記）"""
    x = to_frac(x)
    sign = "-" if x < 0 else ""
    x = abs(x)
    if x.denominator == 1:
        n = x.numerator
        if n >= 10**9:
            m, e = f"{float(n):.{digits - 1}e}".split("e")
            return rf"{sign}{m} \times 10^{{{int(e)}}}"
        return sign + f"{n:,}".replace(",", "{,}")
    if x.denominator < 10**7 and x.numerator < 10**7:
        return rf"{sign}\frac{{{x.numerator}}}{{{x.denominator}}}"
    v = float(x)
    if v != 0 and (v < 1e-3 or v >= 1e9):
        m, e = f"{v:.{digits - 1}e}".split("e")
        return rf"{sign}{m} \times 10^{{{int(e)}}}"
    return sign + f"{v:,.{digits}g}".replace(",", "{,}")
