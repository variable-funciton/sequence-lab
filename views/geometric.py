"""等比数列とその和（後期課題10 対応）

公比 r の 6 つの場合（0<r<1, r=1, r>1, −1<r<0, r=−1, r<−1）で、
項 a_n と和 S_n のふるまいがどう変わるかを比べる。
"""

from fractions import Fraction as F

import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from utils.sequences import (
    RATIO_CASES, fmt_num, geometric_limit, geometric_sums, geometric_terms, latex_num,
)

# ---------------- 6 つの場合の設定 ----------------
CASES = {
    "0<r<1": dict(
        label=r"$0<r<1$", short="0 < r < 1", color="#2ca02c", alert="success",
        options=[F(1, 10), F(1, 5), F(1, 4), F(1, 3), F(1, 2), F(2, 3), F(3, 4), F(4, 5), F(9, 10)],
        default=F(1, 2), demo=F(1, 2),
        term="項はすべて同じ符号で、絶対値がだんだん小さくなり **0 に近づく**（減衰）。",
        sum=r"和 $S_n$ は増え方がにぶくなり、**一定の値 $\dfrac{a}{1-r}$ に近づく**（収束）。",
        formula=r"S_n = \frac{a(1-r^n)}{1-r}",
        tip=r"$1-r>0$ なので、分母が正になる $\dfrac{a(1-r^n)}{1-r}$ の形を使うと計算しやすい。",
    ),
    "r=1": dict(
        label=r"$r=1$", short="r = 1", color="#7f7f7f", alert="warning",
        options=[F(1)], default=F(1), demo=F(1),
        term=r"すべての項が初項と同じ **$a, a, a, \dots$**（一定）。",
        sum=r"和は $S_n = na$（**等差数列**のように一定の割合で増える）。",
        formula=r"S_n = na",
        tip=r"⚠️ 公式 $\dfrac{a(1-r^n)}{1-r}$ は **分母が $0$ になるので使えない**。必ず別扱いにする。",
    ),
    "r>1": dict(
        label=r"$r>1$", short="r > 1", color="#d62728", alert="error",
        options=[F(11, 10), F(6, 5), F(3, 2), F(2), F(5, 2), F(3), F(4)],
        default=F(2), demo=F(3, 2),
        term="項はすべて同じ符号で、絶対値が **急激に大きくなる**（指数関数的な増加）。",
        sum=r"和 $S_n$ も限りなく大きくなる（**発散**）。複利で元利合計が増える様子がこれ。",
        formula=r"S_n = \frac{a(r^n-1)}{r-1}",
        tip=r"$r-1>0$ なので、分母が正になる $\dfrac{a(r^n-1)}{r-1}$ の形を使うと計算しやすい。",
    ),
    "-1<r<0": dict(
        label=r"$-1<r<0$", short="−1 < r < 0", color="#1f77b4", alert="info",
        options=[F(-9, 10), F(-4, 5), F(-3, 4), F(-2, 3), F(-1, 2), F(-1, 3), F(-1, 4), F(-1, 5), F(-1, 10)],
        default=F(-1, 2), demo=F(-1, 2),
        term="項の **符号が交互に入れかわり**（＋, −, ＋, −, …）、絶対値は小さくなって **0 に近づく**。",
        sum=r"和 $S_n$ は **上下に振れながら** $\dfrac{a}{1-r}$ に近づく（振動しながら収束）。",
        formula=r"S_n = \frac{a(1-r^n)}{1-r}",
        tip=r"$r<0$ のとき $r^n$ の符号は $n$ の偶奇で変わる。$(-2)^3=-8$, $(-2)^4=16$ に注意。",
    ),
    "r=-1": dict(
        label=r"$r=-1$", short="r = −1", color="#9467bd", alert="warning",
        options=[F(-1)], default=F(-1), demo=F(-1),
        term=r"項は **$a, -a, a, -a, \dots$** をくり返す（振動）。",
        sum=r"和は **$a, 0, a, 0, \dots$** をくり返し、一定の値には近づかない。",
        formula=r"S_n = \frac{a\{1-(-1)^n\}}{2} = \begin{cases} a & (n\text{ が奇数}) \\ 0 & (n\text{ が偶数}) \end{cases}",
        tip=r"公式は使える（分母 $1-r=2$）。$n$ の **偶奇で場合分け** すると見通しがよい。",
    ),
    "r<-1": dict(
        label=r"$r<-1$", short="r < −1", color="#ff7f0e", alert="error",
        options=[F(-4), F(-3), F(-5, 2), F(-2), F(-3, 2), F(-6, 5), F(-11, 10)],
        default=F(-2), demo=F(-3, 2),
        term="項の **符号が交互に入れかわり**、絶対値は **急激に大きくなる**。",
        sum=r"和 $S_n$ は **正負に大きく振れながら** 広がっていく（振動しながら発散）。",
        formula=r"S_n = \frac{a(1-r^n)}{1-r}",
        tip=r"$1-r>0$ なので $\dfrac{a(1-r^n)}{1-r}$ の形が計算しやすい。$r^n$ の符号に注意。",
    ),
}
assert list(CASES) == RATIO_CASES

