"""【都市・防災】地震のマグニチュードとエネルギー — 公比 約 32 の等比数列"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.applied import magnitude_energy_ratio

for k, v in dict(mg_a=6.0, mg_b=8.0).items():
    st.session_state.setdefault(k, v)

st.sidebar.header("設定")
Ma = st.sidebar.slider("地震 A のマグニチュード", 3.0, 9.5, step=0.1, key="mg_a")
Mb = st.sidebar.slider("地震 B のマグニチュード", 3.0, 9.5, step=0.1, key="mg_b")

q = 10 ** 1.5
st.title("地震のマグニチュードとエネルギー：等比数列")
st.markdown(
    "マグニチュード $M$ は地震そのものの規模を表す数で、**$M$ が 1 大きくなると、地震のエネルギーは約 32 倍** になります"
    "（気象庁）。$M$ を 1, 2, 3, … と等差数列で増やすと、エネルギーは **公比 約 32 の等比数列** になります。"
)
with st.container(border=True):
    st.latex(r"E_{M+1} = 10^{1.5}\,E_M \approx 31.6\,E_M,\qquad E_{M+2} = 10^{3}\,E_M = 1000\,E_M")
    st.latex(r"\frac{E_B}{E_A} = 10^{1.5(M_B - M_A)}")

ratio = magnitude_energy_ratio(Mb - Ma)
m = st.columns(3)
m[0].metric("マグニチュードの差", f"{Mb - Ma:+.1f}")
m[1].metric("B のエネルギーは A の", f"{ratio:,.4g} 倍" if ratio >= 1 else f"1/{1 / ratio:,.4g}")
m[2].metric("A を何回合わせると B と同じか", f"約 {ratio:,.0f} 回" if ratio >= 1 else "—")

Ms = [round(3 + 0.5 * k, 1) for k in range(14)]
fig = go.Figure()
fig.add_trace(go.Bar(x=Ms, y=[magnitude_energy_ratio(M - 3) for M in Ms], marker_color="#1f77b4",
                     hovertemplate="M%{x}：M3 の %{y:,.4g} 倍<extra></extra>"))
for M, color, name in ((Ma, "#2ca02c", "A"), (Mb, "#d62728", "B")):
    fig.add_trace(go.Scatter(x=[M], y=[magnitude_energy_ratio(M - 3)], mode="markers+text", text=[name], textposition="top center",
                             marker=dict(color=color, size=14, symbol="diamond"), hovertemplate=f"{name}：M%{{x}}<extra></extra>"))
log_axis = st.toggle("縦軸を対数目盛にする", value=True, key="mg_log")
fig.update_layout(height=400, template="plotly_white", margin=dict(l=10, r=10, t=30, b=10), showlegend=False,
                  xaxis=dict(title="マグニチュード M", dtick=0.5),
                  yaxis=dict(title="エネルギー（M3 を 1 としたとき）", type="log" if log_axis else "linear", exponentformat="power"))
st.plotly_chart(fig, key="mg_chart")
st.caption("ふつうの目盛ではM8 や M9 が大きすぎて、ほかの棒が見えない。対数目盛では等比数列は等間隔に並ぶ。")

with st.expander("マグニチュードとエネルギーの表"):
    rows = [{"M": M, "M3 の何倍か": f"{magnitude_energy_ratio(M - 3):,.4g}", "1 つ小さい M との比": f"{q:.1f}" if M > 3 else "—"}
            for M in range(3, 10)]
    st.dataframe(pd.DataFrame(rows), hide_index=True)

with st.expander("📖 解説：なぜ 32 倍なのか・震度とのちがい"):
    st.markdown(
        r"""
マグニチュード $M$ と地震のエネルギー $E$ [J] の間には、経験的に $\log_{10} E = 4.8 + 1.5M$ という関係がある
（$\log_{10}$ は「10 の何乗か」を表す。2 年生以降で学ぶ）。つまり $E = 10^{4.8 + 1.5M}$ で、$M$ が 1 増えると
$10^{1.5} = 10\sqrt{10} \approx 31.6$ 倍、2 増えると $10^3 = 1000$ 倍。

- **マグニチュード**：地震そのものの大きさ（1 つの地震に 1 つ）。
- **震度**：ある場所での揺れの強さ（場所によってちがう）。震源から遠いほど小さくなる。

**大きい地震ほど少ない**　ある地域で、$M$ が 1 小さい地震はおよそ 10 倍多く起こることが知られている（グーテンベルグ・リヒターの関係）。
地震の回数も、$M$ について等比数列のようにふるまう。
"""
    )

with st.expander("🔧 どこで使われている？"):
    st.markdown(
        r"""
- **防災・耐震設計**：想定する地震の規模（$M$）から、地盤の揺れや建物にかかる力を見積もる。
- **地震の報道**：「M7.0 と M8.0 では、エネルギーは約 32 倍」のように、規模の違いを伝える。
- **ほかの「対数の目盛」**：音の大きさ（デシベル）、酸性の強さ（pH）、星の明るさ（等級）も、目盛が 1 つ違うと何倍、という等比数列の考え方。
- 参考：[気象庁 名古屋地方気象台「マグニチュードとは」](https://www.data.jma.go.jp/nagoya/shosai/info/mini-jishin/magunitude.html)
"""
    )

with st.expander("📝 考えてみよう"):
    st.markdown(
        r"""
1. M8 の地震のエネルギーは、M6 の地震の何倍か。
2. M9 の地震のエネルギーは、M7 の地震の何個分か。
3. エネルギーが約 32000 倍になるのは、マグニチュードがいくつ大きくなったときか。
"""
    )
    with st.popover("答え"):
        st.markdown(
            r"""
1. 2 大きいので $10^3 = 1000$ 倍
2. 2 大きいので約 1000 個分
3. $32\times1000 \approx 10^{1.5}\times10^{3} = 10^{4.5}$ なので 3 大きくなったとき
"""
        )
