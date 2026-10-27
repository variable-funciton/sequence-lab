"""【プログラミングのための数列】ニュートン法 — √2 を求める漸化式から、接線で方程式を解く方法へ"""

import math

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.anim import render as render_anim
from utils.newton import (
    EXAMPLES, bisection, correct_digits, digits_split, heron, newton, poly, poly_tex, reciprocal, true_sqrt,
)

PREC = 60
for k, v in dict(nw_a=2, nw_x0=1.0, nw_N=6, nw_bN=30, nw_ex="sqrt2", nw_eN=6).items():
    st.session_state.setdefault(k, v)

st.title("ニュートン法：√2 を求める漸化式")
st.markdown(
    "電卓やコンピュータは、$\\sqrt{2}$ をどうやって計算しているのでしょうか。"
    "答えの一つは、**漸化式で近い値をくり返し改良していく** 方法です。"
    "ここでは、$\\sqrt{2}$ を求める昔からの方法（バビロニアの方法・ヘロンの方法）から始めて、"
    "方程式を解く **ニュートン法** へ進みます。どれも、短いプログラムで書けます。"
)
tab1, tab2, tab3, tab4 = st.tabs(["① √a を求める漸化式", "② 二分法とくらべる", "③ 発展：接線で考えるニュートン法", "④ どこで使われている？"])

# ================================================================
with tab1:
    c = st.columns(3)
    a = int(c[0].number_input("a（√a を求める）", min_value=2, max_value=1000, step=1, key="nw_a"))
    x0 = c[1].number_input("はじめの値 x₀", min_value=0.1, max_value=1000.0, step=0.5, key="nw_x0")
    N = c[2].slider("くり返す回数", 1, 10, key="nw_N")

    st.markdown(
        rf"面積 ${a}$ の長方形を考えます。横を $x$ とすると縦は $\dfrac{{{a}}}{{x}}$。"
        rf"横と縦の **平均** を新しい横にすると、長方形は正方形（1 辺 $\sqrt{{{a}}}$）に近づいていきます。"
    )
    with st.container(border=True):
        st.latex(rf"x_{{n+1}} = \frac{{1}}{{2}}\left(x_n + \frac{{{a}}}{{x_n}}\right),\qquad x_0 = {x0:g}")
    xs = heron(a, x0, N, PREC)
    t = true_sqrt(a, PREC)
    render_anim("newton_rect", dict(a=a, xs=[float(x) for x in xs]), height=430)

    st.markdown(f"**正しい桁（緑）が 1 回ごとにほぼ 2 倍になる**　（√{a} = {t:.40f}…）")
    rows = []
    for n, x in enumerate(xs):
        ok, rest = digits_split(x, t, 40)
        rows.append(f"<tr><td>{n}</td><td style='font-family:monospace'><span style='color:#2ca02c;font-weight:700'>{ok}</span>"
                    f"<span style='color:#999'>{rest}</span></td><td style='text-align:right'>{correct_digits(x, t)}</td></tr>")
    st.markdown("<table style='font-size:14px'><tr><th>n</th><th>xₙ（小数第 40 位まで）</th><th>正しい桁数</th></tr>"
                + "".join(rows) + "</table>", unsafe_allow_html=True)

    with st.expander("📖 解説：なぜ √a に近づくのか・なぜ桁が倍々になるのか"):
        st.markdown(
            rf"""
**極限**　$x_n$ がある値 $\alpha$ に近づくなら、$\alpha = \dfrac{{1}}{{2}}\left(\alpha + \dfrac{{{a}}}{{\alpha}}\right)$。
整理すると $\alpha^2 = {a}$ なので $\alpha = \sqrt{{{a}}}$（ローン返済の特性方程式と同じ考え方）。

**いつも √a 以上**　相加平均と相乗平均の関係より、$n \ge 1$ のとき
$$x_{{n+1}} = \frac{{1}}{{2}}\left(x_n + \frac{{{a}}}{{x_n}}\right) \ge \sqrt{{x_n\cdot\frac{{{a}}}{{x_n}}}} = \sqrt{{{a}}}$$
さらに $x_n \ge \sqrt{{{a}}}$ なら $\dfrac{{{a}}}{{x_n}} \le x_n$ なので $x_{{n+1}} \le x_n$。
**減り続けて、$\sqrt{{{a}}}$ より小さくならない** ので、ある値に近づく（収束する）。

**誤差が 2 乗で小さくなる**　$e_n = x_n - \sqrt{{{a}}}$ とすると、通分して整理すると
$$e_{{n+1}} = x_{{n+1}} - \sqrt{{{a}}} = \frac{{x_n^2 - 2\sqrt{{{a}}}\,x_n + {a}}}{{2x_n}} = \frac{{e_n^2}}{{2x_n}}$$
誤差が $0.01$ なら次は約 $0.0001\div(2\sqrt{{{a}}})$。誤差の桁数が倍になる＝**正しい桁数がほぼ 2 倍** になる。
このような速さを「**2 次収束**」という。
"""
        )
    st.markdown("**プログラムで書くと**（Python）")
    st.code(f"a = {a}\nx = {x0:g}            # はじめの値\nfor n in range({N}):\n    x = (x + a / x) / 2   # 漸化式\n    print(n + 1, x)", language="python")

