"""数列 第2章(後期期末の範囲):漸化式と数学的帰納法"""
from fractions import Fraction as F

from .ex_core import Problem, ProblemType, Retry, fill_choices
from .radicals import tx
from .seq_common import factor_tex, geo_term_tex, npoly, peval

INTRO = "次の問いに答えよ．"


def _rec_tex(p, q, extra=None):
    """a_{n+1} = p a_n + q(extra があれば + extra)"""
    head = r"a_{n+1} = " + ("" if p == 1 else ("-" if p == -1 else tx(p))) + "a_n"
    if extra:
        head += " + " + extra if not extra.startswith("-") else " - " + extra[1:]
    if q:
        head += f" {'+' if q > 0 else '-'} {tx(abs(q))}"
    return head


def _cond(a1, rec):
    return rf"$a_1 = {tx(a1)}$，$ {rec} $ $(n = 1,\ 2,\ 3,\ \cdots)$"


# ======================================================================
#  漸化式で定まる数列の項
# ======================================================================
def g_rec_terms(rng):
    kind = rng.choice(["lin", "lin", "add"])
    a1 = rng.randint(-3, 5)
    k = rng.choice([4, 5])
    if kind == "lin":
        p = rng.choice([2, 3, -2, -1])
        q = rng.randint(-4, 4)
        rec = _rec_tex(p, q)
        f = lambda n, x: p * x + q
    else:
        s, t = rng.choice([1, 2, 3]), rng.randint(-2, 3)
        rec = _rec_tex(1, 0, extra=npoly([t, s]))
        f = lambda n, x: x + s * n + t
    seq = [F(a1)]
    for n in range(1, k + 2):
        seq.append(f(n, seq[-1]))
    ans = tx(seq[k - 1])
    st = rf"{_cond(a1, rec)} で定められる数列 $\{{a_n\}}$ の第 ${k}$ 項 $a_{k}$ を求めよ．"
    steps = []
    for n in range(1, k):
        steps.append(rf"a_{{{n + 1}}} = {tx(seq[n])}")
    sol = [rf"$n = 1,\ 2,\ \cdots$ を順に代入すると，$ {r',\ '.join(steps)} $．よって $a_{k} = {ans}$．"]
    alts = [(tx(seq[k - 2]), "求める項の番号を確かめよう．"),
            (tx(seq[k]), "求める項の番号を確かめよう．"),
            (tx(-seq[k - 1]) if seq[k - 1] != 0 else tx(seq[k - 1] + 1), "計算を確かめよう．")]
    return Problem("漸化式と項", "基本", st, fill_choices(ans, alts, [(tx(seq[k - 1] + 2), "計算を確かめよう．")], rng),
                   hints=[r"$n = 1$ を代入すると $a_2$，$n = 2$ を代入すると $a_3$，… と順に求まる．"],
                   solution=sol, meta={"seq": seq, "k": k}, exam_answer=ans)


# ======================================================================
#  等差型・等比型
# ======================================================================
def g_rec_arith_geo(rng):
    a1 = rng.choice([x for x in range(-5, 8) if x != 0])
    if rng.random() < 0.5:
        d = rng.choice([x for x in range(-5, 7) if x != 0])
        rec = _rec_tex(1, d)
        gen = npoly([a1 - d, d])
        st = rf"{_cond(a1, rec)} で定められる数列 $\{{a_n\}}$ の一般項を求めよ．"
        sol = [rf"$a_{{n+1}} - a_n = {d}$ より，数列 $\{{a_n\}}$ は初項 ${a1}$，公差 ${d}$ の等差数列である．",
               rf"よって $a_n = {a1} + (n - 1)\cdot{tx(d, True)} = {gen}$．"]
        alts = [(rf"a_n = {npoly([a1, d])}", r"一般項は $a_n = a_1 + (n - 1)d$ である．"),
                (rf"a_n = {npoly([d - a1, a1])}", "初項と公差が入れかわっていないか．"),
                (rf"a_n = {geo_term_tex(a1, d)}" if d not in (0, 1) else rf"a_n = {npoly([a1 + d, d])}",
                 r"$a_{n+1} = a_n + d$ は等差数列(差が一定)である．")]
        meta = {"kind": "arith", "a1": a1, "d": d}
    else:
        r = rng.choice([2, 3, -2, -3, F(1, 2)])
        rec = _rec_tex(r, 0)
        gen = geo_term_tex(a1, r)
        st = rf"{_cond(a1, rec)} で定められる数列 $\{{a_n\}}$ の一般項を求めよ．"
        sol = [rf"数列 $\{{a_n\}}$ は初項 ${a1}$，公比 ${tx(r)}$ の等比数列である．よって $a_n = {gen}$．"]
        alts = [(rf"a_n = {geo_term_tex(a1, r, 'n')}", r"一般項は $a_n = a_1 r^{n-1}$ である．"),
                (rf"a_n = {npoly([a1 - r, r])}", r"$a_{n+1} = ra_n$ は等比数列(比が一定)である．"),
                (rf"a_n = {geo_term_tex(r, a1)}" if abs(a1) != 1 else rf"a_n = {geo_term_tex(-a1, r)}",
                 "初項と公比を確かめよう．")]
        meta = {"kind": "geo", "a1": a1, "r": r}
    ans = rf"a_n = {gen}"
    return Problem("漸化式(等差型・等比型)", "基本", st, fill_choices(ans, alts, [], rng),
                   hints=[r"$a_{n+1} = a_n + d$ は等差数列，$a_{n+1} = ra_n$ は等比数列．"],
                   solution=sol, meta=meta, exam_answer=ans)


