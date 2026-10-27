"""【電気】抵抗器の E 系列 — 公比 10^{1/n} の等比数列と許容差"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.applied import E_SERIES, E_TOL, nearest, series_n, theoretical, tolerance_gaps

st.sidebar.header("設定")
name = st.sidebar.radio("系列", list(E_SERIES), index=1, key="es_series")
tol_pct = st.sidebar.select_slider("許容差 ±[%]", options=[1, 2, 5, 10, 20], value=int(E_TOL[name] * 100), key=f"es_tol_{name}")
R_want = st.sidebar.number_input("ほしい抵抗値 [Ω]", min_value=0.1, max_value=1e8, value=5000.0, step=100.0, key="es_want")

n = series_n(name)
vals = E_SERIES[name]
th = theoretical(n)
q = 10 ** (1 / n)
tol = tol_pct / 100

st.title("抵抗器の E 系列：等比数列で決められた抵抗値")
st.markdown(
    r"抵抗器は 1 Ω から何 MΩ までいろいろな値が必要ですが、すべての値を作るわけにはいきません。"
    r"そこで、**1 桁（10 倍）を同じ倍率で $n$ 段に分けた値** だけを作ります。これが **E 系列**（E6, E12, E24, …）です"
    r"（国際規格 IEC 60063、日本では JIS C 60063）。"
)
with st.container(border=True):
    st.latex(rf"\text{{{name}}}:\quad 10^{{k/{n}}}\ (k = 0, 1, \dots, {n - 1})\ \text{{を 2 けたに丸めた値}},\qquad \text{{公比}}\ \sqrt[{n}]{{10}} \approx {q:.3f}")
    st.markdown("　" + "、".join(f"{v:g}" for v in vals) + f"　（× 1, 10, 100, … Ω）")

best, err = nearest(vals, R_want)
gaps = tolerance_gaps(vals, tol)
m = st.columns(3)
m[0].metric("公比", f"{q:.3f}", delta=f"1 段で約 {100 * (q - 1):.0f}% 増える", delta_color="off")
m[1].metric(f"{R_want:g} Ω に最も近い値", f"{best:g} Ω", delta=f"ずれ {100 * err:+.1f}%", delta_color="off")
m[2].metric(f"±{tol_pct}% の範囲のすき間", "ほぼなし" if all((b - a) / a < 0.045 for a, b in gaps) else f"{len(gaps)} か所")

# 許容差の範囲を帯で表示
fig = go.Figure()
for k, v in enumerate(vals):
    color = "#1f77b4" if k % 2 == 0 else "#ff7f0e"
    fig.add_shape(type="rect", x0=v * (1 - tol), x1=v * (1 + tol), y0=0.2, y1=0.8, fillcolor=color, opacity=0.35, line_width=0)
fig.add_trace(go.Scatter(x=vals, y=[0.5] * n, mode="markers+text", text=[f"{v:g}" for v in vals], textposition="top center",
                         marker=dict(color="#333", size=7), hovertemplate="%{x}<extra></extra>"))
for a, b in gaps:
    fig.add_shape(type="rect", x0=a, x1=b, y0=0, y1=1, fillcolor="#d62728", opacity=0.5, line_width=0)
fig.update_layout(height=230, template="plotly_white", showlegend=False, margin=dict(l=10, r=10, t=20, b=10),
                  xaxis=dict(type="log", range=[-0.03, 1.03], title="抵抗値（1 桁分、対数目盛）"),
                  yaxis=dict(visible=False, range=[0, 1.2]))
st.plotly_chart(fig, key="es_band")
st.caption(f"色の帯は各値の ±{tol_pct}% の範囲。赤い所は、どの値の範囲にも入らないすき間。"
           f"{name} は ±{int(E_TOL[name] * 100)}% の部品と組み合わせると、1〜10 がほぼすき間なくうまるように作られている"
           "（2 けたに丸めているので、ごくわずかなすき間が残る所もある）。許容差を変えて確かめよう。")

fig2 = go.Figure()
ks = list(range(n))
fig2.add_trace(go.Scatter(x=ks, y=th, mode="lines", name="理論値 10^(k/n)", line=dict(color="#9aa0a6", dash="dot")))
fig2.add_trace(go.Scatter(x=ks, y=vals, mode="markers", name=name, marker=dict(color="#d62728", size=8)))
fig2.update_layout(height=300, template="plotly_white", margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=1.08),
                   xaxis=dict(title="段 k"), yaxis=dict(title="値", type="log"))
st.plotly_chart(fig2, key="es_geo")

with st.expander(f"{name} の値と理論値"):
    rows = [{"k": k, name: f"{v:g}", "理論値 10^(k/n)": f"{t:.3f}", "ずれ": f"{100 * (v - t) / t:+.1f}%",
             "前の値との比": f"{v / vals[k - 1]:.3f}" if k else "—"} for k, (v, t) in enumerate(zip(vals, th))]
    st.dataframe(pd.DataFrame(rows), hide_index=True)
    st.caption("E24 の 2.7, 3.0, 3.3, 3.6, 3.9, 4.3, 4.7 などは、理論値から 2〜5% ずれている。"
               "規格ができる前から使われていた値に合わせたためといわれる。")

with st.expander("📖 解説：なぜ等比数列で、なぜ許容差とセットなのか"):
    st.markdown(
        rf"""
