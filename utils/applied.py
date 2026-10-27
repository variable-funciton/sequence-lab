"""応用ページ（物理・学科別）の計算。Streamlit に依存しない純粋な関数。

テスト: python -m tests.test_applied
"""

from __future__ import annotations

import math
from fractions import Fraction

G = 9.8  # 重力加速度 [m/s²]


# =====================================================================
# 共通：漸化式 x_{n+1} = p x_n + q
# =====================================================================
def linear_recurrence(x0, p, q, N: int) -> list:
    """x_0, …, x_N"""
    out = [x0]
    for _ in range(N):
        out.append(p * out[-1] + q)
    return out


def linear_fixed_point(p, q):
    """α = pα + q の解（p = 1 なら None）"""
    return None if p == 1 else q / (1 - p)


def linear_closed_form(x0, p, q, n: int):
    """一般項 x_n = α + p^n (x_0 − α)（p = 1 なら x_0 + nq）"""
    if p == 1:
        return x0 + n * q
    a = q / (1 - p)
    return a + p ** n * (x0 - a)


def first_index(seq, cond):
    """cond(x) が初めて成り立つ番号（なければ None）"""
    for i, x in enumerate(seq):
        if cond(x):
            return i
    return None


# =====================================================================
# 物理：ボールの跳ね返り（反発係数 e）
# =====================================================================
def bounce_heights(h0: float, e: float, N: int) -> list[float]:
    """h_0（最初の高さ）, h_1, …, h_N。h_n = h_0 e^{2n}（速さが e 倍 → 高さは e² 倍）"""
    return [h0 * e ** (2 * n) for n in range(N + 1)]


def bounce_total_distance(h0: float, e: float, N: int | None = None) -> float:
    """N 回はね返るまで（N = None なら止まるまで）に動く道のり。
    h_0 + 2(h_1 + h_2 + … + h_N)。無限等比級数の和は h_0 (1 + e²)/(1 − e²)"""
    r = e * e
    if N is None:
        return h0 * (1 + r) / (1 - r) if r < 1 else math.inf
    return h0 + 2 * sum(h0 * r ** n for n in range(1, N + 1))


def bounce_total_time(h0: float, e: float, N: int | None = None, g: float = G) -> float:
    """最初に落ちるまでの時間 t_0 = √(2h_0/g)。n 回目にはね返ってから次に着地するまで 2 t_0 eⁿ。
    止まるまでの時間は t_0 + 2 t_0 (e + e² + …) = t_0 (1 + e)/(1 − e)"""
    t0 = math.sqrt(2 * h0 / g)
    if N is None:
        return t0 * (1 + e) / (1 - e) if e < 1 else math.inf
    return t0 + 2 * t0 * sum(e ** n for n in range(1, N + 1))


def bounce_path(h0: float, e: float, N: int, g: float = G, pts: int = 40):
    """時刻と高さの点列（N 回目のはね返りの後の着地まで）"""
    t0 = math.sqrt(2 * h0 / g)
    ts, ys = [], []
    for i in range(pts + 1):            # 最初の落下
        t = t0 * i / pts
        ts.append(t); ys.append(h0 - 0.5 * g * t * t)
    T = t0
    for n in range(1, N + 1):
        v = g * t0 * e ** n             # はね返った直後の速さ
        dur = 2 * v / g
        for i in range(1, pts + 1):
            t = dur * i / pts
            ts.append(T + t); ys.append(max(0.0, v * t - 0.5 * g * t * t))
        T += dur
    return ts, ys


# =====================================================================
# 機械：標準数（ルナール数列）
# =====================================================================
RENARD = {
    "R5": [1.00, 1.60, 2.50, 4.00, 6.30],
    "R10": [1.00, 1.25, 1.60, 2.00, 2.50, 3.15, 4.00, 5.00, 6.30, 8.00],
    "R20": [1.00, 1.12, 1.25, 1.40, 1.60, 1.80, 2.00, 2.24, 2.50, 2.80,
            3.15, 3.55, 4.00, 4.50, 5.00, 5.60, 6.30, 7.10, 8.00, 9.00],
    "R40": [1.00, 1.06, 1.12, 1.18, 1.25, 1.32, 1.40, 1.50, 1.60, 1.70,
            1.80, 1.90, 2.00, 2.12, 2.24, 2.36, 2.50, 2.65, 2.80, 3.00,
            3.15, 3.35, 3.55, 3.75, 4.00, 4.25, 4.50, 4.75, 5.00, 5.30,
            5.60, 6.00, 6.30, 6.70, 7.10, 7.50, 8.00, 8.50, 9.00, 9.50],
}


