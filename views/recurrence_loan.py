"""漸化式で見るローン返済（後期課題12 対応）

a_{n+1} = (1 + r) a_n − P  を 1 年ずつ進めて、残高の変化を観察する。
"""

from fractions import Fraction

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.sequences import (
    closed_form, fixed_point, fmt_yen, loan_balances, loan_trend, payment_for_target,
    to_frac, years_to_payoff,
)

# ---------------- プリセット（課題12 の設定） ----------------
PRESETS = {
    "自由に設定": None,
    "課題12 第7問：3年で完済する": dict(a0=3310000, rate=10.0, N=3, mode="payoff"),
    "課題12 第8問：残価設定型ローン（残クレ）": dict(a0=3310000, rate=10.0, N=3, mode="residual", aN=1095610),
    "課題12 第9問：毎年100万円ずつ返済": dict(a0=3310000, rate=10.0, N=3, mode="fixed", P=1000000),
    "課題12 第10問：毎年133.1万円ずつ返済": dict(a0=3310000, rate=10.0, N=3, mode="fixed", P=1331000),
    "利息分だけ返し続ける（残高が減らない）": dict(a0=3310000, rate=10.0, N=10, mode="fixed", P=331000),
}
MODES = {
    "payoff": "N 年後に完済する（a_N = 0）",
    "residual": "N 年後に残価を残す（残クレ）",
    "fixed": "毎年の返済額 P を自分で決める",
}
DEFAULTS = dict(rl_a0=3310000, rl_rate=10.0, rl_N=3, rl_mode="payoff", rl_aN=1095610, rl_P=1000000)
for k, v in DEFAULTS.items():
    st.session_state.setdefault(k, v)


def apply_preset():
    p = PRESETS[st.session_state["rl_preset"]]
    if p:
        for k, v in p.items():
            st.session_state[f"rl_{k}"] = v


def latex_num(x) -> str:
    """LaTeX 用の数値（3{,}310{,}000 のような桁区切り）"""
    x = to_frac(x)
    s = f"{x.numerator:,}" if x.denominator == 1 else f"{float(x):,.2f}"
    return s.replace(",", "{,}")


# ---------------- サイドバー ----------------
st.sidebar.header("設定")
st.sidebar.selectbox("例題を読み込む", list(PRESETS), key="rl_preset", on_change=apply_preset)
a0 = st.sidebar.number_input("借入額 a₀（円）", min_value=0, max_value=10**10, step=10000, key="rl_a0")
rate = st.sidebar.number_input("年利 r（%）", min_value=0.0, max_value=50.0, step=0.5, format="%.2f", key="rl_rate")
N = st.sidebar.number_input("期間 N（年）", min_value=1, max_value=50, step=1, key="rl_N")
mode = st.sidebar.radio("返済の仕方", list(MODES), format_func=MODES.get, key="rl_mode")
if mode == "residual":
    aN_target = st.sidebar.number_input("残価 a_N（円）", min_value=0, max_value=10**10, step=10000, key="rl_aN")
if mode == "fixed":
    P_input = st.sidebar.number_input("毎年の返済額 P（円）", min_value=0, max_value=10**10, step=10000, key="rl_P")

r = to_frac(rate) / 100
N = int(N)
if mode == "payoff":
    P = payment_for_target(a0, r, N, 0)
elif mode == "residual":
    P = payment_for_target(a0, r, N, aN_target)
else:
    P = to_frac(P_input)
bal = loan_balances(a0, r, P, N)
alpha = fixed_point(r, P)

# ---------------- 漸化式と結果 ----------------
st.title("漸化式で見るローン返済")
st.markdown(
    "毎年「**利息がついて $(1+r)$ 倍** になり、そこから **$P$ 円返す**」ので、"
    "$n$ 年後の返済残高 $a_n$ は次の漸化式で表されます。"
)
st.latex(r"a_{n+1} = (1 + r)\,a_n - P")
st.latex(
    rf"a_{{n+1}} = {float(1 + r):g}\,a_n - {latex_num(P)},\qquad a_0 = {latex_num(a0)}"
)

c = st.columns(4)
c[0].metric("毎年の返済額 P", fmt_yen(round(P)) if P.denominator != 1 else fmt_yen(P),
            help="端数が出る場合は円未満を四捨五入して表示しています")
c[1].metric(f"{N} 年後の残高 a_{N}", fmt_yen(round(bal[-1])))
c[2].metric("返済額の合計 N×P", fmt_yen(round(N * P)))
c[3].metric("払った利息の合計", fmt_yen(round(N * P + bal[-1] - bal[0])),
            help="返済額の合計 −（借入額 − 残高）")

trend = loan_trend(a0, r, P)
interest0 = r * to_frac(a0)
if a0 == 0:
    st.info("借入額を入力してください。")
elif trend == "decrease":
    yrs = years_to_payoff(a0, r, P)
    if mode == "residual":
        when = f"{N} 年後に残価 {fmt_yen(round(bal[-1]))} が残り、これを一括で払うか車を返却します（残クレ）。"
    elif yrs and yrs <= N:
        when = f"{yrs} 年目に完済します。"
    elif yrs:
        when = f"{N} 年後にはまだ {fmt_yen(round(bal[-1]))} 残っています（このまま払い続けると {yrs} 年目に完済）。"
    else:
        when = ""
    st.success(
        f"返済額 P が1年目の利息 r·a₀ = {fmt_yen(round(interest0))} より大きいので、残高は年々減ります。" + when
    )
elif trend == "constant":
    st.info(f"返済額 P が利息 r·a₀ = {fmt_yen(round(interest0))} とちょうど同じなので、残高は **ずっと変わりません**。")
