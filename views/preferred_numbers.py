"""【機械】標準数（ルナール数列）— 公比 10^{1/n} の等比数列

部品の寸法や定格の値を段階的に決めるとき、「1 から 10 を n 段に、どの段も同じ倍率で」分けた数を使う。
"""

import math

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.applied import RENARD, nearest, series_n, theoretical

st.sidebar.header("設定")
name = st.sidebar.radio("系列", list(RENARD), index=1, key="pn_series")
x = st.sidebar.number_input("置きかえたい値（任意の正の数）", min_value=0.001, max_value=1e9, value=3.0, step=0.1, format="%.3f", key="pn_x")

n = series_n(name)
vals = RENARD[name]
th = theoretical(n)
q = 10 ** (1 / n)

st.title("標準数（ルナール数列）：公比が一定の等比数列")
st.markdown(
    rf"ねじの長さ、軸の太さ、機械の出力や定格電圧などの値を段階的に用意するとき、"
    rf"**1 から 10 までを同じ倍率で $n$ 段に分けた数** を使います。これを **標準数** といいます"
    rf"（フランスの技術者ルナールが考えた。国際規格 ISO 3、日本では JIS Z 8601）。"
)
with st.container(border=True):
    st.latex(rf"\text{{{name}}}:\quad a_k = 10^{{k/{n}}} = \left(\sqrt[{n}]{{10}}\right)^k \quad (k = 0, 1, \dots, {n - 1}),\qquad"
             rf"\text{{公比}}\ \sqrt[{n}]{{10}} \approx {q:.4f}")

m = st.columns(3)
m[0].metric("段の数", f"{n} 段（1〜10）")
m[1].metric("公比", f"{q:.4f}", delta=f"1 段で約 {100 * (q - 1):.0f}% 増える", delta_color="off")
best, err = nearest(vals, x)
m[2].metric(f"{x:g} に最も近い {name} の数", f"{best:g}", delta=f"ずれ {100 * err:+.1f}%", delta_color="off")

fig = go.Figure()
ks = list(range(n + 1))
fig.add_trace(go.Scatter(x=ks, y=th + [10.0], mode="lines", name="理論値 10^(k/n)", line=dict(color="#9aa0a6", dash="dot")))
fig.add_trace(go.Scatter(x=ks, y=vals + [10.0], mode="markers+text", name=name, marker=dict(color="#d62728", size=9),
                         text=[f"{v:g}" for v in vals + [10.0]] if n <= 20 else None, textposition="top left"))
log_axis = st.toggle("縦軸を対数目盛にする（等比数列が直線に並ぶ）", value=True, key="pn_log")
fig.update_layout(height=400, template="plotly_white", margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=1.05),
                  xaxis=dict(title="段 k", dtick=1 if n <= 20 else 5),
                  yaxis=dict(title="値", type="log" if log_axis else "linear"))
st.plotly_chart(fig, key="pn_chart")
st.caption("対数目盛では、等比数列は等間隔（直線）に並ぶ。値を 10 倍すると次の桁でも同じ並びがくり返される。")

with st.expander(f"{name} の値と理論値の比較"):
    rows = [{"k": k, "標準数": f"{v:.2f}", "理論値 10^(k/n)": f"{t:.4f}", "ずれ": f"{100 * (v - t) / t:+.2f}%",
             "前の数との比": f"{v / vals[k - 1]:.3f}" if k else "—"} for k, (v, t) in enumerate(zip(vals, th))]
    st.dataframe(pd.DataFrame(rows), hide_index=True)
    st.caption("標準数は、理論値を 3 けたに丸めたもの（ずれは 1.3% 以内）。どの段でも「前の数との比」がほぼ同じになっている。")

with st.expander("📖 解説：なぜ等比数列にするのか"):
    st.markdown(
        rf"""
**等差数列で段階を作ると**　1, 2, 3, …, 10 のように同じ差で並べると、1 → 2 は 2 倍なのに 9 → 10 は約 1.1 倍。
小さい所では粗すぎ、大きい所では細かすぎる。

**等比数列で作ると**　どの段も **同じ割合**（{name} なら約 {100 * (q - 1):.0f}%）ずつ大きくなるので、
どんな大きさの所でも同じ細かさで選べる。任意の値を一番近い標準数に置きかえたときのずれも、どこでも同じくらいになる
（{name} では最大で約 ±{100 * (math.sqrt(q) - 1):.0f}%）。

**指数で考えると便利**　標準数は $10^{{k/n}}$ なので、標準数どうしの **積や商も標準数**（指数の和・差になる）。
たとえば R10 で $1.6 \times 2.5 = 10^{{2/10}}\times 10^{{4/10}} = 10^{{6/10}} \approx 4.0$。
寸法を 2 倍・半分にしたり、面積や体積を計算したりしても、標準数の中におさまりやすい。

**粗い系列は細かい系列に含まれる**　R5 ⊂ R10 ⊂ R20 ⊂ R40（R10 の公比の 2 乗が R5 の公比）。
"""
    )

with st.expander("🔧 どこで使われている？"):
    st.markdown(
        r"""
- **電気部品の定格**：ヒューズの定格電流やコンデンサの定格電圧（100, 160, 250, 400, 630 V など：R5）。
- **ねじ・くぎ・軸などの寸法**、機械の出力や容量の段階づけ。
- 電気の **抵抗器の E 系列**（「電気系：E 系列」のページ）も、同じ考え方の等比数列。
- 参考：[Renard series（Wikipedia 英語）](https://en.wikipedia.org/wiki/Renard_series)、JIS Z 8601「標準数」
"""
    )

with st.expander("📝 考えてみよう"):
    st.markdown(
        r"""
1. R5 の公比 $\sqrt[5]{10}$ を小数第 2 位まで求め、1.00, 1.60, 2.50, 4.00, 6.30 と比べよう。
2. R10 で 2.5 の 2 段上の数は何か。$2.5 \times (\sqrt[10]{10})^2$ を計算して確かめよう。
3. R20 の公比を 2 乗すると、どの系列の公比になるか。
"""
    )
    with st.popover("答え"):
        st.markdown(
            r"""
1. $\sqrt[5]{10} \approx 1.58$。$1.58, 2.51, 3.98, 6.31$ を丸めると $1.6, 2.5, 4.0, 6.3$
2. $2.5\times 10^{0.2} \approx 2.5\times1.585 \approx 3.96 \to 4.00$
3. $(10^{1/20})^2 = 10^{1/10}$ なので R10 の公比
"""
        )
