"""【化学・生物】薬の繰り返し投与 — 漸化式 c_{n+1} = r c_n + D と定常状態"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.applied import dosing_curve, dosing_peaks, first_index, linear_fixed_point

PRESETS = {
    "自由に設定": None,
    "半減期と同じ間隔で飲む（r = 1/2）": dict(D=100.0, T=6.0, tau=6.0),
    "半減期より短い間隔（たまりやすい）": dict(D=100.0, T=12.0, tau=6.0),
    "半減期より長い間隔（ほとんどたまらない）": dict(D=100.0, T=4.0, tau=12.0),
}
for k, v in dict(ds_D=100.0, ds_T=6.0, ds_tau=6.0, ds_N=10).items():
    st.session_state.setdefault(k, v)


def apply_preset():
    p = PRESETS[st.session_state["ds_preset"]]
    if p:
        for k, v in p.items():
            st.session_state[f"ds_{k}"] = v


st.sidebar.header("設定")
st.sidebar.selectbox("例を読み込む", list(PRESETS), key="ds_preset", on_change=apply_preset)
D = st.sidebar.number_input("1 回に体に入る量 D [mg]", min_value=1.0, max_value=10000.0, step=10.0, key="ds_D")
T = st.sidebar.number_input("体内での半減期 T [時間]", min_value=0.5, max_value=200.0, step=0.5, key="ds_T")
tau = st.sidebar.number_input("飲む間隔 τ [時間]", min_value=0.5, max_value=200.0, step=0.5, key="ds_tau")
N = st.sidebar.slider("飲む回数", 1, 40, key="ds_N")

r = 0.5 ** (tau / T)
peaks = dosing_peaks(D, r, N)
cmax = linear_fixed_point(r, D)
troughs = [c * r for c in peaks]

st.title("薬の繰り返し投与：漸化式と定常状態")
st.markdown(
    "薬を飲むと体の中の量が増え、その後は一定の割合で減っていきます（半減期 $T$）。"
    "決まった間隔で飲み続けると、前に飲んだ分が残っている所に次の分が加わるので、"
    "飲んだ直後の量 $c_n$ は **ローン返済と同じ形の漸化式** になります。"
)
with st.container(border=True):
    st.latex(rf"c_1 = D,\qquad c_{{n+1}} = r\,c_n + D,\qquad r = \left(\frac{{1}}{{2}}\right)^{{\tau/T}} = {r:.4g}")
    st.markdown(r"特性方程式 $\alpha = r\alpha + D$ の解 $\alpha = \dfrac{D}{1 - r}$ が **定常状態**（飲み続けたときの、飲んだ直後の量）。一般項は")
    st.latex(rf"c_n = \frac{{D(1 - r^n)}}{{1 - r}} = \alpha(1 - r^n),\qquad \alpha = \frac{{{D:g}}}{{1 - {r:.4g}}} \approx {cmax:.4g}\ \text{{mg}}")

n90 = first_index(peaks, lambda c: c >= 0.9 * cmax)
m = st.columns(4)
m[0].metric("1 間隔で残る割合 r", f"{r:.3g}")
m[1].metric("定常状態（飲んだ直後）", f"{cmax:.4g} mg", delta=f"1 回分の {cmax / D:.3g} 倍", delta_color="off")
m[2].metric("定常状態（次に飲む直前）", f"{cmax * r:.4g} mg")
m[3].metric("定常状態の 90% に達する", f"{n90 + 1} 回目" if n90 is not None else f"{N} 回では未到達")

ts, ys = dosing_curve(D, T, tau, N)
fig = go.Figure()
fig.add_trace(go.Scatter(x=ts, y=ys, mode="lines", name="体の中の量", line=dict(color="#1f77b4", width=2.2),
                         hovertemplate="%{x:.1f} 時間：%{y:.1f} mg<extra></extra>"))
fig.add_trace(go.Scatter(x=[n * tau for n in range(N)], y=peaks, mode="markers", name="飲んだ直後 c_n", marker=dict(color="#d62728", size=8)))
fig.add_hline(y=cmax, line_dash="dot", line_color="#d62728", annotation_text=f"定常状態 {cmax:.4g} mg")
fig.add_hline(y=cmax * r, line_dash="dot", line_color="#2ca02c", annotation_text=f"飲む直前の定常値 {cmax * r:.4g} mg",
              annotation_position="bottom right")
fig.update_layout(height=400, template="plotly_white", margin=dict(l=10, r=10, t=30, b=10), showlegend=False,
                  xaxis=dict(title="時間 [時間]"), yaxis=dict(title="体の中の量 [mg]", rangemode="tozero"))
st.plotly_chart(fig, key="ds_chart")
st.caption("飲むたびに増えるが、増え方はだんだん小さくなり、のこぎりの歯のような形で一定の範囲におさまる。")

with st.expander("回ごとの表"):
    rows = [{"n 回目": n, "飲んだ直後 c_n [mg]": f"{c:.4g}", "次に飲む直前 [mg]": f"{tr:.4g}",
             "定常状態に対する割合": f"{100 * c / cmax:.1f}%"} for n, (c, tr) in enumerate(zip(peaks, troughs), start=1)]
    st.dataframe(pd.DataFrame(rows), hide_index=True)

with st.expander("📖 解説：等比級数として見る・ローンとの比較"):
    st.markdown(
        r"""
