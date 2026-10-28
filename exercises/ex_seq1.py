"""数列 第1章(後期期末の範囲):等差数列・等比数列・いろいろな数列の和

等差数列・等比数列の一般項と和、Σ の計算、階差数列、部分分数に分けて求める和、S_n から a_n。
"""
from fractions import Fraction as F

from .ex_core import Problem, ProblemType, Retry, fill_choices
from .radicals import tx
from .seq_common import factor_tex, geo_term_tex, npoly, peval, pow_tex

INTRO = "次の問いに答えよ．"


def _an(c1, c0):
    """a_n = c1 n + c0"""
    return npoly([c0, c1])


def _terms(seq, more=True):
    return ",\\ ".join(tx(x) for x in seq) + (r",\ \cdots" if more else "")


# ======================================================================
#  等差数列の一般項
# ======================================================================
def g_arith(rng):
    a = rng.choice([x for x in range(-12, 16) if x != 0])
    d = rng.choice([x for x in range(-6, 8) if x != 0])
    k = rng.randint(10, 30)
    ak = a + (k - 1) * d
    pair = lambda c1, c0, v: rf"a_n = {_an(c1, c0)},\ a_{{{k}}} = {tx(v)}"
    ans = pair(d, a - d, ak)
    st = rf"初項 ${a}$，公差 ${d}$ の等差数列 $\{{a_n\}}$ の一般項 $a_n$ と第 ${k}$ 項 $a_{{{k}}}$ を求めよ．"
    const = "" if a - d == 0 else (f" + {a - d}" if a - d > 0 else f" - {d - a}")
    sol = [rf"等差数列の一般項は $a_n = a + (n - 1)d$ であるから，$a_n = {a} + (n - 1)\cdot {tx(d, True)} = {_an(d, a - d)}$．",
           rf"$a_{{{k}}} = {d}\cdot {k}{const} = {ak}$．"]
    alts = [(pair(d, a, a + k * d), r"一般項は $a_n = a + (n - 1)d$ である($nd$ ではなく $(n-1)d$)．"),
            (pair(a, d - a, a * k + d - a), "初項と公差が入れかわっていないか確かめよう．"),
            (pair(-d, a + d, a - (k - 1) * d), "公差の符号を確かめよう．")]
    return Problem("等差数列の一般項", "基本", st, fill_choices(ans, alts, [], rng),
                   hints=[r"等差数列の一般項は $a_n = a + (n - 1)d$．"],
                   solution=sol, meta={"a": a, "d": d, "k": k}, exam_answer=ans)


def g_arith2(rng):
    a = rng.randint(-15, 20)
    d = rng.choice([x for x in range(-7, 8) if x != 0])
    p, q = sorted(rng.sample(range(2, 16), 2))
    ap, aq = a + (p - 1) * d, a + (q - 1) * d
    ans = rf"a_n = {_an(d, a - d)}"
    st = rf"第 ${p}$ 項が ${ap}$，第 ${q}$ 項が ${aq}$ である等差数列 $\{{a_n\}}$ の一般項を求めよ．"
    sol = [rf"初項を $a$，公差を $d$ とすると，$a + {p - 1}d = {ap}$，$a + {q - 1}d = {aq}$．",
           rf"辺々引くと ${q - p}d = {aq - ap}$ より $d = {d}$．これを代入して $a = {a}$．",
           rf"よって $a_n = {a} + (n - 1)\cdot{tx(d, True)} = {_an(d, a - d)}$．"]
    alts = [(rf"a_n = {_an(d, a)}", r"一般項は $a_n = a + (n - 1)d$ である．"),
            (rf"a_n = {_an(-d, a + d)}", "公差の符号を確かめよう(後ろの項から前の項を引く)．"),
            (rf"a_n = {_an(d, ap - d)}", r"第 $p$ 項の値は初項ではない．$a + (p-1)d$ とおこう．")]
    return Problem("等差数列(2つの項から一般項)", "標準", st, fill_choices(ans, alts, [], rng),
                   hints=["初項 $a$，公差 $d$ とおいて連立方程式をつくる．"],
                   solution=sol, meta={"a": a, "d": d, "p": p, "q": q}, exam_answer=ans)


