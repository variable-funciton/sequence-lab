"""【情報・AI】文章生成 AI のミニチュア — 晴れ・雨の 2 状態モデルと連立漸化式（マルコフ連鎖）"""

import random

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.anim import render as render_anim
from utils.markov import closed_form, estimate, generate, limit, parse_weather, probs, run_lengths, temperature

for k, v in dict(mk_a=0.7, mk_b=0.4, mk_p1=0.5, mk_N=15).items():
    st.session_state.setdefault(k, v)

st.sidebar.header("AI の確率表（設定）")
a = st.sidebar.slider("晴れ の次に 晴れ を出す確率 a", 0.0, 1.0, step=0.01, key="mk_a")
b = st.sidebar.slider("雨 の次に 晴れ を出す確率 b", 0.0, 1.0, step=0.01, key="mk_b")
st.sidebar.caption(f"晴れ の次に 雨：1 − a = {1 - a:.2f}　／　雨 の次に 雨：1 − b = {1 - b:.2f}")
p1 = st.sidebar.slider("1 つ目に 晴れ を出す確率 p₁（初期条件）", 0.0, 1.0, step=0.05, key="mk_p1")
N = st.sidebar.slider("何個目まで計算するか", 5, 40, key="mk_N")
al = limit(a, b)

st.title("文章生成 AI のミニチュア：確率の漸化式")
st.markdown(
    "文章を作る AI は、「いままでの言葉から、次の言葉を **確率** で選ぶ」ことをくり返して文章を作ります。"
    "ここでは、言葉が「晴れ」と「雨」の 2 つしかない、とても小さな AI を考えます。"
    "この AI は、**直前に出した言葉だけ** を見て、次の言葉を確率で選びます。"
)
c = st.columns(2)
with c[0], st.container(border=True):
    st.markdown("**AI の確率表**（直前の言葉 → 次の言葉）")
    st.dataframe(pd.DataFrame({"次：晴れ": [f"{a:.2f}", f"{b:.2f}"], "次：雨": [f"{1 - a:.2f}", f"{1 - b:.2f}"]}, index=["直前：晴れ", "直前：雨"]))
with c[1]:
    # 状態遷移図
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0, 4], y=[0, 0], mode="markers+text", text=["☀️ 晴れ", "☔ 雨"], textfont=dict(size=16),
                             marker=dict(size=70, color=["#ffe082", "#90caf9"], line=dict(color="#333", width=1.5)), hoverinfo="skip"))
    for (x0, y0, x1, y1, lab, yl) in [(0.55, 0.25, 3.45, 0.25, f"1 − a = {1 - a:.2f}", 0.75), (3.45, -0.25, 0.55, -0.25, f"b = {b:.2f}", -0.75)]:
        fig.add_annotation(x=x1, y=y1, ax=x0, ay=y0, xref="x", yref="y", axref="x", ayref="y", showarrow=True, arrowhead=2, arrowwidth=2, arrowcolor="#555", text="")
        fig.add_annotation(x=2, y=yl, text=lab, showarrow=False, font=dict(size=14))
    for xc, lab, col in [(0, f"a = {a:.2f}", "#f9a825"), (4, f"1 − b = {1 - b:.2f}", "#1e88e5")]:
        fig.add_shape(type="circle", x0=xc - 0.45, x1=xc + 0.45, y0=0.55, y1=1.45, line=dict(color=col, width=2))
        fig.add_annotation(x=xc, y=1.65, text=lab, showarrow=False, font=dict(size=14, color=col))
    fig.update_layout(height=250, template="plotly_white", showlegend=False, margin=dict(l=10, r=10, t=10, b=10),
                      xaxis=dict(visible=False, range=[-1.2, 5.2]), yaxis=dict(visible=False, range=[-1.1, 1.9], scaleanchor="x"))
    st.plotly_chart(fig, key="mk_diagram")

tab1, tab2, tab3, tab4 = st.tabs(["① モデル化と計算", "② AI に言葉を出力させる", "③ AI はどうやって賢くなる？（学習）", "④ 考察"])

