"""【プログラミングのための数列】ハノイの塔 — 手数の漸化式 T_n = 2T_{n−1} + 1 と、計算時間の爆発"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.anim import render as render_anim
from utils.models import hanoi_counts, human_time

for k, v in dict(hn_n=4, hn_N=64, hn_speed="1 秒に 1 手（人が手で動かす）").items():
    st.session_state.setdefault(k, v)
SPEEDS = {"1 秒に 1 手（人が手で動かす）": 1.0, "1 秒に 100 万手": 1e6, "1 秒に 10 億手（パソコン 1 台の目安）": 1e9,
          "1 秒に 100 京手（スーパーコンピュータの目安）": 1e18}

st.title("ハノイの塔：手数の漸化式と計算時間の爆発")
st.markdown(
    "3 本の棒と、大きさのちがう $n$ 枚の円盤があります。すべての円盤を A から C へ移します。"
    "ルールは「**1 回に 1 枚だけ動かす**」「**小さい円盤の上に大きい円盤をのせない**」の 2 つ。最も少ない手数 $T_n$ はいくつでしょうか。"
)

tab1, tab2, tab3 = st.tabs(["① 動かしてみる", "② 手数の漸化式", "③ 計算時間はどこまで増える？"])

with tab1:
    n = st.slider("円盤の枚数 n", 1, 8, key="hn_n")
    render_anim("hanoi", dict(n=n), height=380)
    st.caption(f"{n} 枚では {2 ** n - 1} 手。下の「しくみ」の 3 つの段階に注目しよう。")

with tab2:
    st.markdown(
        r"""
$n$ 枚を A から C へ移すには、いちばん大きい円盤 $n$ を C へ動かす必要があります。そのためには、

1. 上の $n - 1$ 枚を、いったん B へ移す（$T_{n-1}$ 手）
2. いちばん大きい円盤を C へ動かす（1 手）
3. B の $n - 1$ 枚を C へ移す（$T_{n-1}$ 手）

したがって
"""
    )
    st.latex(r"T_1 = 1,\qquad T_n = 2T_{n-1} + 1")
    st.markdown(
        r"""
