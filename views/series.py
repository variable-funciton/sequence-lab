"""いろいろな数列の和（級数）— 和はある値に近づくか（収束）、限りなく大きくなるか（発散）

1/n、1/n²、1/√n などの和 S_N = a_1 + a_2 + … + a_N を、N を大きくしながら観察する。バーゼル問題の紹介。
"""

import math

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.series import (
    EULER_GAMMA, SERIES, ZETA_HALF, basel_bound, harmonic_groups, p_series_partial, partial_sums, pi_from_basel, sample_indices,
)

COLORS = {"harmonic": "#d62728", "basel": "#1f77b4", "sqrt": "#ff7f0e", "quartic": "#17becf", "telescope": "#2ca02c",
          "geometric": "#9467bd", "alternating": "#8c564b"}
NS = [10, 100, 1000, 10_000, 100_000, 1_000_000]
for k, v in dict(sr_keys=["harmonic", "basel", "sqrt"], sr_N=10_000, sr_log=True, sr_p_on=False, sr_p=1.5).items():
    st.session_state.setdefault(k, v)

st.sidebar.header("設定")
keys = st.sidebar.multiselect("数列 aₙ（くらべたいものを選ぶ）", list(SERIES), format_func=lambda k: SERIES[k][0], key="sr_keys")
N = st.sidebar.select_slider("何項まで足すか N", options=NS, format_func=lambda n: f"{n:,}", key="sr_N")
log_x = st.sidebar.toggle("横軸を対数目盛にする", key="sr_log")
p_on = st.sidebar.checkbox("1/nᵖ（p を自分で決める）も表示", key="sr_p_on")
p = st.sidebar.slider("p", 0.5, 3.0, step=0.1, key="sr_p", disabled=not p_on)

st.title("いろいろな数列の和：収束と発散")
st.markdown(
    r"数列 $a_n$ の項を順に足した **部分和** $S_N = a_1 + a_2 + \cdots + a_N$ は、$N$ を大きくするとどうなるでしょうか。"
    r"等比数列 $\dfrac{1}{2^n}$ の和は 1 に近づきました（**収束**）。では $\dfrac{1}{n}$、$\dfrac{1}{n^2}$、$\dfrac{1}{\sqrt{n}}$ は？"
    r"項がどれも 0 に近づくのに、和が一定の値に近づくものと、限りなく大きくなるもの（**発散**）があります。"
)
if not keys and not p_on:
    st.info("左のサイドバーで数列を選んでください。")
    st.stop()

idx = sample_indices(N)
sums = {k: partial_sums(k, N) for k in keys}
if p_on:
    sums["p"] = p_series_partial(p, N)

tab1, tab2, tab3, tab4 = st.tabs(["① 部分和をくらべる", "② 1 項ずつ足す様子", "③ バーゼル問題（1/n² の和）", "④ なぜ収束・発散するのか"])