with tab1:
    st.markdown(
        r"""
$n$ 個目に「晴れ」を出す確率を $p_n$、「雨」を出す確率を $q_n$ とします。$n + 1$ 個目が「晴れ」になるのは、
**$n$ 個目が晴れで、次に晴れを選ぶ** 場合と、**$n$ 個目が雨で、次に晴れを選ぶ** 場合なので
"""
    )
    st.latex(rf"p_{{n+1}} = a\,p_n + b\,q_n = {a:g}\,p_n + {b:g}\,q_n,\qquad q_{{n+1}} = (1 - a)\,p_n + (1 - b)\,q_n = {1 - a:g}\,p_n + {1 - b:g}\,q_n")
    st.markdown(r"毎回どちらかを出すので $p_n + q_n = 1$。$q_n = 1 - p_n$ を代入すると、**1 つの漸化式** になります（ローン返済と同じ形）。")
    st.latex(rf"p_{{n+1}} = (a - b)\,p_n + b = {a - b:g}\,p_n + {b:g}")
    if al is not None:
        st.markdown(rf"特性方程式 $\alpha = {a - b:g}\alpha + {b:g}$ の解は $\alpha = \dfrac{{b}}{{1 - a + b}} = {al:.4f}$。一般項は")
        st.latex(rf"p_n = {al:.4f} + ({a - b:g})^{{n-1}}\left(p_1 - {al:.4f}\right)")
    else:
        st.warning("a = 1、b = 0 のときは、最初の言葉をずっとくり返すので、p_n = p₁ のまま変わらない。")
    ns = list(range(1, N + 1))
    fig2 = go.Figure()
    for q1, col, name in [(1.0, "#ffb300", "p₁ = 1（はじめは必ず晴れ）"), (0.0, "#1e88e5", "p₁ = 0（はじめは必ず雨）"), (p1, "#d62728", f"p₁ = {p1:g}（設定した値）")]:
        fig2.add_trace(go.Scatter(x=ns, y=probs(a, b, q1, N), mode="lines+markers", name=name, line=dict(color=col, width=3 if q1 == p1 else 1.8)))
    if al is not None:
        fig2.add_hline(y=al, line_dash="dot", line_color="#2ca02c", annotation_text=f"極限 {al:.4f}")
    fig2.update_layout(height=360, template="plotly_white", margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=1.12),
                       xaxis=dict(title="n 個目", dtick=1 if N <= 20 else 5), yaxis=dict(title="晴れを出す確率 pₙ", range=[-0.02, 1.02]))
    st.plotly_chart(fig2, key="mk_pn")
    m = st.columns(3)
    m[0].metric("極限 p（晴れ）", f"{al:.4f}" if al is not None else "—")
    m[1].metric("極限 q（雨）", f"{1 - al:.4f}" if al is not None else "—")
    m[2].metric("公比 a − b", f"{a - b:g}", delta="絶対値が 1 より小さいので収束" if abs(a - b) < 1 else "収束しない", delta_color="off")
    st.caption("どの初期条件から始めても、同じ値に近づく。近づく速さは (a − b)ⁿ で決まる。")
    with st.expander("表"):
        ps = probs(a, b, p1, N)
        st.dataframe(pd.DataFrame([{"n": n, "pₙ（漸化式）": f"{p:.6f}", "pₙ（一般項）": f"{closed_form(a, b, p1, n):.6f}", "qₙ = 1 − pₙ": f"{1 - p:.6f}"}
                                   for n, p in enumerate(ps, start=1)]), hide_index=True)
    st.info("このように「直前の状態だけで、次の状態の確率が決まる」モデルを **マルコフ連鎖** といいます（大学で学ぶ確率論の言葉）。")