# ================================================================
with tab2:
    st.markdown(
        r"**二分法**：$x^2 - a$ の符号が変わる範囲 $[\text{下端}, \text{上端}]$ を、中点で半分に分けることをくり返します。"
        r"範囲の幅は 1 回ごとに $\dfrac{1}{2}$ 倍（**等比数列**）。確実だが、ゆっくりです。"
    )
    bN = st.slider("くり返す回数", 5, 60, key="nw_bN")
    a2 = int(st.session_state["nw_a"])
    lo = math.floor(math.sqrt(a2))
    hi = lo + 1
    bs = bisection(a2, lo, hi, bN, PREC)
    t2 = true_sqrt(a2, PREC)
    hx = heron(a2, hi, min(bN, 10), PREC)
    eb = [max(float(abs(m - t2)), 1e-50) for _, _, m in bs]
    eh = [max(float(abs(x - t2)), 1e-50) for x in hx]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=list(range(len(eb))), y=eb, mode="lines+markers", name="二分法（幅が 1/2 倍ずつ）", line=dict(color="#1f77b4")))
    fig.add_trace(go.Scatter(x=list(range(len(eh))), y=eh, mode="lines+markers", name="ニュートン法（誤差が 2 乗ずつ）", line=dict(color="#d62728")))
    fig.update_layout(height=380, template="plotly_white", margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=1.1),
                      xaxis=dict(title="くり返した回数 n"), yaxis=dict(title=f"√{a2} との誤差（対数目盛）", type="log", exponentformat="power"))
    st.plotly_chart(fig, key="nw_cmp")
    st.caption(f"範囲 [{lo}, {hi}] から始めた二分法と、x₀ = {hi} から始めたニュートン法。対数目盛では、二分法はまっすぐ（等比数列）、"
               "ニュートン法は急に落ちていく。1e−50 で止めて表示している（それ以下は計算の桁が足りない）。")
    m = st.columns(2)
    need_b = next((n for n, e in enumerate(eb) if e < 1e-10), None)
    need_h = next((n for n, e in enumerate(eh) if e < 1e-10), None)
    m[0].metric("誤差が 10⁻¹⁰ 未満になる回数（二分法）", f"{need_b} 回" if need_b is not None else f"{bN} 回では未到達")
    m[1].metric("誤差が 10⁻¹⁰ 未満になる回数（ニュートン法）", f"{need_h} 回" if need_h is not None else "—")
    with st.expander("二分法の表"):
        st.dataframe(pd.DataFrame([{"n": n, "下端": f"{l:.12f}", "上端": f"{h:.12f}", "中点": f"{mm:.12f}", "幅": f"{float(h - l):.3e}"}
                                   for n, (l, h, mm) in enumerate(bs[:25])]), hide_index=True)
    st.markdown("**プログラムで書くと**（Python）")
    st.code(f"a = {a2}\nlo, hi = {lo}, {hi}          # √a はこの間にある\nfor n in range({bN}):\n    mid = (lo + hi) / 2\n    if mid * mid > a:\n        hi = mid\n    else:\n        lo = mid\nprint(lo, hi)", language="python")
    st.info("二分法は、範囲さえわかればいつでも使えて失敗しない。ニュートン法は速いが、はじめの値によってはうまくいかないこともある（③）。"
            "実際のプログラムでは、二分法で大まかに近づいてからニュートン法を使う、などの組み合わせもある。")

