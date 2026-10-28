"""数列の問題で共通に使う道具(n の多項式の表示・因数分解、等比数列の一般項の表示)"""
import math
from fractions import Fraction as F

from .radicals import poly_tex, tx


def npoly(coeffs, var="n"):
    """[c0, c1, c2, c3] → 2n^3 - n + 1"""
    terms = []
    for k in range(len(coeffs) - 1, -1, -1):
        body = "" if k == 0 else (var if k == 1 else f"{var}^{{{k}}}")
        terms.append((F(coeffs[k]), body))
    return poly_tex(terms)


def peval(coeffs, x):
    return sum(F(c) * F(x) ** k for k, c in enumerate(coeffs))


def _lcm(a, b):
    return a * b // math.gcd(a, b)


def _lin(q, p, var):
    """q n - p(q > 0)"""
    return poly_tex([(q, var), (-p, "")])


def _divisors(x):
    x = abs(x)
    return [d for d in range(1, x + 1) if x % d == 0] if x else [1]


def _rational_root(ints):
    """整数係数(低次から)の多項式の有理数の根(なければ None)"""
    c0, cn = ints[0], ints[-1]
    if c0 == 0:
        return F(0)
    for qd in _divisors(cn):
        for pn in _divisors(c0):
            for sg in (-1, 1):
                r = F(sg * pn, qd)
                if sum(c * r ** k for k, c in enumerate(ints)) == 0:
                    return r
    return None


def _divide(ints, qd, pn):
    """ints(低次から)を (qd x - pn) で割った商(整数係数)"""
    hi = list(reversed(ints))          # 高次から
    out, rem = [], 0
    cur = F(0)
    for c in hi[:-1]:
        cur = cur * F(pn, qd) + c
        out.append(cur)
    # x - pn/qd で割った商を qd で割る
    out = [c / qd for c in out]
    assert all(c.denominator == 1 for c in out)
    del rem
    return [int(c) for c in reversed(out)]


def factor_tex(coeffs, var="n"):
    """n の多項式(3次まで)をできるだけ因数分解して書く。例: [0, 1/3, 1/2, 1/6] → \\frac{1}{6}n(n + 1)(2n + 1)"""
    cs = [F(c) for c in coeffs]
    while len(cs) > 1 and cs[-1] == 0:
        cs.pop()
    if all(c == 0 for c in cs):
        return "0"
    D = 1
    for c in cs:
        D = _lcm(D, c.denominator)
    ints = [int(c * D) for c in cs]
    g = 0
    for x in ints:
        g = math.gcd(g, abs(x))
    if ints[-1] < 0:
        g = -g
    ints = [x // g for x in ints]
    K = F(g, D)
    factors = []
    # n でくくる
    while len(ints) > 1 and ints[0] == 0:
        ints = ints[1:]
        factors.append(var)
    # 3次以上なら有理数の根で1次式をくくり出す
    while len(ints) > 3:
        root = _rational_root(ints)
        if root is None:
            break
        qd, pn = root.denominator, root.numerator
        factors.append(rf"({_lin(qd, pn, var)})")
        ints = _divide(ints, qd, pn)
    if len(ints) == 3:                     # A n^2 + B n + C
        C, B, A = ints
        disc = B * B - 4 * A * C
        if disc >= 0 and math.isqrt(disc) ** 2 == disc:
            sq = math.isqrt(disc)
            roots = sorted([F(-B + sq, 2 * A), F(-B - sq, 2 * A)], key=lambda r: (r.denominator, -r))
            q1, q2 = roots[0].denominator, roots[1].denominator
            K = K * F(A, q1 * q2)
            for r in roots:
                factors.append(rf"({_lin(r.denominator, r.numerator, var)})")
            ints = None
    if ints is not None and len(ints) == 2:  # B n + C
        C, B = ints
        if C == 0:
            factors.append(var)
            K = K * B
        else:
            factors.append(rf"({poly_tex([(B, var), (C, '')])})")
        ints = None
    if ints is not None and len(ints) == 1:
        K = K * ints[0]
        ints = None
    if ints is not None:                    # 因数分解できない部分
        factors.append(rf"({npoly(ints, var)})")
    if not factors:
        return tx(K)
    nc = factors.count(var)
    others = [f for f in factors if f != var]
    vpart = "" if nc == 0 else (var if nc == 1 else f"{var}^{{{nc}}}")
    # 括弧が1つだけで、ほかに n がないとき括弧を外す
    if not vpart and len(others) == 1 and K == 1:
        return others[0][1:-1]
    uniq = []
    for f in others:
        if f not in uniq:
            uniq.append(f)
    body = vpart + "".join(f if others.count(f) == 1 else f"{f}^{{{others.count(f)}}}" for f in uniq)
    if K == 1:
        return body
    if K == -1:
        return "-" + body
    return tx(K) + body


def pow_tex(base, exp):
    """base^exp(base は有理数、exp は LaTeX)"""
    b = F(base)
    if b.denominator == 1 and b >= 0:
        return f"{b}^{{{exp}}}"
    return rf"\left({tx(b)}\right)^{{{exp}}}"


def geo_term_tex(a, r, exp="n-1"):
    """a r^{exp}"""
    a, r = F(a), F(r)
    p = pow_tex(r, exp)
    if a == 1:
        return p
    if a == -1:
        return "-" + p
    return rf"{tx(a)}\cdot {p}"


def sum_sq(n):
    return n * (n + 1) * (2 * n + 1) // 6