# ======================================================================
#  a_{n+1} = p a_n + q 型
# ======================================================================
def g_rec_linear(rng):
    p = rng.choice([2, 3, -2, 4, F(1, 2), -1])
    al = rng.choice([x for x in range(-4, 5) if x != 0])
    q = al * (1 - p)
    a1 = rng.choice([x for x in range(-3, 7) if x != al])
    if q == 0:
        raise Retry
    rec = _rec_tex(p, q)
    c = a1 - al
    gen = geo_term_tex(c, p) + (f" {'+' if al > 0 else '-'} {abs(al)}")
    st = rf"{_cond(a1, rec)} で定められる数列 $\{{a_n\}}$ の一般項を求めよ．"
    sol = [rf"$\alpha = {tx(p)}\alpha {'+' if q > 0 else '-'} {tx(abs(q))}$ を解くと $\alpha = {al}$．"
           .replace(r"= 1\alpha", r"= \alpha").replace(r"= -1\alpha", r"= -\alpha"),
           rf"漸化式は $a_{{n+1}} {'-' if al > 0 else '+'} {abs(al)} = {tx(p) if p not in (1, -1) else ('-' if p == -1 else '')}"
           rf"(a_n {'-' if al > 0 else '+'} {abs(al)})$ と変形できる．",
           rf"数列 $\{{a_n {'-' if al > 0 else '+'} {abs(al)}\}}$ は初項 $a_1 {'-' if al > 0 else '+'} {abs(al)} = {tx(c)}$，"
           rf"公比 ${tx(p)}$ の等比数列であるから $a_n {'-' if al > 0 else '+'} {abs(al)} = {geo_term_tex(c, p)}$．",
           rf"よって $a_n = {gen}$．"]
    sgn = lambda x: f" {'+' if x > 0 else '-'} {abs(x)}"
    alts = [(rf"a_n = {geo_term_tex(a1 + al, p)}{sgn(-al)}", r"$a_n - \alpha$ の形に変形するときの符号を確かめよう．"),
            (rf"a_n = {geo_term_tex(c, p, 'n')}{sgn(al)}", r"等比数列の一般項は $ar^{n-1}$ である．"),
            (rf"a_n = {geo_term_tex(a1, p)}{sgn(al)}", r"初項は $a_1 - \alpha$ である．"),
            (rf"a_n = {geo_term_tex(c, p)}{sgn(-al)}", r"$a_n = (a_n - \alpha) + \alpha$ に戻すときの符号を確かめよう．")]
    ans = rf"a_n = {gen}"
    alts = [(t_, w) for t_, w in alts if r"0\cdot" not in t_]
    return Problem("漸化式(a_{n+1} = pa_n + q 型)", "標準", st, fill_choices(ans, alts, [], rng),
                   hints=[r"$\alpha = p\alpha + q$ を満たす $\alpha$ を求める．",
                          r"$a_{n+1} - \alpha = p(a_n - \alpha)$ と変形すると，$\{a_n - \alpha\}$ は等比数列．"],
                   solution=sol, meta={"p": p, "q": q, "a1": a1, "al": al}, exam_answer=ans)


