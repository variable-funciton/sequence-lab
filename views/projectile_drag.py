"""【物理】空気抵抗のある斜方投射 — 漸化式（オイラー法）で軌道を計算し、空気抵抗なしと比べる"""

import math

import plotly.graph_objects as go
import streamlit as st

from utils.anim import render as render_anim
from utils.applied import BALLS, G, best_angle, projectile_drag, projectile_summary

DT = 0.002
CUSTOM = "自分で決める"
for k, v in dict(pd_ball="野球のボール", pd_v0=30.0, pd_deg=45.0, pd_k=0.02).items():
    st.session_state.setdefault(k, v)

st.sidebar.header("設定")
ball = st.sidebar.selectbox("投げるもの（空気抵抗の強さ）", [b for b in BALLS if b != "空気抵抗なし"] + [CUSTOM], key="pd_ball")
if ball == CUSTOM:
    k = st.sidebar.slider("空気抵抗の強さ k [1/m]", 0.0, 0.30, step=0.001, format="%.3f", key="pd_k")
else:
    k = BALLS[ball]
    st.sidebar.caption(f"k ≈ {k:g} /m（目安）")
v0 = st.sidebar.slider("初速度 v₀ [m/s]", 5.0, 50.0, step=1.0, key="pd_v0")
deg = st.sidebar.slider("投げ上げる角度 θ [°]", 5.0, 85.0, step=1.0, key="pd_deg")
label = ball if ball != CUSTOM else f"k = {k:g}"


@st.cache_data(show_spinner=False)
def range_curve(v0, k):
    angles = [2.5 * i for i in range(1, 36)]
    return angles, [projectile_drag(v0, a, k, 0.005)[1][-1] for a in angles], best_angle(v0, k)


s0, s1 = projectile_summary(v0, deg, 0.0, DT), projectile_summary(v0, deg, k, DT)

st.title("空気抵抗のある斜方投射：漸化式で軌道を計算する")
st.markdown(
    "空気抵抗を考えないとき、投げたボールの軌道は放物線になり、45° で投げると最も遠くまで飛びます。"
    "実際には **空気抵抗**（速いほど大きい）がはたらくので、軌道はゆがみ、飛距離も変わります。"
    "空気抵抗があると軌道を表す簡単な式は作れませんが、**短い時間 $\\Delta t$ ごとに速度と位置を少しずつ更新する漸化式** "
    "でコンピュータに計算させることができます。"
)
with st.container(border=True):
    st.markdown(rf"**漸化式（オイラー法）**　$\Delta t = {DT}$ 秒ごとに、加速度から速度を、速度から位置を更新する。空気抵抗による加速度の大きさは $kv^2$（速さの 2 乗に比例）。")
    st.latex(r"x_{n+1} = x_n + v_{x,n}\,\Delta t,\qquad y_{n+1} = y_n + v_{y,n}\,\Delta t")
    st.latex(r"v_{x,n+1} = v_{x,n} - k\,|v_n|\,v_{x,n}\,\Delta t,\qquad v_{y,n+1} = v_{y,n} - \left(g + k\,|v_n|\,v_{y,n}\right)\Delta t")
    st.caption("k = 0（空気抵抗なし）なら、x 方向は等速、y 方向は等加速度の式と同じ結果になる。")

st.markdown("**アニメーション**　▶ を押すと、空気抵抗なし（青）と空気抵抗あり（赤）のボールを同時に投げます。点は一定時間ごとの位置です。")
render_anim("projectile", dict(v0=v0, deg=deg, k=k, label=label, dt=DT), height=620)

angles, ranges, (a_best, r_best) = range_curve(v0, k)
m = st.columns(4)
m[0].metric("飛距離（抵抗あり）", f"{s1['range']:.1f} m", delta=f"抵抗なしの {100 * s1['range'] / s0['range']:.0f}%", delta_color="off")
m[1].metric("最高点（抵抗あり）", f"{s1['height']:.1f} m", delta=f"抵抗なし {s0['height']:.1f} m", delta_color="off")
m[2].metric("最もよく飛ぶ角度（抵抗あり）", f"約 {a_best:g}°", delta="抵抗なしなら 45°", delta_color="off")
m[3].metric("終端速度 √(g/k)", f"{math.sqrt(G / k):.1f} m/s" if k > 0 else "—",
            delta=f"時速 {math.sqrt(G / k) * 3.6:.0f} km" if k > 0 else None, delta_color="off")

