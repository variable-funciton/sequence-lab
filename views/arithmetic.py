"""等差数列とその和（後期課題9 対応）"""

import plotly.graph_objects as go
import streamlit as st

from utils.sequences import arithmetic_sums, arithmetic_terms, first_negative_index, fmt_num, max_sum

PRESETS = {
    "自由に設定": None,
    "課題9 第5問：初項47・公差−4（初めて負になる項）": dict(a=47, d=-4, N=16),
    "課題9 第8問：初項2・公差5の和 S₁₀": dict(a=2, d=5, N=10),
    "課題9 第9問：初項35・公差−3（和の最大）": dict(a=35, d=-3, N=25),
    "課題9 第10問：a₅=19, a₁₁=43 の和 S₂₀": dict(a=3, d=4, N=20),
}
for k, v in dict(ar_a=35, ar_d=-3, ar_N=25).items():
    st.session_state.setdefault(k, v)


def apply_preset():
    p = PRESETS[st.session_state["ar_preset"]]
    if p:
        for k, v in p.items():
            st.session_state[f"ar_{k}"] = v


st.sidebar.header("設定")
st.sidebar.selectbox("例題を読み込む", list(PRESETS), key="ar_preset", on_change=apply_preset)
a = st.sidebar.number_input("初項 a", min_value=-1000, max_value=1000, step=1, key="ar_a")
d = st.sidebar.number_input("公差 d", min_value=-100, max_value=100, step=1, key="ar_d")
N = int(st.sidebar.number_input("表示する項数 N", min_value=1, max_value=60, step=1, key="ar_N"))

terms = arithmetic_terms(a, d, N)
sums = arithmetic_sums(a, d, N)

st.title("等差数列とその和")
def tn(x) -> str:
    """LaTeX 用の数（Unicode マイナスを ASCII に）"""
    return fmt_num(x).replace("−", "-")


coef = "" if d == 1 else "-" if d == -1 else str(d)
const = "" if a - d == 0 else f" {'+' if a - d > 0 else '-'} {abs(a - d)}"
st.latex(
    rf"a_n = a + (n-1)d = {a} + (n-1)\cdot({d}) = {coef}n{const}" if d != 0 else rf"a_n = {a}"
)
st.latex(r"S_n = \frac{n(a + \ell)}{2} = \frac{n\{2a + (n-1)d\}}{2}")

c = st.columns(3)
c[0].metric(f"第 {N} 項 a_{N}", fmt_num(terms[-1]))
c[1].metric(f"和 S_{N}", fmt_num(sums[-1]))
neg = first_negative_index(a, d)
c[2].metric("初めて負になる項", f"第 {neg} 項" if neg else "なし")

ms = max_sum(a, d)
if ms:
    ns, best = ms
    st.success(
        f"S_n が最大になるのは n = {'、'.join(map(str, ns))} のとき（最大値 {fmt_num(best)}）。"
        "正の項（と 0 の項）をすべて足し終えたところで和が最大になります。"
    )

tab1, tab2 = st.tabs(["① 項と和のグラフ", "② 和の公式の図解"])

with tab1:
    n_show = st.slider("第何項まで足すか", 1, N, N)
    xs = list(range(1, N + 1))
    fig = go.Figure(go.Bar(
        x=xs, y=[float(t) for t in terms],
        marker_color=[("#1f77b4" if t >= 0 else "#d62728") if n <= n_show else "rgba(160,160,160,0.3)"
                      for n, t in zip(xs, terms)],
        hovertemplate="a_%{x} = %{y}<extra></extra>", name="a_n",
    ))
    fig.update_layout(height=300, template="plotly_white", margin=dict(l=10, r=10, t=30, b=10),
                      title=dict(text="各項 a_n（青：正 / 赤：負）", font_size=14),
                      xaxis=dict(title="n", dtick=1 if N <= 25 else 5), yaxis=dict(title="a_n"))
    st.plotly_chart(fig, key="terms_chart")

    fig2 = go.Figure(go.Scatter(
        x=xs[:n_show], y=[float(s) for s in sums[:n_show]], mode="lines+markers",
        line=dict(color="#9467bd", width=3), marker=dict(size=7), name="S_n",
        hovertemplate="S_%{x} = %{y}<extra></extra>",
    ))
    if ms:
        fig2.add_trace(go.Scatter(x=ms[0], y=[float(ms[1])] * len(ms[0]), mode="markers",
                                  marker=dict(color="#ff7f0e", size=14, symbol="star"), name="最大",
                                  hovertemplate="最大 S_%{x} = %{y}<extra></extra>"))
    sv = [float(s) for s in sums]
    pad = (max(sv) - min(sv)) * 0.1 or 1
    fig2.update_layout(height=300, template="plotly_white", margin=dict(l=10, r=10, t=30, b=10),
                       title=dict(text=f"和 S_n（S_{n_show} = {fmt_num(sums[n_show - 1])}）", font_size=14),
                       showlegend=False, xaxis=dict(title="n", range=[0.5, N + 0.5], dtick=1 if N <= 25 else 5),
                       yaxis=dict(title="S_n", range=[min(sv + [0]) - pad, max(sv + [0]) + pad]))
    st.plotly_chart(fig2, key="sums_chart")

with tab2:
    n2 = st.slider("項数 n", 1, min(N, 30), min(N, 10), key="ar_n2")
    t2 = terms[:n2]
    st.markdown(
        r"$S_n = a_1 + a_2 + \cdots + a_n$ と、それを **逆順に並べたもの** "
        r"$S_n = a_n + a_{n-1} + \cdots + a_1$ を足すと、どの列も $a_1 + a_n$ になります。"
    )
    xs2 = list(range(1, n2 + 1))
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(x=xs2, y=[float(t) for t in t2], name="順に並べた a_k", marker_color="#1f77b4",
                          hovertemplate="a_%{x} = %{y}<extra></extra>"))
    fig3.add_trace(go.Bar(x=xs2, y=[float(t) for t in reversed(t2)], name="逆順に並べた a_(n+1−k)",
                          marker_color="#ff7f0e", hovertemplate="%{y}<extra>逆順</extra>"))
    fig3.add_hline(y=float(t2[0] + t2[-1]), line_dash="dash", line_color="black",
                   annotation_text=f"a₁ + aₙ = {fmt_num(t2[0] + t2[-1])}", annotation_position="top left")
    fig3.update_layout(barmode="relative", height=380, template="plotly_white",
                       margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=1.08),
                       xaxis=dict(title="列 k", dtick=1))
    st.plotly_chart(fig3, key="sum_formula_chart")
    st.latex(
        rf"2S_{{{n2}}} = {n2} \times \{{({tn(t2[0])}) + ({tn(t2[-1])})\}} = {tn(n2 * (t2[0] + t2[-1]))}"
        rf"\quad\Longrightarrow\quad S_{{{n2}}} = {tn(sums[n2 - 1])}"
    )
    if any(t < 0 for t in t2):
        st.caption("※ 負の項があると棒が上下に分かれますが、各列の合計（上向き − 下向き）はやはり a₁ + aₙ です。")
