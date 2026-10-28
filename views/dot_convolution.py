"""数列の内積と畳み込み — Σ a_k b_k と Σ a_k b_{n−k}"""

import math
import random
from fractions import Fraction

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.anim import render as render_anim
from utils.convolution import conv_terms, convolve, dice_dist, dot, moving_average, multiply_digits, parse_seq, pascal


def ftxt(x) -> str:
    x = Fraction(x)
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


st.title("数列の内積と畳み込み")
st.markdown(
    r"2 つの数列 $\{a_k\}$、$\{b_k\}$ から新しい数を作る、2 つの大切な「掛けて足す」計算です。"
    r"**内積** は同じ番号どうしを掛けて足し、**畳み込み** は番号の和が $n$ になる組を掛けて足します。"
)
c = st.columns(2)
with c[0], st.container(border=True):
    st.markdown("**内積**（同じ番号どうし）")
    st.latex(r"a_1b_1 + a_2b_2 + \cdots + a_mb_m = \sum_{k=1}^{m} a_k b_k")
with c[1], st.container(border=True):
    st.markdown("**畳み込み**（番号の和が $n$）")
    st.latex(r"c_n = a_0b_n + a_1b_{n-1} + \cdots + a_nb_0 = \sum_{k=0}^{n} a_k b_{n-k}")

tab1, tab2, tab3, tab4 = st.tabs(["① 内積", "② 畳み込みのしくみ", "③ 畳み込みの例", "④ 積立・薬・回路も畳み込み"])

# ================================================================
DOT_EX = {
    "買い物の合計（単価 × 個数）": ("120, 80, 300, 150", "3, 5, 1, 2", "単価 [円]", "個数"),
    "成績の重みつき平均（点数 × 重み）": ("70, 85, 60, 90", "0.4, 0.3, 0.2, 0.1", "点数", "重み（合計 1）"),
    "同じ向き・反対向き（似ているか）": ("1, 2, 3, 2, 1", "1, 2, 3, 2, 1", "数列 a", "数列 b"),
    "自分で入れる": ("1, 2, 3", "4, 5, 6", "数列 a", "数列 b"),
}
with tab1:
    ex = st.selectbox("例", list(DOT_EX), key="dc_dotex")
    sa, sb, la, lb = DOT_EX[ex]
    cc = st.columns(2)
    ta = cc[0].text_input(la, value=sa, key=f"dc_da_{ex}")
    tb = cc[1].text_input(lb, value=sb, key=f"dc_db_{ex}")
    try:
        a, b = parse_seq(ta), parse_seq(tb)
    except (ValueError, ZeroDivisionError):
        st.error("数をコンマで区切って入れてください（例：1, 2, 3 や 1/2, 1/3）")
        st.stop()
    m = min(len(a), len(b))
    if len(a) != len(b):
        st.warning(f"長さがちがうので、はじめの {m} 項どうしで計算します。")
    v = dot(a, b)
    st.latex(r"\sum a_k b_k = " + " + ".join(rf"{ftxt(x)}\times{ftxt(y)}" for x, y in zip(a, b)) + rf" = {ftxt(v)}" + (rf" \approx {float(v):.4g}" if Fraction(v).denominator != 1 else ""))
    na, nb = math.sqrt(float(dot(a, a))), math.sqrt(float(dot(b, b)))
    mm = st.columns(3)
    mm[0].metric("内積", f"{float(v):,.6g}")
    mm[1].metric("それぞれの長さ √(Σaₖ²)、√(Σbₖ²)", f"{na:.4g}、{nb:.4g}")
    cos = float(v) / (na * nb) if na and nb else float("nan")
    mm[2].metric("似ている度合い（内積 ÷ 長さの積）", f"{cos:.4f}" if na and nb else "—", delta="1 で同じ向き、0 で無関係、−1 で反対", delta_color="off")
    fig = go.Figure()
    ks = list(range(1, m + 1))
    fig.add_trace(go.Bar(x=ks, y=[float(x) for x in a[:m]], name=la, marker_color="#1f77b4"))
    fig.add_trace(go.Bar(x=ks, y=[float(y) for y in b[:m]], name=lb, marker_color="#ff7f0e"))
    fig.add_trace(go.Bar(x=ks, y=[float(x * y) for x, y in zip(a, b)], name="積 aₖbₖ", marker_color="#d62728"))
    fig.update_layout(barmode="group", height=320, template="plotly_white", margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=1.1),
                      xaxis=dict(title="k", dtick=1))
    st.plotly_chart(fig, key="dc_dot")
    st.caption("赤い棒（積）をすべて足したものが内積。")
    with st.expander("📖 内積の見方：似ている度合いと、三角関数の直交"):
        st.markdown(
            r"""
**似ている度合い**　内積を、それぞれの長さ $\sqrt{a_1^2 + \cdots + a_m^2}$、$\sqrt{b_1^2 + \cdots + b_m^2}$ の積で割った値は、
いつも $-1$ 以上 $1$ 以下になる（コーシー・シュワルツの不等式）。2 年生で学ぶベクトルの内積 $|\vec{a}||\vec{b}|\cos\theta$ の $\cos\theta$ にあたる。
音声や画像が「どれだけ似ているか」を調べるときに使われる。

**三角関数の直交**　1 周期を $N$ 等分した点の $\sin$ の値を並べた数列どうしの内積は、振動数がちがえば 0 になる：
$$\sum_{k=0}^{N-1} \sin\frac{2\pi pk}{N}\,\sin\frac{2\pi qk}{N} = 0\quad(p \ne q)$$
これが、三角関数のアプリの「三角関数の足し合わせ（フーリエ級数）」で、波からそれぞれの振動数の成分を取り出すしくみ。
"""
        )
        Nn = 12
        p_, q_ = st.columns(2)
        p = p_.slider("p", 1, 5, 1, key="dc_p")
        q = q_.slider("q", 1, 5, 2, key="dc_q")
        sp = [math.sin(2 * math.pi * p * k / Nn) for k in range(Nn)]
        sq = [math.sin(2 * math.pi * q * k / Nn) for k in range(Nn)]
        st.write(f"N = {Nn} のとき、内積 = {sum(x * y for x, y in zip(sp, sq)):.6f}" + ("（p = q なら N/2 = 6）" if p == q else "（p ≠ q なので 0）"))

