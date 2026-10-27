"""【都市】マンションの修繕積立金 — 均等積立と段階増額積立（等差数列とその和）"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.applied import repair_plan

for k, v in dict(rf_total=3_000_000, rf_years=30, rf_ratio=0.5, rf_w1=12, rf_c1=1_200_000, rf_w2=24, rf_c2=1_500_000).items():
    st.session_state.setdefault(k, v)

st.sidebar.header("設定（1 戸あたり）")
total = st.sidebar.number_input("計画期間中に必要な修繕費の合計 [円]", min_value=100_000, max_value=50_000_000, step=100_000, key="rf_total")
years = st.sidebar.select_slider("計画期間 [年]", options=[20, 25, 30, 35, 40], key="rf_years")
step = 5   # 段階増額：5 年ごとに上げる
ratio = st.sidebar.slider("段階増額：はじめの月額（均等積立の何倍か）", 0.2, 1.0, step=0.05, key="rf_ratio")
st.sidebar.markdown("**大規模修繕の支出**")
for _k in ("rf_w1", "rf_w2"):   # 計画期間を短くしたとき、範囲の外に出ないように
    st.session_state[_k] = min(st.session_state[_k], years)
w1 = st.sidebar.slider("1 回目 [年目]", 1, years, key="rf_w1")
c1 = st.sidebar.number_input("1 回目の費用 [円]", min_value=0, max_value=50_000_000, step=100_000, key="rf_c1")
w2 = st.sidebar.slider("2 回目 [年目]", 1, years, key="rf_w2")
c2 = st.sidebar.number_input("2 回目の費用 [円]", min_value=0, max_value=50_000_000, step=100_000, key="rf_c2")

m_eq, stepped, d = repair_plan(total, years, step, ratio)
K = years // step

st.title("マンションの修繕積立金：均等積立と段階増額積立")
st.markdown(
    "マンションでは、外壁の塗り替えや防水工事などの大規模な修繕に備えて、毎月 **修繕積立金** を積み立てます。"
    "国土交通省のガイドラインでは、主に 2 つの積み立て方が説明されています。"
)
c = st.columns(2)
with c[0], st.container(border=True):
    st.markdown("**均等積立方式**：期間中ずっと同じ月額（定数の数列）")
    st.latex(rf"\text{{月額}} = \frac{{{total:,}}}{{12\times{years}}} \approx {m_eq:,.0f}\ \text{{円}}".replace(",", "{,}"))
with c[1], st.container(border=True):
    st.markdown(f"**段階増額積立方式**：はじめは安く、{step} 年ごとに $d$ 円ずつ上げる（**等差数列**）")
    st.latex(rf"a_k = a_1 + (k - 1)d\quad(k = 1, \dots, {K}),\qquad 12\times{step}\times\sum_{{k=1}}^{{{K}}} a_k = {total:,}".replace(",", "{,}"))

m = st.columns(4)
m[0].metric("均等積立の月額", f"{m_eq:,.0f} 円")
m[1].metric("段階増額：はじめの月額", f"{stepped[0]:,.0f} 円")
m[2].metric(f"段階増額：{step} 年ごとの増額 d", f"{d:,.0f} 円")
m[3].metric("段階増額：最後の月額", f"{stepped[-1]:,.0f} 円", delta=f"はじめの {stepped[-1] / stepped[0]:.2f} 倍", delta_color="off")
st.caption(f"等差数列の和の公式：$\\sum_{{k=1}}^{{{K}}} a_k = \\dfrac{{{K}\\{{2a_1 + ({K} - 1)d\\}}}}{{2}}$ から $d$ を求めている。")

ys = list(range(1, years + 1))
spend = {w1: c1}
spend[w2] = spend.get(w2, 0) + c2
bal_eq, bal_st, s_eq, s_st = [], [], 0.0, 0.0
for y in ys:
    s_eq += 12 * m_eq - spend.get(y, 0)
    s_st += 12 * stepped[y - 1] - spend.get(y, 0)
    bal_eq.append(s_eq); bal_st.append(s_st)

fig = go.Figure()
fig.add_trace(go.Bar(x=ys, y=[m_eq] * years, name="均等積立", marker_color="#1f77b4", opacity=0.6))
fig.add_trace(go.Bar(x=ys, y=stepped, name="段階増額積立", marker_color="#ff7f0e", opacity=0.8))
fig.update_layout(barmode="group", height=300, template="plotly_white", margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=1.1),
                  xaxis=dict(title="年目"), yaxis=dict(title="月額 [円]", tickformat=","))
st.plotly_chart(fig, key="rf_month")

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=[0] + ys, y=[0] + bal_eq, mode="lines+markers", name="均等積立の残高", line=dict(color="#1f77b4")))
fig2.add_trace(go.Scatter(x=[0] + ys, y=[0] + bal_st, mode="lines+markers", name="段階増額積立の残高", line=dict(color="#ff7f0e")))
fig2.add_hline(y=0, line_color="#d62728")
for w, cost in ((w1, c1), (w2, c2)):
    if cost:
        fig2.add_vline(x=w, line_dash="dot", line_color="gray", annotation_text=f"{w} 年目 修繕 {cost / 10000:,.0f} 万円")
fig2.update_layout(height=360, template="plotly_white", margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=1.1),
                   xaxis=dict(title="年目"), yaxis=dict(title="積立金の残高 [円]", tickformat=","))
st.plotly_chart(fig2, key="rf_balance")

short_eq = [y for y, b in zip(ys, bal_eq) if b < 0]
short_st = [y for y, b in zip(ys, bal_st) if b < 0]
if short_st and not short_eq:
    st.warning(f"段階増額積立では {short_st[0]} 年目に残高がマイナス（修繕費が足りない）。はじめが安いぶん、早い時期の修繕に間に合わないことがある。")
elif short_eq or short_st:
    st.error(f"残高がマイナスになる年があります（均等：{short_eq[:1] or 'なし'}、段階：{short_st[:1] or 'なし'}）。必要な総額を見直そう。")
else:
    st.success("どちらの方式でも、修繕のときに残高は足りています。")

with st.expander("年ごとの表"):
    rows = [{"年目": y, "均等の月額": f"{m_eq:,.0f}", "段階の月額": f"{stepped[y - 1]:,.0f}", "修繕費": f"{spend.get(y, 0):,}",
             "均等の残高": f"{bal_eq[y - 1]:,.0f}", "段階の残高": f"{bal_st[y - 1]:,.0f}"} for y in ys]
    st.dataframe(pd.DataFrame(rows), hide_index=True)

with st.expander("📖 解説：等差数列の和で増額の幅を決める"):
    st.markdown(
        rf"""