A_OPTIONS = sorted({F(k, 2) for k in range(-20, 21) if k} | {F(1, 3), F(-1, 3)})

PRESETS = {
    "自由に設定": None,
    "課題10 第1問：初項3・公比−2": dict(a=F(3), case="r<-1", r=F(-2), N=6),
    "課題10 第2問：初項1/2・公比1/3": dict(a=F(1, 2), case="0<r<1", r=F(1, 3), N=6),
    "課題10 第5問：初項5・公比3の和 S₆": dict(a=F(5), case="r>1", r=F(3), N=6),
    "課題10 第6問：初項2・公比−2の和 S₈": dict(a=F(2), case="r<-1", r=F(-2), N=8),
    "課題10 第7問：初項1・公比2（S_n = 255 となる n）": dict(a=F(1), case="r>1", r=F(2), N=10),
}

st.session_state.setdefault("gs_a", F(2))
st.session_state.setdefault("gs_case", "0<r<1")
st.session_state.setdefault("gs_N", 10)
for key, c in CASES.items():
    st.session_state.setdefault(f"gs_r_{key}", c["default"])


def apply_preset():
    p = PRESETS[st.session_state["gs_preset"]]
    if p:
        st.session_state["gs_a"] = p["a"]
        st.session_state["gs_case"] = p["case"]
        st.session_state[f"gs_r_{p['case']}"] = p["r"]
        st.session_state["gs_N"] = p["N"]


# ---------------- サイドバー ----------------
st.sidebar.header("設定")
st.sidebar.selectbox("例題を読み込む", list(PRESETS), key="gs_preset", on_change=apply_preset)
a = st.sidebar.select_slider("初項 a", options=A_OPTIONS, key="gs_a", format_func=fmt_num)
N = st.sidebar.slider("項数 N", 1, 30, key="gs_N")

# ---------------- 本体 ----------------
st.title("等比数列とその和")
st.markdown("初項 $a$ に、同じ数 $r$（**公比**）を次々にかけてできる数列を **等比数列** といいます。")
f1, f2 = st.columns(2)
with f1, st.container(border=True):
    st.markdown("**一般項**")
    st.latex(r"a_n = a\,r^{\,n-1}")
    st.caption("指数は n ではなく **n − 1**（初項には r を 1 回もかけていない）")
with f2, st.container(border=True):
    st.markdown("**初項から第 n 項までの和**")
    st.latex(r"S_n = \begin{cases} \dfrac{a(1-r^n)}{1-r} = \dfrac{a(r^n-1)}{r-1} & (r \neq 1) \\[2mm] na & (r = 1) \end{cases}")

st.markdown("##### 公比 $r$ の範囲を選ぶ")
case = st.radio("公比の範囲", list(CASES), key="gs_case", horizontal=True,
                format_func=lambda k: CASES[k]["label"], label_visibility="collapsed")
cfg = CASES[case]
if len(cfg["options"]) > 1:
    r = st.select_slider("公比 r", options=cfg["options"], key=f"gs_r_{case}", format_func=fmt_num)
else:
    r = cfg["options"][0]
    st.markdown(f"公比 $r = {latex_num(r)}$（この場合は 1 つの値だけ）")

terms = geometric_terms(a, r, N)
sums = geometric_sums(a, r, N)
limit = geometric_limit(a, r)

# ---------------- この場合のポイント（強調表示） ----------------
alert = getattr(st, cfg["alert"])
alert(f"**公比 {cfg['short']} のとき**\n\n- {cfg['term']}\n- {cfg['sum']}")
st.latex(cfg["formula"])
st.markdown(cfg["tip"])

m = st.columns(4)
m[0].metric("公比 r", fmt_num(r))
m[1].metric(f"第 {N} 項 a_{N}", fmt_num(terms[-1]))
m[2].metric(f"和 S_{N}", fmt_num(sums[-1]))
m[3].metric("S_n の近づく値", fmt_num(limit) if limit is not None else "なし",
            help="|r| < 1 のときだけ、S_n は a/(1−r) に限りなく近づく（無限等比級数・発展）")

st.latex(
    rf"a_{{{N}}} = {latex_num(a)} \cdot \left({latex_num(r)}\right)^{{{N - 1}}} = {latex_num(terms[-1])},"
    rf"\qquad S_{{{N}}} = {latex_num(sums[-1])}"
)

tab1, tab2, tab3 = st.tabs(["① 項と和のグラフ", "② 6 つの場合を一覧で比べる", "③ 和の公式の導き方"])

