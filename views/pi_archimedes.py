"""【プログラミングのための数列】円周率の近似 — アルキメデスの正多角形の漸化式、桁落ち、計算の速さの比較"""

import math

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.models import archimedes, gauss_legendre, pi_digits, side_doubling

@st.cache_data(show_spinner=False)
def series_digits():
    """ライプニッツの級数とバーゼル問題で、項の数 1, 10, …, 10⁶ のときの正しい桁数"""
    lei, bas = [], []
    s_l, s_b = 0.0, 0.0
    targets = {10 ** e for e in range(0, 7)}
    for k in range(1, 10 ** 6 + 1):
        s_l += (1 if k % 2 else -1) / (2 * k - 1)
        s_b += 1 / (k * k)
        if k in targets:
            lei.append((k, pi_digits(4 * s_l)))
            bas.append((k, pi_digits(math.sqrt(6 * s_b))))
    return lei, bas


for k, v in dict(pa_k=2, pa_K=12).items():
    st.session_state.setdefault(k, v)

st.title("円周率の近似：アルキメデスの方法")
st.markdown(
    "紀元前 3 世紀、アルキメデスは、円に内側から接する正多角形（**内接**）と外側から接する正多角形（**外接**）の周の長さで円周をはさみ、"
    "正 6 角形から始めて辺の数を 2 倍ずつ増やして、正 96 角形で $3\\frac{10}{71} < \\pi < 3\\frac{1}{7}$ を示しました。"
    "辺の数を 2 倍にするときの計算は、**2 つの数列の漸化式** になっています。"
)
tab1, tab2, tab3 = st.tabs(["① 正多角形ではさむ", "② プログラムの落とし穴：桁落ち", "③ 計算の速さをくらべる"])

with tab1:
    with st.container(border=True):
        st.markdown(r"直径 1 の円に内接・外接する正 $n$ 角形の周の長さを $a_n$、$b_n$ とする（$a_n < \pi < b_n$）。正 6 角形では $a_6 = 3$、$b_6 = 2\sqrt{3}$。")
        st.latex(r"b_{2n} = \frac{2a_nb_n}{a_n + b_n}\ (\text{調和平均}),\qquad a_{2n} = \sqrt{a_n\,b_{2n}}\ (\text{相乗平均})")
        st.caption("π を一度も使わずに、足し算・掛け算・割り算・平方根だけで計算できる。")
    k = st.slider("辺の数を 2 倍にする回数（図）", 0, 5, key="pa_k")
    rows = archimedes(12)
    n, a, b = rows[k]
    fig = go.Figure()
    th = [2 * math.pi * i / 400 for i in range(401)]
    fig.add_trace(go.Scatter(x=[0.5 * math.cos(t) for t in th], y=[0.5 * math.sin(t) for t in th], mode="lines", line=dict(color="#333", width=2), name="円（直径 1）"))
    pin = [(0.5 * math.cos(2 * math.pi * i / n), 0.5 * math.sin(2 * math.pi * i / n)) for i in range(n + 1)]
    R = 0.5 / math.cos(math.pi / n)
    pout = [(R * math.cos(2 * math.pi * i / n), R * math.sin(2 * math.pi * i / n)) for i in range(n + 1)]
    fig.add_trace(go.Scatter(x=[p[0] for p in pin], y=[p[1] for p in pin], mode="lines", line=dict(color="#1f77b4", width=2), name=f"内接 正{n}角形"))
    fig.add_trace(go.Scatter(x=[p[0] for p in pout], y=[p[1] for p in pout], mode="lines", line=dict(color="#d62728", width=2), name=f"外接 正{n}角形"))
    fig.update_layout(height=420, template="plotly_white", margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=1.08),
                      xaxis=dict(visible=False, range=[-0.62, 0.62]), yaxis=dict(visible=False, range=[-0.62, 0.62], scaleanchor="x"))
    c = st.columns([1.1, 1])
    with c[0]:
        st.plotly_chart(fig, key="pa_poly")
    with c[1]:
        st.metric(f"内接 正{n}角形の周 a_{n}", f"{a:.10f}")
        st.metric(f"外接 正{n}角形の周 b_{n}", f"{b:.10f}")
        st.metric("π をはさむ幅 b − a", f"{b - a:.3e}", delta=f"正しい桁数 {min(pi_digits(a), pi_digits(b))} 桁", delta_color="off")
        if n == 96:
            st.success(f"アルキメデスの結果：3 + 10/71 = {3 + 10 / 71:.6f} < π < 3 + 1/7 = {3 + 1 / 7:.6f}")
    tab = [{"n": f"{nn:,}", "内接 aₙ": f"{aa:.12f}", "外接 bₙ": f"{bb:.12f}", "幅 bₙ − aₙ": f"{bb - aa:.3e}",
            "前との幅の比": f"{(bb - aa) / (rows[i - 1][2] - rows[i - 1][1]):.4f}" if i else "—"} for i, (nn, aa, bb) in enumerate(rows)]
    st.dataframe(pd.DataFrame(tab), hide_index=True)
    st.caption("辺の数を 2 倍にするたびに、幅はほぼ 1/4 になる（公比 1/4 の等比数列に近い）。正しい桁数は 2 回で約 1 桁ずつしか増えない。")

