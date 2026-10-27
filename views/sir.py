"""【生物・社会】感染症の流行モデル（SIR モデル）— 連立漸化式と基本再生産数"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.models import sir

for k, v in dict(ir_R0=2.5, ir_D=7, ir_Npop=100000, ir_I0=10, ir_days=200, ir_on=True, ir_red=40, ir_start=20, ir_end=80, ir_cap=5000).items():
    st.session_state.setdefault(k, v)

st.sidebar.header("設定")
R0 = st.sidebar.slider("基本再生産数 R₀", 0.5, 6.0, step=0.1, key="ir_R0")
D = st.sidebar.slider("感染してから回復するまでの日数", 3, 21, key="ir_D")
Npop = st.sidebar.number_input("人口 N", min_value=1000, max_value=10_000_000, step=1000, key="ir_Npop")
I0 = st.sidebar.number_input("はじめの感染者数", min_value=1, max_value=10000, step=1, key="ir_I0")
days = st.sidebar.slider("日数", 50, 365, key="ir_days")
st.sidebar.markdown("**対策（人と人の接触を減らす）**")
on = st.sidebar.checkbox("対策をする", key="ir_on")
for _k in ("ir_start", "ir_end"):
    st.session_state[_k] = min(st.session_state[_k], days)
red = st.sidebar.slider("接触を何 % 減らすか", 0, 90, step=5, key="ir_red", disabled=not on)
start = st.sidebar.slider("対策を始める日", 0, days, key="ir_start", disabled=not on)
end = st.sidebar.slider("対策を終える日", 0, days, key="ir_end", disabled=not on)
cap = st.sidebar.number_input("医療で対応できる感染者数の目安", min_value=0, max_value=10_000_000, step=500, key="ir_cap")

gamma = 1 / D
S0, I0s, Rr0 = sir(Npop, I0, R0, gamma, days)
S1, I1, R1 = sir(Npop, I0, R0, gamma, days, red / 100 if on else 0.0, start, end)

st.title("感染症の流行モデル（SIR モデル）")
st.markdown(
    "人々を **S**（まだ感染していない人）、**I**（感染している人）、**R**（回復した人）の 3 つに分け、"
    "1 日ごとの人数の変化を **連立漸化式** で表します。$\\beta$ は 1 人の感染者が 1 日にうつす割合、$\\gamma$ は 1 日に回復する割合です。"
)
with st.container(border=True):
    st.latex(r"S_{n+1} = S_n - \beta\frac{S_n I_n}{N},\qquad I_{n+1} = I_n + \beta\frac{S_n I_n}{N} - \gamma I_n,\qquad R_{n+1} = R_n + \gamma I_n")
    st.markdown(rf"$\gamma = \dfrac{{1}}{{\text{{回復までの日数}}}} = \dfrac{{1}}{{{D}}}$、$\beta = R_0\,\gamma = {R0 * gamma:.3f}$。"
                r"**基本再生産数** $R_0 = \dfrac{\beta}{\gamma}$ は、みんなが感染していないとき、1 人の感染者が回復するまでに平均何人にうつすかを表す。")


def peak(I):
    i = max(range(len(I)), key=I.__getitem__)
    return i, I[i]


d0, p0 = peak(I0s)
d1, p1 = peak(I1)
m = st.columns(4)
m[0].metric("ピークの感染者数（対策なし）", f"{p0:,.0f} 人", delta=f"{d0} 日目", delta_color="off")
m[1].metric("ピークの感染者数（対策あり）", f"{p1:,.0f} 人" if on else "—", delta=(f"{d1} 日目、{100 * (1 - p1 / p0):.0f}% 減" if on and p0 > 0 else None), delta_color="off")
m[2].metric("最終的に感染した人の割合（対策なし）", f"{100 * Rr0[-1] / Npop:.1f}%" if I0s[-1] < 1 else f"{100 * (Rr0[-1] + I0s[-1]) / Npop:.1f}%（流行中）")
m[3].metric("集団免疫の目安 1 − 1/R₀", f"{100 * max(0, 1 - 1 / R0):.0f}%")

show_all = st.toggle("S と R も表示する", value=False, key="ir_all")
vis = True if show_all else "legendonly"
fig = go.Figure()
xs = list(range(days + 1))
fig.add_trace(go.Scatter(x=xs, y=S0, mode="lines", name="S（対策なし）", line=dict(color="#1f77b4", width=1.5, dash="dot"), visible=vis))
fig.add_trace(go.Scatter(x=xs, y=I0s, mode="lines", name="I（対策なし）", line=dict(color="#d62728", width=3)))
fig.add_trace(go.Scatter(x=xs, y=Rr0, mode="lines", name="R（対策なし）", line=dict(color="#2ca02c", width=1.5, dash="dot"), visible=vis))
if on:
    fig.add_trace(go.Scatter(x=xs, y=I1, mode="lines", name="I（対策あり）", line=dict(color="#ff7f0e", width=3)))
    fig.add_vrect(x0=start, x1=end, fillcolor="rgba(255,127,14,0.08)", line_width=0, annotation_text="対策の期間", annotation_position="top left")
if cap:
    fig.add_hline(y=cap, line_dash="dash", line_color="#7f7f7f", annotation_text="医療で対応できる目安")
fig.update_layout(height=440, template="plotly_white", margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=1.1),
                  xaxis=dict(title="日"), yaxis=dict(title="人数", tickformat=","))
st.plotly_chart(fig, key="ir_chart")
st.caption("赤：対策なしの感染者数、オレンジ：対策ありの感染者数。接触を減らすと山が低く、遅くなる（「流行曲線を平らにする」）。"
           "対策を早く終えすぎると、あとから山がくることもある。")

# R0 を変えたときのピーク
R0s = [round(1.0 + 0.25 * i, 2) for i in range(1, 21)]
peaks = [peak(sir(Npop, I0, r, gamma, 365)[1])[1] for r in R0s]
fig2 = go.Figure(go.Bar(x=R0s, y=peaks, marker_color=["#d62728" if abs(r - R0) < 0.13 else "#9aa0a6" for r in R0s],
                        hovertemplate="R₀ = %{x}：ピーク %{y:,.0f} 人<extra></extra>"))
fig2.update_layout(height=280, template="plotly_white", margin=dict(l=10, r=10, t=40, b=10),
                   title=dict(text="R₀ とピークの感染者数（対策なし）", x=0.5, xanchor="center"),
                   xaxis=dict(title="R₀"), yaxis=dict(title="ピークの人数", tickformat=","))
st.plotly_chart(fig2, key="ir_r0")

with st.expander("日ごとの表（対策なし）"):
    st.dataframe(pd.DataFrame([{"日": n, "S": f"{s:,.0f}", "I": f"{i:,.0f}", "R": f"{r:,.0f}"} for n, (s, i, r) in enumerate(zip(S0, I0s, Rr0)) if n % 5 == 0]),
                 hide_index=True)

with st.expander("📖 解説：R₀ と流行の山"):
    st.markdown(
        r"""