# ======================================================================
#  等比数列の一般項
# ======================================================================
RATIOS = [F(2), F(3), F(-2), F(-3), F(1, 2), F(-1, 2), F(1, 3)]


def g_geo(rng):
    a = F(rng.choice([1, 2, 3, 5, -1, -2, -3, 4]))
    r = rng.choice(RATIOS)
    k = rng.randint(4, 7)
    ak = a * r ** (k - 1)
    pair = lambda t, v: rf"a_n = {t},\ a_{{{k}}} = {tx(v)}"
    ans = pair(geo_term_tex(a, r), ak)
    st = rf"初項 ${tx(a)}$，公比 ${tx(r)}$ の等比数列 $\{{a_n\}}$ の一般項 $a_n$ と第 ${k}$ 項 $a_{{{k}}}$ を求めよ．"
    sol = [rf"等比数列の一般項は $a_n = ar^{{n-1}}$ であるから，$a_n = {geo_term_tex(a, r)}$．",
           rf"$a_{{{k}}} = {geo_term_tex(a, r, str(k - 1))} = {tx(ak)}$．"]
    alts = [(pair(geo_term_tex(a, r, "n"), a * r ** k), r"一般項は $a_n = ar^{n-1}$ である($r^n$ ではない)．"),
            ((pair(geo_term_tex(r, a), r * a ** (k - 1)) if abs(a) != 1
              else pair(geo_term_tex(a, 1 / r), a / r ** (k - 1))), "初項と公比を確かめよう．"),
            (pair(geo_term_tex(-a, r), -ak), "符号を確かめよう．"),
            (pair(geo_term_tex(a, r), a * r ** k), r"第 $k$ 項は $ar^{k-1}$ である．")]
    return Problem("等比数列の一般項", "基本", st, fill_choices(ans, alts, [], rng),
                   hints=[r"等比数列の一般項は $a_n = ar^{n-1}$．"],
                   solution=sol, meta={"a": a, "r": r, "k": k, "ak": ak}, exam_answer=ans)


def g_geo2(rng):
    a = F(rng.choice([1, 2, 3, -1, -2, 4, 5]))
    r = rng.choice([F(2), F(3), F(-2), F(-3), F(1, 2), F(-1, 2)])
    p = rng.choice([2, 3])
    q = p + 3
    ap, aq = a * r ** (p - 1), a * r ** (q - 1)
    ans = rf"a_n = {geo_term_tex(a, r)}"
    st = (rf"第 ${p}$ 項が ${tx(ap)}$，第 ${q}$ 項が ${tx(aq)}$ である等比数列 $\{{a_n\}}$ の一般項を求めよ．"
          r"ただし，公比は実数とする．")
    sol = [rf"初項を $a$，公比を $r$ とすると，$ar^{{{p - 1}}} = {tx(ap)}$，$ar^{{{q - 1}}} = {tx(aq)}$．".replace("r^{1}", "r"),
           rf"辺々割ると $r^3 = {tx(r ** 3)}$．$r$ は実数であるから $r = {tx(r)}$．"
           rf"これを代入して $a = {tx(a)}$．",
           rf"よって $a_n = {geo_term_tex(a, r)}$．"]
    alts = [(rf"a_n = {geo_term_tex(ap, r)}", r"第 $p$ 項の値は初項ではない．$ar^{p-1}$ とおこう．"),
            (rf"a_n = {geo_term_tex(a * r, r)}", "初項を求めるときの計算を確かめよう．"),
            (rf"a_n = {geo_term_tex(a, -r)}", r"$r^3$ の符号から $r$ の符号が決まる．"),
            (rf"a_n = {geo_term_tex(a, r, 'n')}", r"一般項は $ar^{n-1}$ である．")]
    return Problem("等比数列(2つの項から一般項)", "標準", st, fill_choices(ans, alts, [], rng),
                   hints=["初項 $a$，公比 $r$ とおき，2つの式を辺々割る．"],
                   solution=sol, meta={"a": a, "r": r, "p": p, "q": q}, exam_answer=ans)