with tab2:
    st.markdown("▶ を押すと、AI が確率表にしたがって言葉を 1 つずつ出力します（乱数を使うので、毎回ちがう文章になります）。"
                "下のグラフは、それまでに出力した言葉のうち「晴れ」の割合です。")
    render_anim("markov", dict(a=a, b=b, p1=p1, limit=al), height=470)
    st.caption("たくさん出力すると、晴れの割合は ① で求めた極限に近づく（大数の法則）。式で求めた確率と、AI が実際に作る文章の性質が一致する。")

with tab3:
    st.markdown(
        "確率表の 0.7 や 0.4 は、人が決めるのではありません。たくさんの文章（ここでは天気の記録）から、"
        "**「晴れ」の次に何が来たかを数えて、割合を求める** ことで決まります。これが **学習** のいちばん簡単な形です。"
    )
    txt = st.text_area("天気の記録（「晴」「雨」や ☀ ☔ を並べる）", value="晴晴晴雨雨晴晴雨晴晴晴晴雨雨雨晴晴雨晴晴", key="mk_txt")
    seq = parse_weather(txt)
    if len(seq) < 2:
        st.warning("2 つ以上の天気を入れてください。")
    else:
        cnt, ea, eb = estimate(seq)
        cc = st.columns(2)
        with cc[0]:
            st.dataframe(pd.DataFrame({"次：晴れ": [cnt[(1, 1)], cnt[(0, 1)]], "次：雨": [cnt[(1, 0)], cnt[(0, 0)]]}, index=["直前：晴れ", "直前：雨"]))
            st.caption(f"記録の長さ {len(seq)}（並びの組 {len(seq) - 1} 組）を数えた回数")
        with cc[1]:
            st.metric("学習した a = P(晴れ → 晴れ)", f"{ea:.3f}" if ea is not None else "—")
            st.metric("学習した b = P(雨 → 晴れ)", f"{eb:.3f}" if eb is not None else "—")
            le = limit(ea, eb) if ea is not None and eb is not None else None
            st.metric("この AI がたくさん出力したときの晴れの割合", f"{le:.3f}" if le is not None else "—")
    st.markdown("**データがふえると、学習した確率は本当の確率に近づく**　サイドバーの a、b を「本当の天気の確率」として天気の記録を作り、"
                "記録の長さを変えて学習させてみます。")
    rng = random.Random(5)
    sizes = [10, 30, 100, 300, 1000, 3000, 10000, 30000]
    rows, ea_l, eb_l = [], [], []
    for n_ in sizes:
        s_ = generate(a, b, 0.5, n_, rng)
        _, x_, y_ = estimate(s_)
        ea_l.append(x_); eb_l.append(y_)
        rows.append({"記録の長さ": f"{n_:,}", "学習した a": f"{x_:.3f}" if x_ is not None else "—", "学習した b": f"{y_:.3f}" if y_ is not None else "—"})
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=sizes, y=ea_l, mode="lines+markers", name="学習した a", line=dict(color="#f9a825")))
    fig3.add_trace(go.Scatter(x=sizes, y=eb_l, mode="lines+markers", name="学習した b", line=dict(color="#1e88e5")))
    fig3.add_hline(y=a, line_dash="dot", line_color="#f9a825", annotation_text=f"本当の a = {a:g}")
    fig3.add_hline(y=b, line_dash="dot", line_color="#1e88e5", annotation_text=f"本当の b = {b:g}", annotation_position="bottom right")
    fig3.update_layout(height=320, template="plotly_white", margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=1.12),
                       xaxis=dict(title="学習に使った記録の長さ（対数目盛）", type="log"), yaxis=dict(title="確率", range=[-0.02, 1.02]))
    st.plotly_chart(fig3, key="mk_learn")
    st.caption("記録が短いと、学習した確率は本当の値から大きくずれる。記録が長くなるほど正確になる（AI に大量のデータが必要な理由）。")