# ================================================================
CONV_EX = {
    "さいころ 2 個の目の和（の場合の数）": ("1, 1, 1, 1, 1, 1", "1, 1, 1, 1, 1, 1"),
    "(1 + 2x + 3x²)(1 + x + x² + x³) の係数": ("1, 2, 3", "1, 1, 1, 1"),
    "3 つずつの移動平均（データをならす）": ("2, 8, 3, 9, 4, 10, 5", "1/3, 1/3, 1/3"),
    "自分で入れる": ("1, 2, 1", "1, 3"),
}
with tab2:
    ex2 = st.selectbox("例", list(CONV_EX), key="dc_convex")
    sa, sb = CONV_EX[ex2]
    cc = st.columns(2)
    ta = cc[0].text_input("数列 a₀, a₁, …", value=sa, key=f"dc_ca_{ex2}")
    tb = cc[1].text_input("数列 b₀, b₁, …", value=sb, key=f"dc_cb_{ex2}")
    try:
        a, b = parse_seq(ta), parse_seq(tb)
    except (ValueError, ZeroDivisionError):
        st.error("数をコンマで区切って入れてください")
        st.stop()
    if len(a) + len(b) > 30:
        st.warning("項が多いので、はじめの 15 項ずつにします。")
        a, b = a[:15], b[:15]
    cv = convolve(a, b)
    st.markdown("**アニメーション**　b を左右に反転して 1 つずつずらし、a と重なった所を掛けて足すと、cₙ が 1 つずつできていきます。")
    render_anim("convolution", dict(a=[float(x) for x in a], b=[float(x) for x in b], atext=[ftxt(x) for x in a], btext=[ftxt(x) for x in b]), height=600)
    st.latex(r"c = (" + r",\ ".join(ftxt(x) for x in cv) + ")")
    st.caption(f"長さ {len(a)} と長さ {len(b)} の数列を畳み込むと、長さ {len(a)} + {len(b)} − 1 = {len(cv)} の数列になる。")
    with st.expander("多項式の掛け算と同じ"):
        st.markdown(
            r"""
$a$ を多項式 $a_0 + a_1x + a_2x^2 + \cdots$、$b$ を $b_0 + b_1x + \cdots$ の係数と考えると、積の $x^n$ の係数は、
$x^k$ と $x^{n-k}$ を掛けた項を集めたもの $\sum a_kb_{n-k}$ ＝ **畳み込み** $c_n$。展開の計算そのもの。
"""
        )
        def poly_str(s):  # noqa: E306
            terms = []
            for i, x in enumerate(s):
                if x == 0:
                    continue
                coef = ftxt(x)
                t = coef if i == 0 else (("" if coef == "1" else coef) + ("x" if i == 1 else f"x^{{{i}}}"))
                terms.append(t)
            return " + ".join(terms).replace("+ -", "- ") or "0"
        st.latex(rf"({poly_str(a)})({poly_str(b)}) = {poly_str(cv)}")

