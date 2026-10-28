"""【カオス】テントマップの力学系 — x_{n+1} = f(x_n)、分数で正確に計算する・2 進数で見る・コンピュータの落とし穴"""

import math
import random
from fractions import Fraction

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from utils.tentmap import binary_digits, eventual_period, float_collapse_step, orbit, parse_x0, tent, to_logistic

PRESETS = ["1/7", "1/5", "1/3", "0.3", "2/9", "3/8", "0.123456", "1/11", "5/13"]
for k, v in dict(tc_x0="0.3", tc_N=30, tc_eps=1e-9).items():
    st.session_state.setdefault(k, v)

st.sidebar.header("設定")
st.sidebar.selectbox("初期値の例", PRESETS, index=None, placeholder="選ぶと下の欄に入る", key="tc_pick",
                     on_change=lambda: st.session_state.update(tc_x0=st.session_state["tc_pick"]) if st.session_state["tc_pick"] else None)
s0 = st.sidebar.text_input("初期値 x₀（分数 1/7 や小数 0.3 で、0〜1）", key="tc_x0")
N = st.sidebar.slider("くり返す回数", 5, 80, key="tc_N")
try:
    x0 = parse_x0(s0)
except (ValueError, ZeroDivisionError):
    st.sidebar.error("0 以上 1 以下の分数か小数を入れてください（例：1/7、0.3）")
    x0 = Fraction(3, 10)

st.title("テントマップのカオス力学系")
st.markdown(
    "三角関数のアプリの「テントマップの変換と合成」で扱った関数 $f$ を、**くり返しほどこして数列を作ります**。"
    "式はかんたんな 1 次式なのに、ふるまいはカオス（予測できない動き）になります。"
)
with st.container(border=True):
    st.latex(r"x_{n+1} = f(x_n),\qquad f(x) = \begin{cases} 2x & \left(0 \le x \le \frac{1}{2}\right) \\ 2 - 2x & \left(\frac{1}{2} < x \le 1\right) \end{cases}")

xs = orbit(x0, N)
ep = eventual_period(x0)
tab1, tab2, tab3, tab4, tab5 = st.tabs(["① 数列とくもの巣図", "② 2 進数で見る", "③ わずかな差が 2 倍ずつ広がる", "④ コンピュータの落とし穴", "⑤ ロジスティック写像とのつながり"])


def frac_str(x: Fraction) -> str:
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


