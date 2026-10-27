"""ハノイの塔・交通渋滞・汚染と自浄・ロジスティック写像・SIR モデル・円周率の計算。Streamlit に依存しない。

テスト: python -m tests.test_applied
"""

from __future__ import annotations

import math
import random

import numpy as np


# =====================================================================
# ハノイの塔
# =====================================================================
def hanoi_moves(n: int, src: int = 0, dst: int = 2, via: int = 1, out=None) -> list[tuple[int, int, int]]:
    """n 枚の円盤を src から dst へ移す手順 [(円盤の番号, from, to)]（円盤 1 がいちばん小さい）"""
    if out is None:
        out = []
    if n == 0:
        return out
    hanoi_moves(n - 1, src, via, dst, out)
    out.append((n, src, dst))
    hanoi_moves(n - 1, via, dst, src, out)
    return out


def hanoi_counts(N: int) -> list[int]:
    """T_1, …, T_N（T_1 = 1、T_{n+1} = 2T_n + 1）"""
    out = [1]
    for _ in range(N - 1):
        out.append(2 * out[-1] + 1)
    return out


def _sig(x: float) -> str:
    """有効数字 3 けた程度（1000 以上は桁区切りの整数）"""
    return f"{x:,.0f}" if x >= 1000 else f"{x:.3g}"


def human_time(sec: float) -> str:
    """秒 → 「約 ○ 年」などの読みやすい表示"""
    if sec < 1e-3:
        return f"{sec * 1e6:.3g} マイクロ秒"
    if sec < 1:
        return f"{sec * 1e3:.3g} ミリ秒"
    if sec < 60:
        return f"{sec:.3g} 秒"
    if sec < 3600:
        return f"{sec / 60:.3g} 分"
    if sec < 86400:
        return f"{sec / 3600:.3g} 時間"
    year = sec / (365.25 * 86400)
    if year < 1:
        return f"{sec / 86400:.3g} 日"
    if year < 1e4:
        return f"{_sig(year)} 年"
    if year < 1e8:
        return f"{_sig(year / 1e4)} 万年"
    if year < 1e12:
        return f"{_sig(year / 1e8)} 億年"
    return f"{_sig(year / 1e12)} 兆年"


# =====================================================================
# 交通渋滞のセルオートマトン（ナーゲル・シュレッケンベルグ模型）
# =====================================================================
def nasch_step(pos: list[int], vel: list[int], L: int, vmax: int, p: float, rng: random.Random):
    """1 ステップ。pos は円形の道路（L マス）上の位置（小さい順）。4 つの規則を順に使う
    1) 加速 v ← min(v + 1, vmax)  2) 減速 v ← min(v, 前の車までの空きマス)
    3) ゆらぎ 確率 p で v ← max(v − 1, 0)  4) 移動 x ← x + v"""
    n = len(pos)
    new_v = []
    for i in range(n):
        gap = (pos[(i + 1) % n] - pos[i] - 1) % L if n > 1 else L - 1
        v = min(vel[i] + 1, vmax)
        v = min(v, gap)
        if v > 0 and rng.random() < p:
            v -= 1
        new_v.append(v)
    new_pos = [(x + v) % L for x, v in zip(pos, new_v)]
    order = sorted(range(n), key=lambda i: new_pos[i])
    return [new_pos[i] for i in order], [new_v[i] for i in order]


def nasch_init(L: int, density: float, seed: int = 1):
    n = max(1, min(L, round(L * density)))
    rng = random.Random(seed)
    pos = sorted(rng.sample(range(L), n))
    return pos, [0] * n, rng


def nasch_flow(L: int, density: float, vmax: int, p: float, warm: int = 200, steps: int = 300, seed: int = 1) -> tuple[float, float]:
    """十分に時間がたったあとの (平均速度, 流量 = 密度 × 平均速度)"""
    pos, vel, rng = nasch_init(L, density, seed)
    for _ in range(warm):
        pos, vel = nasch_step(pos, vel, L, vmax, p, rng)
    s = 0
    for _ in range(steps):
        pos, vel = nasch_step(pos, vel, L, vmax, p, rng)
        s += sum(vel)
    mean_v = s / (steps * len(pos))
    return mean_v, len(pos) / L * mean_v


# =====================================================================
# 環境汚染と自浄作用
# =====================================================================
def pollution(c0: float, k: float, load: float, N: int, change_at: int | None = None, load2: float | None = None) -> list[float]:
    """c_{n+1} = (1 − k)c_n + L。change_at 回目から流入量を load2 に変える"""
    out = [c0]
    for n in range(N):
        L = load2 if (change_at is not None and n >= change_at) else load
        out.append((1 - k) * out[-1] + L)
    return out


# =====================================================================
# ロジスティック写像
# =====================================================================
def logistic(a: float, x0: float, N: int) -> list[float]:
    out = [x0]
    for _ in range(N):
        x = out[-1]
        out.append(a * x * (1 - x))
    return out


