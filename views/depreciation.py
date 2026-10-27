"""【ビジネス】減価償却 — 定額法（等差数列）と定率法（等比数列）"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.applied import declining_balance, pure_declining, straight_line

# 国税庁 No.2106 の例（平成24年4月1日以後に取得、耐用年数 10 年）
LIFE, RATE, REVISED, GUARANTEE = 10, 0.200, 0.250, 0.06552
for k, v in dict(dp_cost=1_000_000).items():
    st.session_state.setdefault(k, v)

st.sidebar.header("設定")
cost = int(st.sidebar.number_input("取得価額 [円]", min_value=10_000, max_value=1_000_000_000, step=10_000, key="dp_cost"))
st.sidebar.caption(f"耐用年数 {LIFE} 年（定額法の償却率 0.100、定率法の償却率 {RATE:.3f}・改定償却率 {REVISED:.3f}・保証率 {GUARANTEE}）")

sl = straight_line(cost, LIFE)
db = declining_balance(cost, LIFE, RATE, REVISED, GUARANTEE)
pure = pure_declining(cost, RATE, LIFE)
book_sl = [cost]
for a in sl:
    book_sl.append(book_sl[-1] - a)
book_db = [cost] + [r[1] - r[3] for r in db]

st.title("減価償却：定額法と定率法")
st.markdown(
    "会社が機械や車などを買ったとき、その代金は買った年だけの費用にせず、**使える年数（耐用年数）に分けて少しずつ費用にします**。"
    "これを **減価償却** といいます。帳簿の上での価値（帳簿価額）の減らし方には、主に 2 つの方法があります。"
)
c = st.columns(2)
with c[0], st.container(border=True):
    st.markdown("**定額法**：毎年 **同じ額** ずつ減らす → 帳簿価額は **等差数列**")
    st.latex(rf"b_n = b_0 - n\times(b_0\times 0.100) = {cost:,} - {int(cost * 0.1):,}\;n".replace(",", "{,}"))
with c[1], st.container(border=True):
    st.markdown("**定率法**：毎年 **残りの額の一定割合** を減らす → 帳簿価額は **等比数列**")
    st.latex(rf"b_n = b_0(1 - {RATE:.1f})^n = {cost:,}\times{1 - RATE:.1f}^{{n}}".replace(",", "{,}"))

switch_year = next(r[0] for r in db if r[4])
m = st.columns(4)
m[0].metric("定額法：毎年の償却費", f"{sl[0]:,} 円")
m[1].metric("定率法：1 年目の償却費", f"{db[0][3]:,} 円")
m[2].metric("定率法：計算を切り替える年", f"{switch_year} 年目")
m[3].metric(f"{LIFE} 年後の帳簿価額", "1 円（どちらも）", delta=f"切り替えないと {pure[-1]:,.0f} 円残る", delta_color="off")

ys = list(range(LIFE + 1))
fig = go.Figure()
fig.add_trace(go.Scatter(x=ys, y=book_sl, mode="lines+markers", name="定額法（等差数列）", line=dict(color="#2ca02c", width=3)))
fig.add_trace(go.Scatter(x=ys, y=book_db, mode="lines+markers", name="定率法（国税庁の計算方法）", line=dict(color="#d62728", width=3)))
fig.add_trace(go.Scatter(x=ys, y=pure, mode="lines", name="切り替えない等比数列", line=dict(color="#d62728", dash="dot")))
fig.add_vline(x=switch_year - 1, line_dash="dash", line_color="gray", annotation_text=f"{switch_year} 年目から切り替え")
fig.update_layout(height=400, template="plotly_white", margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=1.08),
                  xaxis=dict(title="年数 n", dtick=1), yaxis=dict(title="帳簿価額 [円]（年度末）", tickformat=","))
st.plotly_chart(fig, key="dp_book")

with st.expander("年ごとの表（国税庁の計算例と同じ数値になる）", expanded=True):
    rows = []
    for (y, book, pre, a, sw), s in zip(db, sl):
        rows.append({"年": y, "定額法 償却費": f"{s:,}", "定率法 期首帳簿価額": f"{book:,}", "調整前償却額（×0.200）": f"{pre:,.0f}",
                     "償却保証額": f"{cost * GUARANTEE:,.0f}", "定率法 償却費": f"{a:,}", "計算": "改定取得価額×0.250" if sw else "期首帳簿価額×0.200"})
    st.dataframe(pd.DataFrame(rows), hide_index=True)
    st.caption("取得価額 100 万円のとき、7 年目の調整前償却額 52,429 円が償却保証額 65,520 円を下回るので、"
               "7 年目からは改定取得価額 262,144 円 × 0.250 = 65,536 円ずつ償却する（国税庁 No.2106 の例）。最後の年は 1 円を残す。")

with st.expander("📖 解説：等差数列・等比数列と、切り替えが必要な理由"):
    st.markdown(
        r"""
