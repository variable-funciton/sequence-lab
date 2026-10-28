"""根号を含む数の厳密計算

Rad は √n(n は平方因子を含まない正の整数)の有理数係数の一次結合を表す。
    例: (√6 + √2)/4 = Rad({6: 1/4, 2: 1/4})
足し算・掛け算・割り算(分母の有理化)ができるので、
加法定理・2倍角・半角の公式で出てくる値をそのまま計算できる。

三角関数の厳密値(π/12 の倍数の角)も、ここでまとめて扱う。
"""
import math
from fractions import Fraction as F

__all__ = ["Rad", "R", "sqrt_rad", "squarefree", "pi_tex", "sin_ex", "cos_ex", "tan_ex", "TRIG_EX",
           "nested_sqrt_tex", "tx", "coef_tex", "poly_tex", "sq_tex"]


def squarefree(n):
    """n = k^2 m(m は平方因子なし)の (k, m)"""
    n = int(n)
    k, m, d = 1, n, 2
    while d * d <= m:
        while m % (d * d) == 0:
            m //= d * d
            k *= d
        d += 1
    return k, m


def _primes(n):
    out, d = set(), 2
    while d * d <= n:
        while n % d == 0:
            out.add(d)
            n //= d
        d += 1
    if n > 1:
        out.add(n)
    return out