with tab1:
    m = st.columns(3)
    m[0].metric("初期値", frac_str(x0))
    if ep:
        pre, per = ep
        m[1].metric("くり返しの周期", f"{per}", delta=(f"{pre} 回目から" if pre else "はじめから"), delta_color="off")
    else:
        m[1].metric("くり返しの周期", "見つからない")
    m[2].metric(f"x_{N}", frac_str(xs[-1]) if xs[-1].denominator < 10 ** 8 else f"{float(xs[-1]):.6f}")
    fig = make_subplots(rows=1, cols=2, column_widths=[0.55, 0.45], subplot_titles=("xₙ の変化", "くもの巣図"))
    fig.add_trace(go.Scatter(x=list(range(N + 1)), y=[float(v) for v in xs], mode="lines+markers", marker=dict(size=5),
                             line=dict(color="#1f77b4", width=1.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=[0, 0.5, 1], y=[0, 1, 0], mode="lines", line=dict(color="#2ca02c", width=2), hoverinfo="skip"), row=1, col=2)
    fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", line=dict(color="#999", dash="dot"), hoverinfo="skip"), row=1, col=2)
    cx, cy = [float(xs[0])], [0.0]
    for n in range(min(N, 60)):
        cx += [float(xs[n]), float(xs[n + 1])]; cy += [float(xs[n + 1]), float(xs[n + 1])]
    fig.add_trace(go.Scatter(x=cx, y=cy, mode="lines", line=dict(color="#d62728", width=1.2), hoverinfo="skip"), row=1, col=2)
    fig.update_yaxes(range=[-0.02, 1.02], row=1, col=1)
    fig.update_xaxes(title_text="n", row=1, col=1)
    fig.update_xaxes(range=[0, 1], title_text="xₙ", row=1, col=2)
    fig.update_yaxes(range=[0, 1.02], title_text="xₙ₊₁", row=1, col=2)
    fig.update_layout(height=400, template="plotly_white", showlegend=False, margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig, key="tc_cob")
    st.dataframe(pd.DataFrame([{"n": n, "xₙ（分数）": frac_str(v) if v.denominator < 10 ** 12 else "（大きな分数）", "小数": f"{float(v):.10f}"}
                               for n, v in enumerate(xs[:41])]), hide_index=True, height=260)
    st.info(
        "**分数で始めると、必ずいつかくり返す**　分母が奇数の分数（1/7、1/5 など）は、分母が変わらないまま 0〜1 の中を動くので、"
        "いつか同じ値にもどって周期的になる。分母が 2 の累乗（3/8 など）なら、いつか 0 になって止まる。"
        "周期が長くなるのは、分母が大きい分数（5/13 で周期 6 など）。"
        "**くり返さない（カオスの）軌道** は、無理数（√2 − 1 など）から始めたときに現れる。"
    )

with tab2:
    st.markdown(
        r"""
$x$ を 2 進数の小数で $x = 0.b_1b_2b_3\cdots$ と表すと、$f$ のはたらきはとても簡単になります。

- $b_1 = 0$（$x \le \frac{1}{2}$）のとき：$2x = 0.b_2b_3b_4\cdots$　→ **1 けた左にずらす**
- $b_1 = 1$（$x > \frac{1}{2}$）のとき：$2 - 2x = 1 - 0.b_2b_3\cdots$　→ **1 けたずらして、0 と 1 を入れかえる**

つまり、$n$ 回後の値は、初期値の **$n + 1$ けた目より後ろ** の数字だけで決まります。
"""
    )
    K = 40
    rows = []
    for n, v in enumerate(xs[:16]):
        b = binary_digits(v, K)
        rows.append(f"<tr><td>{n}</td><td style='font-family:monospace;letter-spacing:1px'>0.<span style='color:#d62728;font-weight:700'>{b[0]}</span>{b[1:]}</td>"
                    f"<td>{'そのまま 1 けたずらす' if b[0] == '0' else '1 けたずらして 0 と 1 を入れかえる'}</td></tr>")
    st.markdown("<table style='font-size:14px'><tr><th>n</th><th>xₙ（2 進数、40 けた）</th><th>次の xₙ₊₁ は</th></tr>" + "".join(rows) + "</table>",
                unsafe_allow_html=True)
    st.caption("赤い数字（1 けた目）が 0 か 1 かで、次の操作が決まる。周期的な分数は 2 進数でもくり返しの模様になっている（1/7 = 0.001001001…）。")

with tab3:
    eps = st.select_slider("2 つ目の初期値のずれ", options=[1e-3, 1e-6, 1e-9, 1e-12], format_func=lambda v: f"{v:g}", key="tc_eps")
    e = Fraction(eps).limit_denominator(10 ** 15)
    y0 = min(Fraction(1), x0 + e)
    ys = orbit(y0, N)
    diff = [float(abs(a - b)) for a, b in zip(xs, ys)]
    fig3 = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.55, 0.45], vertical_spacing=0.08)
    fig3.add_trace(go.Scatter(x=list(range(N + 1)), y=[float(v) for v in xs], mode="lines", name=f"x₀ = {frac_str(x0)}", line=dict(color="#1f77b4")), row=1, col=1)
    fig3.add_trace(go.Scatter(x=list(range(N + 1)), y=[float(v) for v in ys], mode="lines", name=f"x₀ + {eps:g}", line=dict(color="#d62728", dash="dash")), row=1, col=1)
    fig3.add_trace(go.Scatter(x=list(range(N + 1)), y=[max(d, 1e-18) for d in diff], mode="lines+markers", name="2 つの差", line=dict(color="#9467bd")), row=2, col=1)
    fig3.add_trace(go.Scatter(x=list(range(N + 1)), y=[min(1.0, eps * 2 ** n) for n in range(N + 1)], mode="lines", name=f"{eps:g} × 2ⁿ",
                              line=dict(color="#2ca02c", dash="dot")), row=2, col=1)
    fig3.update_yaxes(type="log", exponentformat="power", title_text="差", row=2, col=1)
    fig3.update_xaxes(title_text="n", row=2, col=1)
    fig3.update_layout(height=480, template="plotly_white", margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=1.08))
    st.plotly_chart(fig3, key="tc_sens")
    n_lost = next((n for n, d in enumerate(diff) if d > 0.1), None)
    st.markdown(
        rf"""
傾きが $\pm2$ なので、2 つの値の差は（同じ側にいる間は）**1 回ごとにちょうど 2 倍**：差は公比 2 の等比数列 ${eps:g}\times2^n$。
$2^{{10}} \approx 1000$ なので、10 回ごとに差は約 1000 倍。ずれ ${eps:g}$ は約 {math.ceil(math.log2(0.1 / eps))} 回で 0.1 をこえる
（この例では {n_lost if n_lost is not None else '—'} 回目）。
はじめの値を 10 けた正確に知っていても、約 33 回後には何もわからなくなる。これが **カオス**（初期値に敏感）。
"""
    )