with tab1:
    fig = go.Figure()
    for k, S in sums.items():
        name = SERIES[k][0] if k != "p" else f"1/n^{p:g}"
        color = COLORS.get(k, "#7f7f7f")
        fig.add_trace(go.Scatter(x=idx, y=S[idx - 1], mode="lines", name=name, line=dict(color=color, width=2.5),
                                 hovertemplate="N = %{x:,}：%{y:.6f}<extra>" + name + "</extra>"))
        lim = SERIES[k][3] if k != "p" else None
        if lim is not None:
            fig.add_hline(y=lim, line_dash="dot", line_color=color, annotation_text=f"{lim:.6f}", annotation_position="top left")
    fig.update_layout(height=440, template="plotly_white", margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=1.1),
                      xaxis=dict(title="N（足した項の数）", type="log" if log_x else "linear"), yaxis=dict(title="部分和 S_N"))
    st.plotly_chart(fig, key="sr_main")
    st.caption("点線は、和が近づいていく値（極限）。横軸を対数目盛にすると、10 項・100 項・1000 項 … を同じ間隔で見られる。")

    rows = []
    for k, S in sums.items():
        name = SERIES[k][0] if k != "p" else f"1/n^{p:g}"
        row = {"数列 aₙ": name}
        for n in NS:
            if n <= N:
                row[f"S_{n:,}"] = f"{S[n - 1]:.6f}"
        if k != "p":
            row["N → ∞"] = "収束：" + (f"{SERIES[k][3]:.6f}") if SERIES[k][3] is not None else "発散（∞）"
        else:
            row["N → ∞"] = "収束" if p > 1 else "発散（∞）"
        rows.append(row)
    st.dataframe(pd.DataFrame(rows), hide_index=True)

    c = st.columns(3)
    if "harmonic" in sums:
        c[0].metric(f"1/n の和（N = {N:,}）", f"{sums['harmonic'][-1]:.4f}", delta=f"logₑN + γ ≈ {math.log(N) + EULER_GAMMA:.4f}", delta_color="off")
    if "sqrt" in sums:
        c[1].metric(f"1/√n の和（N = {N:,}）", f"{sums['sqrt'][-1]:.2f}", delta=f"2√N + ζ(1/2) ≈ {2 * math.sqrt(N) + ZETA_HALF:.2f}", delta_color="off")
    if "basel" in sums:
        c[2].metric(f"1/n² の和（N = {N:,}）", f"{sums['basel'][-1]:.6f}", delta=f"π²/6 との差 {math.pi ** 2 / 6 - sums['basel'][-1]:.2e}", delta_color="off")
    st.info(
        "**観察のポイント**\n"
        "- $\\frac{1}{n}$ の和は、1 万項で約 9.8、100 万項で約 14.4。ゆっくりだが、いつまでも増え続ける（発散）。"
        "横軸を対数目盛にすると、ほぼまっすぐ増えていく（$N$ が 10 倍になるたびに約 2.3 ずつ増える）。\n"
        "- $\\frac{1}{\\sqrt{n}}$ の和は、もっと速く増える（$2\\sqrt{N}$ 程度）。\n"
        "- $\\frac{1}{n^2}$ の和は、1.6449… に近づき、2 をこえない（収束）。"
    )

with tab2:
    k2 = st.selectbox("数列", list(SERIES), format_func=lambda k: SERIES[k][0], key="sr_k2")
    n2 = st.slider("何項まで足すか", 1, 40, 12, key="sr_n2")
    name, tex, f, lim, lim_tex = SERIES[k2]
    ns = np.arange(1, n2 + 1, dtype=float)
    terms = f(ns)
    S2 = np.cumsum(terms)
    st.latex(rf"a_n = {tex},\qquad S_{{{n2}}} = " + " + ".join(f"{t:.3g}" for t in terms[:6]) + (r" + \cdots" if n2 > 6 else "")
             + rf" \approx {S2[-1]:.5f}")
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=ns, y=terms, name="項 aₙ", marker_color="#9aa0a6", hovertemplate="a_%{x} = %{y:.5f}<extra></extra>"))
    fig2.add_trace(go.Scatter(x=ns, y=S2, mode="lines+markers", name="部分和 Sₙ", line=dict(color=COLORS[k2], width=3),
                              hovertemplate="S_%{x} = %{y:.5f}<extra></extra>"))
    if lim is not None:
        fig2.add_hline(y=lim, line_dash="dot", line_color=COLORS[k2], annotation_text=f"極限 {lim:.5f}")
    fig2.update_layout(height=380, template="plotly_white", margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=1.1),
                       xaxis=dict(title="n", dtick=1 if n2 <= 20 else 5))
    st.plotly_chart(fig2, key="sr_steps")
    st.caption("灰色の棒が足す項、線が部分和。項はどれも 0 に近づいていくが、それだけでは和が収束するとは限らない。")

