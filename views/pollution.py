"""【都市】環境汚染と自浄作用 — c_{n+1} = (1 − k)c_n + L（湖沼）と、下流へ減っていく等比数列（河川）"""

import math

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.applied import first_index
from utils.models import pollution

for k, v in dict(pl_c0=2.0, pl_k=0.2, pl_L=1.0, pl_N=40, pl_cut=True, pl_m=10, pl_L2=0.4, pl_std=3.0,
                 rv_c0=20.0, rv_k=0.05, rv_km=60, rv_std=3.0).items():
    st.session_state.setdefault(k, v)

st.title("環境汚染と自浄作用：漸化式で見る水質の変化")
st.markdown(
    "湖や川に流れこんだ汚れ（有機物など）は、微生物による分解や、水の入れかわりによって少しずつ減っていきます（**自浄作用**）。"
    "「毎年、一定の割合で減り、一定の量が流れこむ」と考えると、汚れの濃度は **ローン返済と同じ形の漸化式** になります。"
)
tab1, tab2 = st.tabs(["① 湖：流入と自浄のつり合い", "② 川：下流へ行くほど減る"])

with tab1:
    c = st.columns(4)
    c0 = c[0].number_input("いまの濃度 c₀ [mg/L]", min_value=0.0, max_value=100.0, step=0.5, key="pl_c0")
    k = c[1].slider("1 年で減る割合 k（自浄）", 0.02, 0.8, step=0.01, key="pl_k")
    L = c[2].number_input("1 年に流れこむ量 L [mg/L 相当]", min_value=0.0, max_value=50.0, step=0.1, key="pl_L")
    N = c[3].slider("年数", 10, 100, key="pl_N")
    st.session_state["pl_m"] = min(st.session_state["pl_m"], N)
    c = st.columns(3)
    cut = c[0].checkbox("途中で流入を減らす（排水の規制）", key="pl_cut")
    m_ = c[1].slider("何年目から", 1, N, key="pl_m", disabled=not cut) if cut else None
    L2 = c[2].number_input("規制後の流入量", min_value=0.0, max_value=50.0, step=0.1, key="pl_L2", disabled=not cut) if cut else None
    std = st.slider("目標とする濃度（環境基準の例）[mg/L]", 0.5, 20.0, step=0.5, key="pl_std")

    with st.container(border=True):
        st.latex(rf"c_{{n+1}} = (1 - k)\,c_n + L = {1 - k:.2f}\,c_n + {L:g}")
        st.markdown(rf"特性方程式 $\alpha = (1 - k)\alpha + L$ の解 $\alpha = \dfrac{{L}}{{k}} = {L / k:.3g}$ mg/L が **定常状態**（流入と自浄がつり合う濃度）。一般項は")
        st.latex(rf"c_n = \frac{{L}}{{k}} + (1 - k)^n\left(c_0 - \frac{{L}}{{k}}\right)")

    cs = pollution(c0, k, L, N, m_ if cut else None, L2 if cut else None)
    ss1 = L / k
    ss2 = (L2 / k) if cut else None
    n10 = math.ceil(math.log(0.1) / math.log(1 - k))
    mm = st.columns(4)
    mm[0].metric("定常状態 L/k", f"{ss1:.3g} mg/L")
    if cut:
        mm[1].metric("規制後の定常状態", f"{ss2:.3g} mg/L")
    mm[2].metric("定常状態との差が 1/10 になるまで", f"{n10} 年", delta=f"(1 − k)ⁿ ≦ 0.1", delta_color="off")
    below = first_index(cs, lambda x: x <= std)
    mm[3].metric(f"目標 {std:g} mg/L 以下になる年", f"{below} 年目" if below is not None else f"{N} 年では達しない")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=list(range(N + 1)), y=cs, mode="lines+markers", name="濃度 cₙ", line=dict(color="#1f77b4", width=2.5)))
    fig.add_hline(y=ss1, line_dash="dot", line_color="#d62728", annotation_text=f"定常状態 {ss1:.3g}")
    if cut:
        fig.add_hline(y=ss2, line_dash="dot", line_color="#2ca02c", annotation_text=f"規制後の定常状態 {ss2:.3g}", annotation_position="bottom right")
        fig.add_vline(x=m_, line_dash="dash", line_color="gray", annotation_text="規制")
    fig.add_hline(y=std, line_color="#ff7f0e", annotation_text=f"目標 {std:g}", annotation_position="top left")
    fig.update_layout(height=400, template="plotly_white", margin=dict(l=10, r=10, t=30, b=10), showlegend=False,
                      xaxis=dict(title="年 n"), yaxis=dict(title="濃度 [mg/L]", rangemode="tozero"))
    st.plotly_chart(fig, key="pl_lake")
    st.caption("どこから始めても、濃度は定常状態 L/k に近づく。流入を減らすと、新しい定常状態に向かって等比数列のように近づいていく。")
    with st.expander("年ごとの表"):
        st.dataframe(pd.DataFrame([{"年": n, "濃度 cₙ": f"{x:.4f}"} for n, x in enumerate(cs)]), hide_index=True)