# ================================================================
with tab3:
    sub = st.radio("例", ["さいころの目の和", "パスカルの三角形", "移動平均", "掛け算の筆算"], horizontal=True, key="dc_sub")
    if sub == "さいころの目の和":
        nd = st.slider("さいころの個数", 1, 10, 2, key="dc_nd")
        d = dice_dist(nd)
        st.markdown(rf"1 個の確率 $\left(\frac{{1}}{{6}}, \dots, \frac{{1}}{{6}}\right)$ を **{nd} 回畳み込む** と、{nd} 個の目の和の確率になる"
                    r"（和が $n$ になるのは、1 個目が $k$、残りが $n - k$ の場合をすべて足したもの）。")
        sums = list(range(nd, 6 * nd + 1))
        fig = go.Figure(go.Bar(x=sums, y=[float(p) for p in d], marker_color="#1f77b4", hovertemplate="和 %{x}：%{y:.4f}<extra></extra>"))
        mu, var = 3.5 * nd, 35 / 12 * nd
        gx = [nd + (5 * nd) * i / 200 for i in range(201)]
        fig.add_trace(go.Scatter(x=gx, y=[math.exp(-(x - mu) ** 2 / (2 * var)) / math.sqrt(2 * math.pi * var) for x in gx], mode="lines",
                                 line=dict(color="#d62728", dash="dot"), name="正規分布（つりがね形）"))
        fig.update_layout(height=340, template="plotly_white", margin=dict(l=10, r=10, t=30, b=10), showlegend=False,
                          xaxis=dict(title="目の和"), yaxis=dict(title="確率"))
        st.plotly_chart(fig, key="dc_dice")
        if nd == 2:
            st.caption("2 個なら、和が 7 になる確率が最大で 6/36 = 1/6。")
        st.caption("個数をふやすと、つりがね形（点線の正規分布）に近づいていく（中心極限定理）。")
    elif sub == "パスカルの三角形":
        nr = st.slider("何段目まで", 1, 15, 8, key="dc_nr")
        rows = pascal(nr)
        st.markdown(r"$(1, 1)$ を何回も畳み込むと、$(1 + x)^n$ の係数（二項係数）が出てくる。前の段と $(1, 1)$ の畳み込みは「となりどうしを足す」こと。")
        st.markdown("<div style='font-family:monospace;text-align:center;line-height:1.7'>" +
                    "<br>".join(" ".join(f"{v}" for v in r) for r in rows) + "</div>", unsafe_allow_html=True)
    elif sub == "移動平均":
        w = st.slider("何日の平均か（幅 w）", 1, 15, 7, key="dc_w")
        rng = random.Random(3)
        days = list(range(1, 91))
        data = [15 + 8 * math.sin(2 * math.pi * (d - 20) / 120) + rng.gauss(0, 2.5) for d in days]
        ma = moving_average(data, w)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=days, y=data, mode="lines+markers", marker=dict(size=4), line=dict(color="#9aa0a6"), name="毎日の値"))
        fig.add_trace(go.Scatter(x=days[w - 1:], y=ma, mode="lines", line=dict(color="#d62728", width=3), name=f"{w} 日の移動平均"))
        fig.update_layout(height=340, template="plotly_white", margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=1.1),
                          xaxis=dict(title="日"), yaxis=dict(title="値（例：気温）"))
        st.plotly_chart(fig, key="dc_ma")
        st.caption(f"(1/{w}, …, 1/{w}) との畳み込み。細かい上下（ノイズ）がならされ、大きな変化が見やすくなる。株価や感染者数のグラフでもよく使われる。")
    else:
        cc = st.columns(2)
        x = int(cc[0].number_input("かけられる数", min_value=1, max_value=10 ** 8, value=123, key="dc_x"))
        y = int(cc[1].number_input("かける数", min_value=1, max_value=10 ** 8, value=45, key="dc_y"))
        raw, digits, prod = multiply_digits(x, y)
        st.markdown("各けたの数字を（1 の位から）並べた数列どうしを畳み込むと、くり上がりをする前の各けたの値になる。")
        L_ = max(len(raw), len(digits))
        st.dataframe(pd.DataFrame([{"けた": f"10^{i}", "畳み込み（くり上がり前）": raw[i] if i < len(raw) else "",
                                    "くり上がり後": digits[i] if i < len(digits) else ""} for i in range(L_)]), hide_index=True)
        st.success(f"{x} × {y} = {prod}（確かめ：{x * y}）")
        st.caption("大きな数の掛け算をコンピュータで速く行う方法（高速フーリエ変換を使う掛け算）は、この畳み込みを速く計算する工夫。")

