"""【生物・社会】ロジスティック写像とカオス — x_{n+1} = a x_n (1 − x_n)"""

import math

import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from utils.models import bifurcation, logistic, period_of

PRESETS = {
    "自由に設定": None,
    "a = 2.8（一定の値に近づく）": 2.8,
    "a = 3.2（2 つの値を交互に）": 3.2,
    "a = 3.5（4 つの値をくり返す）": 3.5,
    "a = 3.7（カオス）": 3.7,
    "a = 3.83（カオスの中の周期 3）": 3.83,
    "a = 4.0（カオス）": 4.0,
}
for k, v in dict(lg_a=2.8, lg_x0=0.2, lg_N=60).items():
    st.session_state.setdefault(k, v)


def apply_preset():
    v = PRESETS[st.session_state["lg_preset"]]
    if v is not None:
        st.session_state["lg_a"] = v


st.sidebar.header("設定")
st.sidebar.selectbox("例を読み込む", list(PRESETS), key="lg_preset", on_change=apply_preset)
a = st.sidebar.slider("係数 a", 0.5, 4.0, step=0.01, key="lg_a")
x0 = st.sidebar.slider("はじめの値 x₀", 0.01, 0.99, step=0.01, key="lg_x0")
N = st.sidebar.slider("くり返す回数", 10, 200, key="lg_N")

xs = logistic(a, x0, N)
per = period_of(a, x0)
if per is None and 1 < a <= 3:   # a = 3 付近は近づき方がとてもおそいので、周期の判定がしにくい
    per = 1

st.title("ロジスティック写像とカオス")
st.markdown(
    r"生き物の数（の割合）$x_n$ が、「多いと増えるが、増えすぎるとえさが足りなくなって減る」ようすを、次の漸化式で表します。"
    r"$x_n$ が小さいときは約 $a$ 倍に増え、1 に近いと $(1 - x_n)$ が小さくなってブレーキがかかります。"
)
with st.container(border=True):
    st.latex(rf"x_{{n+1}} = a\,x_n(1 - x_n),\qquad a = {a:g},\ x_0 = {x0:g}")
    st.markdown("こんなに簡単な式なのに、$a$ を変えるだけで、**一定の値に近づく → 2 つの値を行き来する → 4 つ、8 つ … → 予測できない（カオス）** と、ふるまいががらりと変わります。")

msg = ("0 に近づく（絶滅）" if a <= 1 else
       f"一定の値 1 − 1/a = {1 - 1 / a:.4f} に近づく" if per == 1 else
       f"{per} つの値をくり返す（周期 {per}）" if per else "くり返しが見つからない（カオス）")
m = st.columns(3)
m[0].metric("ふるまい", msg)
m[1].metric(f"x_{N}", f"{xs[-1]:.6f}")
m[2].metric("特性方程式の解（不動点）", f"{1 - 1 / a:.4f}" if a > 1 else "0", delta="x = ax(1 − x) の解", delta_color="off")

tab1, tab2, tab3 = st.tabs(["① 数列の変化とくもの巣図", "② 分岐図", "③ はじめの値のわずかな差（カオス）"])

with tab1:
    fig = make_subplots(rows=1, cols=2, column_widths=[0.55, 0.45], subplot_titles=("xₙ の変化", "くもの巣図（y = ax(1 − x) と y = x）"))
    fig.add_trace(go.Scatter(x=list(range(N + 1)), y=xs, mode="lines+markers", marker=dict(size=4), line=dict(color="#1f77b4", width=1.5),
                             hovertemplate="n = %{x}：%{y:.5f}<extra></extra>"), row=1, col=1)
    gx = [i / 200 for i in range(201)]
    fig.add_trace(go.Scatter(x=gx, y=[a * x * (1 - x) for x in gx], mode="lines", line=dict(color="#2ca02c", width=2), hoverinfo="skip"), row=1, col=2)
    fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", line=dict(color="#999", dash="dot"), hoverinfo="skip"), row=1, col=2)
    cx, cy = [xs[0]], [0.0]
    for n in range(min(N, 120)):
        cx += [xs[n], xs[n + 1]]; cy += [xs[n + 1], xs[n + 1]]
    fig.add_trace(go.Scatter(x=cx, y=cy, mode="lines", line=dict(color="#d62728", width=1.2), hoverinfo="skip"), row=1, col=2)
    fig.update_xaxes(title_text="n", row=1, col=1)
    fig.update_yaxes(range=[0, 1.02], row=1, col=1)
    fig.update_xaxes(range=[0, 1], title_text="xₙ", row=1, col=2)
    fig.update_yaxes(range=[0, 1.02], title_text="xₙ₊₁", row=1, col=2)
    fig.update_layout(height=420, template="plotly_white", showlegend=False, margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig, key="lg_series")
    st.caption("くもの巣図：曲線で xₙ から xₙ₊₁ を求め、直線 y = x で横に移して次の xₙ にする、をくり返す。"
               "1 点に吸いこまれる（収束）、四角をくり返す（周期 2）、あちこち動き回る（カオス）を見比べよう。")