with tab2:
    st.markdown(
        r"""
半径 1 の円に内接する正 $n$ 角形の 1 辺を $s_n$ とすると（$s_6 = 1$）、図形の性質から
$$s_{2n} = \sqrt{2 - \sqrt{4 - s_n^2}}$$
が成り立ちます。周の半分 $\dfrac{n s_n}{2}$ は $\pi$ に近づくはずですが、コンピュータで計算すると……
"""
    )
    K = st.slider("くり返す回数", 5, 35, key="pa_K")
    bad, good = side_doubling(K, False), side_doubling(K, True)
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=list(range(K + 1)), y=[v for _, v in bad], mode="lines+markers", name="そのままの式", line=dict(color="#d62728")))
    fig2.add_trace(go.Scatter(x=list(range(K + 1)), y=[v for _, v in good], mode="lines+markers", name="工夫した式", line=dict(color="#2ca02c")))
    fig2.add_hline(y=math.pi, line_dash="dot", line_color="gray", annotation_text="π")
    fig2.update_layout(height=360, template="plotly_white", margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=1.1),
                       xaxis=dict(title="辺の数を 2 倍にした回数"), yaxis=dict(title="周の半分 n·sₙ/2", range=[2.9, 3.5]))
    st.plotly_chart(fig2, key="pa_bad")
    st.dataframe(pd.DataFrame([{"回数": i, "n": f"{nb:,}", "そのままの式": f"{vb:.15f}", "工夫した式": f"{vg:.15f}"}
                               for i, ((nb, vb), (_, vg)) in enumerate(zip(bad, good)) if i % 2 == 0 or i == K]), hide_index=True)
    st.markdown(
        r"""
**何が起きたか（桁落ち）**　$n$ が大きくなると $s_n$ はとても小さくなり、$\sqrt{4 - s_n^2}$ は 2 にとても近くなります。
コンピュータの小数は **約 16 桁** しか覚えていないので、$2 - (2 \text{ にとても近い数})$ を計算すると、正しい桁がほとんど消えてしまいます。
10 回目あたりから工夫した式とずれはじめ、16 回目からは大きく外れ、最後は 0 になってしまいます（グラフの外に出た点もある）。

**工夫した式**　分子と分母に $\sqrt{2 + \sqrt{4 - s_n^2}}$ をかけて、引き算をなくします（分母の有理化と同じ考え方）。
$$s_{2n} = \sqrt{2 - \sqrt{4 - s_n^2}} = \frac{s_n}{\sqrt{2 + \sqrt{4 - s_n^2}}}$$
数学としては同じ式でも、**プログラムでは計算の順番で結果が変わる** ことがある。
"""
    )