def bifurcation(a_min: float = 2.5, a_max: float = 4.0, na: int = 600, warm: int = 400, keep: int = 120, x0: float = 0.3):
    """分岐図の点（a, x）。各 a で warm 回くり返したあとの keep 個の値"""
    a = np.linspace(a_min, a_max, na)
    x = np.full(na, x0)
    for _ in range(warm):
        x = a * x * (1 - x)
    A, X = [], []
    for _ in range(keep):
        x = a * x * (1 - x)
        A.append(a.copy()); X.append(x.copy())
    return np.concatenate(A), np.concatenate(X)


def period_of(a: float, x0: float = 0.3, warm: int = 3000, maxp: int = 64, tol: float = 1e-7) -> int | None:
    """十分くり返したあとの周期（maxp までに見つからなければ None ＝ カオスなど）"""
    x = x0
    for _ in range(warm):
        x = a * x * (1 - x)
    orbit = [x]
    for _ in range(maxp):
        x = a * x * (1 - x)
        orbit.append(x)
    for p in range(1, maxp + 1):
        if abs(orbit[p] - orbit[0]) < tol:
            return p
    return None


# =====================================================================
# 感染症の SIR モデル（1 日ごとの差分方程式）
# =====================================================================
def sir(N: int, I0: float, R0: float, gamma: float, days: int, reduce: float = 0.0, start: int = 0, end: int | None = None):
    """S_{n+1} = S_n − βS_nI_n/N、I_{n+1} = I_n + βS_nI_n/N − γI_n、R_{n+1} = R_n + γI_n（β = R0·γ）。
    start 日目から end 日目まで、接触を reduce の割合だけ減らす（β を (1 − reduce) 倍）"""
    beta = R0 * gamma
    S, I, R = [N - I0], [I0], [0.0]
    for d in range(days):
        b = beta * (1 - reduce) if (start <= d < (end if end is not None else days + 1)) else beta
        new = b * S[-1] * I[-1] / N
        rec = gamma * I[-1]
        S.append(S[-1] - new); I.append(I[-1] + new - rec); R.append(R[-1] + rec)
    return S, I, R


# =====================================================================
# 円周率（アルキメデスの方法）
# =====================================================================
def archimedes(K: int) -> list[tuple[int, float, float]]:
    """直径 1 の円に内接・外接する正 n 角形の周の長さ（n = 6, 12, 24, …）を漸化式で
        b_{2n} = 2 a_n b_n / (a_n + b_n)（外接、調和平均）、a_{2n} = √(a_n b_{2n})（内接、相乗平均）
    a_6 = 3、b_6 = 2√3。π を使わずに計算できる。戻り値 [(n, 内接 a_n, 外接 b_n)]"""
    n, a, b = 6, 3.0, 2 * math.sqrt(3)
    out = [(n, a, b)]
    for _ in range(K):
        b = 2 * a * b / (a + b)
        a = math.sqrt(a * b)
        n *= 2
        out.append((n, a, b))
    return out


def side_doubling(K: int, stable: bool) -> list[tuple[int, float]]:
    """半径 1 の円に内接する正 n 角形の 1 辺 s_n（s_6 = 1）から、正 2n 角形の 1 辺を求める
        そのまま：s_{2n} = √(2 − √(4 − s_n²))（近い数どうしの引き算で桁落ちする）
        工夫した式：s_{2n} = s_n / √(2 + √(4 − s_n²))（同じ値だが、引き算がない）
    戻り値 [(n, 周の長さの半分 = π の近似 n·s_n/2)]"""
    n, s = 6, 1.0
    out = [(n, n * s / 2)]
    for _ in range(K):
        r = math.sqrt(4 - s * s)
        s = s / math.sqrt(2 + r) if stable else math.sqrt(max(0.0, 2 - r))
        n *= 2
        out.append((n, n * s / 2))
    return out


def gauss_legendre(K: int, prec: int = 120):
    """ガウス＝ルジャンドルの方法（算術幾何平均）で π を求める。正しい桁数がほぼ倍々に増える。
    a_0 = 1, b_0 = 1/√2, t_0 = 1/4, p_0 = 1
    a_{n+1} = (a_n + b_n)/2, b_{n+1} = √(a_n b_n), t_{n+1} = t_n − p_n(a_n − a_{n+1})², p_{n+1} = 2p_n
    π ≈ (a_{n+1} + b_{n+1})² / (4t_{n+1})。戻り値 [π の近似（Decimal）]"""
    from decimal import Decimal, localcontext
    with localcontext() as ctx:
        ctx.prec = prec
        a, b, t, p = Decimal(1), 1 / Decimal(2).sqrt(), Decimal(1) / 4, Decimal(1)
        out = []
        for _ in range(K):
            an = (a + b) / 2
            b = (a * b).sqrt()
            t -= p * (a - an) ** 2
            a, p = an, 2 * p
            out.append(+((a + b) ** 2 / (4 * t)))
        return out


PI_100 = ("3.1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679")


def pi_digits(x) -> int:
    """π の近似値が何桁（有効数字）正しいか"""
    from decimal import Decimal, localcontext
    with localcontext() as ctx:
        ctx.prec = 110
        err = abs(Decimal(str(x)) - Decimal(PI_100))
        if err == 0:
            return 100
        return max(0, min(100, int(-(err / Decimal(PI_100)).log10())))
