"""【都市】人口の変化を等比数列で表す — 将来推計人口との比較"""

import plotly.graph_objects as go
import streamlit as st

from utils.applied import IPSS_2023, annual_ratio, year_reaching

MODES = {"japan": "日本の総人口（将来推計と比べる）", "own": "自分で 2 つの年の人口を入れる（市町村など）"}
for k, v in dict(pp_mode="japan", pp_y2=2070, pp_P1=50000.0, pp_y1=2015, pp_P2=46000.0, pp_y2o=2025, pp_until=2070).items():
    st.session_state.setdefault(k, v)

st.sidebar.header("設定")
mode = st.sidebar.radio("データ", list(MODES), format_func=MODES.get, key="pp_mode")
if mode == "japan":
    y1, P1 = 2020, IPSS_2023[2020]
    y2 = st.sidebar.selectbox("公比を決めるのに使う年", [2065, 2070], index=1, key="pp_y2")
    P2 = IPSS_2023[y2]
    until = 2070
    unit = "万人"
else:
    P1 = st.sidebar.number_input("はじめの年の人口", min_value=1.0, max_value=1e9, step=1000.0, key="pp_P1")
    y1 = int(st.sidebar.number_input("はじめの年", min_value=1900, max_value=2100, step=1, key="pp_y1"))
    P2 = st.sidebar.number_input("あとの年の人口", min_value=1.0, max_value=1e9, step=1000.0, key="pp_P2")
    y2 = int(st.sidebar.number_input("あとの年", min_value=1901, max_value=2101, step=1, key="pp_y2o"))
    st.session_state["pp_until"] = max(st.session_state["pp_until"], y2 + 1)
    until = int(st.sidebar.number_input("何年まで予測するか", min_value=y2 + 1, max_value=2200, step=5, key="pp_until"))
    unit = "人"
    if y2 <= y1:
        st.error("あとの年は、はじめの年より後にしてください。")
        st.stop()

r = annual_ratio(P1, y1, P2, y2)
years = list(range(y1, until + 1))
model = [P1 * r ** (y - y1) for y in years]

st.title("人口の変化を等比数列で表す")
st.markdown(
    "人口が **毎年同じ割合** で変わると考えると、毎年の人口は等比数列になります。"
    "2 つの年の人口から公比 $r$ を決め、将来の人口を予測して、国の推計と比べてみましょう。"
)
with st.container(border=True):
    st.latex(rf"P_n = P_0 r^n\quad(n\ \text{{年後}}),\qquad r = \left(\frac{{P_{{{y2 - y1}}}}}{{P_0}}\right)^{{1/{y2 - y1}}}"
             rf" = \left(\frac{{{P2:g}}}{{{P1:g}}}\right)^{{1/{y2 - y1}}} \approx {r:.5f}")

m = st.columns(4)
m[0].metric("公比 r（1 年あたり）", f"{r:.5f}", delta=f"毎年 {100 * (r - 1):+.2f}%", delta_color="off")
half = year_reaching(P1, y1, r, P1 / 2) if r < 1 else None
dbl = year_reaching(P1, y1, r, P1 * 2) if r > 1 else None
if mode == "japan":
    y_1oku = year_reaching(P1, y1, r, 10000)
    p2065 = P1 * r ** (2065 - y1)
    m[1].metric("1 億人を下回る年（モデル）", f"{y_1oku} 年", delta="推計では 2056 年", delta_color="off")
    m[2].metric("2065 年の人口（モデル）", f"{p2065:,.0f} 万人", delta=f"推計 {IPSS_2023[2065]:,} 万人", delta_color="off")
    m[3].metric("半分になる年（モデル）", f"{half} 年" if half else "—")
else:
    m[1].metric(f"{until} 年の人口（モデル）", f"{model[-1]:,.0f} 人")
    m[2].metric("半分になる年" if r < 1 else "2 倍になる年", f"{half or dbl} 年" if (half or dbl) else "—")
    m[3].metric("10 年で何倍か", f"{r ** 10:.3f} 倍")

fig = go.Figure()
fig.add_trace(go.Scatter(x=years, y=model, mode="lines", name="等比数列のモデル", line=dict(color="#d62728", width=2.5),
                         hovertemplate="%{x} 年：%{y:,.0f}<extra>モデル</extra>"))