# ================================================================
with tab3:
    st.markdown(
        r"""
曲線 $y = f(x)$ 上の点 $(x_n,\ f(x_n))$ で **接線** を引き、接線が $x$ 軸と交わる点を次の $x_{n+1}$ にします。
接線の傾きを $f'(x_n)$ とすると、接線の式 $y = f(x_n) + f'(x_n)(x - x_n)$ で $y = 0$ として
"""
    )
    st.latex(r"x_{n+1} = x_n - \frac{f(x_n)}{f'(x_n)}\qquad(\text{ニュートン法})")
    st.caption(r"接線の傾きは 2 年生で学ぶ「微分」で求める。ここでは $x^2$ の傾きは $2x$、$x^3$ の傾きは $3x^2$ を使う"
               r"（三角関数アプリの「接線の傾き」のページも参考に）。$f(x) = x^2 - a$ なら $x_{n+1} = x_n - \frac{x_n^2 - a}{2x_n} = \frac{1}{2}(x_n + \frac{a}{x_n})$ で、① と同じ式になる。")
    ex = st.selectbox("例", list(EXAMPLES), format_func=lambda k: EXAMPLES[k][0], key="nw_ex")
    name, coefs, ex0, note = EXAMPLES[ex]
    c = st.columns(2)
    x0e = c[0].number_input("はじめの値 x₀", value=float(ex0), step=0.1, format="%.2f", key=f"nw_x0_{ex}")
    eN = c[1].slider("くり返す回数", 1, 10, key="nw_eN")
    xs3 = newton(coefs, x0e, eN)
    ftex = poly_tex(coefs)
    st.markdown(f"$f(x) = {ftex}$　　{note}")
    render_anim("newton_tangent", dict(coefs=coefs, xs=xs3, fplain=ftex.replace("x^{3}", "x³").replace("x^{2}", "x²"),
                                       range=[-2.2, 1.6] if ex == "cycle" else None), height=520)
    if len(xs3) <= eN:
        st.warning("接線の傾きが 0 になり、接線が x 軸と交わらないので、計算を続けられなくなった。")
    st.dataframe(pd.DataFrame([{"n": n, "xₙ": f"{x:.15g}", "f(xₙ)": f"{poly(coefs, x):.3e}"} for n, x in enumerate(xs3)]), hide_index=True)
    with st.expander("📖 うまくいかない例"):
        st.markdown(
            r"""
- **行ったり来たりする**：$x^3 - 2x + 2 = 0$ を $x_0 = 0$ から始めると $0 \to 1 \to 0 \to 1 \to \cdots$（例で選べる）。
- **接線が水平**：$f'(x_n) = 0$ になると、接線が $x$ 軸と交わらず、次の値が決まらない（$x^2 - 2$ で $x_0 = 0$ にしてみよう）。
- **別の解に行く**：はじめの値によって、どの解に近づくかが変わる（$x^2 - 2$ で $x_0 = -1$ なら $-\sqrt{2}$）。

そのため、プログラムでは「くり返す回数の上限」や「値が変わらなくなったら止める」などの工夫をする。
"""
        )
    st.markdown("**プログラムで書くと**（Python）")
    st.code(f"def f(x):\n    return {ftex.replace('x^{3}', 'x**3').replace('x^{2}', 'x**2').replace('2x', '2*x')}\n\n"
            f"def df(x):                  # 接線の傾き\n    return {poly_tex([c * (len(coefs) - 1 - i) for i, c in enumerate(coefs[:-1])]).replace('x^{2}', 'x**2').replace('3x', '3*x').replace('2x', '2*x')}\n\n"
            f"x = {x0e:g}\nfor n in range({eN}):\n    x = x - f(x) / df(x)    # 漸化式\n    print(n + 1, x)", language="python")

# ================================================================
with tab4:
    st.markdown(
        r"""
- **電卓・コンピュータの平方根**：$\sqrt{x}$ を計算する部品の中では、① のような漸化式（や、その仲間）を数回くり返している。
  正しい桁数が倍々になるので、数回で必要な精度になる。
- **割り算を掛け算で**：$\dfrac{1}{a}$ は、$f(x) = \dfrac{1}{x} - a$ にニュートン法を使った $x_{n+1} = x_n(2 - ax_n)$ で、
  **掛け算と引き算だけ** で求められる。割り算の回路が遅かった時代の計算機で実際に使われた考え方。
- **3D ゲームの計算**：光の当たり方の計算に $\dfrac{1}{\sqrt{x}}$ が大量に必要になるため、だいたいの値からニュートン法を 1 回だけ使って速く計算する工夫が知られている。
- **回路・構造・化学平衡のシミュレーション**：解の公式がない方程式を、ニュートン法をくり返して解く。
"""
    )
    ar = st.number_input("1/a を割り算なしで求める：a", min_value=1.0, max_value=100.0, value=7.0, step=1.0, key="nw_ra")
    x0r = 0.1 if ar < 10 else 0.01
    rs = reciprocal(ar, x0r, 6)
    st.latex(rf"x_{{n+1}} = x_n(2 - {ar:g}\,x_n),\qquad x_0 = {x0r:g}")
    st.dataframe(pd.DataFrame([{"n": n, "xₙ": f"{x:.15f}", "1/a との差": f"{abs(x - 1 / ar):.2e}"} for n, x in enumerate(rs)]), hide_index=True)
    st.caption(f"1/{ar:g} = {1 / ar:.15f}。掛け算と引き算だけで、6 回でほぼ正しい値になる（x₀ が 0 と 2/a の間にあれば近づく）。")

with st.expander("📝 考えてみよう"):
    st.markdown(
        r"""
1. $x_0 = 1$ から $x_{n+1} = \dfrac{1}{2}\left(x_n + \dfrac{2}{x_n}\right)$ で $x_1, x_2, x_3$ を分数で求めよう。
2. $x_3^2$ と 2 の差を求め、$x_3$ が $\sqrt{2}$ にどれだけ近いか確かめよう。
3. 二分法で、範囲 [1, 2] の幅を 0.001 より小さくするには、何回くり返せばよいか。
"""
    )
    with st.popover("答え"):
        st.markdown(
            r"""
1. $x_1 = \dfrac{3}{2},\ x_2 = \dfrac{17}{12},\ x_3 = \dfrac{577}{408}$
2. $\left(\dfrac{577}{408}\right)^2 = \dfrac{332929}{166464}$ で、2 との差は $\dfrac{1}{166464} \approx 0.000006$
3. $\left(\dfrac{1}{2}\right)^n < 0.001$ より $n = 10$（$2^{10} = 1024$）
"""
        )