with tab3:
    st.markdown("π を求めるいろいろな方法で、正しい桁数が計算の回数とともにどう増えるかをくらべます。")
    gl = gauss_legendre(6)
    ar = archimedes(40)
    lei_pts, bas_pts = series_digits()
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=[p[0] for p in lei_pts], y=[p[1] for p in lei_pts], mode="lines+markers", name="ライプニッツの級数 1 − 1/3 + 1/5 − …（項の数）"))
    fig3.add_trace(go.Scatter(x=[p[0] for p in bas_pts], y=[p[1] for p in bas_pts], mode="lines+markers", name="バーゼル問題 √(6 Σ 1/n²)（項の数）"))
    fig3.add_trace(go.Scatter(x=list(range(1, 41)), y=[min(pi_digits(a), pi_digits(b)) for _, a, b in ar[1:]], mode="lines+markers", name="アルキメデス（2 倍にした回数）"))
    fig3.add_trace(go.Scatter(x=list(range(1, 7)), y=[pi_digits(x) for x in gl], mode="lines+markers", name="ガウス＝ルジャンドル（くり返しの回数）", line=dict(width=3)))
    fig3.update_layout(height=420, template="plotly_white", margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="v", y=1.0, x=0.01, bgcolor="rgba(255,255,255,0.7)"),
                       xaxis=dict(title="計算の回数（対数目盛）", type="log", exponentformat="power"), yaxis=dict(title="正しい桁数", range=[0, 105]))
    st.plotly_chart(fig3, key="pa_cmp")
    st.caption("アルキメデスの方法はふつうの小数（約 16 桁）で計算しているので、16 桁くらいで止まる。ガウス＝ルジャンドルは 120 桁の小数で計算。")
    st.markdown(
        r"""
| 方法 | 正しい桁数の増え方 | 10 桁にするには |
|:--|:--|:--|
| ライプニッツの級数 $\dfrac{\pi}{4} = 1 - \dfrac{1}{3} + \dfrac{1}{5} - \cdots$ | 項を 10 倍にして約 1 桁 | 約 100 億項 |
| バーゼル問題 $\dfrac{\pi^2}{6} = \sum \dfrac{1}{n^2}$ | 項を 10 倍にして約 1 桁 | 約 100 億項 |
| アルキメデス（正多角形） | 2 倍を 1 回で約 0.6 桁（幅が 1/4 倍） | 約 15 回（正 20 万角形くらい） |
| ガウス＝ルジャンドル（算術幾何平均） | 1 回ごとに約 2 倍（ニュートン法と同じ 2 次収束） | 4 回 |

コンピュータで π を何兆桁も計算するときは、ガウス＝ルジャンドルのような **速く収束する漸化式** と、大きな数の掛け算を速くする工夫が使われる。
"""
    )
    st.markdown("**プログラムで書くと**（Python、アルキメデスの方法）")
    st.code("import math\na, b, n = 3.0, 2 * math.sqrt(3), 6     # 正 6 角形\nfor i in range(4):\n    b = 2 * a * b / (a + b)    # 外接（調和平均）\n    a = math.sqrt(a * b)       # 内接（相乗平均）\n    n = 2 * n\n    print(n, a, b)             # 96 角形で 3.1410 < π < 3.1427", language="python")

with st.expander("📝 考えてみよう"):
    st.markdown(
        r"""
1. 正 6 角形の内接・外接の周（直径 1）が $3$ と $2\sqrt{3}$ になることを図で確かめよう。
2. 漸化式で $b_{12}$ と $a_{12}$ を求めよう（$\sqrt{3} \approx 1.732$）。
3. 幅 $b_n - a_n$ が 1 回ごとに約 $\dfrac{1}{4}$ になるとき、幅を $10^{-6}$ より小さくするには、正 6 角形の幅（約 0.46）から何回 2 倍にすればよいか。
"""
    )
    with st.popover("答え"):
        st.markdown(
            r"""
1. 内接正 6 角形の 1 辺は半径と同じ $\dfrac{1}{2}$ なので周は 3。外接正 6 角形の 1 辺は $\dfrac{1}{\sqrt{3}}$ なので周は $2\sqrt{3}$
2. $b_{12} = \dfrac{2\cdot3\cdot2\sqrt{3}}{3 + 2\sqrt{3}} = 12(2 - \sqrt{3}) \approx 3.2154$、$a_{12} = \sqrt{3\times3.2154} \approx 3.1058$
3. $0.46\times\left(\dfrac{1}{4}\right)^k < 10^{-6}$ より $4^k > 4.6\times10^5$。$4^9 \approx 2.6\times10^5$、$4^{10} \approx 1.05\times10^6$ より 10 回
"""
        )