# =====================================================================
# ① 項と和のグラフ
# =====================================================================
with tab1:
    n_show = st.slider("第何項まで表示するか", 1, N, N, key="gs_nshow")
    xs = list(range(1, N + 1))
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08,
                        subplot_titles=("各項 a_n（棒の色：正は濃く、負は薄く）", "和 S_n"))
    fig.add_trace(go.Bar(
        x=xs[:n_show], y=[float(t) for t in terms[:n_show]], name="a_n",
        marker_color=[cfg["color"] if t > 0 else "rgba(120,120,120,0.55)" for t in terms[:n_show]],
        marker_line=dict(color=cfg["color"], width=1.5),
        customdata=[fmt_num(t) for t in terms[:n_show]],
        hovertemplate="a_%{x} = %{customdata}<extra></extra>",
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=xs[:n_show], y=[float(s) for s in sums[:n_show]], name="S_n", mode="lines+markers",
        line=dict(color=cfg["color"], width=3), marker=dict(size=8),
        customdata=[fmt_num(s) for s in sums[:n_show]],
        hovertemplate="S_%{x} = %{customdata}<extra></extra>",
    ), row=2, col=1)
    if limit is not None:
        fig.add_hline(y=float(limit), line_dash="dash", line_color="black", row=2, col=1,
                      annotation_text=f"a/(1−r) = {fmt_num(limit)}", annotation_position="top right")
    fig.add_hline(y=0, line_color="black", line_width=1, row=1, col=1)
    fig.add_hline(y=0, line_color="black", line_width=1, row=2, col=1)
    fig.update_layout(height=620, template="plotly_white", showlegend=False,
                      margin=dict(l=10, r=10, t=40, b=10))
    fig.update_xaxes(range=[0.4, N + 0.6], dtick=1 if N <= 20 else 5)
    fig.update_xaxes(title_text="n", row=2, col=1)
    st.plotly_chart(fig, key="geo_main")
    if case in ("r>1", "r<-1") and N > 15:
        st.caption("※ 値が急激に大きくなるため、最初のほうの項はグラフ上でほとんど 0 に見えます。項数 N を小さくすると見やすくなります。")

    with st.expander("項と和の表"):
        rows = "| n | " + " | ".join(str(n) for n in xs[:min(N, 12)]) + " |\n"
        rows += "|:--|" + ":--:|" * min(N, 12) + "\n"
        rows += "| $a_n$ | " + " | ".join(f"${latex_num(t)}$" for t in terms[:12]) + " |\n"
        rows += "| $S_n$ | " + " | ".join(f"${latex_num(s)}$" for s in sums[:12]) + " |\n"
        st.markdown(rows)
        if N > 12:
            st.caption("最初の 12 項まで表示しています。")

# =====================================================================
# ② 6 つの場合を一覧で比べる
# =====================================================================
with tab2:
    st.markdown(f"初項 $a = {latex_num(a)}$ のまま、公比だけを代表的な値に変えて並べました。"
                "**太枠** が今選んでいる場合です。")
    which = st.radio("表示するもの", ["項 a_n", "和 S_n"], horizontal=True, key="gs_grid_kind")
    n_grid = 10
    keys = RATIO_CASES
    titles = [f"{CASES[k]['short']}（r = {fmt_num(r if k == case else CASES[k]['demo'])}）" for k in keys]
    grid = make_subplots(rows=2, cols=3, subplot_titles=titles, vertical_spacing=0.16, horizontal_spacing=0.06)
    for i, k in enumerate(keys):
        rr = r if k == case else CASES[k]["demo"]
        vals = geometric_terms(a, rr, n_grid) if which == "項 a_n" else geometric_sums(a, rr, n_grid)
        row, col = i // 3 + 1, i % 3 + 1
        grid.add_trace(go.Bar(
            x=list(range(1, n_grid + 1)), y=[float(v) for v in vals],
            marker_color=CASES[k]["color"], opacity=1.0 if k == case else 0.55,
            hovertemplate="n=%{x}: %{y:.4g}<extra></extra>",
        ), row=row, col=col)
        lim = geometric_limit(a, rr)
        if which == "和 S_n" and lim is not None:
            grid.add_hline(y=float(lim), line_dash="dash", line_color="black", line_width=1, row=row, col=col)
        if k == case:
            axis = "" if i == 0 else str(i + 1)
            grid.add_shape(type="rect", xref=f"x{axis} domain", yref=f"y{axis} domain",
                           x0=0, x1=1, y0=0, y1=1, line=dict(color=CASES[k]["color"], width=4))
    grid.update_layout(height=560, template="plotly_white", showlegend=False,
                       margin=dict(l=10, r=10, t=50, b=10))
    grid.update_xaxes(dtick=2)
    st.plotly_chart(grid, key="geo_grid")

    st.markdown("##### まとめ")
    st.markdown(
        r"""
| 公比 $r$ | 項の符号 | 項の絶対値 $\lvert a_n\rvert$ | 和 $S_n$ のふるまい | 和の公式 |
|:--:|:--:|:--:|:--|:--:|
| $0<r<1$ | 一定 | 小さくなり $0$ へ | $\dfrac{a}{1-r}$ に近づく（収束） | $\dfrac{a(1-r^n)}{1-r}$ |
| $r=1$ | 一定 | 変わらない | $na$（一定の割合で増える） | **$na$**（公式は使えない） |
| $r>1$ | 一定 | 急激に大きくなる | 限りなく大きくなる（発散） | $\dfrac{a(r^n-1)}{r-1}$ |
| $-1<r<0$ | 交互 | 小さくなり $0$ へ | 振動しながら $\dfrac{a}{1-r}$ に近づく | $\dfrac{a(1-r^n)}{1-r}$ |
| $r=-1$ | 交互 | 変わらない | $a, 0, a, 0, \dots$ をくり返す | $\dfrac{a\{1-(-1)^n\}}{2}$ |
| $r<-1$ | 交互 | 急激に大きくなる | 振動しながら発散 | $\dfrac{a(1-r^n)}{1-r}$ |
"""
    )
    st.caption(
        "見分け方：**符号** は r が正か負かで、**大きさ** は |r| が 1 より小さいか大きいかで決まる。"
        "|r| < 1 のときだけ、和が一定の値に近づく（a/(1−r) は数学Ⅲで学ぶ「無限等比級数」の和）。"
        "a が負のときは、上の表の符号がすべて反対になる。"
    )

