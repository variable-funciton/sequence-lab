"""【電気】はしご形回路の合成抵抗 — 漸化式・極限・黄金比"""

from fractions import Fraction

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.applied import fibonacci, ladder, ladder_limit

for k, v in dict(ld_Rs=1.0, ld_Rp=1.0, ld_N=4).items():
    st.session_state.setdefault(k, v)

st.sidebar.header("設定")
Rs = st.sidebar.number_input("横（直列）の抵抗 R₁ [Ω]", min_value=0.1, max_value=1000.0, step=0.5, key="ld_Rs")
Rp = st.sidebar.number_input("縦（並列）の抵抗 R₂ [Ω]", min_value=0.1, max_value=1000.0, step=0.5, key="ld_Rp")
N = st.sidebar.slider("段数 N", 1, 15, key="ld_N")

exact = float(Rs).is_integer() and float(Rp).is_integer()
seq = ladder(Fraction(int(Rs)), Fraction(int(Rp)), 15) if exact else ladder(float(Rs), float(Rp), 15)
lim = ladder_limit(Rs, Rp)

st.title("はしご形回路の合成抵抗：漸化式と極限")
st.markdown(
    r"横の抵抗 $R_1$ と縦の抵抗 $R_2$ を、はしごのように何段もつないだ回路の、左の端子から見た合成抵抗 $x_n$ を求めます。"
    r"1 段ふやすと「**右側の回路全体を 1 つの抵抗 $x_n$ とみる**」ことで、漸化式が作れます。"
)


def draw(Nd):
    """N 段のはしご形回路（6 段まで）"""
    k = min(Nd, 6)
    fig = go.Figure()
    line = dict(color="#333", width=2)

    def seg(x0, y0, x1, y1):
        fig.add_shape(type="line", x0=x0, y0=y0, x1=x1, y1=y1, line=line)

    def res(x0, y0, x1, y1, label):
        if y0 == y1:   # 横
            xm = (x0 + x1) / 2
            seg(x0, y0, xm - 0.22, y0); seg(xm + 0.22, y0, x1, y0)
            fig.add_shape(type="rect", x0=xm - 0.22, x1=xm + 0.22, y0=y0 - 0.08, y1=y0 + 0.08, line=line, fillcolor="#fff")
            fig.add_annotation(x=xm, y=y0 + 0.17, text=label, showarrow=False, font=dict(color="#1f77b4"))
        else:          # 縦
            ym = (y0 + y1) / 2
            seg(x0, y0, x0, ym - 0.18); seg(x0, ym + 0.18, x0, y1)
            fig.add_shape(type="rect", x0=x0 - 0.07, x1=x0 + 0.07, y0=ym - 0.18, y1=ym + 0.18, line=line, fillcolor="#fff")
            fig.add_annotation(x=x0 + 0.2, y=ym, text=label, showarrow=False, font=dict(color="#d62728"))

    for i in range(k):
        res(i, 1, i + 1, 1, "R₁")
        res(i + 1, 1, i + 1, 0, "R₂")
        seg(i, 0, i + 1, 0)
    if Nd > 6:
        fig.add_annotation(x=k + 0.35, y=0.5, text=f"… 全部で {Nd} 段", showarrow=False)
    fig.add_trace(go.Scatter(x=[0, 0], y=[1, 0], mode="markers+text", text=["A", "B"], textposition="middle left",
                             marker=dict(size=10, color="white", line=dict(color="#333", width=2)), hoverinfo="skip"))
    if Nd >= 2:   # 右側の (N−1) 段を x_{N−1} とみる
        fig.add_shape(type="rect", x0=0.75, x1=k + 0.3, y0=-0.15, y1=1.3, line=dict(color="#2ca02c", dash="dash"))
        fig.add_annotation(x=(k + 1) / 2, y=1.4, text=f"右側の {Nd - 1} 段 → 合成抵抗 x_{Nd - 1}", showarrow=False, font=dict(color="#2ca02c"))
    fig.update_layout(height=260, template="plotly_white", showlegend=False, margin=dict(l=30, r=10, t=10, b=10),
                      xaxis=dict(visible=False, range=[-0.4, k + 1.2]), yaxis=dict(visible=False, range=[-0.3, 1.6], scaleanchor="x"))
    return fig


st.plotly_chart(draw(N), key="ld_circuit")

with st.container(border=True):
    st.markdown("**漸化式**　左端の $R_1$ と、「$R_2$ と右側の回路 $x_n$ の並列」の直列")
    st.latex(r"x_1 = R_1 + R_2,\qquad x_{n+1} = R_1 + \frac{R_2\,x_n}{R_2 + x_n}")
    st.markdown(r"**極限**　$n$ が大きくなると $x_n$ はある値 $x$ に近づく。$x = R_1 + \dfrac{R_2 x}{R_2 + x}$ を解くと")
    st.latex(rf"x^2 - R_1 x - R_1 R_2 = 0 \quad\Rightarrow\quad x = \frac{{R_1 + \sqrt{{R_1^2 + 4R_1R_2}}}}{{2}} \approx {lim:.6g}\ \Omega")