**等比数列にする理由**　抵抗値の誤差は「何 Ω ずれるか」ではなく「何 % ずれるか」で考える。
同じ割合で並べておけば、どの大きさの所でも、ほしい値に最も近い値とのずれが同じくらいになる。

**許容差とセット**　抵抗器には「表示の値から ±10% 以内」のような **許容差** がある。
E12 の公比は約 1.21 なので、となりの値の ±10% の範囲どうしがほぼつながり、どんな値もどれかの抵抗器の範囲に入る。
そのため、許容差 ±20% には E6、±10% には E12、±5% には E24 のように組み合わせて使う。

**系列の関係**　E6 ⊂ E12 ⊂ E24（E12 の公比の 2 乗が E6 の公比）。機械で使う **標準数**（ルナール数列）も同じ考え方。
"""
    )

with st.expander("🔧 どこで使われている？"):
    st.markdown(
        r"""
- **電子回路の設計**：計算で 5 kΩ が必要になっても 5 kΩ の抵抗器は E12 にはないので、4.7 kΩ を使ったり、
  2 つの抵抗をつないで近い値を作ったりする。
- **コンデンサ** の容量（μF など）も E 系列で作られている。
- 参考：[ローム「公称抵抗値標準数他」（各 E 系列の値の表）](https://fscdn.rohm.com/jp/products/databook/applinote/passive/resistor/common/resistance_value-j.pdf)、
  [E series of preferred numbers（Wikipedia 英語）](https://en.wikipedia.org/wiki/E_series_of_preferred_numbers)
"""
    )

with st.expander("📝 考えてみよう"):
    st.markdown(
        r"""
1. E6 の公比 $\sqrt[6]{10}$ を小数第 2 位まで求め、1.0, 1.5, 2.2, 3.3, 4.7, 6.8 が等比数列に近いことを確かめよう。
2. E12 で 4.7 kΩ の次に大きい値は何か。また、4.7 kΩ の ±10% の範囲を求めよう。
3. 3 kΩ がほしいとき、E12 で最も近い値はどれか（このページの右上の欄で確かめよう）。
"""
    )
    with st.popover("答え"):
        st.markdown(
            r"""
1. $\sqrt[6]{10} \approx 1.47$。$1, 1.47, 2.15, 3.16, 4.64, 6.81$ を丸めると E6 の値になる（3.16 は 3.3 とやや離れている）
2. 5.6 kΩ。4.7 kΩ の ±10% は 4.23〜5.17 kΩ
3. 3.3 kΩ（ずれ +10%）。2.7 kΩ（ずれ −10%）と同じくらいだが、比で考えると 3.3 のほうがわずかに近い
"""
        )
