"""演習:漸化式と数学的帰納法(漸化式と項、等差型・等比型、a_{n+1} = pa_n + q 型、数学的帰納法)

問題は exercises/ex_seq2.py の生成関数で作る。画面・LaTeX は exercises/ex_core.py(応用数学ラボ・Triangle_phase と同じしくみ)。
"""

import streamlit as st

from exercises import ex_seq2 as ex
from exercises.ex_core import render

st.title("演習：漸化式と数学的帰納法")
st.caption("漸化式で定まる項、等差型・等比型の漸化式、a_{n+1} = pa_n + q 型の漸化式、数学的帰納法(等式・倍数)")
render("seq2", ex.REGISTRY, "漸化式と数学的帰納法")