**流行が広がる条件**　はじめはほとんどの人が感染していない（$S \approx N$）ので、$I_{n+1} \approx I_n + (\beta - \gamma)I_n = (1 + \beta - \gamma)I_n$。
**等比数列** に近く、$\beta > \gamma$（$R_0 > 1$）なら増え、$R_0 < 1$ なら減る。

**ピーク**　感染者が増えるのは $\beta\dfrac{S_n}{N} > \gamma$、つまり $\dfrac{S_n}{N} > \dfrac{1}{R_0}$ の間。
まだ感染していない人の割合が $\dfrac{1}{R_0}$ まで下がると、感染者数は減りはじめる。
$1 - \dfrac{1}{R_0}$ が **集団免疫** の目安（$R_0 = 2.5$ なら 60%）。

**対策の効果**　接触を減らすと $\beta$ が小さくなり、実質の再生産数 $R_0(1 - \text{減らした割合})$ が下がる。
これが 1 より小さければ、その間は感染者が減っていく。

**このモデルの限界**　年齢や地域のちがい、潜伏期間、ワクチン、行動の変化などを省いた、最も簡単なモデル。
実際の感染症の予測には、もっと詳しいモデルが使われる。数値はすべて説明のための例。
"""
    )

with st.expander("🔧 どこで使われている？"):
    st.markdown(
        r"""
- **感染症対策の検討**：接触を減らす期間や程度、ワクチン接種の効果などを、このモデルを詳しくしたもので比べる。
- **医療の体制**：ピークの患者数と時期の見積もりから、病床などの準備を考える。
- **情報やうわさの広がり**、**コンピュータウイルスの広がり** なども、同じ形のモデルで考えられる。
- SIR モデルは、ケルマックとマッケンドリックが 1927 年に発表したモデルがもとになっている。
"""
    )

with st.expander("📝 考えてみよう"):
    st.markdown(
        r"""
1. $R_0 = 0.8$ にすると、感染者数はどうなるか。
2. $R_0 = 3$ のとき、集団免疫の目安 $1 - \dfrac{1}{R_0}$ を求めよう。
3. 対策で接触を 50% 減らすと、$R_0 = 2.5$ の実質の再生産数はいくらになるか。そのとき感染者数は増えるか。
"""
    )
    with st.popover("答え"):
        st.markdown(
            r"""
1. $R_0 < 1$ なので、はじめから減っていく（流行しない）
2. $1 - \dfrac{1}{3} = \dfrac{2}{3} \approx 67\%$
3. $2.5\times0.5 = 1.25$。1 より大きいので、ゆっくりだが増える
"""
        )
