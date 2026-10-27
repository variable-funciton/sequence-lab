"""課題9・10・12 の数値で計算ロジックを検証する"""
from fractions import Fraction as F
from utils.sequences import *

def test_loan_kadai12():
    r = F(1, 10)
    # 第7問: 3 年で完済 → P = 1,331,000
    assert payment_for_target(3310000, r, 3) == 1331000
    # 第8問: 残価 1,095,610 → P = 1,000,000
    assert payment_for_target(3310000, r, 3, 1095610) == 1000000
    # 第9問: 毎年 100 万円 → 3 年後 1,095,610 円残る
    assert loan_balances(3310000, r, 1000000, 3)[-1] == 1095610
    # 第10問: 毎年 1,331,000 円 → 完済
    assert loan_balances(3310000, r, 1331000, 3)[-1] == 0
    # 一般項と漸化式が一致
    for n, a in enumerate(loan_balances(3310000, r, 1000000, 10)):
        assert closed_form(3310000, r, 1000000, n) == a
    assert fixed_point(r, 1000000) == 10000000
    assert loan_trend(3310000, r, 331000) == "constant"
    assert loan_trend(3310000, r, 300000) == "increase"
    assert years_to_payoff(3310000, r, 1331000) == 3
    assert payment_for_target(1200, 0, 12) == 100
    assert to_frac(0.1) == F(1, 10)

def test_interest_kadai10():
    s = simple_interest(1000000, F(2, 100), 5)
    assert s[-1] - s[0] == 100000           # 第8問
    c = compound_interest(1000000, F(1, 10), 3)
    assert c[-1] - c[0] == 331000           # 第9問
    d = compound_interest(1000000, F(-2, 10), 3)
    assert d[0] - d[-1] == 488000           # 第10問
    assert abs(doubling_years(0.1) - 7.27) < 0.01

def test_arithmetic_kadai9():
    assert arithmetic_terms(-5, 3, 20)[-1] == 52                    # 第4問
    assert first_negative_index(47, -4) == 13                       # 第5問
    assert arithmetic_sums(2, 5, 10)[-1] == 245                     # 第8問
    assert max_sum(35, -3) == ([12], 222)                           # 第9問
    assert max_sum(10, -2) == ([5, 6], 30)                          # a_6 = 0 のとき 2 つ
    assert first_negative_index(5, 1) is None
    assert fmt_yen(1331000) == "1,331,000 円" and fmt_num(F(-3, 2)) == "−3/2"

def test_geometric_kadai10():
    from utils.sequences import (geometric_terms, geometric_sums, geometric_limit,
                                 ratio_case, latex_num, RATIO_CASES)
    assert geometric_terms(3, -2, 4) == [3, -6, 12, -24]                     # 第1問
    assert geometric_terms(F(1, 2), F(1, 3), 3)[-1] == F(1, 18)              # 第2問
    assert geometric_terms(2, -3, 2)[1] == -6                                # 第3問
    assert geometric_sums(5, 3, 6)[-1] == 1820                               # 第5問
    assert geometric_sums(2, -2, 8)[-1] == -170                              # 第6問
    assert geometric_sums(1, 2, 8)[-1] == 255                                # 第7問
    # 公式と、項を直接足した値が一致（6 つの場合すべて）
    for r in [F(1, 2), 1, 2, F(-1, 2), -1, -3]:
        t = geometric_terms(3, r, 9)
        assert geometric_sums(3, r, 9) == [sum(t[:k]) for k in range(1, 10)]
    assert geometric_sums(4, -1, 4) == [4, 0, 4, 0]
    assert geometric_limit(3, F(1, 2)) == 6 and geometric_limit(3, 2) is None
    assert [ratio_case(r) for r in [F(1, 2), 1, 2, F(-1, 2), -1, -3]] == RATIO_CASES
    assert latex_num(1820) == "1{,}820" and latex_num(F(-1, 18)) == r"-\frac{1}{18}"
    assert "10^{" in latex_num(3 ** 30)


if __name__ == "__main__":
    for f in [test_loan_kadai12, test_interest_kadai10, test_arithmetic_kadai9, test_geometric_kadai10]:
        f(); print(f.__name__, "ok")
