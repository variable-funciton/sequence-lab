"""【物理】ボールの跳ね返り — 等比数列と無限等比級数

反発係数 e のボールを高さ h₀ から落とすと、はね返る高さは毎回 e² 倍（等比数列）。
はね返りは無限に続くのに、止まるまでの道のりと時間は有限（無限等比級数の和）。
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.anim import render as render_anim
from utils.applied import G, bounce_heights, bounce_total_distance, bounce_total_time

PRESETS = {
    "自由に設定": None,
    "よくはねるボール（e = 0.9）": dict(h0=2.0, e=0.9),
    "ふつうのボール（e = 0.8）": dict(h0=2.0, e=0.8),
    "あまりはねないボール（e = 0.5）": dict(h0=2.0, e=0.5),
}
for k, v in dict(bo_h0=2.0, bo_e=0.8, bo_N=8).items():
    st.session_state.setdefault(k, v)


def apply_preset():
    p = PRESETS[st.session_state["bo_preset"]]
    if p:
        for k, v in p.items():
            st.session_state[f"bo_{k}"] = v


st.sidebar.header("設定")
st.sidebar.selectbox("例を読み込む", list(PRESETS), key="bo_preset", on_change=apply_preset)
h0 = st.sidebar.number_input("落とす高さ h₀ [m]", min_value=0.1, max_value=50.0, step=0.1, format="%.1f", key="bo_h0")
e = st.sidebar.slider("反発係数 e", 0.10, 0.95, step=0.05, key="bo_e")
N = st.sidebar.slider("表示するはね返りの回数 N", 1, 30, key="bo_N")

hs = bounce_heights(h0, e, N)
D_inf, T_inf = bounce_total_distance(h0, e), bounce_total_time(h0, e)
D_N, T_N = bounce_total_distance(h0, e, N), bounce_total_time(h0, e, N)

st.title("ボールの跳ね返り：等比数列と無限等比級数")
st.markdown(
    r"床にぶつかるたびに、はね返る速さが **反発係数 $e$ 倍** になります。"
    r"高さは速さの 2 乗に比例するので、はね返る高さは毎回 **$e^2$ 倍**（等比数列）。"
    r"はね返りは無限に続くのに、止まるまでの **道のりと時間は有限** です。"
)
c1, c2 = st.columns(2)
with c1, st.container(border=True):
    st.markdown("**n 回目にはね返った高さ**（公比 $e^2$ の等比数列）")
    st.latex(rf"h_n = h_0 (e^2)^n = {h0:g}\times {e * e:.4g}^{{\,n}}")
with c2, st.container(border=True):
    st.markdown("**止まるまでの道のり**（下り $h_0$ と、上り下りの $2h_n$ の和）")
    st.latex(rf"L = h_0 + 2(h_1 + h_2 + \cdots) = h_0 + \frac{{2h_0 e^2}}{{1 - e^2}} = h_0\,\frac{{1 + e^2}}{{1 - e^2}}")

m = st.columns(4)
m[0].metric("1 回目の高さ h₁", f"{hs[1]:.3g} m")
m[1].metric(f"{N} 回目の高さ", f"{hs[N]:.3g} m")
m[2].metric("止まるまでの道のり", f"{D_inf:.3g} m", delta=f"{N} 回までで {D_N:.3g} m", delta_color="off")
m[3].metric("止まるまでの時間", f"{T_inf:.3g} 秒", delta=f"{N} 回までで {T_N:.3g} 秒", delta_color="off")

st.markdown("**アニメーション**　▶ を押すとボールが落ちてはね返ります（右のグラフに高さの変化がかかれていきます）。")
render_anim("bounce", dict(h0=h0, e=e, g=G), height=470)

# 部分和の収束
ns = list(range(0, 31))
fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=ns, y=[bounce_total_distance(h0, e, n) for n in ns], mode="lines+markers", name="n 回までの道のり",
                          line=dict(color="#9467bd")))
fig2.add_hline(y=D_inf, line_dash="dot", line_color="#9467bd", annotation_text=f"極限 {D_inf:.3g} m")
fig2.update_layout(height=280, template="plotly_white", margin=dict(l=10, r=10, t=30, b=10), showlegend=False,
                   xaxis=dict(title="はね返りの回数 n"), yaxis=dict(title="道のり [m]"))
st.plotly_chart(fig2, key="bo_sum")
st.caption("はね返るたびに道のりは増えるが、増え方はどんどん小さくなり、一定の値に近づく（無限等比級数の収束）。")

with st.expander("回ごとの表"):
    rows = [{"回 n": n, "高さ h_n [m]": f"{hs[n]:.4g}", "前の回との比": f"{hs[n] / hs[n - 1]:.4g}" if n else "—",
             "ここまでの道のり [m]": f"{bounce_total_distance(h0, e, n):.4g}", "ここまでの時間 [秒]": f"{bounce_total_time(h0, e, n):.4g}"}
            for n in range(N + 1)]
    st.dataframe(pd.DataFrame(rows), hide_index=True)

with st.expander("📖 解説：なぜ e² 倍で、時間はなぜ有限か"):
    st.markdown(
        r"""