**一般項**　両辺に 1 を足すと $T_n + 1 = 2(T_{n-1} + 1)$。$T_n + 1$ は初項 2、公比 2 の等比数列なので
$$T_n + 1 = 2^n,\qquad T_n = 2^n - 1$$
（ローン返済と同じ「特性方程式」の考え方：$\alpha = 2\alpha + 1$ より $\alpha = -1$。）
"""
    )
    rows = [{"n": i, "T_n（漸化式）": f"{t:,}", "2ⁿ − 1": f"{2 ** i - 1:,}"} for i, t in enumerate(hanoi_counts(20), start=1)]
    st.dataframe(pd.DataFrame(rows), hide_index=True, height=300)
    st.markdown("**プログラムで書くと**（Python、再帰呼び出し）")
    st.code(
        "def hanoi(n, a, c, b):          # n 枚を a から c へ（b を使う）\n"
        "    if n == 0:\n"
        "        return 0\n"
        "    k = hanoi(n - 1, a, b, c)     # 上の n-1 枚を b へ\n"
        "    print(n, a, '->', c)          # いちばん大きい円盤を c へ\n"
        "    k += 1\n"
        "    k += hanoi(n - 1, b, c, a)    # n-1 枚を c へ\n"
        "    return k                      # 手数\n\n"
        "print(hanoi(4, 'A', 'C', 'B'))   # 15",
        language="python",
    )
    st.caption("関数の中で同じ関数を呼ぶ（再帰）。プログラムの形が、そのまま漸化式 Tₙ = 2Tₙ₋₁ + 1 になっている。")

with tab3:
    c = st.columns(2)
    Nmax = c[0].slider("円盤の枚数 n（最大）", 10, 100, key="hn_N")
    sp_name = c[1].selectbox("1 秒あたりの手数", list(SPEEDS), key="hn_speed")
    sp = SPEEDS[sp_name]
    T = 2 ** Nmax - 1
    m = st.columns(3)
    m[0].metric(f"{Nmax} 枚の手数", f"{float(T):.3e}" if Nmax > 30 else f"{T:,}")
    m[1].metric("かかる時間", human_time(T / sp))
    m[2].metric("1 枚ふやすと", "手数も時間も約 2 倍")
    st.markdown(
        "**伝説**　インドの寺院には 64 枚の金の円盤があり、僧侶たちが 1 秒に 1 枚ずつ動かしていて、すべて移し終わると世界が終わる……"
        f"という話があります（19 世紀にフランスの数学者リュカがパズルと一緒に広めた話）。$2^{{64}} - 1$ 手を 1 秒に 1 手で動かすと **{human_time(2 ** 64 - 1)}**。"
        "宇宙の年齢（約 138 億年）よりはるかに長い時間です。"
    )
    ns = list(range(1, Nmax + 1))
    fig = go.Figure()
    for name, f, color in [("n（データ量に比例）", lambda k: k, "#2ca02c"), ("n²", lambda k: k * k, "#ff7f0e"),
                           ("n³", lambda k: k ** 3, "#9467bd"), ("2ⁿ − 1（ハノイの塔）", lambda k: 2 ** k - 1, "#d62728")]:
        fig.add_trace(go.Scatter(x=ns, y=[f(k) / sp for k in ns], mode="lines", name=name, line=dict(color=color, width=2.5),
                                 hovertemplate="n = %{x}：%{y:.3g} 秒<extra>" + name + "</extra>"))
    for sec, lab in [(1, "1 秒"), (3600, "1 時間"), (365.25 * 86400, "1 年"), (138e8 * 365.25 * 86400, "宇宙の年齢")]:
        fig.add_hline(y=sec, line_dash="dot", line_color="gray", annotation_text=lab, annotation_position="top left")
    fig.update_layout(height=420, template="plotly_white", margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=1.1),
                      xaxis=dict(title="データの量 n（円盤の枚数）"), yaxis=dict(title=f"計算時間 [秒]（{sp_name.split('（')[0]}）", type="log", exponentformat="power"))
    st.plotly_chart(fig, key="hn_growth")
    st.caption("縦軸は対数目盛。n や n² の時間は少しずつしか増えないが、2ⁿ は n が 1 増えるごとに 2 倍になり、直線的に（＝指数的に）はね上がる。")
    rows = []
    for k in (10, 20, 30, 40, 50, 64, 80, 100):
        if k <= Nmax:
            rows.append({"n": k, "n² の計算": human_time(k * k / sp), "n³ の計算": human_time(k ** 3 / sp), "2ⁿ の計算": human_time((2 ** k - 1) / sp)})
    st.dataframe(pd.DataFrame(rows), hide_index=True)
    with st.expander("📖 解説：計算量とコンピュータの速さ"):
        st.markdown(
            r"""
プログラムの計算にかかる手数が、データの量 $n$ に対してどう増えるかを **計算量** という。

- $n$、$n^2$、$n^3$ のように増える（**多項式**）なら、コンピュータが 1000 倍速くなれば、扱えるデータの量も大きく増やせる。
- $2^n$ のように増える（**指数**）と、コンピュータが 1000 倍速くなっても、扱える $n$ は 10 しか増えない（$2^{10} = 1024$）。

ハノイの塔は「最も少ない手数」が $2^n - 1$ なので、どんな工夫をしても速くはできない。
一方、プログラムの工夫で $2^n$ の計算を $n^2$ に減らせる問題もあり、それを考えるのがアルゴリズムの研究。
**パスワードや暗号の安全性** は、逆に「調べつくすのに $2^n$ 回かかるので、事実上できない」ことを利用している（鍵の長さ $n$ を 1 増やすと、破るのに 2 倍かかる）。
"""
        )

with st.expander("📝 考えてみよう"):
    st.markdown(
        r"""
1. 漸化式 $T_n = 2T_{n-1} + 1$ を使って、$T_1$ から $T_6$ まで求めよう。
2. 1 秒に 1 手で、10 枚のハノイの塔を完成させるのに何分かかるか。
3. 1 秒に 10 億手できるコンピュータで、1 年以内に終わる最大の枚数はいくつか（1 年 ≈ $3.2\times10^7$ 秒、$2^{10} \approx 10^3$）。
"""
    )
    with st.popover("答え"):
        st.markdown(
            r"""
1. $1, 3, 7, 15, 31, 63$
2. $2^{10} - 1 = 1023$ 秒 ≈ 17 分
3. $10^9\times3.2\times10^7 = 3.2\times10^{16}$ 手。$2^{54} \approx 1.8\times10^{16}$、$2^{55} \approx 3.6\times10^{16}$ より 54 枚
"""
        )
