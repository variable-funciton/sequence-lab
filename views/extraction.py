"""【化学】溶媒抽出のくり返し・段階希釈 — 1 回ごとに一定の割合が残る等比数列"""

import plotly.graph_objects as go
import streamlit as st

from utils.applied import extraction_limit, extraction_remaining

for k, v in dict(ex_D=4.0, ex_Vw=100.0, ex_Vo=90.0, ex_n=3, dl_c0=1.0, dl_f=10, dl_n=6).items():
    st.session_state.setdefault(k, v)

st.title("溶媒抽出のくり返し・段階希釈：等比数列")
tab1, tab2 = st.tabs(["① 溶媒抽出：少しずつ何回も抽出する", "② 段階希釈：薄めることをくり返す"])

with tab1:
    c = st.columns(4)
    Dk = c[0].number_input("分配比 D", min_value=0.1, max_value=100.0, step=0.5, key="ex_D",
                           help="有機溶媒の中の濃度 ÷ 水の中の濃度")
    Vw = c[1].number_input("水溶液の体積 V_w [mL]", min_value=1.0, max_value=1000.0, step=10.0, key="ex_Vw")
    Vo = c[2].number_input("使える有機溶媒の合計 V_o [mL]", min_value=1.0, max_value=1000.0, step=10.0, key="ex_Vo")
    n = c[3].slider("何回に分けるか n", 1, 10, key="ex_n")

    st.markdown(
        r"水に溶けている物質を、水と混ざらない有機溶媒（エーテルなど）を加えてふり混ぜ、有機溶媒の側へ移す操作が **溶媒抽出** です。"
        r"1 回の抽出で水に残る割合 $q$ は一定なので、$n$ 回くり返すと残る割合は **$q^n$**（公比 $q$ の等比数列）。"
    )
    with st.container(border=True):
        st.latex(r"q = \frac{V_w}{D\,v + V_w}\quad(v = \tfrac{V_o}{n}\ \text{：1 回に使う有機溶媒}),\qquad \text{水に残る割合} = q^n")
    rem1, remn = extraction_remaining(Dk, Vw, Vo, 1), extraction_remaining(Dk, Vw, Vo, n)
    m = st.columns(3)
    m[0].metric("1 回で全部使う", f"{100 * rem1:.2f}% 残る", delta=f"抽出 {100 * (1 - rem1):.2f}%", delta_color="off")
    m[1].metric(f"{n} 回に分ける", f"{100 * remn:.2f}% 残る", delta=f"抽出 {100 * (1 - remn):.2f}%", delta_color="off")
    m[2].metric("限りなく細かく分けると", f"{100 * extraction_limit(Dk, Vw, Vo):.2f}% 残る")

    ns = list(range(1, 11))
    fig = go.Figure()
    fig.add_trace(go.Bar(x=ns, y=[100 * extraction_remaining(Dk, Vw, Vo, k) for k in ns], marker_color=["#d62728" if k == n else "#1f77b4" for k in ns],
                         hovertemplate="%{x} 回に分ける：%{y:.2f}% 残る<extra></extra>"))
    fig.add_hline(y=100 * extraction_limit(Dk, Vw, Vo), line_dash="dot", line_color="#2ca02c", annotation_text="限りなく細かく分けたとき")
    fig.update_layout(height=320, template="plotly_white", margin=dict(l=10, r=10, t=30, b=10), showlegend=False,
                      xaxis=dict(title="同じ量の溶媒を何回に分けるか", dtick=1), yaxis=dict(title="水に残る割合 [%]", rangemode="tozero"))
    st.plotly_chart(fig, key="ex_chart")
    st.caption("同じ量の溶媒でも、何回かに分けて抽出したほうが多く取り出せる。ただし回数を増やしても、ある値より少なくはならない。")

    with st.expander("📖 解説：1 回で残る割合 q の求め方"):
        st.markdown(
            r"""
水 $V_w$ mL に物質が $m$ あり、有機溶媒 $v$ mL を加えてふり混ぜたら、水に $x$ 残ったとする。
分配比 $D$ は「有機溶媒の濃度 ÷ 水の濃度」なので
$$D = \frac{(m - x)/v}{x/V_w}\quad\Longrightarrow\quad x = m\cdot\frac{V_w}{Dv + V_w} = mq$$
水の側はそのままにして、新しい有機溶媒でくり返すと、毎回 $q$ 倍になるので $n$ 回後は $mq^n$。

**分けたほうが得な理由**　たとえば $D = 4$、$V_w = 100$ mL、$V_o = 90$ mL のとき
- 1 回（90 mL）：$q = \dfrac{100}{360 + 100} \approx 0.217$
- 3 回（30 mL ずつ）：$q^3 = \left(\dfrac{100}{120 + 100}\right)^3 \approx 0.094$

**極限**　$n \to \infty$ のとき $\left(\dfrac{1}{1 + \frac{DV_o}{nV_w}}\right)^n \to e^{-DV_o/V_w}$（$e \approx 2.718$。2 年生以降で学ぶ）。
"""
        )