**等比級数として見る**　$n$ 回目を飲んだ直後には、1 回前の分が $r$ 倍、2 回前の分が $r^2$ 倍、… 残っているので
$$c_n = D + Dr + Dr^2 + \cdots + Dr^{n-1} = \frac{D(1 - r^n)}{1 - r}$$
$0 < r < 1$ なので $n \to \infty$ で $r^n \to 0$、$c_n \to \dfrac{D}{1 - r}$（無限等比級数の和）。

**ローン返済との比較**　ローンは $a_{n+1} = (1 + r)a_n - P$（利息で増えて、返済で減る）、
薬は $c_{n+1} = rc_n + D$（体の中で減って、飲んで増える）。どちらも $x_{n+1} = px_n + q$ の形で、
特性方程式 $\alpha = p\alpha + q$ の解に近づくか（$|p| < 1$）、離れていくか（$p > 1$）が決まる。

**間隔と半減期の関係**　間隔 $\tau$ が半減期 $T$ と同じなら $r = \dfrac{1}{2}$ で、定常状態は 1 回分の 2 倍。
間隔が短いほど $r$ が 1 に近く、たくさんたまる。定常状態に近づく速さは $r^n$ で決まり、半減期の約 3〜4 倍の時間で 90% 程度になる。
"""
    )

with st.expander("🔧 どこで使われている？"):
    st.markdown(
        r"""
- **薬の飲み方（用法）の設計**：効き目のある量を保ちつつ、多すぎないように、1 回の量と間隔を決める（薬物動態学）。
- **カフェインやアルコール** なども、体の中で一定の割合で減っていくものとして同じように考えられる。
- 同じ形の漸化式は、**湖や部屋の汚れの濃度**（毎日一定量が入り、一定の割合で入れかわる）などにも現れる。
- ⚠️ このページは数列の学習用の簡単なモデル（体に入る速さや個人差などを省略）です。実際の薬は医師・薬剤師の指示に従ってください。
- 参考：[Introducing Mathematical Biology, Ch.18 Repeated intravenous bolus doses（Sheffield 大学、英語）](https://sheffield.pressbooks.pub/introducingmathematicalbiology/chapter/repeated-intravenous-bolus-doses/)
"""
    )

with st.expander("📝 考えてみよう"):
    st.markdown(
        r"""
1. 1 回 100 mg、半減期と同じ間隔で飲むとき、$c_1, c_2, c_3$ を求めよう。
2. 1. の定常状態（飲んだ直後の量）を求めよう。
3. 間隔を半減期の 2 倍にすると、定常状態はいくらになるか。
"""
    )
    with st.popover("答え"):
        st.markdown(
            r"""
1. $r = \dfrac{1}{2}$。$c_1 = 100,\ c_2 = 150,\ c_3 = 175$ mg
2. $\dfrac{100}{1 - 1/2} = 200$ mg
3. $r = \dfrac{1}{4}$ なので $\dfrac{100}{1 - 1/4} = \dfrac{400}{3} \approx 133$ mg
"""
        )
