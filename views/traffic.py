"""【都市】交通渋滞のセルオートマトン — 車の位置と速さを 1 ステップずつ計算し、自然渋滞の発生を再現する"""

import plotly.graph_objects as go
import streamlit as st

from utils.anim import render as render_anim
from utils.models import nasch_flow

L = 100
for k, v in dict(tf_density=0.15, tf_p=0.2, tf_vmax=5, tf_seed=1).items():
    st.session_state.setdefault(k, v)

st.sidebar.header("設定")
density = st.sidebar.slider("車の密度（マスのうち車がいる割合）", 0.02, 0.8, step=0.01, key="tf_density")
p = st.sidebar.slider("ゆらぎ p（理由なく減速する確率）", 0.0, 0.5, step=0.05, key="tf_p")
vmax = st.sidebar.slider("最高速度 v_max（マス/ステップ）", 1, 7, key="tf_vmax")
seed = st.sidebar.number_input("乱数の種（変えると別の試行）", min_value=1, max_value=9999, step=1, key="tf_seed")


@st.cache_data(show_spinner=False)
def fundamental(vmax, p):
    ds = [round(0.02 * i, 2) for i in range(1, 46)]
    return ds, [nasch_flow(L, d, vmax, p, seed=7)[1] for d in ds]


st.title("交通渋滞のセルオートマトン：自然渋滞はなぜ起こる？")
st.markdown(
    "道路を **マス目** に分け、車の位置と速さを **1 ステップずつ** 決まった規則で更新していきます（**セルオートマトン**）。"
    "事故も工事もないのに、車がある密度をこえると、どこからともなく渋滞が生まれます（**自然渋滞**）。"
)
with st.container(border=True):
    st.markdown("**ナーゲル・シュレッケンベルグ模型**（1992 年）：各ステップで、すべての車について次の順に速さ $v$ を決め、位置 $x$ を進める。")
    st.markdown(
        r"""
1. **加速**：$v \leftarrow \min(v + 1,\ v_{\max})$（最高速度まで 1 ずつ速くなる）
2. **減速**：$v \leftarrow \min(v,\ \text{前の車までの空きマス})$（ぶつからない）
3. **ゆらぎ**：確率 $p$ で $v \leftarrow \max(v - 1,\ 0)$（よそ見や、気まぐれなブレーキ）
4. **移動**：$x_{n+1} = x_n + v_n$（位置の漸化式）
"""
    )

st.markdown("**アニメーション**　▶ を押すと車が動き出します（緑：速い、赤：止まっている）。右の時空図では、渋滞が帯になって見えます。")
render_anim("traffic", dict(L=L, density=density, vmax=vmax, p=p, seed=int(seed)), height=440)

ds, flows = fundamental(vmax, p)
v_now, q_now = nasch_flow(L, density, vmax, p, seed=int(seed))
i_max = max(range(len(flows)), key=flows.__getitem__)
m = st.columns(3)
m[0].metric("平均速度（十分たったあと）", f"{v_now:.2f} マス/ステップ", delta=f"最高速度の {100 * v_now / vmax:.0f}%", delta_color="off")
m[1].metric("流量（1 ステップに地点を通る車の数）", f"{q_now:.3f}")
m[2].metric("流量が最大になる密度", f"約 {ds[i_max]:.2f}", delta=f"ゆらぎがなければ 1/(v_max+1) = {1 / (vmax + 1):.2f}", delta_color="off")

fig = go.Figure()
fig.add_trace(go.Scatter(x=ds, y=flows, mode="lines+markers", name="流量", line=dict(color="#1f77b4", width=2.5)))
fig.add_trace(go.Scatter(x=[density], y=[q_now], mode="markers", marker=dict(color="#d62728", size=14, symbol="diamond"), name="いまの密度"))
fig.add_vline(x=ds[i_max], line_dash="dot", line_color="gray", annotation_text="ここをこえると渋滞")
fig.update_layout(height=360, template="plotly_white", margin=dict(l=10, r=10, t=30, b=10), showlegend=False,
                  title=dict(text="基本図：車の密度と流量", x=0.5, xanchor="center"),
                  xaxis=dict(title="密度"), yaxis=dict(title="流量 = 密度 × 平均速度", rangemode="tozero"))
st.plotly_chart(fig, key="tf_fd")
st.caption("密度が小さいうちは、車が増えるほど流量も増える（自由流）。ある密度をこえると、車が増えるほど流量が減る（渋滞流）。")

with st.expander("📖 解説：自然渋滞のしくみ"):
    st.markdown(
        r"""
- 車が少ないうちは、だれかがブレーキを踏んでも、後ろの車との間が空いているので影響が広がらない。
- 密度がある値をこえると、1 台の小さな減速で後ろの車が次々にブレーキを踏み、**止まる車の列** ができる。
- 列の先頭の車は空いた前方へ出ていき、後ろに新しい車がつくので、渋滞の列は **車の進む向きと反対へ** 移動していく（時空図の左下へ向かう帯）。
- ゆらぎ $p = 0$ にすると、密度が小さいときは渋滞が起きにくい。$p$ を大きくすると、低い密度でも渋滞が起きる。

**数列としての見方**　1 台の車の位置 $x_n$ は、$x_{n+1} = x_n + v_n$ という漸化式で決まる。ただし $v_n$ は前の車との距離で変わるので、
すべての車の数列が互いに関係し合っている。一般項は求められないが、コンピュータで 1 ステップずつ計算すると、全体の様子がわかる。
"""
    )

with st.expander("🔧 どこで使われている？"):
    st.markdown(
        r"""
- **交通工学**：高速道路の上り坂やトンネルの入口など、少しの減速が起きやすい所（サグ）で自然渋滞が起こりやすい。車間距離を十分にとる、速度を一定に保つ、などの対策の効果をシミュレーションで調べる。
- **信号の制御・道路の計画**：流量が最大になる密度をこえないように、入口で流入を調整する（ランプメータリング）。
- **人の流れ**：駅や会場の通路、避難のシミュレーションにも、同じようなセルオートマトンが使われる。
- 同じ規則で $v_{\max} = 1$、$p = 0$ にすると、ウルフラムの「ルール 184」とよばれる最も簡単な交通のモデルになる。
"""
    )

with st.expander("📝 考えてみよう"):
    st.markdown(
        r"""
1. $p = 0$、$v_{\max} = 5$ で、密度を 0.1 と 0.3 にしたとき、平均速度はどうちがうか。
2. 密度を 0.15 にして、$p$ を 0、0.2、0.4 と変えると、渋滞の帯はどう変わるか。
3. 時空図で、渋滞の帯が 1 ステップに何マスくらい後ろへ動いているか読み取ろう。
"""
    )
    with st.popover("答え（例）"):
        st.markdown(
            r"""
1. 0.1 では全員が最高速度 5 で走れる。0.3 では車間がつまって、平均速度は 2 くらいに下がる
2. $p$ が大きいほど、帯（渋滞）が多く、太くなる
3. 1 ステップに 1 マス以下の速さで、ゆっくり後ろへ動く（車の進む向きと反対）
"""
        )
