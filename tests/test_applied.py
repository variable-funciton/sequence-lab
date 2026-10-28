"""応用ページ（物理・学科別）の計算のテスト:  python -m tests.test_applied"""
import math
from fractions import Fraction as F

from utils.applied import *  # noqa: F401,F403


def near(a, b, tol=1e-9):
    assert abs(a - b) <= tol * max(1.0, abs(b)), (a, b)


def test_recurrence():
    for p, q, x0 in [(F(1, 2), 3, 10), (F(11, 10), -5, 100), (F(-1, 2), 1, 0)]:
        xs = linear_recurrence(F(x0), p, q, 12)
        assert all(linear_closed_form(F(x0), p, q, n) == x for n, x in enumerate(xs))
    assert linear_fixed_point(F(1, 2), 3) == 6
    assert linear_closed_form(2, 1, 3, 4) == 14


def test_bounce():
    h = bounce_heights(2.0, 0.8, 5)
    near(h[1] / h[0], 0.64); near(h[3], 2 * 0.64 ** 3)
    near(bounce_total_distance(2.0, 0.8), 2 * 1.64 / 0.36)
    near(bounce_total_distance(2.0, 0.8, 400), bounce_total_distance(2.0, 0.8), 1e-9)
    t0 = math.sqrt(2 * 2.0 / 9.8)
    near(bounce_total_time(2.0, 0.8), t0 * 1.8 / 0.2)
    near(bounce_total_time(2.0, 0.8, 500), bounce_total_time(2.0, 0.8), 1e-9)
    ts, ys = bounce_path(2.0, 0.8, 3)
    near(ts[-1], bounce_total_time(2.0, 0.8, 3)); near(max(ys), 2.0)
    # n 回目の山の高さ
    peak = max(y for t, y in zip(ts, ys) if t > t0 + 1e-9 and t < t0 + 2 * t0 * 0.8 - 1e-9)
    near(peak, 2.0 * 0.64, 1e-2)


def test_preferred():
    for name, vals in RENARD.items():
        n = series_n(name)
        assert len(vals) == n
        for v, t in zip(vals, theoretical(n)):
            assert abs(v - t) / t < 0.013, (name, v, t)
    assert set(RENARD["R5"]) <= set(RENARD["R10"]) <= set(RENARD["R20"]) <= set(RENARD["R40"])
    for name, vals in E_SERIES.items():
        n = series_n(name)
        assert len(vals) == n
        for v, t in zip(vals, theoretical(n)):
            assert abs(v - t) / t < 0.06, (name, v, t)
    assert set(E_SERIES["E6"]) <= set(E_SERIES["E12"]) <= set(E_SERIES["E24"])
    v, err = nearest(E_SERIES["E12"], 5000)
    assert v == 4700 and abs(err) < 0.07
    v, _ = nearest(E_SERIES["E6"], 0.95)
    near(v, 1.0)
    # 許容差の範囲で 1〜10 がほぼすき間なくうまる（丸めのため、わずかなすき間は残る）
    for k in E_SERIES:
        assert all((b - a) / a < 0.045 for a, b in tolerance_gaps(E_SERIES[k], E_TOL[k])), k
    assert tolerance_gaps(E_SERIES["E6"], E_TOL["E6"]) == []
    assert len(tolerance_gaps(E_SERIES["E12"], 0.05)) == 12   # E12 に ±5% だと、すべての間にすき間


def test_damping():
    p = viscous_peaks(10, 0.8, 5)
    near(p[5], 10 * 0.8 ** 5)
    assert friction_peaks(10, 3, 5) == [10, 7, 4, 1, 0, 0]
    assert periods_below(1, 0.5, 0.01) == 7
    near(log_decrement(math.exp(-0.3)), 0.3)
    ts, xs = viscous_curve(1, 0.8, 1.0, 3)
    near(xs[200], 0.8)                       # 1 周期後の山
    ts, xs = friction_curve(10, 2, 1.0, 10)
    # 1 周期ごとの山（t = 0, 1, 2, …）は 2 ずつ減る
    for k in range(1, 4):
        i = min(range(len(ts)), key=lambda j: abs(ts[j] - k))
        near(xs[i], 10 - 2 * k, 1e-6)
    assert abs(xs[-1]) <= 0.5 + 1e-9         # 最後は |x| ≤ Δ で止まる


def test_ladder():
    Rs = ladder(F(1), F(1), 8)
    assert Rs[0] == 2 and Rs[1] == F(5, 3) and Rs[2] == F(13, 8)
    for n, R in enumerate(Rs, start=1):
        assert R == F(fibonacci(2 * n + 1), fibonacci(2 * n))
    near(float(Rs[-1]), (1 + math.sqrt(5)) / 2, 1e-5)
    near(ladder_limit(2, 3), float(ladder(F(2), F(3), 60)[-1]))


