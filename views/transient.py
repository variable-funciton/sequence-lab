"""【電気】過渡現象を漸化式で計算する（差分法）— x_{n+1} = (1 − h)x_n + hE"""

import math

import pandas as pd
import streamlit as st

from utils.anim import render as render_anim
from utils.applied import exact_charge, linear_closed_form, linear_recurrence

CIRCUITS = {
    "RC": "RC 回路：コンデンサの充電（電圧 v）",
    "RL": "RL 回路：コイルに流れる電流（電流 i）",
}
for k, v in dict(tr_c="RC", tr_E=10.0, tr_R=1000.0, tr_C=100.0, tr_L=0.5, tr_h=0.2).items():
    st.session_state.setdefault(k, v)

st.sidebar.header("設定")
kind = st.sidebar.radio("回路", list(CIRCUITS), format_func=CIRCUITS.get, key="tr_c")
E = st.sidebar.number_input("電源の電圧 E [V]", min_value=1.0, max_value=100.0, step=1.0, key="tr_E")
R = st.sidebar.number_input("抵抗 R [Ω]", min_value=1.0, max_value=1e6, step=100.0, key="tr_R")
if kind == "RC":
    C_uF = st.sidebar.number_input("静電容量 C [μF]", min_value=1.0, max_value=1e5, step=10.0, key="tr_C")
    tau = R * C_uF * 1e-6
    final, unit, sym = E, "V", "v"
else:
    L = st.sidebar.number_input("インダクタンス L [H]", min_value=0.01, max_value=100.0, step=0.1, key="tr_L")
    tau = L / R
    final, unit, sym = E / R, "A", "i"
h = st.sidebar.select_slider("時間のきざみ h = Δt / τ", options=[0.05, 0.1, 0.2, 0.5, 1.0, 1.5, 1.9, 2.1, 2.5], key="tr_h")
t_end = 5.0 if h <= 1 else 8 * h  # τ の何倍まで（きざみが粗いときは 8 ステップ分）

N = int(round(t_end / h))
xs = linear_recurrence(0.0, 1 - h, h * final, N)
dt = h * tau

st.title("過渡現象を漸化式で計算する（差分法）")
st.markdown(
    "スイッチを入れた直後、コンデンサの電圧やコイルの電流は少しずつ変化します（**過渡現象**）。"
    "この変化は本来は微分方程式で表されますが、時間を短い間隔 $\\Delta t$ に区切ると、"
    "**ローン返済と同じ形の漸化式** $x_{n+1} = px_n + q$ になり、電卓やコンピュータで順に計算できます。"
)

with st.container(border=True):
    if kind == "RC":
        st.markdown(r"**RC 回路**　電流 $\dfrac{E - v}{R}$ がコンデンサにたまるので、$\Delta t$ の間に電圧は $\dfrac{E - v}{RC}\Delta t$ だけ上がる。")
        st.latex(r"v_{n+1} = v_n + \frac{\Delta t}{RC}(E - v_n) = (1 - h)\,v_n + hE,\qquad h = \frac{\Delta t}{\tau},\ \tau = RC")
    else:
        st.markdown(r"**RL 回路**　コイルの電圧 $E - Ri$ に比例して電流が増えるので、$\Delta t$ の間に電流は $\dfrac{E - Ri}{L}\Delta t$ だけ増える。")
        st.latex(r"i_{n+1} = i_n + \frac{\Delta t}{L}(E - Ri_n) = (1 - h)\,i_n + h\frac{E}{R},\qquad h = \frac{\Delta t}{\tau},\ \tau = \frac{L}{R}")
    st.markdown(rf"特性方程式 $\alpha = (1 - h)\alpha + h\cdot{final:.4g}$ の解は $\alpha = {final:.4g}$（最終的な値）。一般項は")
    st.latex(rf"{sym}_n = {final:.4g}\left\{{1 - (1 - h)^n\right\}},\qquad 1 - h = {1 - h:g}")

m = st.columns(4)
m[0].metric("時定数 τ", f"{tau * 1000:.4g} ms" if tau < 1 else f"{tau:.4g} s")
m[1].metric("きざみ Δt", f"{dt * 1000:.4g} ms" if dt < 1 else f"{dt:.4g} s")
m[2].metric("公比 1 − h", f"{1 - h:g}")
exact_end = final * (1 - math.exp(-t_end))
m[3].metric(f"{t_end:g}τ 後の値（漸化式）", f"{xs[-1]:.4g} {unit}", delta=f"正しい値 {exact_end:.4g} {unit}", delta_color="off")