with tab4:
    st.markdown("#### 考察 1：AI は最初の言葉を「忘れる」")
    st.markdown(
        rf"""
① のグラフで、$p_1 = 1$ と $p_1 = 0$ の差は $(a - b)^{{n-1}}$（いまは ${a - b:g}^{{n-1}}$）で、どんどん 0 に近づきます。
つまり、何個か後の言葉は、最初の言葉にほとんど関係しなくなります。直前の 1 つしか見ないので、昔のことを覚えていられないのです。
本物の文章生成 AI は、**何千語も前までの文脈** を使って次の言葉を決めることで、話の流れを保っています。
"""
    )
    st.markdown("#### 考察 2：確率がかたよると、同じ言葉をくり返す")
    st.markdown(
        rf"""
晴れが続く回数の平均は $\dfrac{{1}}{{1 - a}}$（いまは {(f"{1 / (1 - a):.3g} 回" if a < 1 else "限りなく続く")}）です（$a = 1$ だと永遠に続く）。
$a = 0.99$ にすると平均 100 回も「晴れ」が続きます。② で試してみよう。
文章生成 AI でも、確率の高い言葉ばかり選ぶと、同じ言い回しをくり返してしまうことがあります。
"""
    )
    st.markdown("#### 考察 3：「温度」で文章の性格を変える")
    T = st.slider("温度 T", 0.2, 3.0, 1.0, step=0.1, key="mk_T")
    aT, bT = temperature(a, T), temperature(b, T)
    alT = limit(aT, bT)
    cc = st.columns(3)
    cc[0].metric("温度をかけた a", f"{aT:.3f}", delta=f"もとは {a:.2f}", delta_color="off")
    cc[1].metric("温度をかけた b", f"{bT:.3f}", delta=f"もとは {b:.2f}", delta_color="off")
    cc[2].metric("晴れの割合の極限", f"{alT:.3f}" if alT is not None else "—")
    rngT = random.Random(11)
    sT = generate(aT, bT, p1, 60, rngT)
    st.markdown("温度をかけた AI の出力の例：" + "".join("☀️" if x else "☔" for x in sT))
    st.caption("文章生成 AI では、確率を少し変える「温度」というつまみがある。温度を低くすると、確率の高い言葉ばかり選ぶので、ありきたりでくり返しの多い文章になる。"
               "高くすると、どの言葉も同じくらいの確率になり、意外性はあるがでたらめな文章になる。")
    st.markdown("#### 本物の AI とのちがい")
    st.markdown(
        r"""
- このページの AI は「直前の 1 語から、表に書いた確率で次を選ぶ」モデル。情報理論を作ったシャノンが 1948 年に、
  英語の文章をこの方法でまねて作ってみせたのが始まりの一つ。
- 本物の文章生成 AI も「次の言葉の確率を求めて、1 語ずつ選ぶ」点は同じ。ただし、長い文脈全体を見て、
  巨大なネットワークで確率を計算している（確率表を数えるのではなく、たくさんの数のパラメータを、データに合うように少しずつ調整して学習する）。
- それでも、「確率を学習する → 確率で選んで出力する → くり返す」という骨組みは、このミニチュアと共通。
"""
    )

with st.expander("📝 考えてみよう"):
    st.markdown(
        r"""
1. $a = 0.7$、$b = 0.4$、$p_1 = 1$ のとき、$p_2$、$p_3$ を求めよう。
2. 1. の極限を、漸化式 $p_{n+1} = 0.3p_n + 0.4$ から求めよう。
3. $a = 0.9$、$b = 0.1$ のとき、極限はいくらか。$a = 0.7$、$b = 0.4$ のときと比べて、近づく速さはどうか。
"""
    )
    with st.popover("答え"):
        st.markdown(
            r"""
1. $p_2 = 0.7$、$p_3 = 0.3\times0.7 + 0.4 = 0.61$
2. $\alpha = 0.3\alpha + 0.4$ より $\alpha = \dfrac{4}{7} \approx 0.571$
3. $\alpha = \dfrac{0.1}{1 - 0.9 + 0.1} = 0.5$。公比 $a - b = 0.8$ が 0.3 より 1 に近いので、近づくのはずっとおそい（同じ天気が長く続く）
"""
        )