# ======================================================================
#  等差数列・等比数列の和
# ======================================================================
def g_arith_sum(rng):
    kind = rng.choice(["and", "last", "mod"])
    if kind == "and":
        a = rng.randint(-10, 15)
        d = rng.choice([x for x in range(-5, 7) if x != 0])
        n = rng.randint(8, 30)
        l = a + (n - 1) * d
        st = rf"初項 ${a}$，公差 ${d}$，項数 ${n}$ の等差数列の和を求めよ．"
        pre = []
    elif kind == "last":
        a = rng.randint(-5, 15)
        d = rng.choice([2, 3, 4, 5, 6, 7])
        n = rng.randint(8, 25)
        l = a + (n - 1) * d
        st = rf"等差数列 ${a},\ {a + d},\ {a + 2 * d},\ \cdots,\ {l}$ の和を求めよ．"
        pre = [rf"公差は ${d}$．${l}$ が第 $n$ 項とすると $ {a} + (n - 1)\cdot {d} = {l}$ より $n = {n}$．"]
    else:
        m = rng.choice([3, 4, 5, 6, 7])
        r0 = rng.randint(0, m - 1)
        N = rng.choice([50, 100, 100, 200])
        a = r0 if r0 > 0 else m
        l = max(x for x in range(1, N + 1) if x % m == r0)
        d = m
        n = (l - a) // d + 1
        word = f"{m} で割ると {r0} 余る数" if r0 else f"{m} の倍数"
        st = rf"$1$ から ${N}$ までの自然数のうち，{word}の和を求めよ．"
        pre = [rf"求める数は ${a},\ {a + d},\ \cdots,\ {l}$ であり，初項 ${a}$，公差 ${d}$ の等差数列である．"
               rf"${l} = {a} + (n - 1)\cdot {d}$ より項数は $n = {n}$．"]
    S = F(n * (a + l), 2)
    sol = pre + [rf"等差数列の和の公式 $S_n = \dfrac{{n(a + l)}}{{2}}$ より，"
                 rf"$S = \dfrac{{{n}({a} + {tx(l, True)})}}{{2}} = {tx(S)}$．"]
    alts = [(tx(2 * S), r"和の公式 $S_n = \dfrac{n(a+l)}{2}$ の $\dfrac{1}{2}$ を忘れていないか．"),
            (tx(F((n - 1) * (a + l - d), 2)), "項数を確かめよう．"),
            (tx(F((n + 1) * (a + l + d), 2)), "項数を確かめよう．"),
            (tx(S + l), "最後の項を2回数えていないか．")]
    return Problem("等差数列の和", "基本", st, fill_choices(tx(S), alts, [], rng),
                   hints=[r"等差数列の和は $S_n = \dfrac{n(a + l)}{2} = \dfrac{n\{2a + (n-1)d\}}{2}$．",
                          "項数 $n$ を先に求める．"],
                   solution=sol, meta={"a": a, "d": d, "n": n, "S": S}, exam_answer=tx(S))


