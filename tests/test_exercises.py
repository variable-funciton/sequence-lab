"""演習の問題の答えを確かめる(pytest または python tests/test_exercises.py)"""
import os
import sys
from fractions import Fraction as F

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from exercises import ex_seq1, ex_seq2  # noqa: E402
from exercises.ex_core import build, correct_choice, rng_for  # noqa: E402
from exercises.seq_common import peval  # noqa: E402

N = 150


def _each(registry):
    for t in registry:
        for seed in range(N):
            yield t, build(t, rng_for("test", seed, t.key))


def test_seq1():
    for t, p in _each(ex_seq1.REGISTRY):
        m = p.meta
        assert len({c.tex for c in p.choices}) == 4 and sum(c.correct for c in p.choices) == 1
        if t.key == "s1_arith_sum":
            assert m["S"] == sum(m["a"] + i * m["d"] for i in range(m["n"]))
        elif t.key == "s1_geo_sum" and m["kind"] == "num":
            assert m["S"] == sum(m["a"] * m["r"] ** i for i in range(m["n"]))
        elif t.key == "s1_sigma":
            f = lambda x: m["p"] * x * x + m["q"] * x + m["c"]
            if "N" in m:
                assert m["val"] == sum(f(i) for i in range(1, m["N"] + 1))
            else:
                for n in range(1, 7):
                    assert peval(m["co"], n) == sum(f(i) for i in range(1, n + 1))
        elif t.key == "s1_diff_seq":
            for n, v in enumerate(m["seq"], 1):
                assert peval(m["co"], n) == v
        assert p.exam_answer == correct_choice(p).tex


def test_seq2():
    for t, p in _each(ex_seq2.REGISTRY):
        m = p.meta
        assert len({c.tex for c in p.choices}) == 4 and sum(c.correct for c in p.choices) == 1
        if t.key == "s2_rec_linear":
            pp, q, a1, al = F(m["p"]), F(m["q"]), F(m["a1"]), F(m["al"])
            a = a1
            for n in range(1, 7):
                assert a == (a1 - al) * pp ** (n - 1) + al
                a = pp * a + q
        elif t.key == "s2_induction" and m["kind"] in ("lin", "sq", "kk1", "cube"):
            for n in range(1, 7):
                assert sum(peval(m["f"], i) for i in range(1, n + 1)) == peval(m["g"], n)
        elif t.key == "s2_induction" and m["kind"] == "pow":
            for n in range(1, 8):
                assert (m["a"] ** n + m["c"]) % m["m"] == 0


if __name__ == "__main__":
    test_seq1()
    test_seq2()
    print("ok")