xN = seq[N - 1]
m = st.columns(3)
m[0].metric(f"{N} 段の合成抵抗 x_{N}", f"{float(xN):.6g} Ω")
m[1].metric("極限（無限に続くとき）", f"{lim:.6g} Ω")
m[2].metric("極限とのずれ", f"{abs(float(xN) - lim) / lim * 100:.2g} %")

ns = list(range(1, 16))
fig = go.Figure()
fig.add_trace(go.Scatter(x=ns, y=[float(v) for v in seq], mode="lines+markers", name="x_n", line=dict(color="#1f77b4")))
fig.add_trace(go.Scatter(x=[N], y=[float(xN)], mode="markers", marker=dict(size=14, color="#d62728"), name=f"いまの N = {N}"))
fig.add_hline(y=lim, line_dash="dot", line_color="#2ca02c", annotation_text=f"極限 {lim:.4g} Ω")
fig.update_layout(height=320, template="plotly_white", margin=dict(l=10, r=10, t=30, b=10), showlegend=False,
                  xaxis=dict(title="段数 n", dtick=1), yaxis=dict(title="合成抵抗 x_n [Ω]"))
st.plotly_chart(fig, key="ld_conv")
st.caption("数段で極限の値にほぼ一致する。段数を増やしても合成抵抗は一定の値をこえない。")

with st.expander("段ごとの表"):
    rows = []
    for n, v in enumerate(seq, start=1):
        row = {"段数 n": n, "x_n [Ω]": f"{float(v):.8g}"}
        if exact:
            row["分数で"] = f"{v.numerator}/{v.denominator}" if v.denominator != 1 else str(v.numerator)
        rows.append(row)
    st.dataframe(pd.DataFrame(rows), hide_index=True)
    if Rs == Rp:
        st.caption(r"R₁ = R₂ = R のとき、x_n / R は 2, 5/3, 13/8, 34/21, … とフィボナッチ数の比になる。")

with st.expander("📖 解説：R₁ = R₂ = R のときと黄金比"):
    st.markdown(
        r"""
$R_1 = R_2 = R$ のとき、漸化式は $x_{n+1} = R + \dfrac{R x_n}{R + x_n}$。$y_n = \dfrac{x_n}{R}$ とおくと
$$y_1 = 2,\qquad y_{n+1} = 1 + \frac{y_n}{1 + y_n}$$
計算すると $y_n = 2,\ \dfrac{5}{3},\ \dfrac{13}{8},\ \dfrac{34}{21},\ \dots$。分子・分母に **フィボナッチ数**
$1, 1, 2, 3, 5, 8, 13, 21, 34, \dots$ が 1 つおきに現れ、$y_n = \dfrac{F_{2n+1}}{F_{2n}}$。

極限は $y^2 - y - 1 = 0$ の正の解
$$y = \frac{1 + \sqrt{5}}{2} \approx 1.618 \quad(\textbf{黄金比})$$
無限に続くはしご形回路の合成抵抗は $\dfrac{1 + \sqrt{5}}{2}R$。

**極限の求め方の考え方**　回路が無限に続くなら、左から 1 段取り除いても残りは同じ回路なので、合成抵抗も同じ $x$。
これが「$x_{n+1} = x_n = x$ とおく」ことの意味（自己相似）。
"""
    )

with st.expander("🔧 どこで使われている？"):
    st.markdown(
        r"""
- **長い送電線・ケーブルのモデル**：電線の抵抗（横）と、電線と地面の間のもれ（縦）が少しずつ続いている、と考えるとはしご形回路になる。
- **D/A 変換器（R-2R ラダー）**：抵抗 $R$ と $2R$ のはしご形回路で、ディジタルの数をアナログの電圧に変える（各段で電流が半分ずつ、等比数列）。
- **減衰器（アッテネーター）**：はしご形回路で、信号を段ごとに一定の割合で小さくする。
- 参考：[鈴鹿高専「はしご型回路の合成抵抗」](https://www.suzuka-ct.ac.jp/info/lab/akira/zyugyou/denkidensi/H14/inf_ladder.pdf)
"""
    )

with st.expander("📝 考えてみよう"):
    st.markdown(
        r"""
1. $R_1 = R_2 = 1\ \Omega$ のとき、$x_2,\ x_3$ を漸化式で求めよう。
2. $R_1 = 1\ \Omega$、$R_2 = 2\ \Omega$ のとき、無限に続くはしご形回路の合成抵抗を求めよう。
3. $R_1 = 2\ \Omega$、$R_2 = 4\ \Omega$ のときは、2. の何倍か。
"""
    )
    with st.popover("答え"):
        st.markdown(
            r"""
1. $x_2 = 1 + \dfrac{2}{1 + 2} = \dfrac{5}{3}$、$x_3 = 1 + \dfrac{5/3}{1 + 5/3} = 1 + \dfrac{5}{8} = \dfrac{13}{8}$
2. $x^2 - x - 2 = 0$ より $x = 2\ \Omega$
3. すべての抵抗が 2 倍なので、合成抵抗も 2 倍（$x^2 - 2x - 8 = 0$ より $x = 4\ \Omega$）
"""
        )