def test_transient():
    v = euler_charge(10, 0.1, 50)
    for n in (5, 20, 50):
        near(v[n], 10 * (1 - 0.9 ** n))
    assert abs(v[50] - exact_charge(10, 5)) < 0.1
    w = euler_charge(10, 2.5, 6)
    assert abs(w[6] - 10) > abs(w[1] - 10)   # h > 2 では発散


def test_chemistry():
    near(remaining_fraction(30.1, 30.1), 0.5)
    assert halvings_to_below(0.001) == 10
    c = dosing_peaks(10, 0.5, 6)
    assert c[:3] == [10, 15, 17.5]
    near(c[-1], 20 * (1 - 0.5 ** 6))
    ts, ys = dosing_curve(10, 4, 4, 3)
    near(max(ys), 17.5)
    one, three = extraction_remaining(4, 100, 90, 1), extraction_remaining(4, 100, 90, 3)
    near(one, 100 / 460); near(three, (100 / 220) ** 3)
    assert three < one and extraction_limit(4, 100, 90) < extraction_remaining(4, 100, 90, 50)


def test_city():
    r = annual_ratio(12615, 2020, 8700, 2070)
    near(12615 * r ** 50, 8700)
    y = year_reaching(12615, 2020, r, 10000)
    assert 2045 < y < 2056
    m, st, d = repair_plan(3_000_000, 30, 5, 0.5)
    near(m, 3_000_000 / 360)
    near(sum(12 * a for a in st), 3_000_000)
    assert st[0] < m < st[-1] and d > 0
    near(magnitude_energy_ratio(1), 10 ** 1.5); near(magnitude_energy_ratio(2), 1000)


def test_business():
    dep = straight_line(1_000_000, 10)
    assert dep[0] == 100_000 and sum(dep) == 999_999
    assert straight_line(900_000, 9)[0] == 100_800           # 9 年 → 償却率 0.112
    rows = declining_balance(1_000_000, 10, 0.200, 0.250, 0.06552)
    assert [r[3] for r in rows[:6]] == [200000, 160000, 128000, 102400, 81920, 65536]
    y7 = rows[6]
    assert round(y7[2]) == 52429 and y7[4] and y7[1] == 262144 and y7[3] == 65536   # 国税庁 No.2106 の例
    assert rows[-1][3] == 65535 and sum(r[3] for r in rows) == 999_999
    b = pure_declining(100, 0.2, 3)
    near(b[3], 51.2)
    s = savings(10000, 0.01, 24)
    near(s[24], savings_closed(10000, 0.01, 24))
    near(savings_closed(savings_payment(1e6, 0.002, 120), 0.002, 120), 1e6)




def test_series():
    from utils.series import SERIES, basel_bound, harmonic_groups, p_series_partial, partial_sums, pi_from_basel
    S = partial_sums("harmonic", 11)
    near(S[9], 7381 / 2520); assert S[9] < 3 < S[10]
    near(partial_sums("telescope", 99)[-1], 1 - 1 / 100)
    near(partial_sums("geometric", 10)[-1], 1 - 2 ** -10)
    B = partial_sums("basel", 10 ** 5)
    assert B[-1] < basel_bound(10 ** 5) and abs(math.pi ** 2 / 6 - B[-1] - 1e-5) < 1e-9
    assert abs(pi_from_basel(math.pi ** 2 / 6) - math.pi) < 1e-12
    for i, (a, b, s) in enumerate(harmonic_groups(8)):
        assert i == 0 or s >= 0.5
    near(p_series_partial(2, 50)[-1], partial_sums("basel", 50)[-1])
    for k, v in SERIES.items():
        if v[3] is not None:
            assert abs(partial_sums(k, 10 ** 6)[-1] - v[3]) < 2e-6, k


def test_projectile_drag():
    s0 = projectile_summary(20, 45, 0.0)
    near(s0["range"], 400 / 9.8, 2e-3); near(s0["height"], 100 / 9.8, 2e-3)
    s1 = projectile_summary(30, 45, 0.0061)
    assert s1["range"] < projectile_summary(30, 45, 0.0)["range"] and s1["x_top"] > s1["range"] / 2   # 下りが急
    a, r = best_angle(30, 0.14)
    assert 25 < a < 40
    a0, _ = best_angle(30, 0.0)
    assert abs(a0 - 45) <= 0.5


def test_newton():
    from utils.newton import (bisection, correct_digits, heron, newton, poly_tex, reciprocal, true_sqrt)
    from fractions import Fraction
    xs, t = heron(2, 1, 7), true_sqrt(2)
    d = [correct_digits(x, t) for x in xs]
    assert d[:7] == [0, 1, 2, 5, 11, 24, 48]                    # 正しい桁数がほぼ倍々
    assert abs(float(xs[3]) - 577 / 408) < 1e-15
    for x in xs[1:]:
        assert x >= t                                          # 相加相乗平均：n ≧ 1 で √2 以上
    bs = bisection(2, 1, 2, 10)
    assert float(bs[10][1] - bs[10][0]) == 2 ** -10
    near(newton([1, 0, -2, -5], 2.0, 8)[-1], 2.0945514815423265)
    assert newton([1, 0, -2, 2], 0.0, 4) == [0.0, 1.0, 0.0, 1.0, 0.0]
    near(reciprocal(7, 0.1, 8)[-1], 1 / 7)
    assert poly_tex([1, 0, -2, -5]) == "x^{3} - 2x - 5"