def series_n(name: str) -> int:
    """'R10' → 10、'E24' → 24"""
    return int(name[1:])


def theoretical(n: int, decades: int = 1) -> list[float]:
    """公比 10^{1/n} の等比数列 1, 10^{1/n}, …（decades 桁分）"""
    return [10 ** (k / n) for k in range(n * decades)]


def nearest(values: list[float], x: float):
    """x に最も近い値（桁をまたいで探す）と相対誤差。values は 1〜10 の 1 桁分"""
    if x <= 0:
        raise ValueError("x must be positive")
    e = math.floor(math.log10(x))
    cands = [v * 10 ** k for k in (e - 1, e, e + 1) for v in values]
    best = min(cands, key=lambda v: abs(math.log(v / x)))
    return best, (best - x) / x


# =====================================================================
# 機械：減衰振動
# =====================================================================
def viscous_peaks(A0: float, r: float, N: int) -> list[float]:
    """粘性減衰：1 周期ごとに振幅が r 倍（等比数列）"""
    return [A0 * r ** n for n in range(N + 1)]


def friction_peaks(A0: float, d: float, N: int) -> list[float]:
    """摩擦（クーロン摩擦）：1 周期ごとに振幅が d ずつ減る（等差数列）。0 より小さくはならない"""
    return [max(0.0, A0 - d * n) for n in range(N + 1)]


def periods_below(A0: float, r: float, ratio: float) -> int | None:
    """振幅が A0 × ratio 以下になる最初の周期 n（r^n ≤ ratio）"""
    if not 0 < r < 1:
        return None
    n = 0
    a = A0
    while a > A0 * ratio + 1e-12:
        a *= r; n += 1
    return n


def log_decrement(r: float) -> float:
    """対数減衰率 δ = ln(x_n / x_{n+1}) = −ln r"""
    return -math.log(r)


def viscous_curve(A0: float, r: float, T: float, cycles: float, pts: int = 600):
    """x(t) = A0 r^{t/T} cos(2πt/T)"""
    ts = [cycles * T * i / pts for i in range(pts + 1)]
    return ts, [A0 * r ** (t / T) * math.cos(2 * math.pi * t / T) for t in ts]


def friction_curve(A0: float, d: float, T: float, cycles: float, pts_half: int = 40):
    """クーロン摩擦のある振動。半周期ごとに中心が ±Δ（Δ = d/4）に移り、振幅が 2Δ ずつ減る。
    |位置| ≤ Δ で止まった所で止まる"""
    D = d / 4
    ts, xs = [0.0], [A0]
    s, t = A0, 0.0
    half = T / 2
    while t < cycles * T - 1e-9:
        if abs(s) <= D + 1e-12:          # 静止摩擦で止まる
            ts.append(cycles * T); xs.append(s)
            break
        c = D if s > 0 else -D
        for i in range(1, pts_half + 1):
            tau = half * i / pts_half
            ts.append(t + tau); xs.append(c + (s - c) * math.cos(math.pi * tau / half))
        s = 2 * c - s
        t += half
    return ts, xs


# =====================================================================
# 電気：E 系列
# =====================================================================
E_SERIES = {
    "E6": [1.0, 1.5, 2.2, 3.3, 4.7, 6.8],
    "E12": [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2],
    "E24": [1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
            3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1],
}
E_TOL = {"E6": 0.20, "E12": 0.10, "E24": 0.05}   # 対応する許容差（代表的な組み合わせ）


def tolerance_gaps(values: list[float], tol: float) -> list[tuple[float, float]]:
    """隣り合う値の許容差の範囲 [v(1−tol), v(1+tol)] の間にできるすき間（下端, 上端）。重なればすき間なし"""
    vs = values + [10.0]
    gaps = []
    for a, b in zip(vs, vs[1:]):
        hi, lo = a * (1 + tol), b * (1 - tol)
        if lo > hi + 1e-12:
            gaps.append((hi, lo))
    return gaps