def g_geo_sum(rng):
    kind = rng.choice(["num", "num", "sym"])
    if kind == "num":
        a = F(rng.choice([1, 2, 3, 5, -1, -2, 4]))
        r = rng.choice([F(2), F(3), F(-2), F(-3), F(1, 2)])
        n = rng.randint(5, 8)
        S = a * (r ** n - 1) / (r - 1)
        st = rf"初項 ${tx(a)}$，公比 ${tx(r)}$，項数 ${n}$ の等比数列の和を求めよ．"
        sol = [rf"等比数列の和の公式 $S_n = \dfrac{{a(r^n - 1)}}{{r - 1}}$ より，"
               "$S = \\dfrac{" + tx(a, True) + r"\left\{" + pow_tex(r, n) + r" - 1\right\}}{" + tx(r, True)
               + " - 1} = " + tx(S) + "$．"]
        alts = [(tx(a * (r ** (n + 1) - 1) / (r - 1)), "項数を確かめよう(公比の指数は項数 $n$)．"),
                (tx(a * (r ** (n - 1) - 1) / (r - 1)), "項数を確かめよう．"),
                (tx((r ** n - 1) / (r - 1)), "初項 $a$ を掛けるのを忘れていないか．"),
                (tx(a * r ** (n - 1)), "それは第 $n$ 項である．和を求めよう．")]
        return Problem("等比数列の和", "基本", st, fill_choices(tx(S), alts, [], rng),
                       hints=[r"$S_n = \dfrac{a(r^n - 1)}{r - 1} = \dfrac{a(1 - r^n)}{1 - r}$($r \neq 1$)．"],
                       solution=sol, meta={"kind": kind, "a": a, "r": r, "n": n, "S": S}, exam_answer=tx(S))
    a = rng.choice([1, 2, 3])
    r = rng.choice([2, 3, 4])
    if a == 1:
        st = rf"$ 1 + {r} + {r}^2 + \cdots + {r}^{{n-1}}$ を求めよ．"
    else:
        st = rf"$ {a} + {a}\cdot {r} + {a}\cdot {r}^2 + \cdots + {a}\cdot {r}^{{n-1}}$ を求めよ．"

    def form(e, den=None):
        """a(r^e - 1)/(r - 1) をできるだけ簡単に"""
        den = r - 1 if den is None else den
        k = F(a, den)
        core = rf"{r}^{{{e}}} - 1" if e != "n" else rf"{r}^n - 1"
        if k == 1:
            return core
        if k.denominator == 1:
            return rf"{k}({core})"
        num = core if k.numerator == 1 else rf"{k.numerator}({core})"
        return rf"\frac{{{num}}}{{{k.denominator}}}"

    ans = form("n")
    num = f"{r}^n - 1" if a == 1 else f"{a}({r}^n - 1)"
    sol = [rf"初項 ${a}$，公比 ${r}$，項数 $n$ の等比数列の和であるから，$\dfrac{{{num}}}{{{r} - 1}} = {ans}$．"]
    alts = [(form("n+1"), r"項数は $n$ である(最後の項の指数は $n-1$)．"),
            (form("n-1"), r"項数は $n$ である．"),
            (form("n", den=r), r"分母は $r - 1$ である．")]
    alts = [(t_, w) for t_, w in alts if t_ != ans]
    return Problem("等比数列の和", "基本", st, fill_choices(ans, alts, [(rf"{r}^n", "和の公式を使おう．")], rng),
                   hints=[r"$S_n = \dfrac{a(r^n - 1)}{r - 1}$．項数を数えよう．"],
                   solution=sol, meta={"kind": kind, "a": a, "r": r}, exam_answer=ans)


# ======================================================================
#  Σ の計算
# ======================================================================
def _sigma_poly(p, q, c):
    """Σ_{k=1}^n (p k^2 + q k + c) の n の多項式の係数"""
    # Σk^2 = n^3/3 + n^2/2 + n/6, Σk = n^2/2 + n/2, Σ1 = n
    return [F(0), p * F(1, 6) + q * F(1, 2) + c, p * F(1, 2) + q * F(1, 2), p * F(1, 3)]