# =====================================================================
# ③ 和の公式の導き方
# =====================================================================
with tab3:
    st.markdown(r"$S_n$ と、それに **公比 $r$ をかけた $rS_n$** を、1 つずらして並べます。")
    st.latex(r"""
\begin{array}{rcccccccl}
S_n  &=& a &+& ar &+& \cdots &+& ar^{n-1} \\
rS_n &=&   & & ar &+& \cdots &+& ar^{n-1} \;+\; ar^{n} \\ \hline
S_n - rS_n &=& a & & & & & & \;-\; ar^{n}
\end{array}
""")
    st.markdown(r"真ん中の項がすべて消えて $(1-r)S_n = a(1-r^n)$。"
                r"$r \neq 1$ なら両辺を $1-r$ で割って公式が得られます。"
                r"**$r = 1$ だと $1 - r = 0$ で割れない** ので、$S_n = na$ を別に考えます。")

    n3 = st.slider("実際の数で確かめる（項数）", 2, 6, min(max(N, 2), 5), key="gs_n3")
    if r == 1:
        st.latex(
            rf"S_{{{n3}}} = " + " + ".join([latex_num(a)] * n3)
            + rf" = {n3} \times {latex_num(a)} = {latex_num(n3 * a)}"
        )
    else:
        t3 = geometric_terms(a, r, n3 + 1)

        def signed(v):
            s = latex_num(v)
            return s if s.startswith("-") else "+" + s

        top = " & ".join([latex_num(t3[0])] + [signed(v) for v in t3[1:n3]] + [""])
        bottom = " & ".join([""] + [signed(v) for v in t3[1:n3]] + [signed(t3[n3])])
        st.latex(
            r"\begin{array}{r" + "c" * (n3 + 1) + "}"
            + rf"S_{{{n3}}} = & {top} \\ "
            + rf"\left({latex_num(r)}\right)S_{{{n3}}} = & {bottom} \\ \hline "
            + rf"\left(1 - ({latex_num(r)})\right)S_{{{n3}}} = & {latex_num(t3[0])} & "
            + " & " * (n3 - 1) + rf"{signed(-t3[n3])}"
            + r"\end{array}"
        )
        st.latex(
            rf"S_{{{n3}}} = \frac{{{latex_num(t3[0] - t3[n3])}}}{{{latex_num(1 - r)}}}"
            rf" = {latex_num(geometric_sums(a, r, n3)[-1])}"
        )

    with st.expander("⚠️ よくある間違い"):
        st.markdown(
            r"""
- **指数のずれ**：一般項は $ar^{n-1}$。$ar^{n}$ と書くと、初項が $ar$ になってしまう（課題10 第1問の選択肢(4)）。
- **$r=1$ で公式を使う**：分母 $1-r$ が $0$ になる。$S_n = na$ を使う。
- **負の公比のかっこ**：$-2^{3}$ と $(-2)^{3}$ は別物。$r=-2$ なら $r^n = (-2)^n$ とかっこをつける。
- **和の項数**：$S_n$ は初項から **$n$ 個** の和。公式の指数 $r^n$ は項数 $n$ と同じ（一般項の $n-1$ と混同しない）。
"""
        )