# =====================================================================
# 電気：はしご形回路
# =====================================================================
def ladder(Rs, Rp, N: int) -> list:
    """N 段のはしご形回路を左から見た抵抗 R_1, …, R_N。
    R_1 = Rs + Rp（いちばん右の 1 段）、R_{n+1} = Rs + Rp R_n /(Rp + R_n)"""
    out = [Rs + Rp]
    for _ in range(N - 1):
        Rn = out[-1]
        out.append(Rs + Rp * Rn / (Rp + Rn))
    return out


def ladder_limit(Rs: float, Rp: float) -> float:
    """x = Rs + Rp x/(Rp + x) ⇔ x² − Rs x − Rs Rp = 0 の正の解"""
    return (Rs + math.sqrt(Rs * Rs + 4 * Rs * Rp)) / 2


def fibonacci(n: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


# =====================================================================
# 電気：過渡現象を差分（漸化式）で計算
# =====================================================================
def euler_charge(E: float, h: float, N: int) -> list[float]:
    """v_{n+1} = v_n + h(E − v_n) = (1 − h)v_n + hE、v_0 = 0（h = Δt/τ）"""
    return linear_recurrence(0.0, 1 - h, h * E, N)


def exact_charge(E: float, t_over_tau: float) -> float:
    return E * (1 - math.exp(-t_over_tau))


# =====================================================================
# 化学：半減期・繰り返し投与・抽出
# =====================================================================
NUCLIDES = {
    "ヨウ素131": (8.02, "日"),
    "セシウム134": (2.06, "年"),
    "セシウム137": (30.1, "年"),
    "炭素14": (5730.0, "年"),
}


def remaining_fraction(t: float, T_half: float) -> float:
    """(1/2)^{t/T}"""
    return 0.5 ** (t / T_half)


def halvings_to_below(ratio: float) -> int:
    """(1/2)^n ≤ ratio となる最小の n"""
    n, x = 0, 1.0
    while x > ratio + 1e-15:
        x /= 2; n += 1
    return n


def dosing_peaks(D: float, r: float, N: int) -> list[float]:
    """投与直後の量 c_1, …, c_N。c_1 = D、c_{n+1} = r c_n + D"""
    return linear_recurrence(D, r, D, N - 1)


def dosing_curve(D: float, T_half: float, tau: float, N: int, pts: int = 40):
    """投与間隔 τ で N 回投与したときの量の時間変化（投与の瞬間に D 増え、半減期 T_half で減る）"""
    ts, ys = [], []
    c = 0.0
    for n in range(N):
        c += D
        for i in range(pts + 1):
            t = tau * i / pts
            ts.append(n * tau + t); ys.append(c * 0.5 ** (t / T_half))
        c *= 0.5 ** (tau / T_half)
    return ts, ys


def extraction_remaining(Dk: float, Vw: float, Vo_total: float, n: int) -> float:
    """有機溶媒 Vo_total を n 回に分けて抽出したとき、水層に残る割合 q^n。
    1 回あたり q = Vw / (Dk·(Vo_total/n) + Vw)（Dk：分配比）"""
    v = Vo_total / n
    return (Vw / (Dk * v + Vw)) ** n


def extraction_limit(Dk: float, Vw: float, Vo_total: float) -> float:
    """n → ∞ の極限 e^{−Dk Vo / Vw}"""
    return math.exp(-Dk * Vo_total / Vw)


# =====================================================================
# 都市：人口・修繕積立金・地震のマグニチュード
# =====================================================================
# 国立社会保障・人口問題研究所「日本の将来推計人口（令和5年推計）」出生中位（死亡中位）推計（万人）
# 2020 年は国勢調査。2056 年は「1 億人を下回る」年（ここでは 1 億人として扱う目安）
IPSS_2023 = {2020: 12615, 2056: 10000, 2065: 9159, 2070: 8700}


def annual_ratio(P1: float, y1: int, P2: float, y2: int) -> float:
    """2 つの年の人口から、毎年一定の割合で変わるとしたときの公比 r（P2 = P1 r^{y2−y1}）"""
    return (P2 / P1) ** (1 / (y2 - y1))


def year_reaching(P0: float, y0: int, r: float, target: float) -> int | None:
    """P0 r^n が初めて target 以下（r < 1）/ 以上（r > 1）になる年"""
    if r == 1:
        return None
    n, P = 0, P0
    while (P > target if r < 1 else P < target):
        P *= r; n += 1
        if n > 10000:
            return None
    return y0 + n


def repair_plan(total: float, years: int, step: int, start_ratio: float):
    """修繕積立金：計画期間 years 年に total 円を積み立てる（1 戸あたり）。
    均等積立：毎月 m = total / (12·years)。
    段階増額：step 年ごとに月額を d ずつ上げる（等差数列）。初めの月額 = start_ratio × m。
    戻り値：(均等の月額, 段階の月額のリスト（年ごと）, 増額 d)"""
    K = years // step                      # 段階の数（step 年 × K）
    if K * step != years:
        raise ValueError("years は step の倍数にする")
    m = total / (12 * years)
    a1 = start_ratio * m
    # total = 12·step·Σ_{k=0}^{K−1}(a1 + k d) = 12·step·(K a1 + K(K−1)/2 d)
    d = (total / (12 * step) - K * a1) / (K * (K - 1) / 2) if K > 1 else 0.0
    stepped = [a1 + (y // step) * d for y in range(years)]
    return m, stepped, d


def magnitude_energy_ratio(dM: float) -> float:
    """マグニチュードが dM 違うときのエネルギーの比 10^{1.5 dM}（1 違うと約 32 倍）"""
    return 10 ** (1.5 * dM)


# =====================================================================
# ビジネス：減価償却・積立
# =====================================================================
def straight_line(cost: int, life: int) -> list[int]:
    """定額法（平成19年4月1日以後）：毎年 cost × 償却率（1/life の小数第 4 位を切り上げ。例：9 年 → 0.112）。
    帳簿価額は最後に 1 円残す。戻り値：各年の償却費"""
    rate = Fraction(math.ceil(1000 / life - 1e-9), 1000)
    dep, book = [], cost
    for y in range(life):
        a = int(cost * rate)
        if y == life - 1 or book - a < 1:
            a = book - 1
        dep.append(a); book -= a
    return dep


def declining_balance(cost: int, life: int, rate, revised_rate, guarantee_rate):
    """定率法（平成24年4月1日以後取得、200% 定率法）。国税庁 No.2106 の計算方法。
    調整前償却額 = 期首未償却残高 × 償却率。これが償却保証額（取得価額 × 保証率）に満たない年から
    改定取得価額 × 改定償却率 に切り替える。最後は 1 円を残す。
    戻り値：[(年, 期首帳簿価額, 調整前償却額, 償却費, 切替後か)]"""
    rate, revised_rate, guarantee_rate = Fraction(str(rate)), Fraction(str(revised_rate)), Fraction(str(guarantee_rate))
    guarantee = cost * guarantee_rate
    rows, book, switched, base = [], Fraction(cost), False, None
    for y in range(1, life + 1):
        pre = book * rate
        if not switched and pre < guarantee:
            switched, base = True, book
        a = base * revised_rate if switched else pre
        a = Fraction(round(a))          # 円未満は四捨五入（国税庁の例と同じ表示）
        if y == life or book - a < 1:
            a = book - 1
        rows.append((y, int(book), float(pre), int(a), switched))
        book -= a
    return rows


def pure_declining(cost: float, rate: float, N: int) -> list[float]:
    """切り替えなしで、毎年 (1 − 償却率) 倍になる帳簿価額（等比数列） b_0, …, b_N"""
    return [cost * (1 - rate) ** n for n in range(N + 1)]


def savings(P: float, r: float, N: int, a0: float = 0.0) -> list[float]:
    """毎期の終わりに P 積み立てる：a_{n+1} = (1 + r) a_n + P"""
    return linear_recurrence(a0, 1 + r, P, N)


def savings_closed(P: float, r: float, n: int) -> float:
    """a_0 = 0 のとき a_n = P{(1+r)^n − 1}/r"""
    return P * n if r == 0 else P * ((1 + r) ** n - 1) / r


def savings_payment(target: float, r: float, n: int) -> float:
    """n 期後に target にするための毎期の積立額"""
    return target / n if r == 0 else target * r / ((1 + r) ** n - 1)