with tab4:
    x_f = float(x0) if x0 not in (0, 1) else 0.3
    fl = [x_f]
    for _ in range(80):
        v = fl[-1]
        fl.append(2 * v if v <= 0.5 else 2 - 2 * v)
    ex = orbit(x0, 80)
    k0 = float_collapse_step(x_f)
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(x=list(range(81)), y=[float(v) for v in ex], mode="lines+markers", name="分数で正確に計算", marker=dict(size=4), line=dict(color="#1f77b4")))
    fig4.add_trace(go.Scatter(x=list(range(81)), y=fl, mode="lines+markers", name="コンピュータの小数（float）で計算", marker=dict(size=4), line=dict(color="#d62728", dash="dash")))
    fig4.update_layout(height=360, template="plotly_white", margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=1.1),
                       xaxis=dict(title="n"), yaxis=dict(title="xₙ", range=[-0.02, 1.02]))
    st.plotly_chart(fig4, key="tc_float")
    st.markdown(
        f"""
コンピュータのふつうの小数（倍精度、float）は、**2 進数で 53 けた** しか覚えていません。テントマップは 1 回ごとに 2 進数を 1 けたずつ左へずらすので、
約 53 回で覚えていた数字を使い切り、**{k0 if k0 else '—'} 回目に 0 になって、その後はずっと 0** になってしまいます（どんな初期値でも同じ）。
分数（Python の `Fraction`）で正確に計算すると、本当のふるまい（周期的、またはカオス）が見えます。
"""
    )
    st.code(f"from fractions import Fraction\n\nx = {x_f!r}                 # 小数で計算すると……\ny = Fraction({x0.numerator}, {x0.denominator})   # 分数で計算すると……\n"
            "for n in range(60):\n    x = 2 * x if x <= 0.5 else 2 - 2 * x\n    y = 2 * y if y <= Fraction(1, 2) else 2 - 2 * y\nprint(x, y)", language="python")