fig = go.Figure()
fig.add_trace(go.Scatter(x=angles, y=[projectile_drag(v0, a, 0.0, 0.005)[1][-1] for a in angles], mode="lines", name="空気抵抗なし",
                         line=dict(color="#1f77b4", width=2.5)))
fig.add_trace(go.Scatter(x=angles, y=ranges, mode="lines", name=label, line=dict(color="#d62728", width=2.5)))
fig.add_trace(go.Scatter(x=[45, a_best], y=[v0 * v0 / G, r_best], mode="markers+text", text=["45°", f"約 {a_best:g}°"],
                         textposition="top center", marker=dict(color=["#1f77b4", "#d62728"], size=11), showlegend=False))
fig.add_vline(x=deg, line_dash="dot", line_color="gray", annotation_text=f"いまの角度 {deg:g}°")
fig.update_layout(height=360, template="plotly_white", margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=1.1),
                  xaxis=dict(title="投げ上げる角度 θ [°]", dtick=15), yaxis=dict(title="飛距離 [m]", rangemode="tozero"))
st.plotly_chart(fig, key="pd_range")
st.caption("空気抵抗があると、最もよく飛ぶ角度は 45° より小さくなる。抵抗が強いものほど、その角度は小さい。")

with st.expander("📖 解説：空気抵抗があると何が変わるか"):
    st.markdown(
        r"""
**軌道が左右対称でなくなる**　上がっていく間も下りてくる間も速さが減るので、下りのほうがゆっくりで、急な角度で落ちてくる。
最高点は、飛距離の真ん中より遠い所になる（アニメーションの点の間隔を見よう）。

**45° より低く投げたほうが遠くへ飛ぶ**　高く投げると空中にいる時間が長くなり、その間ずっと抵抗を受けて横向きの速さが減る。
そのため、抵抗が強いほど、最もよく飛ぶ角度は小さくなる。

**終端速度**　真下に落ちるとき、重力 $mg$ と空気抵抗 $mkv^2$ がつり合うと、それ以上速くならない。$g = kv^2$ より
$$v = \sqrt{\frac{g}{k}}\quad(\text{終端速度})$$
ピンポン球やシャトルは $k$ が大きいので、終端速度が小さい（すぐに落ちる速さが一定になる）。

**漸化式で計算する理由**　空気抵抗が速さの 2 乗に比例するとき、軌道を $x$ と $y$ の簡単な式で表すことはできない。
そこで、$\Delta t$ ごとに「いまの速度で少し進み、いまの加速度で速度を少し変える」ことをくり返す（**オイラー法**）。
これは、ローン返済や過渡現象のページと同じ「前の値から次の値を決める」漸化式の考え方。
$\Delta t$ を小さくするほど正確になる（このページは 0.002 秒）。
"""
    )

with st.expander("🔧 どこで使われている？"):
    st.markdown(
        r"""
- **スポーツ**：野球の打球、ゴルフ、サッカーのボールの飛び方の分析。実際には回転による力（マグヌス効果）もはたらき、このページの計算より複雑になる。
- **砲丸投げ**：重くて小さいので空気抵抗の影響が小さく、ほぼ放物線（砲丸を選んで確かめよう）。
- **雨つぶ・パラシュート**：空気抵抗で終端速度になるので、高い所から落ちても速くなりすぎない。
- **ロケット・人工衛星・気象のシミュレーション**：コンピュータは、同じように短い時間ごとの漸化式で運動を計算している。
- 空気抵抗の強さ $k$ は、空気の密度・物の大きさ・形から決まる値の目安（$k = \dfrac{\rho C_d A}{2m}$）。
"""
    )
    st.page_link("views/transient.py", label="同じ考え方：過渡現象を漸化式で計算", icon="⚡")

with st.expander("📝 考えてみよう"):
    st.markdown(
        r"""
1. 空気抵抗なしで、初速度 30 m/s、45° で投げたときの飛距離を $\dfrac{v_0^2}{g}$ で求め、このページの値と比べよう。
2. 野球のボールで、飛距離が最も大きくなる角度を探そう。45° と比べてどうか。
3. ピンポン球の終端速度を $\sqrt{g/k}$（$k = 0.14$）で求めよう。
"""
    )
    with st.popover("答え"):
        st.markdown(
            r"""
1. $\dfrac{30^2}{9.8} \approx 91.8$ m（漸化式でもほぼ同じ値になる）
2. 初速度 30 m/s では約 42〜43°。45° より少し小さい
3. $\sqrt{9.8/0.14} \approx 8.4$ m/s（時速約 30 km）
"""
        )