with tab3:
    S = partial_sums("basel", N)
    st.markdown(
        r"""
$$1 + \frac{1}{2^2} + \frac{1}{3^2} + \frac{1}{4^2} + \cdots = \frac{\pi^2}{6} = 1.6449340668\cdots$$

平方数の逆数の和がいくつになるかという問題は、17 世紀にイタリアのメンゴリが出し、ベルヌーイ兄弟など多くの数学者が挑戦しましたが、
長い間解けませんでした。1734 年ごろ、スイスの **オイラー** が、答えが $\dfrac{\pi^2}{6}$ であることを示しました。
オイラーやベルヌーイ家の出身地 **バーゼル**（スイス）にちなんで **バーゼル問題** とよばれます。

整数だけでできた和に、円周率 $\pi$ が現れるのが驚きです。
"""
    )
    m = st.columns(3)
    m[0].metric(f"S_N（N = {N:,}）", f"{S[-1]:.10f}")
    m[1].metric("π²/6", f"{math.pi ** 2 / 6:.10f}", delta=f"差 {math.pi ** 2 / 6 - S[-1]:.2e}（約 1/N）", delta_color="off")
    m[2].metric("√(6 S_N) で π を近似", f"{pi_from_basel(S[-1]):.8f}", delta=f"π = {math.pi:.8f}", delta_color="off")
    rows = [{"N": f"{n:,}", "S_N": f"{S[n - 1]:.10f}", "π²/6 − S_N": f"{math.pi ** 2 / 6 - S[n - 1]:.3e}", "1/N": f"{1 / n:.3e}",
             "√(6 S_N)": f"{pi_from_basel(S[n - 1]):.8f}"} for n in NS if n <= N]
    st.dataframe(pd.DataFrame(rows), hide_index=True)
    st.caption("N を 10 倍にすると、π²/6 との差はほぼ 1/10 になる（差は約 1/N）。100 万項足しても、π は小数第 5 位くらいまでしか合わない（収束がおそい）。")
    with st.expander("📖 オイラーの考え方（あらすじ）"):
        st.markdown(
            r"""
オイラーは、$\sin x$ を多項式のように考えました（「テイラー展開」：三角関数のアプリの発展のページ）。

$$\frac{\sin x}{x} = 1 - \frac{x^2}{3!} + \frac{x^4}{5!} - \cdots$$

左辺は $x = \pm\pi, \pm2\pi, \pm3\pi, \dots$ で 0 になるので、多項式の因数分解のように

$$\frac{\sin x}{x} = \left(1 - \frac{x^2}{\pi^2}\right)\left(1 - \frac{x^2}{4\pi^2}\right)\left(1 - \frac{x^2}{9\pi^2}\right)\cdots$$

と書けると考えました。右辺を展開したときの $x^2$ の係数は $-\dfrac{1}{\pi^2}\left(1 + \dfrac{1}{4} + \dfrac{1}{9} + \cdots\right)$、
左辺の $x^2$ の係数は $-\dfrac{1}{6}$。この 2 つが等しいとおくと

$$1 + \frac{1}{4} + \frac{1}{9} + \cdots = \frac{\pi^2}{6}$$

（無限個の因数の積を、ふつうの多項式と同じように扱ってよいことは、後に厳密に示されました。）
オイラーは同じ方法で $1 + \dfrac{1}{2^4} + \dfrac{1}{3^4} + \cdots = \dfrac{\pi^4}{90}$ なども求めています。
"""
        )