**高さが $e^2$ 倍になる理由**　高さ $h$ から落ちると、床に着く直前の速さは $v = \sqrt{2gh}$（$h = \dfrac{v^2}{2g}$）。
はね返った直後の速さは $ev$ なので、上がる高さは $\dfrac{(ev)^2}{2g} = e^2 h$。

**止まるまでの道のり**　はね返るたびに上がって下りるので $2h_n$ ずつ進む。
$$L = h_0 + 2\sum_{n=1}^{\infty} h_0 (e^2)^n = h_0 + 2\cdot\frac{h_0 e^2}{1 - e^2} = h_0\,\frac{1 + e^2}{1 - e^2}$$

**止まるまでの時間**　最初に落ちる時間を $t_0 = \sqrt{\dfrac{2h_0}{g}}$ とすると、$n$ 回目のはね返りから次の着地までは
上がる時間と下りる時間で $2t_0 e^n$（速さが $e^n$ 倍なので時間も $e^n$ 倍）。こちらは公比 $e$ の等比数列。
$$T = t_0 + 2t_0(e + e^2 + \cdots) = t_0 + \frac{2t_0 e}{1 - e} = t_0\,\frac{1 + e}{1 - e}$$

はね返りは無限回あるのに、時間の和は有限なので、ボールはある時刻で止まる。
（実際には、空気の抵抗や、はね返りが小さくなると $e$ が変わることなどで、理論とは少しずれる。）
"""
    )

with st.expander("🔧 どこで使われている？"):
    st.markdown(
        r"""
- **球技のボールの検査**：ボールを決まった高さから落としてはね返る高さを測り、反発の具合（反発係数）が基準に入っているかを調べる。
- **衝突の解析**：機械の部品どうしの衝突や、物の落下の衝撃を考えるとき、はね返りの速さの比 $e$ を使う。
- **数学の考え方**：「無限に足しても有限になる」ことは、アキレスと亀の話（ゼノンの逆理）と同じ構造。
"""
    )
    st.markdown("- 参考：[On the Stopping Time of a Bouncing Ball（arXiv、英語）](https://arxiv.org/abs/0706.1978)")

with st.expander("📝 考えてみよう"):
    st.markdown(
        r"""
1. $h_0 = 2$ m、$e = 0.5$ のとき、3 回目にはね返った高さは何 m か。
2. 同じボールが止まるまでに動く道のりを求めよう。
3. はね返る高さが初めて 1 cm 以下になるのは何回目か（$e = 0.8$、$h_0 = 2$ m）。表で確かめよう。
"""
    )
    with st.popover("答え"):
        st.markdown(
            r"""
1. $h_3 = 2\times(0.25)^3 = \dfrac{1}{32} = 0.03125$ m
2. $L = 2\times\dfrac{1 + 0.25}{1 - 0.25} = \dfrac{10}{3} \approx 3.33$ m
3. $2\times 0.64^n \le 0.01$、つまり $0.64^n \le 0.005$ となる最小の $n$ は $n = 12$（$0.64^{11} \approx 0.0074$、$0.64^{12} \approx 0.0047$）
"""
        )