def g_sigma(rng):
    p = rng.choice([0, 0, 1, 2, 3])
    q = rng.choice([x for x in range(-4, 6) if x != 0 or p != 0])
    c = rng.randint(-3, 4)
    if p == 0 and q == 0:
        raise Retry
    body = npoly([c, q, p], "k")
    numeric = rng.random() < 0.3
    co = _sigma_poly(p, q, c)
    if numeric:
        N = rng.choice([10, 15, 20])
        val = peval(co, N)
        st = rf"$\displaystyle \sum_{{k=1}}^{{{N}}} ({body})$ の値を求めよ．"
        ans = tx(val)
        sol = [rf"$\displaystyle \sum_{{k=1}}^{{n}} ({body}) = {factor_tex(co)}$ に $n = {N}$ を代入して ${ans}$．"]
        alts = [(tx(peval(_sigma_poly(p, q, 0), N) + c), r"$\displaystyle\sum_{k=1}^{n} c = cn$ である(定数も $n$ 個たす)．"),
                (tx(peval(co, N - 1)), "項数を確かめよう．"),
                (tx(peval(co, N + 1)), "項数を確かめよう．")]
        return Problem("Σ の計算(値)", "基本", st, fill_choices(ans, alts, [], rng),
                       hints=[r"$\displaystyle\sum_{k=1}^{n} k = \frac{1}{2}n(n+1)$，$\displaystyle\sum_{k=1}^{n} k^2 = \frac{1}{6}n(n+1)(2n+1)$，"
                              r"$\displaystyle\sum_{k=1}^{n} c = cn$．"],
                       solution=sol, meta={"p": p, "q": q, "c": c, "N": N, "val": val}, exam_answer=ans)
    ans = factor_tex(co)
    st = rf"$\displaystyle \sum_{{k=1}}^{{n}} ({body})$ を求めよ．"
    sol = [r"$\displaystyle\sum_{k=1}^{n} k = \frac{1}{2}n(n+1)$，$\displaystyle\sum_{k=1}^{n} k^2 = \frac{1}{6}n(n+1)(2n+1)$，"
           r"$\displaystyle\sum_{k=1}^{n} 1 = n$ を使う．",
           rf"$\displaystyle \sum_{{k=1}}^{{n}} ({body}) = {npoly(co)} = {ans}$．"]
    co_c = _sigma_poly(p, q, 0)
    co_c[0] += c
    wrong_k = [F(0), p * F(1, 6) - q * F(1, 2) + c, p * F(1, 2) + q * F(1, 2), p * F(1, 3)]   # Σk = n(n-1)/2 の誤り
    alts = [(factor_tex(co_c), r"$\displaystyle\sum_{k=1}^{n} c = cn$ である(定数も $n$ 個たす)．"),
            (factor_tex(wrong_k), r"$\displaystyle\sum_{k=1}^{n} k = \frac{1}{2}n(n+1)$ である．"),
            (factor_tex([x * 2 for x in co]), r"公式の $\frac{1}{2}$，$\frac{1}{6}$ を確かめよう．"),
            (factor_tex([F(0), p * F(1, 3) + q * F(1, 2) + c, p * F(1, 2) + q * F(1, 2), p * F(2, 3)]),
             r"$\displaystyle\sum_{k=1}^{n} k^2 = \frac{1}{6}n(n+1)(2n+1)$ である．")]
    return Problem("Σ の計算", "標準", st, fill_choices(ans, alts, [], rng),
                   hints=[r"$\displaystyle\sum (pa_k + qb_k) = p\sum a_k + q\sum b_k$ と分ける．",
                          r"$\displaystyle\sum_{k=1}^{n} k = \frac{1}{2}n(n+1)$，$\displaystyle\sum_{k=1}^{n} k^2 = \frac{1}{6}n(n+1)(2n+1)$．"],
                   solution=sol, meta={"p": p, "q": q, "c": c, "co": co}, exam_answer=ans)


