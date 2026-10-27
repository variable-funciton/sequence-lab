"""【ビジネス】積立と複利 — 漸化式 a_{n+1} = (1 + r)a_n + P（ローン返済の逆）"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.applied import savings, savings_closed, savings_payment

MODES = {"forward": "毎月の積立額から、将来の金額を求める", "target": "目標の金額から、毎月の積立額を求める"}
for k, v in dict(sv_mode="forward", sv_P=10000, sv_rate=3.0, sv_years=20, sv_target=5_000_000).items():
    st.session_state.setdefault(k, v)

st.sidebar.header("設定")
mode = st.sidebar.radio("求めるもの", list(MODES), format_func=MODES.get, key="sv_mode")
rate = st.sidebar.number_input("想定利回り（年率）[%]", min_value=0.0, max_value=20.0, step=0.5, format="%.2f", key="sv_rate")
years = int(st.sidebar.number_input("積立期間 [年]", min_value=1, max_value=50, step=1, key="sv_years"))
r = rate / 100 / 12
N = 12 * years
if mode == "forward":
    P = st.sidebar.number_input("毎月の積立額 [円]", min_value=0, max_value=10_000_000, step=1000, key="sv_P")
else:
    target = st.sidebar.number_input("目標の金額 [円]", min_value=10_000, max_value=1_000_000_000, step=100_000, key="sv_target")
    P = savings_payment(target, r, N)

bal = savings(P, r, N)
paid = [P * n for n in range(N + 1)]

st.title("積立と複利：ローン返済の逆向きの漸化式")
st.markdown(
    "毎月決まった額を積み立て、残高に毎月利息がつくとします。$n$ か月後の残高 $a_n$ は、"
    "ローン返済の漸化式の「$-P$（返す）」が「$+P$（積み立てる）」に変わった形になります。"
)
c = st.columns(2)
with c[0], st.container(border=True):
    st.markdown("**積立**（増やす）")
    st.latex(r"a_0 = 0,\qquad a_{n+1} = (1 + r)\,a_n + P")
    st.latex(r"a_n = P\{1 + (1 + r) + \cdots + (1 + r)^{n-1}\} = \frac{P\{(1 + r)^n - 1\}}{r}")
with c[1], st.container(border=True):
    st.markdown("**ローン返済**（減らす）")
    st.latex(r"a_{n+1} = (1 + r)\,a_n - P")
    st.markdown(r"→「漸化式で見るローン返済」のページ。どちらも特性方程式 $\alpha = (1 + r)\alpha \pm P$ で一般項が求められる。")

m = st.columns(4)
m[0].metric("月利 r", f"{100 * r:.4g}%", delta=f"年率 {rate:g}% ÷ 12", delta_color="off")
m[1].metric("毎月の積立額", f"{P:,.0f} 円")
m[2].metric(f"{years} 年後の残高", f"{bal[-1]:,.0f} 円")
m[3].metric("積み立てた元本の合計", f"{paid[-1]:,.0f} 円", delta=f"増えた分 {bal[-1] - paid[-1]:,.0f} 円", delta_color="off")

xs = [n / 12 for n in range(N + 1)]
step = max(1, N // 240)
fig = go.Figure()
fig.add_trace(go.Scatter(x=xs[::step], y=paid[::step], mode="lines", name="積み立てた元本（等差数列）", line=dict(color="#1f77b4", width=2),
                         fill="tozeroy", fillcolor="rgba(31,119,180,0.15)"))
fig.add_trace(go.Scatter(x=xs[::step], y=bal[::step], mode="lines", name="残高（利息を含む）", line=dict(color="#d62728", width=3),
                         fill="tonexty", fillcolor="rgba(214,39,40,0.12)"))
fig.update_layout(height=400, template="plotly_white", margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=1.08),
                  xaxis=dict(title="年"), yaxis=dict(title="円", tickformat=","))
st.plotly_chart(fig, key="sv_chart")
st.caption("青い部分が自分で積み立てた分、赤い部分が利息で増えた分。期間が長いほど、利息の利息（複利）で差が大きくなる。")

with st.expander("年ごとの表"):
    rows = [{"年": y, "残高（漸化式）": f"{bal[12 * y]:,.0f}", "残高（一般項）": f"{savings_closed(P, r, 12 * y):,.0f}",
             "元本": f"{paid[12 * y]:,.0f}", "増えた分": f"{bal[12 * y] - paid[12 * y]:,.0f}"} for y in range(1, years + 1)]
    st.dataframe(pd.DataFrame(rows), hide_index=True)

with st.expander("📖 解説：等比数列の和として見る"):
    st.markdown(
        r"""
$n$ か月後の残高を、1 回ごとの積立に分けて考える。最初の月に積み立てた $P$ は $n - 1$ か月分の利息がついて $P(1 + r)^{n-1}$、
次の月の分は $P(1 + r)^{n-2}$、…、最後の月の分は $P$。これらを足すと、公比 $1 + r$ の等比数列の和：
$$a_n = P + P(1 + r) + \cdots + P(1 + r)^{n-1} = \frac{P\{(1 + r)^n - 1\}}{r}$$

**目標額から逆算**　$n$ か月後に $S$ 円にしたいなら、$S = \dfrac{P\{(1 + r)^n - 1\}}{r}$ を $P$ について解いて
$$P = \frac{Sr}{(1 + r)^n - 1}$$
（ローンの毎月の返済額の式と、形がよく似ている。）

**注意**　実際の投資では利回りは毎年変わり、元本を下回ることもある。このページは「一定の利回りが続いた場合」の計算。
"""
    )

with st.expander("🔧 どこで使われている？"):
    st.markdown(
        r"""
- **積立預金・積立投資（つみたて NISA など）**：毎月の積立額・利回り・期間から将来の金額を見積もる。
- **会社の資金計画**：将来の設備の買いかえに備えて、毎年いくら積み立てるか（減債基金）。
- **年金**：働いている間に積み立て、受け取るときは取りくずす（積立とローン返済の両方の形）。
- 参考：[金融庁「つみたてシミュレーター」](https://www.fsa.go.jp/policy/nisa2/tsumitate-simulator/index.html)
  （計算方法の細かい違いで、このページの結果とはわずかにずれることがある）
"""
    )

with st.expander("📝 考えてみよう"):
    st.markdown(
        r"""
1. 利息がつかない（$r = 0$）とき、毎月 1 万円を 10 年積み立てるといくらになるか。
2. 月利 1% で毎月 1 万円を積み立てる。$a_1, a_2, a_3$ を漸化式で求めよう。
3. 年率 3%（月利 0.25%）で毎月 1 万円を 20 年積み立てると、いくらになるか。このページで確かめよう。
"""
    )
    with st.popover("答え"):
        st.markdown(
            r"""
1. $10000\times120 = 1200000$ 円（等差数列）
2. $a_1 = 10000$、$a_2 = 1.01\times10000 + 10000 = 20100$、$a_3 = 1.01\times20100 + 10000 = 30301$ 円
3. $\dfrac{10000(1.0025^{240} - 1)}{0.0025} \approx 3283000$ 円（元本 240 万円）
"""
        )