# ======================================================================
#  数学的帰納法
# ======================================================================
def _sum_template(rng):
    """等式 Σ f(k) = g(n) の証明。(左辺の tex, 右辺の係数, f の係数, 説明用の情報)"""
    kind = rng.choice(["lin", "lin", "sq", "kk1", "cube", "geo", "frac"])
    if kind == "lin":
        a = rng.choice([1, 2, 3, 4])
        b = rng.choice([x for x in range(-2, 4) if a + x > 0])
        f = [b, a]                            # ak + b
        g = [F(0), F(a + 2 * b, 2), F(a, 2)]  # n(an + a + 2b)/2
        terms = [a * k + b for k in (1, 2, 3)]
        lhs = rf"{' + '.join(map(str, terms))} + \cdots + ({npoly(f)})"
        return kind, lhs, f, g
    if kind == "sq":
        return kind, r"1^2 + 2^2 + 3^2 + \cdots + n^2", [0, 0, 1], [F(0), F(1, 6), F(1, 2), F(1, 3)]
    if kind == "kk1":
        return kind, r"1\cdot 2 + 2\cdot 3 + 3\cdot 4 + \cdots + n(n + 1)", [0, 1, 1], [F(0), F(2, 3), F(1), F(1, 3)]
    if kind == "cube":
        return kind, r"1^3 + 2^3 + 3^3 + \cdots + n^3", [0, 0, 0, 1], [F(0), F(0), F(1, 4), F(1, 2), F(1, 4)]
    if kind == "geo":
        r = rng.choice([2, 3])
        return kind, rf"1 + {r} + {r}^2 + \cdots + {r}^{{n-1}}", r, None
    return kind, r"\frac{1}{1\cdot 2} + \frac{1}{2\cdot 3} + \cdots + \frac{1}{n(n+1)}", None, None


def _rhs_tex(kind, g, n="n", extra=None):
    if kind == "geo":
        r = extra
        return rf"\frac{{{r}^{{{n}}} - 1}}{{{r - 1}}}" if r != 2 else rf"2^{{{n}}} - 1"
    if kind == "frac":
        return rf"\frac{{{n}}}{{{n} + 1}}"
    if kind == "cube":
        return rf"\left\{{\frac{{1}}{{2}}{n}({n} + 1)\right\}}^2"
    return factor_tex(g, n)


def g_induction(rng):
    if rng.random() < 0.35:
        return _induction_div(rng)
    kind, lhs, f, g = _sum_template(rng)
    lhs_k = lhs.replace("n", "k")
    if kind == "geo":
        r = f
        rhs_n, rhs_k = _rhs_tex(kind, g, "n", r), _rhs_tex(kind, g, "k", r)
        rhs_k1 = _rhs_tex(kind, g, "k+1", r)
        term, term_k = rf"{r}^k", rf"{r}^{{k-1}}"
        mid = (rf"\frac{{{r}^k - 1}}{{{r - 1}}} + {r}^k = \frac{{{r}^k - 1 + {r - 1}\cdot {r}^k}}{{{r - 1}}}"
               rf" = \frac{{{r}^{{k+1}} - 1}}{{{r - 1}}}" if r != 2 else r"2^k - 1 + 2^k = 2\cdot 2^k - 1 = 2^{k+1} - 1")
        n1 = ("1", rf"\frac{{{r} - 1}}{{{r - 1}}} = 1" if r != 2 else "2^1 - 1 = 1")
    elif kind == "frac":
        rhs_n, rhs_k, rhs_k1 = r"\frac{n}{n + 1}", r"\frac{k}{k + 1}", r"\frac{k + 1}{k + 2}"
        term, term_k = r"\frac{1}{(k + 1)(k + 2)}", r"\frac{1}{k(k + 1)}"
        mid = (r"\frac{k}{k + 1} + \frac{1}{(k + 1)(k + 2)} = \frac{k(k + 2) + 1}{(k + 1)(k + 2)}"
               r" = \frac{(k + 1)^2}{(k + 1)(k + 2)} = \frac{k + 1}{k + 2}")
        n1 = (r"\frac{1}{1\cdot 2} = \frac{1}{2}", r"\frac{1}{1 + 1} = \frac{1}{2}")
    elif kind == "cube":
        rhs_n, rhs_k = _rhs_tex(kind, g, "n"), _rhs_tex(kind, g, "k")
        rhs_k1 = r"\left\{\frac{1}{2}(k + 1)(k + 2)\right\}^2"
        term, term_k = "(k + 1)^3", "k^3"
        mid = (r"\frac{1}{4}k^2(k + 1)^2 + (k + 1)^3 = \frac{1}{4}(k + 1)^2\{k^2 + 4(k + 1)\}"
               r" = \frac{1}{4}(k + 1)^2(k + 2)^2")
        n1 = ("1^3 = 1", r"\left\{\frac{1}{2}\cdot 1\cdot 2\right\}^2 = 1")
    else:
        rhs_n, rhs_k = factor_tex(g, "n"), factor_tex(g, "k")
        coeffs = _shift_poly(g, 1)
        rhs_k1 = factor_tex(coeffs, "k")
        term = {"sq": "(k + 1)^2", "kk1": "(k + 1)(k + 2)"}.get(kind, f"({npoly([f[0] + f[1], f[1]], 'k')})")
        term_k = {"sq": "k^2", "kk1": "k(k + 1)"}.get(kind, f"({npoly(f, 'k')})")
        mid = rf"{rhs_k} + {term} = {npoly(coeffs, 'k')} = {rhs_k1}"
        n1 = (tx(peval(f, 1)), tx(peval(g, 1)))
    st = rf"数学的帰納法を用いて，すべての自然数 $n$ について次の等式が成り立つことを証明せよ．$$ {lhs} = {rhs_n} $$"
    proof = [rf"[I] $n = 1$ のとき，(左辺)$= {n1[0]}$，(右辺)$= {n1[1]}$ より，等式は成り立つ．",
             rf"[II] $n = k$ のとき等式が成り立つと仮定すると，$ {lhs_k} = {rhs_k} $．",
             rf"$n = k + 1$ のとき，(左辺)$= ({lhs_k}) + {term} = {mid}$．",
             rf"これは $n = k + 1$ のときの右辺 ${rhs_k1}$ に等しいので，$n = k + 1$ のときも等式は成り立つ．",
             r"[I]，[II] より，すべての自然数 $n$ について等式は成り立つ．"]
    q = r"$n = k$ のとき等式が成り立つと仮定する．$n = k + 1$ のときの左辺を，仮定を使って表した式として正しいものはどれか．"
    ans = rf"{rhs_k} + {term}"
    alts = [(rf"{rhs_k} + {term_k}", r"$n = k + 1$ のとき，最後に加わるのは第 $k+1$ 項である．"),
            (rf"{rhs_k1} + {term}", "仮定で使うのは $n = k$ のときの右辺である．"),
            (rf"\left({rhs_k}\right)\cdot {term}", "左辺は和である．$n = k$ までの和に第 $k+1$ 項を加える．")]
    return _induction_problem(st, q, ans, alts, proof, rng, {"kind": kind, "f": f, "g": g})


