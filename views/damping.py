"""【機械】減衰振動 — 振幅の等比数列（粘性減衰）と等差数列（摩擦）"""

import math

import plotly.graph_objects as go
import streamlit as st

from utils.anim import render as render_anim
from utils.applied import friction_peaks, log_decrement, periods_below, viscous_peaks

MODES = {"viscous": "空気や油の抵抗（速さに比例する抵抗）", "friction": "床との摩擦（大きさが一定の摩擦力）"}
for k, v in dict(dm_mode="viscous", dm_A0=10.0, dm_r=0.8, dm_d=1.5, dm_N=10).items():
    st.session_state.setdefault(k, v)

st.sidebar.header("設定")
mode = st.sidebar.radio("振動を止める力", list(MODES), format_func=MODES.get, key="dm_mode")
A0 = st.sidebar.number_input("はじめの振幅 A₀ [mm]", min_value=1.0, max_value=100.0, step=1.0, key="dm_A0")
if mode == "viscous":
    r = st.sidebar.slider("1 周期で振幅が何倍になるか r", 0.30, 0.99, step=0.01, key="dm_r")
else:
    d = st.sidebar.slider("1 周期で振幅が減る量 d [mm]", 0.1, 5.0, step=0.1, key="dm_d")
N = st.sidebar.slider("表示する周期の数", 2, 30, key="dm_N")
T = 1.0

st.title("減衰振動：振幅の減り方と数列")
st.markdown(
    "ばねにつけたおもりの振動は、何かの抵抗を受けてだんだん小さくなります（**減衰振動**）。"
    "1 周期ごとの振幅（山の高さ）を並べると、抵抗の種類によって **等比数列** または **等差数列** になります。"
)

if mode == "viscous":
    peaks = viscous_peaks(A0, r, N)
    with st.container(border=True):
        st.markdown("**速さに比例する抵抗**（空気・油・ダンパー）：毎周期、振幅が同じ **割合** で減る → **等比数列**")
        st.latex(rf"A_n = A_0 r^n = {A0:g}\times {r:g}^{{\,n}},\qquad \text{{対数減衰率}}\ \delta = \log_e\frac{{A_n}}{{A_{{n+1}}}} = -\log_e r \approx {log_decrement(r):.3f}")
    n1 = periods_below(A0, r, 0.1)
    n2 = periods_below(A0, r, 0.01)
    m = st.columns(3)
    m[0].metric("1 周期後の振幅", f"{peaks[1]:.3g} mm")
    m[1].metric("振幅が 1/10 以下になる", f"{n1} 周期後")
    m[2].metric("振幅が 1/100 以下になる", f"{n2} 周期後")
    st.caption("等比数列なので、何周期たっても振幅は 0 にはならない（どこまでも小さくなっていく）。")
else:
    peaks = friction_peaks(A0, d, N)
    with st.container(border=True):
        st.markdown("**大きさが一定の摩擦力**：毎周期、振幅が同じ **量** だけ減る → **等差数列**")
        st.latex(rf"A_n = A_0 - nd = {A0:g} - {d:g}\,n")
    stop = math.ceil(A0 / d) if d > 0 else None
    m = st.columns(3)
    m[0].metric("1 周期後の振幅", f"{peaks[1]:.3g} mm")
    m[1].metric("公差", f"−{d:g} mm")
    m[2].metric("止まるまで", f"約 {stop} 周期" if stop else "—")
    st.caption("等差数列なので、有限の時間で振幅が 0 になる（摩擦でぴたりと止まる）。")

st.markdown("**アニメーション**　▶ を押すと、ばねにつけたおもりが振動します（下のグラフに位置がかかれ、各周期の山 Aₙ に印がつきます）。")
render_anim("damping", dict(mode=mode, A0=A0, r=r if mode == "viscous" else 0.0, d=d if mode == "friction" else 0.0, N=N), height=540)

fig = go.Figure(go.Bar(x=list(range(N + 1)), y=peaks, marker_color="#d62728",
                       hovertemplate="n = %{x}：%{y:.3f} mm<extra></extra>"))
fig.update_layout(height=300, template="plotly_white", showlegend=False, margin=dict(l=10, r=10, t=40, b=10),
                  title=dict(text="各周期の振幅 Aₙ（" + ("等比数列" if mode == "viscous" else "等差数列") + "）", x=0.5, xanchor="center"),
                  xaxis=dict(title="n", dtick=1 if N <= 15 else 5), yaxis=dict(title="mm", rangemode="tozero"))
st.plotly_chart(fig, key="dm_chart")

with st.expander("📖 解説：等比になる理由・等差になる理由"):
    st.markdown(
        r"""
**速さに比例する抵抗（粘性減衰）**　抵抗力は速さに比例するので、振幅が大きいときは大きく、小さいときは小さい。
そのため 1 周期の間に失うエネルギーは、そのときの振幅に対して **いつも同じ割合** になり、振幅は毎周期 $r$ 倍になる。
$$A_n = A_0 r^n \qquad (0 < r < 1)$$
隣り合う山の比の対数 $\delta = \log_e\dfrac{A_n}{A_{n+1}}$ を **対数減衰率** といい、機械や建物の「揺れの止まりやすさ」を表す。
実験で山の高さを何周期か測れば、$\dfrac{A_0}{A_n} = r^{-n}$ から $r$（と $\delta$）が求められる。

**大きさが一定の摩擦（クーロン摩擦）**　摩擦力の大きさは振幅によらず一定なので、
1 往復ごとに **同じ量** だけ振幅が減る（ばね定数 $k$、摩擦力 $f$ なら 1 周期で $d = \dfrac{4f}{k}$）。
$$A_n = A_0 - nd$$
振幅が小さくなり、ばねの力が静止摩擦力に勝てなくなった所で止まる。
"""
    )

with st.expander("🔧 どこで使われている？"):
    st.markdown(
        r"""
- **自動車のショックアブソーバー**（ダンパー）：油の抵抗で、段差を越えたあとの揺れを数周期で小さくする。
- **建物の制振・免震**：ダンパーで地震の揺れを早く減らす。揺れの減り方（減衰）を測って性能を調べる。
- **振動試験**：機械や部品をたたいて揺らし、振幅の減り方から対数減衰率を求める。
- 三角関数のアプリの「バネの単振動と波」でも、摩擦（等差）と抵抗（等比）の減り方をアニメーションで比べられる。
- 参考：[MIT OCW「Estimation of natural frequencies and damping ratios from measured response: the logarithmic decrement」（英語）](https://ocw.mit.edu/courses/2-003sc-engineering-dynamics-fall-2011/resources/estimation-of-natural-frequencies-and-damping-ratios-from-measured-response-the-logarithmic-decrement)
"""
    )

with st.expander("📝 考えてみよう"):
    st.markdown(
        r"""
1. 振幅 10 mm の振動が、1 周期ごとに 0.8 倍になる。3 周期後の振幅は何 mm か。
2. 1. の振動で、振幅が初めて 1 mm 以下になるのは何周期後か。
3. 振幅 10 mm の振動が、摩擦で 1 周期ごとに 1.5 mm ずつ減る。何周期目で止まるか。
"""
    )
    with st.popover("答え"):
        st.markdown(
            r"""
1. $10\times0.8^3 = 5.12$ mm
2. $0.8^{10} \approx 0.107$、$0.8^{11} \approx 0.086$ より 11 周期後
3. $10 - 1.5n \le 0$ より $n \ge 6.66\cdots$。7 周期目の途中で止まる（6 周期後の振幅は 1 mm）
"""
        )