class Rad:
    """Σ q_n √n(q_n は有理数、n は平方因子なし)。n = 1 が有理数の部分"""

    __slots__ = ("t",)

    def __init__(self, terms=None):
        t = {}
        if terms is None:
            terms = {}
        elif not isinstance(terms, dict):
            terms = {1: F(terms)}
        for n, q in terms.items():
            q = F(q)
            if q == 0:
                continue
            k, m = squarefree(n)
            t[m] = t.get(m, F(0)) + q * k
            if t[m] == 0:
                del t[m]
        self.t = t

    # ---- 生成 ----
    @staticmethod
    def sqrt(x):
        """有理数 x ≥ 0 の平方根"""
        x = F(x)
        if x < 0:
            raise ValueError("負の数の平方根")
        if x == 0:
            return Rad()
        return Rad({x.numerator * x.denominator: F(1, x.denominator)})

    # ---- 演算 ----
    def __add__(self, o):
        o = R(o)
        t = dict(self.t)
        for n, q in o.t.items():
            t[n] = t.get(n, F(0)) + q
        return Rad(t)

    __radd__ = __add__

    def __neg__(self):
        return Rad({n: -q for n, q in self.t.items()})

    def __sub__(self, o):
        return self + (-R(o))

    def __rsub__(self, o):
        return R(o) - self

    def __mul__(self, o):
        o = R(o)
        t = {}
        for n1, q1 in self.t.items():
            for n2, q2 in o.t.items():
                g = math.gcd(n1, n2)
                n = (n1 // g) * (n2 // g)
                t[n] = t.get(n, F(0)) + q1 * q2 * g
        return Rad(t)

    __rmul__ = __mul__

    def conj(self, p):
        """素数 p を含む根号の符号を反転した共役"""
        return Rad({n: (-q if n % p == 0 else q) for n, q in self.t.items()})

    def inverse(self):
        if not self.t:
            raise ZeroDivisionError("0 で割った")
        num, den = R(1), self
        primes = set()
        for n in self.t:
            primes |= _primes(n)
        for p in sorted(primes):
            c = den.conj(p)
            num, den = num * c, den * c
        # den は有理数になっている
        assert set(den.t) <= {1}, den.t
        return num * R(1 / den.t[1])

    def __truediv__(self, o):
        return self * R(o).inverse()

    def __rtruediv__(self, o):
        return R(o) * self.inverse()

    def __pow__(self, k):
        out = R(1)
        for _ in range(int(k)):
            out = out * self
        return out

    def __abs__(self):
        return -self if float(self) < 0 else self

    # ---- 比較・変換 ----
    def __float__(self):
        return float(sum(float(q) * math.sqrt(n) for n, q in self.t.items()))

    def __eq__(self, o):
        try:
            o = R(o)
        except (TypeError, ValueError):
            return NotImplemented
        return self.t == o.t

    def __hash__(self):
        return hash(tuple(sorted(self.t.items())))

    def __lt__(self, o):
        return float(self) < float(R(o))

    def __gt__(self, o):
        return float(self) > float(R(o))

    def __le__(self, o):
        return self == o or self < o

    def __ge__(self, o):
        return self == o or self > o

    def __repr__(self):
        return f"Rad({self.tex()})"

    def is_zero(self):
        return not self.t

    def is_rational(self):
        return set(self.t) <= {1}

    def rational(self):
        return self.t.get(1, F(0)) if self.is_rational() else None

    def is_int(self):
        r = self.rational()
        return r is not None and r.denominator == 1

    def single(self):
        """q√n の1項(または0)なら True"""
        return len(self.t) <= 1

    # ---- LaTeX ----
    def tex(self, paren=False):
        """(√6 + √2)/4 のように1つの分数にまとめて書く。paren=True なら負の数・和を ( ) で囲む"""
        if not self.t:
            return "0"
        den = 1
        for q in self.t.values():
            den = den * q.denominator // math.gcd(den, q.denominator)
        items = sorted(((n, q * den) for n, q in self.t.items()), key=lambda x: (x[0] != 1, -x[0]))
        # 係数の最大公約数でくくる(分母と約分できる場合だけ)
        nums = [int(c) for _, c in items]
        neg = all(c < 0 for c in nums) and (den != 1 or len(nums) == 1)
        if neg:
            items = [(n, -c) for n, c in items]
        # 先頭に正の項を持ってくる
        if items[0][1] < 0:
            pos = [x for x in items if x[1] > 0]
            negs = [x for x in items if x[1] < 0]
            items = pos + negs
        parts = []
        for i, (n, c) in enumerate(items):
            c = int(c)
            mag = abs(c)
            if n == 1:
                body = str(mag)
            else:
                body = ("" if mag == 1 else str(mag)) + rf"\sqrt{{{n}}}"
            if i == 0:
                parts.append(("-" if c < 0 else "") + body)
            else:
                parts.append((" - " if c < 0 else " + ") + body)
        num = "".join(parts)
        if den == 1:
            s = num
        else:
            s = rf"\frac{{{num}}}{{{den}}}"
        if neg:
            s = "-" + s
        if paren and (neg or (den == 1 and len(items) > 1)):
            return rf"\left({s}\right)"
        return s


def R(x):
    if isinstance(x, Rad):
        return x
    if isinstance(x, (int, F)):
        return Rad(x)
    raise TypeError(f"Rad に変換できない: {x!r}")


def sqrt_rad(x):
    return Rad.sqrt(x)


def tx(x, paren=False):
    return R(x).tex(paren)


def sq_tex(x):
    """x^2 の表記(分数・負の数・根号は括弧付き)"""
    s = R(x)
    if s.is_int() and s.rational() >= 0:
        return f"{s.tex()}^2"
    return rf"\left({s.tex()}\right)^2"


def coef_tex(c):
    """係数(1 は省略、-1 は「-」)"""
    c = R(c)
    if c == 1:
        return ""
    if c == -1:
        return "-"
    if not c.single() or (not c.is_rational() and len(c.t) > 1):
        return rf"\left({c.tex()}\right)"
    return c.tex()


def poly_tex(terms):
    """[(係数, 本体tex), ...] を符号付きでつなぐ。本体 '' は定数項"""
    out = ""
    for c, body in terms:
        c = F(c)
        if c == 0:
            continue
        mag = tx(abs(c)) if body == "" else (("" if abs(c) == 1 else tx(abs(c))) + body)
        if out == "":
            out = ("-" if c < 0 else "") + mag
        else:
            out += (" - " if c < 0 else " + ") + mag
    return out or "0"


def pi_tex(a):
    """a*π の LaTeX(a は有理数)。例: 5/6 → \\frac{5}{6}\\pi"""
    a = F(a)
    if a == 0:
        return "0"
    s = "-" if a < 0 else ""
    a = abs(a)
    p, q = a.numerator, a.denominator
    if q == 1:
        return s + (r"\pi" if p == 1 else rf"{p}\pi")
    if p == 1:
        return s + rf"\frac{{\pi}}{{{q}}}"
    return s + rf"\frac{{{p}}}{{{q}}}\pi"


# ------------------------------------------------------------
# 三角関数の厳密値(角は π の何倍かを Fraction で持つ。π/12 の倍数)
# ------------------------------------------------------------
_S6, _S2, _S3 = Rad({6: 1}), Rad({2: 1}), Rad({3: 1})
_SIN_Q1 = {
    F(0): R(0),
    F(1, 12): (_S6 - _S2) * F(1, 4),
    F(1, 6): R(F(1, 2)),
    F(1, 4): _S2 * F(1, 2),
    F(1, 3): _S3 * F(1, 2),
    F(5, 12): (_S6 + _S2) * F(1, 4),
    F(1, 2): R(1),
}


def sin_ex(a):
    r = F(a) % 2
    if r <= F(1, 2):
        ref, sg = r, 1
    elif r <= 1:
        ref, sg = 1 - r, 1
    elif r <= F(3, 2):
        ref, sg = r - 1, -1
    else:
        ref, sg = 2 - r, -1
    if ref not in _SIN_Q1:
        raise ValueError(f"π/12 の倍数ではない角: {a}")
    v = _SIN_Q1[ref]
    return v if sg > 0 else -v


def cos_ex(a):
    return sin_ex(F(a) + F(1, 2))


def tan_ex(a):
    c = cos_ex(a)
    return None if c.is_zero() else sin_ex(a) / c


TRIG_EX = {"sin": sin_ex, "cos": cos_ex, "tan": tan_ex}


def nested_sqrt_tex(x):
    """√x の LaTeX(x は正の Rad)。x が Rad の2乗なら外して書く。
    例: (2 - √2)/4 → \\frac{\\sqrt{2 - \\sqrt{2}}}{2}"""
    x = R(x)
    if float(x) < 0:
        raise ValueError("負の数の平方根")
    if x.is_rational():
        return Rad.sqrt(x.rational()).tex()
    # 2乗して x になる Rad を探す(π/12 の倍数の三角関数の値など)
    for v in list(_SIN_Q1.values()) + [_SIN_Q1[k] * 2 for k in _SIN_Q1]:
        if v * v == x:
            return v.tex()
    # x = N / d^2(N は整数係数)の形にして √N / d
    den = 1
    for q in x.t.values():
        den = den * q.denominator // math.gcd(den, q.denominator)
    k, m = squarefree(den)
    d = k * m           # den * m = (k m)^2
    N = x * (den * m)   # x = N / d^2
    # N の係数の公約数のうち平方数をくくり出す
    g = 0
    for q in N.t.values():
        g = math.gcd(g, int(q))
    s = 1
    for p in range(math.isqrt(abs(g)), 0, -1):
        if g % (p * p) == 0:
            s = p
            break
    N = N * F(1, s * s)
    gg = math.gcd(s, d)          # 例: 2√(…)/4 → √(…)/2
    s, d = s // gg, d // gg
    num = ("" if s == 1 else str(s)) + rf"\sqrt{{{N.tex()}}}"
    return num if d == 1 else rf"\frac{{{num}}}{{{d}}}"