with tab5:
    st.markdown(
        r"""
ロジスティック写像 $x_{n+1} = 4x_n(1 - x_n)$（$a = 4$、「ロジスティック写像とカオス」のページ）は、テントマップと **同じ動き** をしています。
テントマップの値 $y$ を $x = \sin^2\dfrac{\pi y}{2}$ で移すと、

- $y \le \frac{1}{2}$ のとき、$y$ は $2y$ になり、$\sin^2\dfrac{\pi(2y)}{2} = \sin^2\pi y = \left(2\sin\dfrac{\pi y}{2}\cos\dfrac{\pi y}{2}\right)^2 = 4x(1 - x)$（**2 倍角の公式**）
- $y > \frac{1}{2}$ のとき、$y$ は $2 - 2y$ になり、$\sin^2\dfrac{\pi(2 - 2y)}{2} = \sin^2(\pi - \pi y) = \sin^2\pi y$ で、同じく $4x(1 - x)$

つまり「テントマップを 1 回ほどこしてから $\sin^2$ で移す」のと「$\sin^2$ で移してからロジスティック写像を 1 回ほどこす」のが同じ。
三角関数の 2 倍角の公式が、2 つのカオスを結びつけています。
"""
    )
    y = x0 if x0 not in (0, 1) else Fraction(3, 10)
    rows = []
    xl = to_logistic(y)
    for n in range(8):
        rows.append({"n": n, "テントマップ yₙ": f"{float(y):.6f}", "sin²(πyₙ/2)": f"{to_logistic(y):.6f}", "ロジスティック xₙ（a = 4）": f"{xl:.6f}"})
        y = tent(y); xl = 4 * xl * (1 - xl)
    st.dataframe(pd.DataFrame(rows), hide_index=True)
    st.caption("2 列目と 3 列目が一致する（ロジスティック写像は float で計算しているので、くり返すと少しずつずれていく）。")
    rng = random.Random(1)
    ys_ = []
    for _ in range(4000):
        v = Fraction(rng.getrandbits(50), 2 ** 50)
        for _ in range(rng.randint(1, 12)):
            v = tent(v)
        ys_.append(float(v))
    fig5 = make_subplots(rows=1, cols=2, subplot_titles=("テントマップの値の分布（どこも同じくらい）", "ロジスティック写像の値の分布（両端に多い）"))
    fig5.add_trace(go.Histogram(x=ys_, xbins=dict(start=0, end=1, size=0.05), marker_color="#1f77b4", histnorm="probability density"), row=1, col=1)
    fig5.add_trace(go.Histogram(x=[to_logistic(v) for v in ys_], xbins=dict(start=0, end=1, size=0.05), marker_color="#d62728", histnorm="probability density"), row=1, col=2)
    gx = np.linspace(0.01, 0.99, 99)
    fig5.add_trace(go.Scatter(x=gx, y=1 / (np.pi * np.sqrt(gx * (1 - gx))), mode="lines", line=dict(color="#333", dash="dot"), name="1/(π√(x(1−x)))"), row=1, col=2)
    fig5.update_layout(height=330, template="plotly_white", showlegend=False, margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig5, key="tc_hist")
    st.caption("テントマップをくり返した値は 0〜1 に一様に散らばる。sin² で移すと両端に集まる分布（点線）になる。")

with st.expander("🔧 どこで使われている？"):
    st.markdown(
        r"""
- **乱数のしくみ**：コンピュータの乱数も「前の値から次の値を決める漸化式」で作る。カオスのように予測しにくく、かつ周期が非常に長くなるように工夫されている。
- **パン生地をこねる**：のばして折りたたむ操作をくり返すと、近くにあった 2 点が離れていく。テントマップは「のばして折る」の 1 次元版。
- **数値計算の注意**：④ のように、コンピュータの小数には限りがあるので、くり返しの計算では誤差に気をつける必要がある。
"""
    )
    st.page_link("views/logistic.py", label="ロジスティック写像とカオス", icon="🦋")

with st.expander("📝 考えてみよう"):
    st.markdown(
        r"""
1. $x_0 = \dfrac{1}{7}$ から $x_1, x_2, x_3, x_4$ を分数で求めよう。周期はいくつか。
2. $x_0 = \dfrac{3}{8}$ から始めると、何回目に 0 になるか。
3. $x = \dfrac{2}{3}$ は $f(x) = x$ を満たす（不動点）。2 進数で $\dfrac{2}{3} = 0.101010\cdots$ を使って、$f$ で動かないことを確かめよう。
"""
    )
    with st.popover("答え"):
        st.markdown(
            r"""
1. $\dfrac{2}{7}, \dfrac{4}{7}, \dfrac{6}{7}, \dfrac{2}{7}$。$\dfrac{2}{7} \to \dfrac{4}{7} \to \dfrac{6}{7}$ をくり返すので周期 3
2. $\dfrac{3}{8} \to \dfrac{3}{4} \to \dfrac{1}{2} \to 1 \to 0$ より 4 回目
3. 1 けた目が 1 なので、ずらして $0.01010\cdots$、0 と 1 を入れかえて $0.10101\cdots = \dfrac{2}{3}$
"""
        )
