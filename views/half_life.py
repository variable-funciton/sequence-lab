"""【化学】放射性物質の半減期 — 公比 1/2 の等比数列"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.applied import NUCLIDES, halvings_to_below, remaining_fraction

for k, v in dict(hl_nuc="セシウム137", hl_N0=1000.0, hl_k=8).items():
    st.session_state.setdefault(k, v)

st.sidebar.header("設定")
nuc = st.sidebar.selectbox("放射性物質", list(NUCLIDES), key="hl_nuc")
T, unit = NUCLIDES[nuc]
N0 = st.sidebar.number_input("はじめの量（相対値）", min_value=1.0, max_value=1e6, step=100.0, key="hl_N0")
K = st.sidebar.slider("何半減期分を表示するか", 2, 15, key="hl_k")
t_q = st.sidebar.number_input(f"経過時間 t [{unit}]", min_value=0.0, max_value=T * 20, value=float(round(T * 2.5, 2)), step=T / 10,
                              key=f"hl_t_{nuc}")

st.title("放射性物質の半減期：公比 1/2 の等比数列")
st.markdown(
    "放射性物質は、ほかの物質に変わりながら（壊変しながら）減っていきます。"
    f"量が半分になるまでの時間を **半減期** といい、{nuc} では約 **{T:g} {unit}** です。"
    "半減期ごとに量を見ると、**公比 $\\dfrac{1}{2}$ の等比数列** になります。"
)
with st.container(border=True):
    st.latex(rf"N_k = N_0\left(\frac{{1}}{{2}}\right)^k \quad(k\ \text{{半減期後}}),\qquad "
             rf"N(t) = N_0\left(\frac{{1}}{{2}}\right)^{{t/T}}\quad (T = {T:g}\ \text{{{unit}}})")

frac = remaining_fraction(t_q, T)
m = st.columns(4)
m[0].metric(f"{t_q:g} {unit} 後の量", f"{N0 * frac:.4g}", delta=f"はじめの {100 * frac:.3g}%", delta_color="off")
m[1].metric("1/10 以下になるまで", f"{halvings_to_below(0.1)} 半減期", delta=f"約 {halvings_to_below(0.1) * T:g} {unit}", delta_color="off")
m[2].metric("1/1000 以下になるまで", f"{halvings_to_below(0.001)} 半減期", delta=f"約 {halvings_to_below(0.001) * T:g} {unit}", delta_color="off")
r1 = 0.5 ** (1 / T)
m[3].metric(f"1 {unit}ごとの公比", f"{r1:.5f}", delta=f"1 {unit}で約 {100 * (1 - r1):.3g}% 減る", delta_color="off")

ts = [K * T * i / 400 for i in range(401)]
fig = go.Figure()
fig.add_trace(go.Scatter(x=ts, y=[N0 * remaining_fraction(t, T) for t in ts], mode="lines", name="N(t)", line=dict(color="#1f77b4", width=2.5)))
ks = list(range(K + 1))
fig.add_trace(go.Scatter(x=[k * T for k in ks], y=[N0 * 0.5 ** k for k in ks], mode="markers+text", name="半減期ごと",
                         text=[f"1/{2 ** k}" if k else "1" for k in ks] if K <= 8 else None, textposition="top right",
                         marker=dict(color="#d62728", size=9)))
fig.add_trace(go.Scatter(x=[t_q], y=[N0 * frac], mode="markers", name="いま", marker=dict(color="#2ca02c", size=13, symbol="diamond")))
log_axis = st.toggle("縦軸を対数目盛にする（等比数列が直線になる）", key="hl_log")
fig.update_layout(height=400, template="plotly_white", margin=dict(l=10, r=10, t=30, b=10), showlegend=False,
                  xaxis=dict(title=f"経過時間 [{unit}]"), yaxis=dict(title="量", type="log" if log_axis else "linear"))
st.plotly_chart(fig, key="hl_chart")

with st.expander("半減期ごとの表"):
    rows = [{"k（半減期の回数）": k, f"時間 [{unit}]": f"{k * T:g}", "残る割合": f"1/{2 ** k}", "残る量": f"{N0 * 0.5 ** k:.4g}"}
            for k in ks]
    st.dataframe(pd.DataFrame(rows), hide_index=True)

with st.expander("📖 解説：半減期と等比数列"):
    st.markdown(
        r"""
放射性物質の原子がある時間内に壊変する確率は、いつも同じ（原子の数や経過時間によらない）。
そのため、同じ時間がたつごとに **同じ割合** で減り、量は等比数列になる。

- 半減期 $T$ ごとに見ると公比 $\dfrac{1}{2}$：$N_k = N_0\left(\dfrac{1}{2}\right)^k$
- 1 年（1 日）ごとに見ると公比 $\left(\dfrac{1}{2}\right)^{1/T}$。たとえばセシウム 137（約 30 年）では 1 年で約 2.3% ずつ減る。
- $\left(\dfrac{1}{2}\right)^{10} = \dfrac{1}{1024}$ なので、**半減期の 10 倍で約 1000 分の 1**。

**炭素 14 による年代測定**　生物が生きている間は、体の中の炭素 14 の割合は大気と同じ。死ぬと取り込まれなくなり、半減期約 5730 年で減っていく。
残っている割合が $\dfrac{1}{4}$ なら 2 半減期、つまり約 11000 年前と推定できる。

**生物学的半減期**　体に取り込まれた物質は、壊変だけでなく、排出によっても減る。排出で半分になる時間を生物学的半減期、
両方を合わせて実際に半分になる時間を実効半減期という（環境省の資料を参照）。
"""
    )

with st.expander("🔧 どこで使われている？"):
    st.markdown(
        r"""
- **放射線の管理・除染の計画**：何年後にどれだけ減るかの見積もり。
- **医療**：検査や治療に使う放射性物質は、半減期の短いものが選ばれる。
- **年代測定**：炭素 14 で遺跡や化石の年代を調べる。
- 半減期の値は代表的な値（資料によってわずかに異なる）。
- 参考：[環境省「放射性物質の半減期とは、どういうものですか」](https://www.env.go.jp/chemi/rhm/h28kisoshiryo/h28qa-02-04.html)
"""
    )

with st.expander("📝 考えてみよう"):
    st.markdown(
        r"""
1. ヨウ素 131（半減期 約 8 日）は、24 日後にははじめの何分の 1 になるか。
2. ある物質が 1/16 になるまでに 20 年かかった。半減期は何年か。
3. 化石の炭素 14 の割合が生きている生物の 1/8 だった。約何年前の生物か（半減期 5730 年）。
"""
    )
    with st.popover("答え"):
        st.markdown(
            r"""
1. 24 日 = 3 半減期なので $\left(\dfrac{1}{2}\right)^3 = \dfrac{1}{8}$
2. $\dfrac{1}{16} = \left(\dfrac{1}{2}\right)^4$ なので 4 半減期 = 20 年、半減期は 5 年
3. 3 半減期なので $5730\times3 = 17190$、約 17000 年前
"""
        )