else:
    st.error(f"返済額 P が利息 r·a₀ = {fmt_yen(round(interest0))} より小さいので、**返しても借金が増えていきます**。")
payoff_year = years_to_payoff(a0, r, P) if trend == "decrease" else None
if payoff_year and payoff_year < N:
    st.info(
        f"{payoff_year} 年目に完済しています。グラフと表のそれ以降の値は、同じ漸化式で計算を続けたもの"
        "（マイナスは返しすぎた額に、さらに利息がついたと考えた値）です。"
    )
if bal[-1] < 0:
    st.warning(f"{N} 年後の残高がマイナス（{fmt_yen(round(bal[-1]))}）です。これは **返しすぎた額**（手元に戻る・利益になる額）を表します。")

# ---------------- 1 年ずつ進める ----------------
st.subheader("1 年ずつ進めてみる")
n_show = st.slider("何年目まで進めるか", 0, N, N) if N > 1 else N

colors = []
for n, b in enumerate(bal):
    if n > n_show:
        colors.append("rgba(160,160,160,0.25)")
    else:
        colors.append("#1f77b4" if b >= 0 else "#2ca02c")
fig = go.Figure(go.Bar(
    x=list(range(N + 1)), y=[float(b) for b in bal], marker_color=colors,
    text=[f"{float(b) / 10000:,.1f}万" if n <= n_show else "" for n, b in enumerate(bal)],
    textposition="outside", cliponaxis=False,
    hovertemplate="a_%{x} = %{y:,.0f} 円<extra></extra>", name="残高 a_n",
))
ymax = max(max(float(b) for b in bal), 0)
ymin = min(min(float(b) for b in bal), 0)
if alpha is not None:
    a_f = float(alpha)
    if ymin - (ymax - ymin) <= a_f <= ymax + (ymax - ymin) * 1.0:
        fig.add_hline(y=a_f, line_dash="dash", line_color="#ff7f0e",
                      annotation_text=f"α = P/r = {a_f:,.0f} 円（この残高だと利息 = 返済）",
                      annotation_position="top left", annotation_font_color="#ff7f0e")
    else:
        st.caption(f"※ α = P/r = {a_f:,.0f} 円 はグラフの範囲外です。")
if mode == "residual":
    fig.add_hline(y=float(aN_target), line_dash="dot", line_color="#9467bd",
                  annotation_text="残価", annotation_position="bottom right")
fig.update_layout(
    height=430, template="plotly_white", margin=dict(l=10, r=10, t=30, b=10), showlegend=False,
    xaxis=dict(title="n（年）", dtick=1 if N <= 20 else 5),
    yaxis=dict(title="返済残高 a_n（円）", tickformat=","),
)
st.plotly_chart(fig, key="loan_bar")

if n_show >= 1:
    prev, cur = bal[n_show - 1], bal[n_show]
    st.latex(
        rf"a_{{{n_show}}} = {float(1 + r):g} \times {latex_num(round(prev))} - {latex_num(round(P))}"
        rf" = {latex_num(round((1 + r) * prev))} - {latex_num(round(P))} = {latex_num(round(cur))}"
    )
    st.caption(f"{n_show} 年目：利息 {fmt_yen(round(r * prev))} がついたあと、{fmt_yen(round(P))} を返済しています。")

with st.expander("年ごとの返済表"):
    rows = [{
        "年 n": n,
        "年初の残高 a_(n−1)": fmt_yen(round(bal[n - 1])),
        "利息 r·a_(n−1)": fmt_yen(round(r * bal[n - 1])),
        "返済 P": fmt_yen(round(P)),
        "年末の残高 a_n": fmt_yen(round(bal[n])),
    } for n in range(1, N + 1)]
    st.dataframe(pd.DataFrame(rows), hide_index=True)

# ---------------- 一般項 ----------------
with st.expander("一般項を求める（特性方程式の考え方）"):
    if r == 0:
        st.markdown("$r = 0$ のときは等差数列 $a_n = a_0 - nP$ です。")
    else:
        st.markdown(
            r"漸化式 $a_{n+1} = (1+r)a_n - P$ で $a_{n+1} = a_n = \alpha$ とおいた **特性方程式** "
            r"$\alpha = (1+r)\alpha - P$ を解くと $\alpha = \dfrac{P}{r}$。"
            r"漸化式から特性方程式を引くと"
        )
        st.latex(r"a_{n+1} - \alpha = (1+r)(a_n - \alpha)")
        st.markdown(r"となり、$\{a_n - \alpha\}$ は公比 $1+r$ の **等比数列** です。よって")
        st.latex(r"a_n = \alpha + (1+r)^n (a_0 - \alpha), \qquad \alpha = \frac{P}{r}")
        st.latex(
            rf"\alpha = \frac{{{latex_num(round(P))}}}{{{float(r):g}}} = {latex_num(round(alpha))}"
            rf",\qquad a_n = {latex_num(round(alpha))} + {float(1 + r):g}^n\,({latex_num(round(to_frac(a0) - alpha))})"
        )
        ok = all(closed_form(a0, r, P, n) == b for n, b in enumerate(bal))
        st.caption("✅ 一般項に n = 0, 1, …, N を代入した値は、漸化式で 1 年ずつ計算した値と一致します。" if ok else "")
        st.markdown(
            r"$a_0 > \alpha$ だと $a_n - \alpha$ が $(1+r)$ 倍ずつ **増え**、"
            r"$a_0 < \alpha$ だと $a_n$ は $\alpha$ から遠ざかるように **減って** いきます。"
            r"$a_N$ に完済（$0$）や残価を代入すれば、返済額 $P$ を求める方程式になります。"
        )
        st.latex(r"P = \frac{r\{(1+r)^N a_0 - a_N\}}{(1+r)^N - 1}")