# ================================================================
with tab4:
    st.markdown(
        r"""
これまでのページの漸化式も、畳み込みで書けます。**毎回の入力** と、**1 つの入力がその後どう変わるか**（応答）の畳み込みです。

| ページ | 入力 $u_k$ | 1 つの入力の、$j$ 回後の大きさ $h_j$ | 結果 $x_n = \sum u_k h_{n-k}$ |
|:--|:--|:--|:--|
| 積立と複利 | 毎回の積立額 $P$ | $(1 + r)^j$（利息で増える） | $n$ 回目の残高 |
| 薬の繰り返し投与 | 毎回の量 $D$ | $r^j$（体の中で減る） | 飲んだ直後の量 |
| 環境汚染と自浄 | 毎年の流入 $L$ | $(1 - k)^j$（自浄で減る） | 湖の濃度 |
| 過渡現象（RC 回路） | 電源の電圧 | $(1 - h)^j$ | コンデンサの電圧 |

漸化式 $x_{n+1} = px_n + u_n$ をくり返すと $x_n = u_{n-1} + pu_{n-2} + p^2u_{n-3} + \cdots$ となり、$h_j = p^j$ との畳み込みになる。
入力が毎回同じ（$u_k = P$）なら、等比数列の和の公式になる。
"""
    )
    cc = st.columns(3)
    P = cc[0].number_input("毎回の積立額", min_value=0, max_value=100000, value=10000, step=1000, key="dc_P")
    r = cc[1].number_input("1 回の利率 r [%]", min_value=0.0, max_value=20.0, value=5.0, step=0.5, key="dc_r") / 100
    nn = cc[2].slider("回数", 1, 30, 10, key="dc_nn")
    bonus = st.checkbox("5 回目だけ 5 倍積み立てる（入力が毎回同じでなくても計算できる）", key="dc_bonus")
    u = [P * (5 if (bonus and k == 4) else 1) for k in range(nn)]
    h = [(1 + r) ** j for j in range(nn)]
    conv = convolve(u, h)[:nn]
    rec, x_ = [], 0.0
    for k in range(nn):
        x_ = (1 + r) * x_ + u[k]
        rec.append(x_)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=list(range(1, nn + 1)), y=conv, name="畳み込み Σ uₖ (1+r)ⁿ⁻ᵏ", marker_color="#1f77b4"))
    fig.add_trace(go.Scatter(x=list(range(1, nn + 1)), y=rec, mode="markers", name="漸化式 xₙ₊₁ = (1+r)xₙ + uₙ", marker=dict(color="#d62728", size=10, symbol="x")))
    fig.update_layout(height=320, template="plotly_white", margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=1.1),
                      xaxis=dict(title="回数 n"), yaxis=dict(title="残高 [円]", tickformat=","))
    st.plotly_chart(fig, key="dc_save")
    st.caption(f"どちらの計算でも同じ値になる（{nn} 回後：畳み込み {conv[-1]:,.0f} 円、漸化式 {rec[-1]:,.0f} 円）。")
    st.markdown(
        r"""
**どこで使われている？**
- **信号処理・ディジタルフィルタ**：音声のノイズ除去、エコー（反響）の効果、スマートフォンのカメラの画像処理は、入力の数列と「応答」の数列の畳み込み。
- **画像処理・AI**：画像のぼかし・輪郭の強調、画像を認識する AI（畳み込みニューラルネットワーク）。
- **確率**：独立な 2 つの量の和の分布（さいころの和）。
- **建物・機械の振動**：地震の揺れ（入力）と建物の揺れ方（応答）の畳み込みで、建物の揺れを計算する。
"""
    )

with st.expander("📝 考えてみよう"):
    st.markdown(
        r"""
1. $(3, 1, 2)$ と $(2, 4, 5)$ の内積を求めよう。
2. $(1, 2)$ と $(1, 3, 1)$ の畳み込みを求め、$(1 + 2x)(1 + 3x + x^2)$ の展開と比べよう。
3. さいころ 2 個の目の和が 4 になる場合の数を、畳み込み $c_4 = \sum a_kb_{4-k}$ の考え方で数えよう。
"""
    )
    with st.popover("答え"):
        st.markdown(
            r"""
1. $3\cdot2 + 1\cdot4 + 2\cdot5 = 20$
2. $(1,\ 5,\ 7,\ 2)$。$(1 + 2x)(1 + 3x + x^2) = 1 + 5x + 7x^2 + 2x^3$
3. (1 個目, 2 個目) = (1, 3), (2, 2), (3, 1) の 3 通り
"""
        )