with tab2:
    c = st.columns(3)
    c0 = c[0].number_input("もとの濃度 c₀ [mol/L]", min_value=0.001, max_value=100.0, step=0.1, format="%.3f", key="dl_c0")
    f = c[1].select_slider("1 回で何倍に薄めるか", options=[2, 5, 10, 100], key="dl_f")
    nd = c[2].slider("くり返す回数", 1, 12, key="dl_n")
    st.markdown(
        r"一定の倍率で薄めることをくり返すと、濃度は **公比 $\dfrac{1}{f}$ の等比数列**。"
        r"細菌の数を数える、標準液を作る、などで使われます（**段階希釈**）。"
    )
    with st.container(border=True):
        st.latex(rf"c_n = c_0\left(\frac{{1}}{{{f}}}\right)^n,\qquad c_{{{nd}}} = {c0:g}\times\left(\frac{{1}}{{{f}}}\right)^{{{nd}}} = {c0 * (1 / f) ** nd:.3e}\ \text{{mol/L}}")
    ks = list(range(nd + 1))
    fig2 = go.Figure(go.Scatter(x=ks, y=[c0 * (1 / f) ** k for k in ks], mode="lines+markers", line=dict(color="#9467bd")))
    fig2.update_layout(height=300, template="plotly_white", margin=dict(l=10, r=10, t=30, b=10),
                       xaxis=dict(title="薄めた回数 n", dtick=1), yaxis=dict(title="濃度 [mol/L]（対数目盛）", type="log", exponentformat="power"))
    st.plotly_chart(fig2, key="dl_chart")
    st.caption("対数目盛では、等比数列は直線になる。10 倍希釈なら 1 回ごとに 1 けたずつ下がる。")
    with st.expander("📖 解説：pH や細菌数とのつながり"):
        st.markdown(
            r"""
- **pH**：強い酸の水溶液を 10 倍に薄めると、水素イオンの濃度が $\dfrac{1}{10}$ になり、pH は 1 大きくなる（十分に濃いうち）。
  10 倍希釈をくり返すと pH は 1, 2, 3, … と **等差数列** に（濃度は等比数列、pH はその指数）。
- **細菌の数を数える**：10 倍希釈を何回かくり返して、数えられる数（数十〜数百個）まで薄めてから培養し、
  数えた数に $10^n$ をかけてもとの数を求める。
"""
        )

with st.expander("🔧 どこで使われている？"):
    st.markdown(
        r"""
- **溶媒抽出**：植物から香りや薬の成分を取り出す、分析の前に目的の物質だけを集める、金属の精製など。
- **段階希釈**：検量線用の標準液づくり、微生物検査、薬の濃度の調整。
- 同じ「1 回ごとに一定の割合が残る」考え方は、**洗濯のすすぎ**（少ない水で何回もすすぐほうがよく落ちる）にも当てはまる。
- 参考：分析化学の教科書の「溶媒抽出」の章（分配比と抽出率）
"""
    )

with st.expander("📝 考えてみよう"):
    st.markdown(
        r"""
1. 1 回の抽出で物質の 60% が有機溶媒に移る。同じ操作を 3 回くり返すと、水に残るのは何 % か。
2. 1. で、水に残る量を 1% 以下にするには何回くり返せばよいか。
3. 濃度 1 mol/L の溶液を 10 倍希釈で 4 回薄めると何 mol/L か。
"""
    )
    with st.popover("答え"):
        st.markdown(
            r"""
1. 毎回 40% 残るので $0.4^3 = 0.064$、6.4%
2. $0.4^4 = 0.0256$、$0.4^5 = 0.01024$、$0.4^6 \approx 0.0041$ より 6 回
3. $1\times\left(\dfrac{1}{10}\right)^4 = 10^{-4}$ mol/L
"""
        )
