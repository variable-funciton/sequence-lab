"""単利と複利 — 等差数列と等比数列の比較（後期課題10 対応）"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.sequences import compound_interest, doubling_years, fmt_yen, simple_interest, to_frac

PRESETS = {
    "自由に設定": None,
    "課題10 第8問：年利2%の単利で5年": dict(a0=1000000, rate=2.0, N=5),
    "課題10 第9問：年利10%の複利で3年": dict(a0=1000000, rate=10.0, N=3),
    "課題10 第10問：毎年20%減（0.8倍）で3年": dict(a0=1000000, rate=-20.0, N=3),
    "長期で比べる：年利5%で30年": dict(a0=1000000, rate=5.0, N=30),
}
for k, v in dict(ci_a0=1000000, ci_rate=10.0, ci_N=10).items():
    st.session_state.setdefault(k, v)


def apply_preset():
    p = PRESETS[st.session_state["ci_preset"]]
    if p:
        for k, v in p.items():
            st.session_state[f"ci_{k}"] = v


st.sidebar.header("設定")
st.sidebar.selectbox("例題を読み込む", list(PRESETS), key="ci_preset", on_change=apply_preset)
a0 = st.sidebar.number_input("元本 a₀（円）", min_value=0, max_value=10**10, step=10000, key="ci_a0")
rate = st.sidebar.number_input("年利 r（%）　※マイナスで「毎年減る」", min_value=-90.0, max_value=100.0,
                               step=0.5, format="%.2f", key="ci_rate")
N = int(st.sidebar.number_input("年数 N", min_value=1, max_value=60, step=1, key="ci_N"))

r = to_frac(rate) / 100
simple = simple_interest(a0, r, N)
comp = compound_interest(a0, r, N)

st.title("単利と複利：等差数列と等比数列")
c1, c2 = st.columns(2)
with c1, st.container(border=True):
    st.markdown("**単利**：利息は毎年 **元本にだけ** つく → 毎年同じ額ずつ増える")
    st.latex(rf"a_n = a_0(1 + nr) \quad\text{{（公差 }} a_0 r = {float(r * to_frac(a0)):,.0f}\text{{ の等差数列）}}")
with c2, st.container(border=True):
    st.markdown("**複利**：利息は毎年 **利息込みの合計** につく → 毎年同じ倍率で増える")
    st.latex(rf"a_n = a_0(1 + r)^n \quad\text{{（公比 }} 1 + r = {float(1 + r):g}\text{{ の等比数列）}}")

m = st.columns(4)
m[0].metric(f"単利：{N}年後", fmt_yen(round(simple[-1])))
m[1].metric(f"複利：{N}年後", fmt_yen(round(comp[-1])))
m[2].metric("単利の増減額", fmt_yen(round(simple[-1] - simple[0])))
m[3].metric("複利の増減額", fmt_yen(round(comp[-1] - comp[0])),
            delta=f"単利との差 {float(comp[-1] - simple[-1]):+,.0f} 円", delta_color="off")

n_show = st.slider("何年目まで表示するか", 0, N, N)
xs = list(range(N + 1))
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=xs[: n_show + 1], y=[float(v) for v in simple[: n_show + 1]], name="単利（等差数列）",
    mode="lines+markers", line=dict(color="#2ca02c", width=3), marker=dict(size=8),
    hovertemplate="%{x}年後：%{y:,.0f} 円<extra>単利</extra>",
))
fig.add_trace(go.Scatter(
    x=xs[: n_show + 1], y=[float(v) for v in comp[: n_show + 1]], name="複利（等比数列）",
    mode="lines+markers", line=dict(color="#d62728", width=3), marker=dict(size=8),
    hovertemplate="%{x}年後：%{y:,.0f} 円<extra>複利</extra>",
))
fig.add_hline(y=float(a0), line_dash="dot", line_color="gray", annotation_text="元本",
              annotation_position="bottom right")
allv = [float(v) for v in simple + comp]
pad = (max(allv) - min(allv)) * 0.08 or 1
fig.update_layout(
    height=440, template="plotly_white", margin=dict(l=10, r=10, t=30, b=10),
    legend=dict(orientation="h", y=1.05),
    xaxis=dict(title="年数 n", range=[-0.5, N + 0.5], dtick=1 if N <= 20 else 5),
    yaxis=dict(title="元利合計（円）", tickformat=",", range=[min(allv) - pad, max(allv) + pad]),
)
st.plotly_chart(fig, key="interest_chart")

dy = doubling_years(r)
if dy:
    st.caption(f"複利 {float(rate):g}% では、約 {dy:.1f} 年で元本が 2 倍になります（72 ÷ 年利% ≈ {72 / float(rate):.1f} 年：72 の法則）。")
if r < 0:
    st.info("年利がマイナスのとき、複利では毎年 **残っている額の** 一定割合ずつ減るので、減り方はだんだん小さくなります（0 にはならない）。")

with st.expander("年ごとの表"):
    rows = []
    for n in range(1, N + 1):
        rows.append({
            "年 n": n,
            "単利 a_n": fmt_yen(round(simple[n])),
            "単利のその年の増減": fmt_yen(round(simple[n] - simple[n - 1])),
            "複利 a_n": fmt_yen(round(comp[n])),
            "複利のその年の増減": fmt_yen(round(comp[n] - comp[n - 1])),
        })
    st.dataframe(pd.DataFrame(rows), hide_index=True)
    st.caption("単利は「その年の増減」が毎年同じ（等差）、複利は前年の (1+r) 倍になっていく（等比）ことを確かめよう。")