# ======================================================================
#  階差数列
# ======================================================================
def g_diff_seq(rng):
    a1 = rng.randint(-3, 6)
    p = rng.choice([1, 2, 3, 4])
    q = rng.randint(-3, 3)
    b = lambda k: p * k + q
    seq = [a1]
    for k in range(1, 6):
        seq.append(seq[-1] + b(k))
    # a_n = a1 + Σ_{k=1}^{n-1}(pk + q) = a1 + p(n-1)n/2 + q(n-1)
    co = [F(a1) - q, F(-p, 2) + q, F(p, 2)]
    ans = rf"a_n = {npoly(co)}"
    btex = npoly([q, p])
    st = rf"数列 $ {_terms(seq)} $ の一般項 $a_n$ を求めよ．"
    sol = [rf"階差数列 $\{{b_n\}}$ は $ {_terms([b(k) for k in range(1, 6)])} $ で，初項 ${b(1)}$，公差 ${p}$ の等差数列であるから $b_n = {btex}$．",
           rf"$n \geqq 2$ のとき $\displaystyle a_n = a_1 + \sum_{{k=1}}^{{n-1}} b_k = {a1} + \sum_{{k=1}}^{{n-1}}({npoly([q, p], 'k')})"
           rf" = {a1} + {p}\cdot\frac{{1}}{{2}}(n-1)n {'+' if q >= 0 else '-'} {abs(q)}(n - 1) = {npoly(co)}$．"
           .replace(r" + 0(n - 1)", "").replace(r" 1(n - 1)", r" (n - 1)").replace(r"+ 1\cdot\frac", r"+ \frac"),
           rf"$a_1 = {a1}$ であるから，この式は $n = 1$ のときも成り立つ．よって ${ans}$．"]
    wrong1 = [F(a1), F(p, 2) + q, F(p, 2)]          # Σ を n まで
    wrong2 = [F(-q), F(-p, 2) + q, F(p, 2)]        # a1 を忘れる
    wrong3 = [F(a1 - b(1)), F(b(1)), F(0)]
    alts = [(rf"a_n = {npoly(wrong1)}", r"$a_n = a_1 + \displaystyle\sum_{k=1}^{n-1} b_k$ である(和は $n-1$ まで)．"),
            (rf"a_n = {npoly(wrong2)}", "初項 $a_1$ を加えるのを忘れていないか．"),
            (rf"a_n = {npoly(wrong3)}", "隣どうしの差が一定ではないので，等差数列ではない．階差数列を考えよう．")]
    return Problem("階差数列", "標準", st, fill_choices(ans, alts, [], rng),
                   hints=["隣どうしの差(階差数列)を調べる．",
                          r"$n \geqq 2$ のとき $a_n = a_1 + \displaystyle\sum_{k=1}^{n-1} b_k$．$n = 1$ のときも確かめる．"],
                   solution=sol, meta={"seq": seq, "co": co}, exam_answer=ans)


REGISTRY = [
    ProblemType("s1_arith", "等差数列の一般項", "基本", g_arith, intro=INTRO, points=5, height=1 / 3, unit="等差数列"),
    ProblemType("s1_arith2", "等差数列(2つの項から一般項)", "標準", g_arith2, intro=INTRO, points=5, height=1 / 3,
                unit="等差数列"),
    ProblemType("s1_geo", "等比数列の一般項", "基本", g_geo, intro=INTRO, points=5, height=1 / 3, unit="等比数列"),
    ProblemType("s1_geo2", "等比数列(2つの項から一般項)", "標準", g_geo2, intro=INTRO, points=5, height=1 / 3,
                unit="等比数列"),
    ProblemType("s1_arith_sum", "等差数列の和", "基本", g_arith_sum, intro=INTRO, points=5, height=1 / 3,
                unit="等差数列の和"),
    ProblemType("s1_geo_sum", "等比数列の和", "基本", g_geo_sum, intro=INTRO, points=5, height=1 / 3, unit="等比数列の和"),
    ProblemType("s1_sigma", "Σ の計算", "標準", g_sigma, intro=INTRO, points=5, height=1 / 3, unit="一般の数列(Σ)"),
    ProblemType("s1_diff_seq", "階差数列", "標準", g_diff_seq, intro=INTRO, points=5, height=1 / 2, unit="一般の数列(階差数列)"),
]