**定額法**　償却費が毎年同じなので、帳簿価額は公差 $-(\text{取得価額}\times\text{償却率})$ の **等差数列**。
償却率は耐用年数の逆数（10 年なら $\dfrac{1}{10} = 0.100$）。

**定率法**　毎年「その年の初めの帳簿価額 × 償却率」を償却するので、帳簿価額は毎年 $(1 - \text{償却率})$ 倍、**公比 0.8 の等比数列**。
償却率は定額法の 2 倍（200% 定率法：$0.100\times2 = 0.200$）。はじめの年に多く償却し、だんだん少なくなる。

**切り替えが必要な理由**　等比数列 $b_0\times0.8^n$ は、何年たっても 0 にならない（10 年後でも約 10.7% 残る）。
そこで、償却額がある額（償却保証額）より小さくなった年からは、その年の帳簿価額（改定取得価額）を残りの年数で
**均等に** 償却する（改定償却率 0.250 ＝ 残り 4 年で割る）。最後は 1 円だけ残して、資産が帳簿に残っていることがわかるようにする。

**どちらを使うか**　機械のように、新しいうちに価値が大きく下がるものは定率法の考え方が実際に近い。
定率法は初めの年の費用が大きいので、その年の利益（税金）を小さくできる。
"""
    )

with st.expander("🔧 どこで使われている？"):
    st.markdown(
        r"""
- **会社の会計・税金の計算**：機械・車・パソコン・建物などの費用を、耐用年数に分けて計上する。
- **設備投資の判断**：「ローン返済で学ぶ漸化式」のページの設備投資のタブと合わせて考えると、借入・返済・費用の関係がわかる。
- 耐用年数ごとの償却率・改定償却率・保証率は、国税庁の表で決められている（このページは耐用年数 10 年の例）。
- 参考：[国税庁 No.2106「定額法と定率法による減価償却（平成19年4月1日以後に取得する場合）」](https://www.nta.go.jp/taxes/shiraberu/taxanswer/shotoku/2106.htm)
"""
    )

with st.expander("📝 考えてみよう"):
    st.markdown(
        r"""
1. 取得価額 100 万円、耐用年数 10 年の機械を定額法で償却する。4 年目の終わりの帳簿価額はいくらか。
2. 同じ機械を、償却率 0.2 の定率法（切り替えなし）で償却する。3 年目の償却費はいくらか。
3. 2. で、帳簿価額が初めて取得価額の半分以下になるのは何年目の終わりか。
"""
    )
    with st.popover("答え"):
        st.markdown(
            r"""
1. 毎年 10 万円なので $100 - 4\times10 = 60$ 万円
2. 2 年目の終わりの帳簿価額は $100\times0.8^2 = 64$ 万円なので、$64\times0.2 = 12.8$ 万円
3. $0.8^3 = 0.512$、$0.8^4 = 0.4096$ より 4 年目の終わり
"""
        )