with tab4:
    st.markdown("#### 1/n の和が発散すること（14 世紀のオレームの方法）")
    st.markdown(
        r"""
項を 1 個、1 個、2 個、4 個、8 個、… とまとめると、2 番目以降のどのまとまりも $\dfrac{1}{2}$ 以上になります。

$$1 + \frac{1}{2} + \underbrace{\left(\frac{1}{3} + \frac{1}{4}\right)}_{> \frac{1}{4} + \frac{1}{4} = \frac{1}{2}} + \underbrace{\left(\frac{1}{5} + \frac{1}{6} + \frac{1}{7} + \frac{1}{8}\right)}_{> \frac{1}{8}\times4 = \frac{1}{2}} + \cdots$$

したがって $S_{2^k} \ge 1 + \dfrac{k}{2}$。$k$ をいくらでも大きくできるので、和は限りなく大きくなる（発散）。
"""
    )
    g = harmonic_groups(7)
    st.dataframe(pd.DataFrame([{"まとまり": f"1/{a}" if a == b else f"1/{a} 〜 1/{b}", "項の数": b - a + 1, "和": f"{s:.4f}",
                                "1/2 以上か": "—" if i == 0 else ("○" if s >= 0.5 else "×")} for i, (a, b, s) in enumerate(g)]), hide_index=True)

    st.markdown("#### 1/√n の和も発散すること（くらべる）")
    st.markdown(r"$n \ge 1$ のとき $\sqrt{n} \le n$ なので $\dfrac{1}{\sqrt{n}} \ge \dfrac{1}{n}$。発散する和より大きいので、これも発散する。")

    st.markdown("#### 1/n² の和が 2 をこえないこと（分数の差に分ける）")
    st.markdown(
        r"""
$n \ge 2$ のとき $\dfrac{1}{n^2} < \dfrac{1}{n(n-1)} = \dfrac{1}{n-1} - \dfrac{1}{n}$ なので

$$S_N < 1 + \left(1 - \frac{1}{2}\right) + \left(\frac{1}{2} - \frac{1}{3}\right) + \cdots + \left(\frac{1}{N-1} - \frac{1}{N}\right) = 2 - \frac{1}{N} < 2$$

部分和は増え続けるが 2 をこえない。増え続けて、ある値をこえない数列は、一定の値に近づく（収束）。
"""
    )
    S = partial_sums("basel", N)
    st.caption(f"確かめ：N = {N:,} のとき S_N = {S[-1]:.6f} < 2 − 1/N = {basel_bound(N):.6f}")

    st.markdown("#### 1/nᵖ の和（p 級数）")
    st.markdown(
        r"""
$\dfrac{1}{n^p}$ の和は、**$p > 1$ なら収束、$p \le 1$ なら発散** することが知られています。
$p = 1$（調和級数）がちょうど境目。サイドバーで「1/nᵖ も表示」にして、$p$ を 1 の前後で変えて観察しよう
（$p$ が 1 に近いと、収束する場合でも非常にゆっくり近づく）。
"""
    )

with st.expander("🔧 どこで使われている？"):
    st.markdown(
        r"""
- **コンピュータの計算**：$\sin x$ や $\pi$ などの値は、収束する和を必要な項まで計算して求める。速く収束する式を選ぶことが大切
  （$1/n^2$ の和で $\pi$ を求めるのはおそすぎる）。
- **物理・工学**：ボールの跳ね返りの道のり（無限等比級数）、フーリエ級数（三角関数の和で波を表す）。
- **積み木の張り出し**：同じ積み木をずらして積むと、張り出しの長さは $\dfrac{1}{2}\left(1 + \dfrac{1}{2} + \dfrac{1}{3} + \cdots\right)$ になり、
  調和級数が発散するので、（理論上は）いくらでも遠くまで張り出せる。
- 参考：[The Basel Problem（arXiv、英語）](https://arxiv.org/abs/2010.03953)
"""
    )

with st.expander("📝 考えてみよう"):
    st.markdown(
        r"""
1. $\dfrac{1}{1\cdot2} + \dfrac{1}{2\cdot3} + \cdots + \dfrac{1}{N(N+1)}$ を、$\dfrac{1}{n(n+1)} = \dfrac{1}{n} - \dfrac{1}{n+1}$ を使って計算しよう。$N \to \infty$ ではどうなるか。
2. 調和級数の部分和が初めて 3 をこえるのは何項目か。② のタブで確かめよう。
3. オレームの方法で、$S_{1024} \ge 6$ を示そう（$1024 = 2^{10}$）。
"""
    )
    with st.popover("答え"):
        st.markdown(
            r"""
1. $1 - \dfrac{1}{N+1}$。$N \to \infty$ で 1 に近づく
2. $S_{10} \approx 2.929$、$S_{11} \approx 3.020$ より 11 項目
3. $S_{2^{10}} \ge 1 + \dfrac{10}{2} = 6$
"""
        )