計画期間 {years} 年を {step} 年ずつ {K} 段階に分け、$k$ 段階目の月額を $a_k = a_1 + (k - 1)d$ とする。
1 段階は $12\times{step} = {12 * step}$ か月なので、積み立てる総額は
$${12 * step}\sum_{{k=1}}^{{{K}}} a_k = {12 * step}\times\frac{{{K}\{{2a_1 + ({K} - 1)d\}}}}{{2}}$$
これが必要な総額 $S$ に等しくなるように $d$ を決める：
$$d = \frac{{\dfrac{{S}}{{{12 * step}}} - {K}a_1}}{{\dfrac{{{K}\times{K - 1}}}{{2}}}}$$

**2 つの方式の比べ方**
- 総額は同じ。段階増額は **はじめの負担が軽い** かわりに、後になるほど月額が上がる。
- 段階増額では、値上げのたびに所有者の合意が必要で、合意できずに積立金が不足することがある。
  ガイドラインでは、将来にわたって安定的に積み立てる観点から **均等積立方式が望ましい** としている。
- 早い時期に大きな修繕があると、段階増額では残高が足りなくなりやすい（上のグラフで確かめよう）。
"""
    )

with st.expander("🔧 どこで使われている？"):
    st.markdown(
        r"""
- **マンションの長期修繕計画**：30 年以上の計画期間で、いつ・どんな工事に・いくらかかるかを見積もり、積立金の額を決める。
- **道路・橋・上下水道などのインフラ** でも、将来の修繕・更新の費用を見積もって、計画的に予算を確保する（アセットマネジメント）。
- このページの金額は説明のための例。実際の目安は国土交通省のガイドラインを参照。
- 参考：[国土交通省「マンションの修繕積立金に関するガイドライン」（令和6年6月改定）](https://www.mlit.go.jp/jutakukentiku/house/content/001747009.pdf)
"""
    )

with st.expander("📝 考えてみよう"):
    st.markdown(
        r"""
1. 30 年で 1 戸あたり 360 万円を積み立てる。均等積立の月額はいくらか。
2. 1. を段階増額（5 年ごとに 6 段階）で、はじめの月額を 5000 円にする。毎回いくら上げればよいか。
3. 2. の最後の 5 年間の月額はいくらか。
"""
    )
    with st.popover("答え"):
        st.markdown(
            r"""
1. $\dfrac{3600000}{360} = 10000$ 円
2. $60\times\dfrac{6(2\times5000 + 5d)}{2} = 3600000$ より $10000 + 5d = 20000$、$d = 2000$ 円
3. $a_6 = 5000 + 5\times2000 = 15000$ 円
"""
        )