if mode == "japan":
    xs = sorted(IPSS_2023)
    fig.add_trace(go.Scatter(x=xs, y=[IPSS_2023[x] for x in xs], mode="markers+text", name="国勢調査・将来推計（出生中位）",
                             text=["2020 国勢調査", "2056 1 億人を下回る", "2065", "2070"], textposition="top right",
                             marker=dict(color="#1f77b4", size=11)))
    fig.add_hline(y=10000, line_dash="dot", line_color="gray", annotation_text="1 億人")
else:
    fig.add_trace(go.Scatter(x=[y1, y2], y=[P1, P2], mode="markers", name="入力した人口", marker=dict(color="#1f77b4", size=11)))
fig.update_layout(height=420, template="plotly_white", margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=1.08),
                  xaxis=dict(title="年"), yaxis=dict(title=f"人口 [{unit}]", tickformat=","))
st.plotly_chart(fig, key="pp_chart")

if mode == "japan":
    st.info(
        "2020 年と 2070 年の 2 点を通る等比数列では、1 億人を下回るのは推計（2056 年）より早く、2065 年の人口は推計より少なめになります。"
        "推計では、減り方が初めはゆるやかで、だんだん速くなっていくためです（毎年同じ割合ではない）。"
        "モデルと実際の差から、「なぜずれるのか」を考えることも大切です。"
    )

with st.expander("📖 解説：等比数列のモデルと、その限界"):
    st.markdown(
        r"""
**公比の求め方**　$y_1$ 年に $P_0$、$y_2$ 年に $P$ なら、$m = y_2 - y_1$ 年で $\dfrac{P}{P_0}$ 倍。毎年 $r$ 倍なら $r^m = \dfrac{P}{P_0}$ なので
$r = \left(\dfrac{P}{P_0}\right)^{1/m}$（$m$ 乗根）。

**何年で半分になるか**　$r^n \le \dfrac{1}{2}$ となる最小の $n$。毎年 1% 減ると約 69 年、2% 減ると約 35 年
（複利の「72 の法則」と同じ考え方で、約 $\dfrac{70}{\text{減る \%}}$ 年）。

**実際の推計の方法**　国の将来推計人口は、男女・年齢ごとの人数に、出生率・死亡率・国外との出入りの仮定を当てはめて、
1 年ずつ計算していく（**コーホート要因法**）。年齢の構成が変わるので、減り方は毎年同じ割合にはならない。
等比数列のモデルは、大まかな見通しを立てたり、変化の速さを比べたりするのに使う。
"""
    )

with st.expander("🔧 どこで使われている？"):
    st.markdown(
        r"""
- **都市計画・インフラの計画**：将来の人口から、必要な道路・上下水道・学校・病院の規模を見積もる。人口が減る地域では施設の統合も考える。
- **公共交通**：利用者数の見通しから、バスや鉄道の本数・路線を計画する。
- 市町村の人口は、各自治体のホームページや国勢調査（総務省統計局）で調べられる。「自分で入れる」モードで、自分の町の将来を予測してみよう。
- 参考：[国立社会保障・人口問題研究所「日本の将来推計人口（令和5年推計）」](https://www.ipss.go.jp/pp-zenkoku/j/zenkoku2023/pp_zenkoku2023.asp)
  （このページの値：2020 年 1 億 2,615 万人、2056 年に 1 億人を下回る、2065 年 9,159 万人、2070 年 8,700 万人。出生中位・死亡中位推計）
"""
    )

with st.expander("📝 考えてみよう"):
    st.markdown(
        r"""
1. 人口 5 万人の町が、毎年 1% ずつ減るとする。10 年後の人口を求めよう（$0.99^{10} \approx 0.904$）。
2. 2020 年に 1 億 2,615 万人、2070 年に 8,700 万人として、50 年で何倍になったか。1 年あたりの公比を電卓で求めよう。
3. 2. の公比で、2056 年の人口を予測し、推計（1 億人）と比べよう。
"""
    )
    with st.popover("答え"):
        st.markdown(
            r"""
1. $50000\times0.99^{10} \approx 45200$ 人
2. $\dfrac{8700}{12615} \approx 0.690$ 倍。公比は $0.690^{1/50} \approx 0.9926$（毎年約 0.74% 減）
3. $12615\times0.9926^{36} \approx 9650$ 万人。推計（1 億人）より約 350 万人少ない
"""
        )