def test_models():
    import random
    from utils.models import (archimedes, gauss_legendre, hanoi_counts, hanoi_moves, logistic, nasch_flow, nasch_init,
                              nasch_step, period_of, pi_digits, pollution, side_doubling, sir)
    # ハノイの塔：手順が正しく、手数 = 2^n − 1
    for n in range(1, 9):
        mv = hanoi_moves(n)
        assert len(mv) == 2 ** n - 1 == hanoi_counts(n)[-1]
        pegs = [list(range(n, 0, -1)), [], []]
        for d, a, b in mv:
            assert pegs[a][-1] == d and (not pegs[b] or pegs[b][-1] > d)
            pegs[b].append(pegs[a].pop())
        assert pegs[2] == list(range(n, 0, -1))
    # 渋滞：車の台数が変わらず、追い越し・衝突がない。p = 0 で密度が小さければ全員最高速度
    pos, vel, rng = nasch_init(100, 0.3, 2)
    for _ in range(200):
        pos, vel = nasch_step(pos, vel, 100, 5, 0.3, rng)
        assert len(set(pos)) == len(pos) == 30
    assert nasch_flow(100, 0.1, 5, 0.0)[0] == 5.0
    assert nasch_flow(100, 0.5, 5, 0.2)[1] < nasch_flow(100, 0.15, 5, 0.2)[1]
    # 汚染：定常状態 L/k に近づく、一般項と一致
    cs = pollution(0, 0.2, 1, 60)
    near(cs[-1], 5, 1e-4); near(cs[10], 5 * (1 - 0.8 ** 10))
    # ロジスティック写像
    assert period_of(2.8) == 1 and period_of(3.2) == 2 and period_of(3.5) == 4 and period_of(3.83) == 3 and period_of(3.7) is None
    near(logistic(2.8, 0.2, 500)[-1], 1 - 1 / 2.8, 1e-9)
    # SIR：総人口一定、ピークは S/N ≈ 1/R0
    S, I, R = sir(100000, 10, 2.5, 1 / 7, 300)
    assert all(abs(s + i + r - 100000) < 1e-6 for s, i, r in zip(S, I, R))
    k = max(range(len(I)), key=I.__getitem__)
    assert abs(S[k] / 100000 - 0.4) < 0.01
    assert max(sir(100000, 10, 2.5, 1 / 7, 300, 0.5, 0, 300)[1]) < max(I)
    # 円周率
    rows = archimedes(4)
    assert rows[4][0] == 96 and 3 + 10 / 71 < rows[4][1] < math.pi < rows[4][2] < 3 + 1 / 7
    assert [pi_digits(x) for x in gauss_legendre(5)] == [3, 8, 19, 40, 84]
    assert abs(side_doubling(30, True)[-1][1] - math.pi) < 1e-14 and side_doubling(30, False)[-1][1] == 0.0


def test_tentmap():
    from fractions import Fraction as Fr
    from utils.tentmap import binary_digits, eventual_period, float_collapse_step, orbit, parse_x0, tent, to_logistic
    assert orbit(Fr(1, 7), 4) == [Fr(1, 7), Fr(2, 7), Fr(4, 7), Fr(6, 7), Fr(2, 7)]
    assert eventual_period(Fr(1, 7)) == (1, 3) and eventual_period(Fr(3, 8)) == (4, 1) and eventual_period(Fr(2, 3)) == (0, 1)
    assert eventual_period(parse_x0("5/13")) == (1, 6) and parse_x0("0.3") == Fr(3, 10)
    assert binary_digits(Fr(1, 7), 9) == "001001001" and binary_digits(Fr(2, 3), 6) == "101010"
    # 2 進数：1 けた目が 1 なら、ずらして 0 と 1 を入れかえる
    for x in (Fr(5, 13), Fr(3, 10), Fr(6, 7)):
        b, nb = binary_digits(x, 30), binary_digits(tent(x), 29)
        assert nb == (b[1:] if b[0] == "0" else "".join("1" if c == "0" else "0" for c in b[1:]))
    assert 50 <= float_collapse_step(0.3) <= 60
    # sin² で移すとロジスティック写像（a = 4）
    for y in (Fr(1, 7), Fr(3, 10), Fr(5, 13)):
        x = to_logistic(y)
        near(to_logistic(tent(y)), 4 * x * (1 - x), 1e-12)


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print("ok", name)
