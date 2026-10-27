"""ニュートン法・二分法（プログラミングのための数列）。Streamlit に依存しない。

テスト: python -m tests.test_applied
"""

from __future__ import annotations

import math
from decimal import Decimal, localcontext


def heron(a, x0, N: int, prec: int = 60) -> list[Decimal]:
    """√a を求める漸化式（バビロニアの方法・ヘロンの方法）x_{n+1} = (x_n + a/x_n)/2。
    桁数の多い小数（prec 桁）で計算する。x_0, …, x_N"""
    with localcontext() as ctx:
        ctx.prec = prec
        a, x = Decimal(str(a)), Decimal(str(x0))
        out = [x]
        for _ in range(N):
            x = (x + a / x) / 2
            out.append(+x)
        return out


def true_sqrt(a, prec: int = 60) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = prec + 10
        return Decimal(str(a)).sqrt()


def correct_digits(x: Decimal, t: Decimal, cap: int = 50) -> int:
    """x が真の値 t と何桁（有効数字）一致しているか（相対誤差から）"""
    if x == t:
        return cap
    with localcontext() as ctx:
        ctx.prec = cap + 20
        err = abs((x - t) / t)
        if err == 0:
            return cap
        d = -err.log10()
    return max(0, min(cap, int(math.floor(float(d)))))


def digits_split(x: Decimal, t: Decimal, show: int = 40) -> tuple[str, str]:
    """x を小数で show 桁表示し、t と一致している先頭部分と、それ以降に分ける"""
    with localcontext() as ctx:
        ctx.prec = show + 10
        sx, st = f"{x:.{show}f}", f"{t:.{show}f}"
    i = 0
    while i < len(sx) and i < len(st) and sx[i] == st[i]:
        i += 1
    return sx[:i], sx[i:]


def bisection(a, lo, hi, N: int, prec: int = 60) -> list[tuple[Decimal, Decimal, Decimal]]:
    """x² − a = 0 を二分法で解く。各回の (下端, 上端, 中点)"""
    with localcontext() as ctx:
        ctx.prec = prec
        a, lo, hi = Decimal(str(a)), Decimal(str(lo)), Decimal(str(hi))
        out = []
        for _ in range(N + 1):
            mid = (lo + hi) / 2
            out.append((lo, hi, mid))
            if mid * mid > a:
                hi = mid
            else:
                lo = mid
        return out


def poly(coefs, x: float) -> float:
    """係数（次数の高い順）の多項式の値"""
    v = 0.0
    for c in coefs:
        v = v * x + c
    return v


def dpoly(coefs) -> list[float]:
    """多項式の接線の傾きを表す多項式（微分）の係数"""
    n = len(coefs) - 1
    return [c * (n - i) for i, c in enumerate(coefs[:-1])]


def newton(coefs, x0: float, N: int) -> list[float]:
    """x_{n+1} = x_n − f(x_n)/f'(x_n)。f'(x_n) = 0 になったらそこで止める"""
    d = dpoly(coefs)
    out = [x0]
    for _ in range(N):
        x = out[-1]
        s = poly(d, x)
        if s == 0:
            break
        out.append(x - poly(coefs, x) / s)
    return out


def reciprocal(a: float, x0: float, N: int) -> list[float]:
    """割り算を使わずに 1/a を求める漸化式 x_{n+1} = x_n(2 − a x_n)"""
    out = [x0]
    for _ in range(N):
        x = out[-1]
        out.append(x * (2 - a * x))
    return out


def poly_tex(coefs) -> str:
    """係数（次数の高い順）→ LaTeX"""
    n = len(coefs) - 1
    terms = []
    for i, c in enumerate(coefs):
        p = n - i
        if c == 0:
            continue
        a = abs(c)
        num = "" if (a == 1 and p > 0) else (str(int(a)) if float(a).is_integer() else str(a))
        var = "" if p == 0 else ("x" if p == 1 else f"x^{{{p}}}")
        sign = "-" if c < 0 else "+"
        terms.append((sign, num + var))
    if not terms:
        return "0"
    s = ("-" if terms[0][0] == "-" else "") + terms[0][1]
    for sign, t in terms[1:]:
        s += f" {sign} {t}"
    return s


# ③ の例：(名前, 係数, 初期値, 説明)
EXAMPLES = {
    "sqrt2": ("x² − 2 = 0（√2）", [1, 0, -2], 2.0, "① の √2 の漸化式と同じ。"),
    "sqrt2_neg": ("x² − 2 = 0（初期値が負）", [1, 0, -2], -1.0, "初期値が負だと −√2 に近づく。どの解に近づくかは初期値で決まる。"),
    "cbrt2": ("x³ − 2 = 0（∛2）", [1, 0, 0, -2], 2.0, "立方根も同じように求められる。"),
    "newton1669": ("x³ − 2x − 5 = 0（ニュートンの例）", [1, 0, -2, -5], 2.0, "ニュートン自身が説明に使った方程式。解は 2.0945514815…"),
    "cycle": ("x³ − 2x + 2 = 0（初期値 0）", [1, 0, -2, 2], 0.0, "0 → 1 → 0 → 1 … と行ったり来たりして、いつまでも近づかない。"),
}