def _shift_poly(g, a):
    """g(k) + f(k+1) の係数(f は呼び出し側で g(k+1) - g(k) になっている)= g(k + 1)"""
    # g(k + 1) を展開
    out = [F(0)] * len(g)
    from math import comb
    for i, c in enumerate(g):
        for j in range(i + 1):
            out[j] += F(c) * comb(i, j) * a ** (i - j)
    return out


def _induction_problem(st, q, ans, alts, proof, rng, meta):
    return Problem("数学的帰納法", "標準", st.replace("証明せよ．", "証明したい．") + "\n\n" + q,
                   fill_choices(ans, alts, [], rng),
                   hints=["[I] $n = 1$ のとき成り立つことを示す．",
                          "[II] $n = k$ のとき成り立つと仮定して，$n = k + 1$ のときも成り立つことを示す．"],
                   solution=proof, meta=meta,
                   exam_short=st, exam_answer="", exam_solution=proof)


def _induction_div(rng):
    kind = rng.choice(["pow", "pow", "cubic"])
    if kind == "pow":
        a = rng.choice([3, 4, 5, 7, 9, 11, 13])
        ms = [m for m in range(2, a) if (a - 1) % m == 0]
        m = rng.choice(ms)
        c = rng.choice([x for x in range(-1, 2 * m) if (x + 1) % m == 0])
        expr = rf"{a}^n" + (f" + {c}" if c > 0 else (f" - {-c}" if c < 0 else ""))
        exk = expr.replace("^n", "^k")
        st = rf"数学的帰納法を用いて，すべての自然数 $n$ について ${expr}$ は ${m}$ の倍数であることを証明せよ．"
        n1 = a + c
        d = c * (a - 1) // m
        step = (rf"{a}^{{k+1}}" + (f" + {c}" if c > 0 else (f" - {-c}" if c < 0 else ""))
                + rf" = {a}\cdot {a}^k" + (f" + {c}" if c > 0 else (f" - {-c}" if c < 0 else ""))
                + rf" = {a}({m}M" + (f" - {c}" if c > 0 else (f" + {-c}" if c < 0 else "")) + ")"
                + (f" + {c}" if c > 0 else (f" - {-c}" if c < 0 else ""))
                + rf" = {m}\left({a}M" + (f" - {d}" if d > 0 else (f" + {-d}" if d < 0 else "")) + r"\right)")
        proof = [rf"[I] $n = 1$ のとき，${a} {'+' if c >= 0 else '-'} {abs(c)} = {n1} = {m}\cdot {n1 // m}$ より，${m}$ の倍数である．",
                 rf"[II] $n = k$ のとき ${exk}$ が ${m}$ の倍数であると仮定すると，整数 $M$ を用いて ${exk} = {m}M$ と表せる．"
                 rf"よって ${a}^k = {m}M" + (f" - {c}" if c > 0 else (f" + {-c}" if c < 0 else "")) + "$．",
                 rf"$n = k + 1$ のとき，$ {step} $．",
                 rf"${a}M" + (f" - {d}" if d > 0 else (f" + {-d}" if d < 0 else "")) + rf"$ は整数であるから，$n = k + 1$ のときも ${m}$ の倍数である．",
                 r"[I]，[II] より，すべての自然数 $n$ について成り立つ．"]
        ans = rf"{a}\cdot {a}^k" + (f" + {c}" if c > 0 else (f" - {-c}" if c < 0 else ""))
        alts = [(rf"{a}^k + {a}" + (f" + {c}" if c > 0 else (f" - {-c}" if c < 0 else "")), r"$a^{k+1} = a\cdot a^k$ である．"),
                (rf"({a}^k" + (f" + {c}" if c > 0 else (f" - {-c}" if c < 0 else "")) + rf")^{{{a}}}" , r"$a^{k+1} = a\cdot a^k$ である．"),
                (rf"{a + 1}\cdot {a}^k" + (f" + {c}" if c > 0 else (f" - {-c}" if c < 0 else "")), r"$a^{k+1} = a\cdot a^k$ である．")]
        q = rf"$n = k + 1$ のとき ${a}^{{k+1}}" + (f" + {c}" if c > 0 else (f" - {-c}" if c < 0 else "")) + "$ を変形した式として正しいものはどれか．"
        meta = {"kind": "pow", "a": a, "m": m, "c": c}
    else:
        st = r"数学的帰納法を用いて，すべての自然数 $n$ について $n^3 + 2n$ は $3$ の倍数であることを証明せよ．"
        proof = [r"[I] $n = 1$ のとき，$1 + 2 = 3$ より，$3$ の倍数である．",
                 r"[II] $n = k$ のとき $k^3 + 2k$ が $3$ の倍数であると仮定すると，整数 $M$ を用いて $k^3 + 2k = 3M$ と表せる．",
                 r"$n = k + 1$ のとき，$(k + 1)^3 + 2(k + 1) = k^3 + 3k^2 + 3k + 1 + 2k + 2 = (k^3 + 2k) + 3(k^2 + k + 1)"
                 r" = 3(M + k^2 + k + 1)$．",
                 r"$M + k^2 + k + 1$ は整数であるから，$n = k + 1$ のときも $3$ の倍数である．",
                 r"[I]，[II] より，すべての自然数 $n$ について成り立つ．"]
        ans = r"(k^3 + 2k) + 3(k^2 + k + 1)"
        alts = [(r"(k^3 + 2k) + 3(k^2 + k)", "展開の定数項を確かめよう．"),
                (r"(k^3 + 2k) + (k^2 + k + 1)", r"$(k+1)^3 = k^3 + 3k^2 + 3k + 1$ である．"),
                (r"(k^3 + 2k) + 3k^2 + 1", r"$(k+1)^3 + 2(k+1)$ を正しく展開しよう．")]
        q = r"$n = k + 1$ のとき $(k + 1)^3 + 2(k + 1)$ を変形した式として正しいものはどれか．"
        meta = {"kind": "cubic"}
    return _induction_problem(st, q, ans, alts, proof, rng, meta)


REGISTRY = [
    ProblemType("s2_rec_terms", "漸化式と項", "基本", g_rec_terms, intro=INTRO, points=5, height=1 / 3,
                unit="漸化式"),
    ProblemType("s2_rec_arith_geo", "漸化式(等差型・等比型)", "基本", g_rec_arith_geo, intro=INTRO, points=5,
                height=1 / 3, unit="漸化式"),
    ProblemType("s2_rec_linear", "漸化式(a_{n+1} = pa_n + q 型)", "標準", g_rec_linear, intro=INTRO, points=5,
                height=1 / 2, unit="漸化式"),
    ProblemType("s2_induction", "数学的帰納法", "標準", g_induction, intro="", points=10, height=1 / 2,
                unit="数学的帰納法"),
]
