"""演習:等差数列・等比数列と和(一般項、2つの項から一般項、和、Σ の計算、階差数列)

問題は exercises/ex_seq1.py の生成関数で作る。画面・LaTeX は exercises/ex_core.py(応用数学ラボ・Triangle_phase と同じしくみ)。
"""

import streamlit as st

from exercises import ex_seq1 as ex
from exercises.ex_core import render

st.title("演習：等差数列・等比数列と和")
st.caption("等差数列・等比数列の一般項(2つの項から求めるものを含む)、等差数列・等比数列の和、Σ の計算、階差数列")
render("seq1", ex.REGISTRY, "等差数列・等比数列と和")