st.markdown("**アニメーション**　▶ を押すとスイッチが入り、電流（オレンジの粒）が流れはじめます。"
            "右のグラフには、正しい変化（灰色）と、漸化式で Δt ごとに計算した値（赤）がかかれていきます。")
render_anim("transient", dict(kind=kind, E=E, R=R, final=final, h=h, unit=unit, sym=sym,
                              tau_text=(f"{tau * 1000:.4g} ms" if tau < 1 else f"{tau:.4g} s")), height=480)

if h < 1:
    st.success(f"0 < 1 − h < 1 なので、(1 − h)ⁿ → 0。値は最終値 {final:.4g} {unit} に近づく（h が小さいほど正しい変化に近い）。")
elif h == 1:
    st.warning("1 − h = 0 なので、1 回で最終値に達してしまう（きざみが粗すぎる）。")
elif h < 2:
    st.warning("−1 < 1 − h < 0 なので、最終値の上下に振れながら近づく（実際の回路ではこんな振動は起きない。きざみが粗すぎる）。")
else:
    st.error("1 − h < −1 なので、(1 − h)ⁿ の絶対値がどんどん大きくなり、計算が発散する（数値計算の不安定）。")

with st.expander("ステップごとの表"):
    rows = [{"n": n, "時間 t = nΔt": f"{n * dt:.4g} s", f"{sym}_n（漸化式）": f"{x:.5g}",
             f"{sym}_n（一般項）": f"{linear_closed_form(0.0, 1 - h, h * final, n):.5g}",
             "正しい値": f"{exact_charge(final, n * h):.5g}"} for n, x in enumerate(xs)]
    st.dataframe(pd.DataFrame(rows), hide_index=True)

with st.expander("📖 解説：等比数列とのつながりと、きざみの大きさ"):
    st.markdown(
        r"""
漸化式 $x_{n+1} = (1 - h)x_n + hE$ は、最終値 $E$ からのずれ $E - x_n$ が **公比 $1 - h$ の等比数列** になることを表す。
$$E - x_{n+1} = (1 - h)(E - x_n)\qquad\Longrightarrow\qquad x_n = E\{1 - (1 - h)^n\}$$

**$h$ を小さくすると**　$(1 - h)^n$ で $n = \dfrac{t}{h}$ とすると $(1 - h)^{t/h}$ は $h \to 0$ で $e^{-t}$ に近づき、
正しい変化 $E(1 - e^{-t/\tau})$ になる（$e \approx 2.718$ は 2 年生以降で学ぶ数）。

**$h$ が大きすぎると**　公比 $1 - h$ が負になると振動し、$|1 - h| > 1$（$h > 2$）では発散する。
コンピュータで計算するときは、きざみを時定数よりじゅうぶん小さくとる必要がある。

この方法（**オイラー法**）は、回路だけでなく、温度の変化、物体の運動など、変化のしかたがわかっている量を計算するときの基本。
"""
    )

with st.expander("🔧 どこで使われている？"):
    st.markdown(
        r"""
- **回路シミュレーター**（SPICE など）：回路の方程式を短い時間ごとの漸化式にして計算している（実際はもっと精度のよい方法を使う）。
- **マイコンでのディジタルフィルタ**：$y_{n+1} = (1 - h)y_n + hx_n$ の形の計算で、センサーの値のノイズをならす（RC 回路と同じはたらき）。
- 参考：[室蘭工業大学「差分法による RL 回路の過渡現象」](https://u.muroran-it.ac.jp/yt-lab/C-Prog/no08.pdf)
"""
    )

with st.expander("📝 考えてみよう"):
    st.markdown(
        r"""
1. $E = 10$ V、$h = 0.5$ のとき、$v_1, v_2, v_3$ を漸化式で求めよう（$v_0 = 0$）。
2. 1. の一般項を求め、$v_n$ が初めて 9.9 V 以上になる $n$ を求めよう。
3. $h = 2.5$ にすると何が起こるか。$v_1, v_2$ を計算して確かめよう。
"""
    )
    with st.popover("答え"):
        st.markdown(
            r"""
1. $v_{n+1} = 0.5v_n + 5$ より $v_1 = 5,\ v_2 = 7.5,\ v_3 = 8.75$
2. $v_n = 10(1 - 0.5^n)$。$0.5^n \le 0.01$ より $n = 7$（$0.5^7 = 0.0078$）
3. $v_{n+1} = -1.5v_n + 25$ より $v_1 = 25,\ v_2 = -12.5$。最終値 10 V のまわりで振れ幅が 1.5 倍ずつ大きくなり、発散する
"""
        )