with tab2:
    c = st.columns(4)
    r0 = c[0].number_input("排水口のすぐ下流の濃度 [mg/L]", min_value=0.1, max_value=200.0, step=1.0, key="rv_c0")
    rk = c[1].slider("1 km 流れる間に減る割合", 0.005, 0.3, step=0.005, format="%.3f", key="rv_k")
    km = c[2].slider("何 km まで", 10, 200, key="rv_km")
    rstd = c[3].number_input("目標の濃度 [mg/L]", min_value=0.1, max_value=50.0, step=0.5, key="rv_std")
    st.latex(rf"c_{{n+1}} = (1 - {rk:g})\,c_n\quad\Rightarrow\quad c_n = {r0:g}\times{1 - rk:g}^{{\,n}}\quad(n\ \text{{km 下流}})")
    rs = [r0 * (1 - rk) ** n for n in range(km + 1)]
    kb = first_index(rs, lambda x: x <= rstd)
    st.metric("目標の濃度以下になる地点", f"{kb} km 下流" if kb is not None else f"{km} km では達しない")
    fig2 = go.Figure(go.Scatter(x=list(range(km + 1)), y=rs, mode="lines", line=dict(color="#9467bd", width=2.5)))
    fig2.add_hline(y=rstd, line_color="#ff7f0e", annotation_text=f"目標 {rstd:g}")
    fig2.update_layout(height=320, template="plotly_white", margin=dict(l=10, r=10, t=30, b=10),
                       xaxis=dict(title="排水口からの距離 [km]"), yaxis=dict(title="濃度 [mg/L]", rangemode="tozero"))
    st.plotly_chart(fig2, key="pl_river")
    st.caption("新しい流入がなければ、1 km ごとに一定の割合で減る等比数列。実際の川では、支流や別の排水口から流入があると、そこで再び濃度が上がる。")

with st.expander("📖 解説：定常状態と、改善に時間がかかる理由"):
    st.markdown(
        r"""
**定常状態**　1 年で減る量 $kc$ と流れこむ量 $L$ がつり合う濃度 $c = \dfrac{L}{k}$。
流入 $L$ を半分にすれば、定常状態も半分になる。自浄の割合 $k$ が大きい（水の入れかわりが速い・分解が速い）ほど、きれいな状態で落ち着く。

**改善には時間がかかる**　定常状態とのずれ $c_n - \dfrac{L}{k}$ は公比 $1 - k$ の等比数列で小さくなる。
$k$ が小さい湖（水がなかなか入れかわらない）では、流入を減らしてもすぐにはきれいにならない。
たとえば $k = 0.1$ なら、ずれが $\dfrac{1}{10}$ になるまで約 22 年（$0.9^{22} \approx 0.098$）。

**モデルの限界**　実際には、底にたまった汚れが溶け出す（内部負荷）、季節で分解の速さが変わる、などがあるので、
このモデルは大まかな見通しを立てるためのもの。
"""
    )

with st.expander("🔧 どこで使われている？"):
    st.markdown(
        r"""
- **水質の管理**：湖や内湾では、流れこむ汚れの総量を減らす取り組み（総量規制）や下水道の整備の効果を、同じような計算で見積もる。
- **河川の水質**：排水口から下流へ向かって、汚れがどれくらい減るか（自浄作用）を見積もり、排水の基準を決める。
- **大気・室内の空気**：換気で毎時一定の割合が入れかわる部屋の CO₂ 濃度も、同じ形の漸化式で表せる（換気の回数が $k$ にあたる）。
- このページの数値は説明のための例。実際の環境基準や水質の値は、環境省や自治体の資料を参照。
"""
    )

with st.expander("📝 考えてみよう"):
    st.markdown(
        r"""
1. $k = 0.2$、$L = 1$ のとき、定常状態の濃度を求めよう。
2. 1. で流入を $L = 0.4$ に減らすと、定常状態はいくらになるか。
3. 1 km で 5% ずつ減る川で、濃度が半分以下になるのは何 km 下流か（$0.95^{13} \approx 0.513$、$0.95^{14} \approx 0.488$）。
"""
    )
    with st.popover("答え"):
        st.markdown(
            r"""
1. $\dfrac{1}{0.2} = 5$ mg/L
2. $\dfrac{0.4}{0.2} = 2$ mg/L
3. 14 km 下流
"""
        )