with tab2:
    A, X = bifurcation(2.5, 4.0, 700, 400, 120)
    fig2 = go.Figure(go.Scattergl(x=A, y=X, mode="markers", marker=dict(size=1.6, color="rgba(31,119,180,0.35)"), hoverinfo="skip"))
    fig2.add_vline(x=a, line_color="#d62728", annotation_text=f"いまの a = {a:g}")
    for v, lab in [(3.0, "3"), (1 + math.sqrt(6), "1+√6"), (3.5699, "3.57…"), (1 + math.sqrt(8), "1+√8")]:
        fig2.add_vline(x=v, line_dash="dot", line_color="gray", annotation_text=lab, annotation_position="bottom")
    fig2.update_layout(height=460, template="plotly_white", margin=dict(l=10, r=10, t=30, b=10),
                       xaxis=dict(title="係数 a", range=[2.5, 4.0]), yaxis=dict(title="十分くり返したあとの xₙ", range=[0, 1]))
    st.plotly_chart(fig2, key="lg_bif")
    st.caption("横軸の a ごとに、十分くり返したあとの値を点で打った図（分岐図）。a = 3 で 2 つに分かれ、1 + √6 ≈ 3.449 で 4 つ、"
               "さらに 8 つ、16 つ … と分かれる間隔がどんどん短くなり、約 3.5699 でカオスになる。カオスの中にも、1 + √8 ≈ 3.828 付近の「周期 3 の窓」のような規則的な所がある。")

with tab3:
    eps = st.select_slider("2 つ目の数列のはじめの値のずれ", options=[1e-3, 1e-6, 1e-9, 1e-12], value=1e-6, format_func=lambda v: f"{v:g}", key="lg_eps")
    ys = logistic(a, x0 + eps, N)
    fig3 = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.6, 0.4], vertical_spacing=0.08)
    fig3.add_trace(go.Scatter(x=list(range(N + 1)), y=xs, mode="lines", name=f"x₀ = {x0:g}", line=dict(color="#1f77b4")), row=1, col=1)
    fig3.add_trace(go.Scatter(x=list(range(N + 1)), y=ys, mode="lines", name=f"x₀ = {x0:g} + {eps:g}", line=dict(color="#d62728", dash="dash")), row=1, col=1)
    fig3.add_trace(go.Scatter(x=list(range(N + 1)), y=[max(abs(u - v), 1e-17) for u, v in zip(xs, ys)], mode="lines", name="2 つの差",
                              line=dict(color="#9467bd")), row=2, col=1)
    fig3.update_yaxes(type="log", exponentformat="power", title_text="差", row=2, col=1)
    fig3.update_xaxes(title_text="n", row=2, col=1)
    fig3.update_layout(height=480, template="plotly_white", margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=1.08))
    st.plotly_chart(fig3, key="lg_sens")
    st.caption("カオスの a（3.7 や 4.0）では、ほんのわずかなずれが、くり返すたびにほぼ一定の倍率で大きくなり（下のグラフで直線的に増える）、"
               "数十回後にはまったく別の値になる。収束する a（2.8 など）では、ずれは小さくなっていく。")

with st.expander("📖 解説：a によるふるまいの変化"):
    st.markdown(
        r"""
| a の範囲 | ふるまい |
|:--|:--|
| $0 < a \le 1$ | 0 に近づく（絶滅） |
| $1 < a \le 3$ | 一定の値 $1 - \dfrac{1}{a}$ に近づく（特性方程式 $x = ax(1 - x)$ の解） |
| $3 < a < 1 + \sqrt{6} \approx 3.449$ | 2 つの値を交互にくり返す（周期 2） |
| $3.449 < a < 3.544\cdots$ | 4 つの値をくり返す（周期 4） |
| …… | 8, 16, 32, … と周期が倍になっていく（周期倍分岐） |
| 約 $3.5699 < a \le 4$ | 多くの $a$ でカオス（規則的なくり返しがない）。ところどころに周期的な「窓」がある |

周期が倍になる $a$ の間隔は、だんだん約 $\dfrac{1}{4.669}$ 倍ずつ短くなる（ファイゲンバウム定数）。この比は、ロジスティック写像に限らず多くの現象で同じになることが知られている。

**なぜ 1 − 1/a か**　一定の値 $\alpha$ に近づくなら $\alpha = a\alpha(1 - \alpha)$。$\alpha \ne 0$ なら $1 = a(1 - \alpha)$ より $\alpha = 1 - \dfrac{1}{a}$。
ただし、$a > 3$ ではこの値のまわりのずれが大きくなっていくので、近づかない（安定でなくなる）。
"""
    )

with st.expander("🔧 どこで使われている？"):
    st.markdown(
        r"""
- **生態学**：生き物の数の年ごとの変化のモデル。生物学者ロバート・メイが 1976 年に、この簡単な式が複雑なふるまいをすることを紹介し、広く知られるようになった。
- **天気予報**：大気の動きもカオスの性質をもつので、はじめの観測のわずかな誤差が大きくなり、遠い先の予報は難しくなる（「バタフライ効果」）。
- **乱数・暗号**：カオスの「予測しにくさ」を利用する研究がある。
- **プログラミング**：コンピュータの数は有限の桁なので、カオスの計算は数十回で誤差が大きくなる（③ のずれ $10^{-12}$ でも同じ）。
"""
    )

with st.expander("📝 考えてみよう"):
    st.markdown(
        r"""
1. $a = 2$、$x_0 = 0.2$ として $x_1, x_2, x_3$ を計算しよう。どんな値に近づくか。
2. $a = 2.8$ のとき、近づく値を $1 - \dfrac{1}{a}$ で求め、グラフと比べよう。
3. $a = 3.2$ のとき、くり返す 2 つの値をグラフから読み取ろう。
"""
    )
    with st.popover("答え"):
        st.markdown(
            r"""
1. $x_1 = 0.32,\ x_2 = 0.4352,\ x_3 \approx 0.4916$。$1 - \dfrac{1}{2} = 0.5$ に近づく
2. $1 - \dfrac{1}{2.8} \approx 0.6429$
3. 約 0.513 と 0.799
"""
        )
