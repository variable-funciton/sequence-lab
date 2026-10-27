"""ローン返済で学ぶ漸化式（月次・総合版）— loan_recurrence_app_v2.py を移植

12 のタブで、元利均等返済・返済不能シナリオ・リボ払い・残クレ・設備投資までを扱う。
移植時の変更点:
  - st.set_page_config は LevelPayment.py（エントリーポイント）で行うため削除
  - ⑫ 設備投資のタブを ⑪ の with ブロックの外に出した（表示は同じ）
  - ⑫ の比較表が字下げのせいでコードブロック表示になっていたのを修正
  - 問13 の検算（≒ 888 万円）、問14 の結論（約8割）の数値を修正
  - 問7・問8 の対数が自然対数であることを明記
  - 返済年数が短いとき「金利上昇の時期」スライダーがエラーになる点を修正
  - use_container_width（新しい Streamlit で廃止予定）を削除
"""

import math

import pandas as pd
import streamlit as st

st.title("ローン返済で学ぶ漸化式")
st.caption("数列の漸化式：a(n+1) = p·a(n) + q 型の応用（月次・総合版）")


# ------------------------------------------------------------
# 共通関数
# ------------------------------------------------------------
def monthly_payment(balance, r, months):
    """元利均等返済の毎月返済額(理想モデル)"""
    if r == 0:
        return balance / months
    q = (1 + r) ** months
    return balance * r * q / (q - 1)


def by_recurrence(A, r, P, N, rounding):
    """漸化式 a_{n+1} = (1+r) a_n - P を a_0 = A から順に計算"""
    a = [A]
    for _ in range(N):
        nxt = (1 + r) * a[-1] - P
        a.append(math.floor(nxt) if rounding else nxt)
    return a


def by_general_term(A, r, P, n):
    """一般項 a_n = (A - P/r)(1+r)^n + P/r"""
    alpha = P / r
    return (A - alpha) * (1 + r) ** n + alpha


def ym(n):
    """月数 → 'x年yか月'"""
    return f"{n // 12}年{n % 12}か月"


def simulate(A, N, r0, cash0, income, living,
             shock_from, shock_len, shock_rate, rate_up_month=None, r_new=None):
    """
    返済+家計のシミュレーション(月次ループ)
      ローン残高:  a_n = (1+r) a_{n-1} - P
      手元資金  :  c_n = c_{n-1} + (収入 - 生活費 - P)
    手元資金が負になった月を「返済不能」とみなす。
    """
    bal, r = A, r0
    P = monthly_payment(bal, r, N)
    cash, paid = cash0, 0.0
    rows, default_month, debt_at_default, paid_at_default = [], None, None, None

    for n in range(1, N + 1):
        if rate_up_month is not None and n == rate_up_month + 1:
            r = r_new
            P = monthly_payment(bal, r, N - n + 1)  # 残高・残期間で再計算
        prev_bal = bal
        bal = (1 + r) * bal - P
        in_shock = shock_from < n <= shock_from + shock_len
        inc = income * (1 - shock_rate) if in_shock else income
        cash += inc - living - P
        paid += P
        rows.append(
            {"n": n, "返済額": P, "収入": inc,
             "貯蓄(万円)": cash / 1e4, "ローン残高(万円)": max(bal, 0) / 1e4}
        )
        if cash < 0:
            default_month, debt_at_default, paid_at_default = n, prev_bal, paid - P
            break

    df = pd.DataFrame(rows).set_index("n")
    return df, default_month, debt_at_default, (paid_at_default if default_month else paid)


# ------------------------------------------------------------
# サイドバー:パラメータ
# ------------------------------------------------------------
with st.sidebar:
    st.header("パラメータ")
    A_man = st.number_input("借入金額 A(万円)", 10, 10000, 1000, step=10)
    annual = st.number_input("年利(%)", 0.1, 20.0, 3.0, step=0.1, format="%.2f")
    years = st.number_input("返済年数", 1, 50, 20)
    use_round = st.checkbox("円未満を切り捨てる(現実のモデル)", value=False)
    st.caption("OFF:理想モデル(教材の基本)/ ON:実務に近いモデル")

A = A_man * 10_000
r = annual / 12 / 100  # 月利
N = 12 * years  # 返済回数(月)
q = (1 + r) ** N
P_ideal = monthly_payment(A, r, N)  # 毎月の返済額(理想)
P = math.ceil(P_ideal) if use_round else P_ideal

a_rec = by_recurrence(A, r, P, N, use_round)
a_gen = [by_general_term(A, r, P, n) for n in range(N + 1)]

# 総支払額(最終回の端数調整を含む):a_N が 0 でなければ最終回で精算する
total_paid = P * N + a_rec[-1]
total_interest = total_paid - A

# ------------------------------------------------------------
# タブ
# ------------------------------------------------------------
t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12 = st.tabs(
    ["① 問題設定", "② 漸化式を解く", "③ 数値で確認", "④ グラフ",
     "⑤ 練習問題", "⑥ 総支払額", "⑦ 返済不能シナリオ", "⑧ 用語集", "⑨ リボ払い", "⑩ 残クレ", "⑪ まとめ", "⑫ 設備投資"]
)

# ---------- ① 問題設定 ----------
with t1:
    st.info("ローンでは一般的に行われる元利均等返済について")
    st.write("まずは ①→③→④→⑥ で「ローンの仕組み」をつかみ、"
             "②⑤⑦ は数列の力試し(発展)として読むのがおすすめです。"
             "⑧は言葉の意味のまとめ、⑨⑩は現代のローンの罠(リボ払い・残クレ)のシミュレーションです。"
             "⑪は全体のまとめ、⑫は借金を「利益を生む設備」に使う場合の例です。")
    st.subheader("問題")
    st.write(
        f"借入金額 **{A:,} 円**、年利 **{annual}%**(月利 r = {r:.6f})で、"
        f"**{N} 回**の毎月均等返済で完済したい。毎月の返済額 P を求めよ。"
    )
    st.markdown("**数列でモデル化する**")
    st.write("n 回目の返済直後の残高を $a_n$ とおく。1か月で利息がつき、P 円返すので、")
    st.latex(r"a_0 = A,\qquad a_{n+1} = (1+r)\,a_n - P")
    st.info("完済する条件は $a_N = 0$。この漸化式を解いて P を求める。")

# ---------- ② 漸化式を解く ----------
with t2:
    st.info("数列の漸化式の解法について")
    st.subheader("解き方(特性方程式の考え方)")

    st.markdown("**Step 1** 漸化式の不動点 α を求める")
    st.latex(r"\alpha = (1+r)\alpha - P \;\Longrightarrow\; \alpha = \frac{P}{r}")

    st.markdown("**Step 2** 漸化式から Step 1 の式を辺々引く")
    st.latex(r"a_{n+1} - \alpha = (1+r)\,(a_n - \alpha)")
    st.write("→ 数列 $\\{a_n - \\alpha\\}$ は **公比 $1+r$ の等比数列**")

    st.markdown("**Step 3** 一般項を求める")
    st.latex(r"a_n - \alpha = (A-\alpha)(1+r)^n")
    st.latex(r"a_n = \left(A - \frac{P}{r}\right)(1+r)^n + \frac{P}{r}")

    st.markdown("**Step 4** $a_N = 0$ から P を求める")
    st.latex(r"\left(A - \frac{P}{r}\right)(1+r)^N + \frac{P}{r} = 0")
    st.latex(r"P = \frac{A\,r\,(1+r)^N}{(1+r)^N - 1}")

    st.markdown("**Step 5** 今回の数値を代入")
    st.write(
        f"A = {A:,},  r = {r:.6f},  N = {N}  より  "
        f"**P ≈ {P_ideal:,.2f} 円**"
    )

# ---------- ③ 数値で確認 ----------
with t3:
    st.info("実際のシミュレート")
    st.subheader("漸化式(ループ計算)と一般項(公式)を比べる")
    max_n = st.slider("表示する項数 n", 1, min(N, 60), min(12, N))
    df = pd.DataFrame(
        {
            "n": range(max_n + 1),
            "漸化式で計算 a_n": a_rec[: max_n + 1],
            "一般項で計算 a_n": a_gen[: max_n + 1],
        }
    )
    df["差"] = df["漸化式で計算 a_n"] - df["一般項で計算 a_n"]
    st.dataframe(
        df,
        column_config={
            "漸化式で計算 a_n": st.column_config.NumberColumn(format="%.2f"),
            "一般項で計算 a_n": st.column_config.NumberColumn(format="%.2f"),
            "差": st.column_config.NumberColumn(format="%.4f"),
        },
        hide_index=True,
    )
    err = max(abs(x - y) for x, y in zip(a_rec, a_gen))
    if use_round:
        st.warning(f"切り捨てを入れたため、最大 {err:,.2f} 円のずれが生じています。なぜでしょう?")
    else:
        st.success(f"全項の最大誤差は {err:.2e} 円(浮動小数点の誤差のみ)。一般項は正しい!")
    st.write(f"**最終項 a_N = {a_rec[-1]:,.2f}**(0に近ければ完済できている)")

    st.subheader("元金部分は等比数列になっている")
    st.write("第 n 回の返済のうち元金にあたる額を $b_n = a_{n-1} - a_n$ とすると、")
    st.latex(r"b_{n+1} = (1+r)\,b_n")
    b = [a_rec[n - 1] - a_rec[n] for n in range(1, min(N, 8) + 1)]
    ratio = [None] + [b[i] / b[i - 1] for i in range(1, len(b))]
    st.dataframe(
        pd.DataFrame({"n": range(1, len(b) + 1), "元金 b_n": b, "b_n / b_(n-1)": ratio}),
        column_config={
            "元金 b_n": st.column_config.NumberColumn(format="%.2f"),
            "b_n / b_(n-1)": st.column_config.NumberColumn(format="%.6f"),
        },
        hide_index=True,
    )
    st.caption(f"公比 1 + r = {1 + r:.6f} に一致します。")

# ---------- ④ グラフ ----------
with t4:
    st.subheader("残高 a_n の推移")
    st.line_chart(pd.DataFrame({"残高": a_rec}))
    st.write("**初めはほとんど減らず、後半に急に減る**(上に凸の)形です。"
             "これは元金部分が等比数列で増えていくためです。")

    st.subheader("毎月の返済の内訳(元金と利息)")
    principal = [a_rec[n - 1] - a_rec[n] for n in range(1, N + 1)]
    interest = [P - p for p in principal]
    st.area_chart(
        pd.DataFrame({"元金": principal, "利息": interest}),
        color=["#1f77b4", "#ff7f0e"],
    )
    st.write("元金は等比数列で**増加**、利息は**減少**します。返済額 P は一定です。")

    st.subheader("考えてみよう")
    st.write("- 金利 r を大きくすると、グラフの形はどう変わるか?")
    st.write("- 返済年数 N を延ばすと、毎月の返済額と総利息はどう変わるか?")

# ---------- ⑤ 練習問題 ----------
with t5:
    st.subheader("練習問題")

    st.markdown("**問1** 次の漸化式で定まる数列の一般項を求めよ。")
    st.latex(r"a_1 = 5,\quad a_{n+1} = 2a_n - 3")
    with st.expander("解答"):
        st.latex(r"\alpha = 2\alpha - 3 \Rightarrow \alpha = 3")
        st.latex(r"a_{n+1} - 3 = 2(a_n - 3),\quad a_1 - 3 = 2")
        st.latex(r"a_n = 2\cdot 2^{n-1} + 3 = 2^n + 3")

    st.markdown("**問2** 現在の設定で、返済開始から 5 年後(60回後)の残高を一般項を用いて求めよ。")
    with st.expander("解答"):
        a60 = by_general_term(A, r, P_ideal, 60) if N >= 60 else 0
        st.latex(r"a_{60} = \left(A - \frac{P}{r}\right)(1+r)^{60} + \frac{P}{r}")
        st.write(f"**a₆₀ ≈ {a60:,.0f} 円**(借入額の {a60 / A:.1%})")

    st.markdown("**問3** 元金部分 $b_n = a_{n-1} - a_n$ が公比 $1+r$ の等比数列であることを示せ。")
    with st.expander("解答"):
        st.latex(r"a_{n+1} = (1+r)a_n - P,\quad a_n = (1+r)a_{n-1} - P")
        st.write("辺々引くと、")
        st.latex(r"a_{n+1} - a_n = (1+r)(a_n - a_{n-1})")
        st.write("両辺に -1 をかけると $b_{n+1} = (1+r)\\,b_n$。よって公比 $1+r$ の等比数列。")

    st.markdown("**問4(発展)** 元金均等返済(毎月の元金が一定)では、毎月の返済額はどんな数列になるか。")
    with st.expander("解答"):
        st.write("毎月の元金は一定(A/N)なので、残高は等差数列で減る。利息は残高に比例して減るので、")
        st.write("**毎月の返済額 $p_n$ は等差数列(公差 $-A r / N$)** になる。")
        st.latex(r"p_n = \frac{A}{N} + \frac{A r (N-n+1)}{N} = p_1 - (n-1)\frac{A r}{N},\qquad p_1 = \frac{A}{N}(1 + rN)")
        st.write("総利息は、この等差数列の和(初項と末項の平均 × 項数)から A を引いて求められる。")

# ---------- ⑥ 総支払額 ----------
with t6:
    st.subheader("最終的な支払総額")

    c1, c2 = st.columns(2)
    c1.metric("毎月の返済額 P", f"{P:,.0f} 円")
    c2.metric("返済回数 N", f"{N} 回")
    c3, c4 = st.columns(2)
    c3.metric("総支払額", f"{total_paid:,.0f} 円")
    c4.metric("総利息", f"{total_interest:,.0f} 円", f"借入額の {total_interest / A:.1%}",
              delta_color="off")

    st.markdown("**公式で求める**")
    st.latex(r"T = N P = \frac{N A\, r\,(1+r)^N}{(1+r)^N - 1},\qquad \text{総利息} = T - A")

    st.markdown("**確認:元金部分の総和は借入額 A に等しい**")
    st.write("元金部分 $b_n$ は初項 $b_1 = P - rA$、公比 $1+r$ の等比数列。その和は、")
    st.latex(r"\sum_{n=1}^{N} b_n = \frac{b_1\{(1+r)^N - 1\}}{r} = A")
    b1 = P_ideal - r * A
    st.write(f"$b_1$ = {b1:,.2f} 円 → 等比数列の和 = **{b1 * (q - 1) / r:,.2f} 円**(= A = {A:,} 円)")

    st.divider()
    st.subheader("年数と金利で総支払額はどう変わる?(万円)")
    year_list = [10, 15, 20, 25, 30, 35]
    rate_list = [1.0, 2.0, 3.0, 4.0, 5.0]
    table = {
        f"年利 {rt:g}%": [
            round(monthly_payment(A, rt / 1200, 12 * y) * 12 * y / 1e4) for y in year_list
        ]
        for rt in rate_list
    }
    st.dataframe(pd.DataFrame(table, index=[f"{y}年" for y in year_list]))

    st.subheader(f"返済年数と総利息(年利 {annual}%)")
    ys = list(range(5, 41))
    st.line_chart(
        pd.DataFrame(
            {"総利息(万円)": [(monthly_payment(A, r, 12 * y) * 12 * y - A) / 1e4 for y in ys]},
            index=ys,
        )
    )
    st.caption("毎月の返済は楽になっても、期間を延ばすと総利息は増えます。")

# ---------- ⑦ 返済不能シナリオ ----------
with t7:
    st.subheader("返済不能(破綻)シナリオのシミュレーション")
    st.write(
        "収入が減ったり金利が上がったりしたとき、手元資金が尽きて返済できなくなるのはいつか。"
        "**手元資金も漸化式**でモデル化できます。"
    )
    st.latex(r"c_{n+1} = c_n + (I - E - P) \quad (c_n:\ n\text{か月後の手元資金},\ I:\text{収入},\ E:\text{生活費})")
    st.caption("※ 学習用の簡易モデルです。法律上の「破産手続き」ではなく、"
               "手元資金が 0 を下回った時点を「返済不能」と定義しています。")

    st.markdown("**家計の条件**")
    h1, h2, h3 = st.columns(3)
    cash0_man = h1.number_input("初期の手元資金(万円)", 0, 10000, 200, step=10)
    income_man = h2.number_input("月収・手取り(万円)", 1.0, 200.0, 30.0, step=1.0)
    living_man = h3.number_input("毎月の生活費(万円)", 0.0, 200.0, 20.0, step=1.0)

    st.markdown("**シナリオ1:収入ショック**(失業・減収など)")
    s1, s2, s3 = st.columns(3)
    shock_rate = s1.slider("収入の減少率(%)", 0, 100, 50) / 100
    max_year = max(int(years) - 1, 1)
    shock_year = s2.slider("開始(返済開始から何年後)", 0, max_year, min(5, max_year))
    shock_len = s3.slider("続く期間(か月)", 1, 120, 60)

    st.markdown("**シナリオ2:金利上昇**(変動金利を想定)")
    use_rate_up = st.checkbox("途中で金利が上がる", value=False, disabled=int(years) < 2,
                              help="返済年数が2年以上のときに使えます。")
    rate_up_month, r_new = None, None
    if use_rate_up:
        u1, u2 = st.columns(2)
        if max_year > 1:
            up_year = u1.slider("上昇する時期(何年後)", 1, max_year, min(10, max_year))
        else:
            up_year = 1
            u1.write("上昇する時期:**1年後**")
        new_annual = u2.number_input("上昇後の年利(%)", 0.1, 30.0, float(annual) + 2.0, step=0.1)
        rate_up_month, r_new = 12 * up_year, new_annual / 1200

    cash0, income, living = cash0_man * 1e4, income_man * 1e4, living_man * 1e4
    sim, default_n, debt, paid_sum = simulate(
        A, N, r, cash0, income, living,
        12 * shock_year, shock_len, shock_rate, rate_up_month, r_new,
    )

    st.divider()
    st.subheader("結果")
    if default_n:
        st.error(f"**{default_n} 回目の返済({ym(default_n)})で手元資金が尽き、返済不能になりました。**")
        m1, m2 = st.columns(2)
        m1.metric("返済不能時のローン残高", f"{debt:,.0f} 円")
        m2.metric("それまでに払った総額", f"{paid_sum:,.0f} 円")
        st.write(f"元の借入額 {A:,} 円のうち、**{debt / A:.1%}** が未返済のまま残ります。")
    else:
        st.success("**最後まで返済できました(完済)。**")
        m1, m2 = st.columns(2)
        m1.metric("総支払額", f"{paid_sum:,.0f} 円")
        m2.metric("完済時の手元資金", f"{sim['貯蓄(万円)'].iloc[-1] * 1e4:,.0f} 円")

    st.line_chart(sim[["貯蓄(万円)", "ローン残高(万円)"]])
    st.caption("貯蓄が 0 を下回った月でシミュレーションを止めています。")

    # ---- 数列としての分析(金利上昇なしの場合のみ厳密に成り立つ) ----
    st.divider()
    st.subheader("等差数列として解く")
    d0 = income - living - P_ideal  # 通常時の毎月の収支
    d_s = income * (1 - shock_rate) - living - P_ideal  # ショック中の毎月の収支
    k = 12 * shock_year
    st.write(f"通常時の毎月の収支 $d_0$ = {d0 / 1e4:,.2f} 万円、"
             f"ショック中の毎月の収支 $d_s$ = {d_s / 1e4:,.2f} 万円")
    st.write(f"**返済負担率** P / 収入 = {P_ideal / income:.1%}"
             f"(一般に 25% 以下が安全、35% を超えると厳しいといわれます)")
    st.latex(r"c_n = c_0 + n\,d\quad(\text{公差 } d \text{ の等差数列})")

    if use_rate_up:
        st.info("金利上昇を入れると返済額 P が途中で変わるため、単純な等差数列では表せません。"
                "区間ごとに分けて考える必要があります(発展課題)。")
    elif d0 < 0:
        st.warning("通常時から収支が赤字です。最初から手元資金が減り続けます。")
        if cash0 > 0:
            st.write(f"理論上、**{math.floor(cash0 / -d0) + 1} 回目**で資金が尽きます。")
    else:
        c_k = cash0 + k * d0  # ショック開始時の手元資金
        st.write(f"ショック開始時({shock_year}年後)の手元資金: "
                 f"$c_k = c_0 + k d_0$ = {c_k / 1e4:,.1f} 万円")
        if d_s >= 0:
            st.write("ショック中も収支は黒字なので、返済不能にはなりません。")
        else:
            j = math.floor(c_k / -d_s) + 1  # ショック開始後 j か月目に資金が負
            st.latex(r"c_k + j\,d_s < 0 \;\Longleftrightarrow\; j > \frac{c_k}{-d_s}")
            if j <= shock_len:
                st.write(f"ショック開始から **{j} か月目**、返済開始から **{k + j} 回目**に資金が尽きる"
                         f"(シミュレーション結果: {default_n} 回目)。")
            else:
                st.write(f"資金が尽きるまで {j} か月かかりますが、ショックは {shock_len} か月で終わるので、"
                         "**耐えきれます**。")
        # 限界の収入減少率
        x_max = 1 - (living + P_ideal) / income
        st.write(f"黒字を保てる収入減少率の限界: **{max(x_max, 0):.1%}**"
                 "(これを超える減収が続くと、貯蓄を取り崩すことになる)")

    with st.expander("練習問題(発展)"):
        st.markdown("**問5** 手元資金 $c_0$ = 300万円、毎月の収支が $d$ = -8万円のとき、"
                    "手元資金が初めて負になるのは何か月後か。")
        st.latex(r"c_n = 300 - 8n < 0 \;\Rightarrow\; n > 37.5")
        st.write("答え:**38か月後**")
        st.markdown("**問6** 金利が上がると、返済不能になりやすくなるのはなぜか。"
                    "残高の漸化式 $a_{n+1} = (1+r)a_n - P$ の観点から説明せよ。")
        st.write("ヒント:$r$ が大きいと、同じ P でも元金に回る額 $b_n = P - r a_{n-1}$ が小さくなる。"
                 "完済に必要な P も大きくなる。")

# ---------- ⑧ 用語集 ----------
with t8:
    st.subheader("用語集(わからなくなったらここへ)")

    st.markdown("**記号の一覧(いまの設定の値つき)**")
    st.dataframe(
        pd.DataFrame(
            {
                "記号": ["A", "年利", "r", "N", "P", "a_n", "b_n", "c_n", "I", "E"],
                "意味": [
                    "借りたお金", "1年あたりの利息の割合", "1か月あたりの利息の割合(月利)",
                    "返済する回数(月)", "毎月の返済額", "n回返したあとの借金の残り(残高)",
                    "n回目の返済のうち借金を減らす部分(元金)", "n か月後の手元のお金(⑦)",
                    "毎月の収入(手取り)", "毎月の生活費",
                ],
                "いまの値": [
                    f"{A:,} 円", f"{annual}%", f"{r:.6f}(= 年利 ÷ 12 ÷ 100)", f"{N} 回",
                    f"{P:,.0f} 円", "③で表示", "③で表示", "⑦で表示",
                    f"{income_man:g} 万円", f"{living_man:g} 万円",
                ],
            }
        ),
        hide_index=True,
    )

    with st.expander("💴 お金のことば"):
        st.markdown(
            """
- **ローン**:お金を借りて、少しずつ返す約束。
- **元利均等返済(がんりきんとうへんさい)**:毎月の返済額が**ずっと同じ**になる返し方。
  「元」=元金、「利」=利息、「均等」=毎月同じ、という意味。
- **元金(がんきん)**:借りたお金そのもの。この部分を返すと、借金が減る。
- **利息**:お金を借りた「レンタル料」。**まだ返していない額(残高)に比例**して決まる。
- **年利・月利**:1年あたり/1か月あたりの利息の割合。**月利 = 年利 ÷ 12**。
  例:年利3% → 月利0.25% → 小数で 0.0025。
- **残高(ざんだか)**:まだ返していない借金の額。
- **完済**:残高がちょうど 0 になること。
- **総支払額**:完済までに払うお金の合計(= 毎月の返済額 × 回数)。
- **総利息**:総支払額 − 借りた額。「借りたことのコスト」。
- **返済負担率**:収入のうち、返済に使う割合(= 返済額 ÷ 収入)。高いほど生活が苦しくなる。
- **変動金利**:途中で金利が変わる契約。金利が上がると返済額も増える。
- **増益率 g**:設備を使ううちに、利益が毎年どれだけ増えるか。
- **達成率 x**:計画に対して、実際に何%の利益が出たか。
- **返済余裕率**:毎月の追加利益 ÷ 毎月の返済額。1倍を下回ると、毎月の収支が赤字になる。
"""
        )

    with st.expander("📈 数列のことば"):
        st.markdown(
            """
- **数列**:数を順番に並べたもの。a₀, a₁, a₂, … の一つひとつを**項**という。
- **初項**:最初の項。ここでは a₀ = A(借りた直後の残高)。
- **漸化式(ぜんかしき)**:「次の項を、前の項を使って表す式」。
  ローンなら「**来月の残高 = 今月の残高に利息を足して、返済額を引いたもの**」。
  例:A=100万、月利1%、返済20万なら a₁ = 100×1.01 − 20 = 81、a₂ = 81×1.01 − 20 = 61.81。
- **一般項**:「n番目の項を、いきなり求める式」。漸化式だと 1つずつ順に計算が必要だが、
  一般項があれば 60番目でも一発で出せる。
- **等比数列・公比**:同じ数を**かけて**進む数列。かける数が公比(ここでは 1 + r)。
- **等差数列・公差**:同じ数を**足して**進む数列。足す数が公差。
- **不動点(特性方程式)**:漸化式の a_{n+1} と a_n を同じ文字 α に置いた方程式の解。
  これを引くと、a_n − α が等比数列に変身して解けるようになる(②の Step 1〜2)。
- **等比数列の和**:初項 a、公比 q、項数 N の和は a(qᴺ − 1)/(q − 1)。⑥で使う。
"""
        )

    with st.expander("⚠️ シナリオ(⑦)のことば"):
        st.markdown(
            """
- **手元資金**:自由に使える貯金。毎月「収入 − 生活費 − 返済額」だけ増減する(**等差数列**)。
- **収入ショック**:失業や減給などで、収入が急に減ること。
- **返済不能**:手元資金が 0 を下回り、返済できなくなること(このアプリでの定義)。
  ※ 法律上の「破産」とは別ものです。
- **毎月の収支 d**:収入 − 生活費 − 返済額。プラスなら貯金が増え、マイナスなら減る。
- **持ちこたえる期間**:手元資金 ÷ 毎月の赤字。ここが短いほど危険。
"""
        )
    with st.expander("🔁🚗 リボ払い・残クレのことば"):
        st.markdown(
            """
- **リボ払い(定額方式)**:毎月の返済額を一定額に決める支払い方。
- **実質年率**:手数料も含めた、1年あたりの金利。
- **残価(ざんか)**:契約終了時の車の予想価格。契約時に決め、その分の支払いを据え置く。
- **残価率**:残価 ÷ 車両価格。
- **差額精算**:実際の価値が残価を下回ったとき、その差を支払うこと。
- **据え置き**:残価ぶんを返さずに残しておくこと。**据え置いた部分にも利息がかかる**。
- **対数 log**:「何乗すればその数になるか」を表す。⑨で完済までの回数 N を求めるのに使う。
"""
        )


def revolving(B, r, P, U=0.0):
    """
    リボ払い(定額方式)の月次シミュレーション
      今月の請求額 = (1+r) × 残高 + 新規利用 U
      支払額       = min(P, 請求額)    ← 最終回は端数調整
      来月の残高   = 請求額 - 支払額
    これは漸化式  a_{n+1} = (1+r) a_n - (P - U)  と同じ。
    """
    repayable = (P - U) > r * B  # 利息より多く元金を減らせるか
    max_months = 1200 if repayable else 120  # 返せない場合は120か月だけ見る
    bal, paid, added = B, 0.0, 0.0
    rows = [{"n": 0, "残高(万円)": B / 1e4}]
    finish = None
    for n in range(1, max_months + 1):
        charge = (1 + r) * bal + U
        added += U
        pay = min(P, charge)
        paid += pay
        bal = charge - pay
        rows.append({"n": n, "残高(万円)": bal / 1e4})
        if bal <= 1e-9:
            finish = n
            break
    return {
        "df": pd.DataFrame(rows).set_index("n"),
        "n": finish,
        "paid": paid,
        "interest": paid - B - added,
        "repayable": repayable,
    }


# ---------- ⑨ リボ払い ----------
with t9:
    st.subheader("リボ払い(定額方式)のシミュレーション")
    st.info(
        "リボ払い=毎月の返済額を**一定額に固定**する支払い方。"
        "毎月の負担は軽くなりますが、金利が高いため、完済まで長くかかり利息が膨らみやすい仕組みです。"
    )
    st.write("リボ払いの罠: 元金が減らず、借金が永遠に終わらないこと")
    st.markdown("**条件を入力**")
    v1, v2, v3 = st.columns(3)
    rv_B = v1.number_input("リボ残高 B(万円)", 1, 500, 30, step=5, key="rv_B") * 10_000
    rv_rate = v2.number_input("実質年率(%)", 0.1, 20.0, 15.0, step=0.5, key="rv_rate")
    rv_P = v3.number_input("毎月の返済額 P(円)", 1000, 200000, 10000, step=1000, key="rv_P")
    rv_U = st.slider("毎月の新しい利用額 U(円)", 0, 20000, 0, step=500, key="rv_U")
    st.caption("U > 0 は「返済しながら、毎月また使ってしまう」ケースです。")

    r_rv = rv_rate / 12 / 100
    P_eff = rv_P - rv_U  # 実質の返済額
    rB = r_rv * rv_B  # 利息だけでかかる月額

    res = revolving(rv_B, r_rv, rv_P, rv_U)

    # ---------- 結果 ----------
    st.divider()
    st.subheader("結果")
    st.write(f"月利 r = {r_rv:.4f}。最初の1か月の利息は rB = **{rB:,.0f} 円**。")

    if not res["repayable"]:
        st.error(
            f"**このままでは完済できません。** 実質の返済額 P − U = {P_eff:,.0f} 円 が、"
            f"利息 rB = {rB:,.0f} 円 以下だからです。元金が減らず、残高は**増え続けます**。"
        )
        st.write("下のグラフは 120 か月(10年)分です。⑦の「返済不能」と同じ状況になります。")
    elif res["n"] is None:
        st.warning("完済まで 100 年以上かかります。実質上、終わりません。")
    else:
        m1, m2 = st.columns(2)
        m1.metric("完済までの期間", ym(res["n"]), f"{res['n']} 回", delta_color="off")
        m2.metric("総支払額", f"{res['paid']:,.0f} 円")
        m3, m4 = st.columns(2)
        m3.metric("総利息", f"{res['interest']:,.0f} 円")
        m4.metric("利息 ÷ 最初の残高", f"{res['interest'] / rv_B:.1%}")

    # ---------- グラフ:低金利との比較 ----------
    st.markdown("**残高の推移:同じ返済額で、年3%だったら?**")
    low = revolving(rv_B, 0.03 / 12, rv_P, rv_U)
    chart_df = pd.concat(
        [
            res["df"]["残高(万円)"].rename(f"リボ(年{rv_rate:g}%)"),
            low["df"]["残高(万円)"].rename("低金利(年3%)"),
        ],
        axis=1,
    )
    st.line_chart(chart_df)
    if res["n"] and low["n"]:
        st.write(
            f"同じ {rv_P:,} 円ずつ返しても、年3% なら総利息は **{low['interest']:,.0f} 円**、"
            f"年{rv_rate:g}% だと **{res['interest']:,.0f} 円**。"
            "金利の差が、利息の差になります。"
        )

    # ---------- 数学:漸化式から N を求める ----------
    st.divider()
    st.subheader("数列で考える")
    st.write("返済額 P が決まっているので、**残高 $a_n$ の漸化式はローンと同じ形**です。")
    st.latex(r"a_0 = B,\qquad a_{n+1} = (1+r)\,a_n - P")
    st.latex(r"a_n = \left(B - \frac{P}{r}\right)(1+r)^n + \frac{P}{r}")
    st.write("完済する $a_N = 0$ を、今度は **N について解く**。")
    st.latex(r"(1+r)^N = \frac{P}{P - rB}\quad\Longrightarrow\quad N = \frac{\log\dfrac{P}{P - rB}}{\log(1+r)}")
    st.write("ここで**真数が正**でなければならないので、$P - rB > 0$ が必要です。")
    st.latex(r"b_1 = P - rB > 0 \quad(\text{最初の月に元金が減る})")
    st.caption("利息 rB より少ない額しか返さないと、元金は1円も減らず、借金は増える一方になります。")

    if res["repayable"]:
        N_real = math.log(P_eff / (P_eff - rB)) / math.log(1 + r_rv)
        st.write(
            f"今の設定:P{' − U' if rv_U else ''} = {P_eff:,.0f} 円、rB = {rB:,.0f} 円 より、"
            f"N = log({P_eff:,.0f} / {P_eff - rB:,.0f}) ÷ log(1 + {r_rv:.4f}) = **{N_real:.2f}**"
            f" → 切り上げて **{math.ceil(N_real)} 回**"
            + (f"(シミュレーション結果: {res['n']} 回)" if res["n"] else "")
        )

    if rv_U > 0:
        st.markdown("**毎月の新規利用 U の影響**")
        st.write("返済しながら毎月 U 円ずつ使うと、漸化式は")
        st.latex(r"a_{n+1} = (1+r)\,a_n - (P - U)")
        st.write(f"となり、**返済額が U 円ぶん減ったのと同じ**効果になります(実質の返済額 = {P_eff:,.0f} 円)。")

    # ---------- 表:返済額による違い ----------
    st.divider()
    st.subheader("毎月の返済額を変えると?")
    table_rows = []
    for p in [5000, 10000, 15000, 20000, 30000]:
        x = revolving(rv_B, r_rv, p, rv_U)
        if not x["repayable"]:
            table_rows.append({"毎月の返済額": f"{p:,} 円", "完済までの期間": "終わらない",
                               "総支払額": "-", "総利息": "-"})
        elif x["n"] is None:
            table_rows.append({"毎月の返済額": f"{p:,} 円", "完済までの期間": "100年以上",
                               "総支払額": "-", "総利息": "-"})
        else:
            table_rows.append({"毎月の返済額": f"{p:,} 円", "完済までの期間": ym(x["n"]),
                               "総支払額": f"{x['paid']:,.0f} 円", "総利息": f"{x['interest']:,.0f} 円"})
    st.dataframe(pd.DataFrame(table_rows), hide_index=True)
    st.caption("返済額がほんの少し増えるだけで、期間と利息が大きく変わります。逆に、減らすと一気に長期化します。")

    # ---------- ローンとの違い ----------
    st.divider()
    st.subheader("ローンとの違いまとめ")
    st.markdown(
        """
| | 住宅ローン(元利均等) | リボ払い(定額方式) |
|---|---|---|
| 漸化式 | $a_{n+1}=(1+r)a_n-P$ | **同じ** |
| 先に決める | 回数 $N$ | 毎月の返済額 $P$ |
| 求める | $P$ | $N$(対数を使う) |
| 金利の目安 | 年1〜3% | 年15%前後 |
| 危険な点 | 収入が減ると返せない | **$P \\le rB$ だと永遠に終わらない**。追加利用で実質の $P$ が減る |
"""
    )
    st.caption("※ このタブは「定額方式」のみ。カード会社には、残高に応じて返済額が変わる方式などもあります。")

    # ---------- 練習問題 ----------
    with st.expander("練習問題"):
        st.markdown("**問7** リボ残高 30万円、年利15%(月利 1.25%)、毎月の返済額 1万円。完済まで何回かかるか。"
                    "ただし自然対数で $\\log 1.6 \\approx 0.470,\\ \\log 1.0125 \\approx 0.01242$ とする。")
        st.write("$rB$ = 0.0125 × 300,000 = 3,750 円 なので、")
        st.latex(r"N = \frac{\log\frac{10000}{10000 - 3750}}{\log 1.0125} = \frac{\log 1.6}{\log 1.0125} \approx \frac{0.470}{0.01242} \approx 37.8")
        st.write("答え:**38回(3年2か月)**")
        st.caption("常用対数 $\\log_{10} 1.6 \\approx 0.2041,\\ \\log_{10} 1.0125 \\approx 0.005395$ を使っても、比は同じ 37.8 になります。")

        st.markdown("**問8** 問7で、毎月 4,000 円ずつ新しく使い続けると、完済までに何回かかるか。"
                    "(自然対数で $\\log 2.667 \\approx 0.981$)")
        st.write("実質の返済額は 10,000 − 4,000 = 6,000 円。")
        st.latex(r"N = \frac{\log\frac{6000}{6000 - 3750}}{\log 1.0125} = \frac{\log 2.667}{\log 1.0125} \approx \frac{0.981}{0.01242} \approx 79")
        st.write("答え:**約79回(6年7か月)**。毎月4,000円の追加利用で、期間は2倍以上に延びる。")

        st.markdown("**問9** 問7の条件で、毎月の返済額を 3,750 円にするとどうなるか。")
        st.write("$P = rB$ なので、毎月の利息 3,750 円をちょうど払うだけ。元金は**1円も減らず**、残高は 30万円のまま。"
                 "$P < rB$ なら残高は増えていく(真数が負になり、N は存在しない)。")


# ---------- ⑩ 残クレ ----------
with t10:
    st.subheader("残価設定型クレジット(残クレ)のシミュレーション")
    st.info(
        "残クレ=車の**数年後の予想価格(残価)をあらかじめ決めて**、"
        "その分を据え置いた残りを分割で払う方法。月々の支払いが安くなる一方、"
        "契約終了時に「返す・買い取る・乗り換える」を選びます。"
    )
    st.write("残クレの罠: 残価にも利息を払い続けるうえ、実際の価値が残価を下回ると、車を返しても差額の支払いが残ること")
    # ---------- 入力 ----------
    st.markdown("**条件を入力**")
    k1, k2, k3 = st.columns(3)
    rc_V = k1.number_input("車両価格 V(万円)", 50, 2000, 400, step=10, key="rc_V") * 10_000
    rc_years = k2.selectbox("契約年数", [3, 4, 5], index=0, key="rc_years")
    rc_rate = k3.number_input("実質年率(%)", 0.1, 15.0, 5.0, step=0.1, key="rc_rate")
    k4, k5 = st.columns(2)
    rc_resid = k4.slider("残価率(%)", 0, 70, 50, key="rc_resid") / 100
    rc_dep = k5.slider("実際の車の年間値下がり率(%)", 0, 40, 25, key="rc_dep") / 100
    st.caption("残価率=契約時に決める「N年後の予想価格 ÷ 車両価格」。"
               "値下がり率は「実際には毎年何%ずつ価値が下がるか」(等比数列で下がると仮定)。")

    rc_N = 12 * rc_years
    rc_r = rc_rate / 12 / 100
    rc_q = (1 + rc_r) ** rc_N
    rc_S = rc_V * rc_resid  # 設定した残価
    rc_M = rc_V * (1 - rc_dep) ** rc_years  # 実際のN年後の車の価値

    P_balloon = rc_r * (rc_V * rc_q - rc_S) / (rc_q - 1)  # 残クレの月々
    P_normal = monthly_payment(rc_V, rc_r, rc_N)  # 通常ローン(残価なし)の月々

    # ---------- 月々の支払い ----------
    st.divider()
    st.subheader("月々の支払い")
    m1, m2, m3 = st.columns(3)
    m1.metric("残クレの月々", f"{P_balloon:,.0f} 円")
    m2.metric("通常ローンの月々", f"{P_normal:,.0f} 円")
    m3.metric("月々の差", f"{P_normal - P_balloon:,.0f} 円", "残クレのほうが安い", delta_color="off")
    st.write(f"契約終了時の**残価 S = {rc_S:,.0f} 円**(車両価格の {rc_resid:.0%})は、まだ払っていません。")

    # ---------- 数列で考える ----------
    st.markdown("**数列で考える**")
    st.write("残高 $a_n$ の漸化式は通常ローンと同じ。違うのは**終わりの条件が $a_N = S$** なところ。")
    st.latex(r"a_0 = V,\qquad a_{n+1} = (1+r)\,a_n - P,\qquad a_N = S")
    st.latex(r"a_n = \left(V - \frac{P}{r}\right)(1+r)^n + \frac{P}{r}")
    st.write("$a_N = S$ を P について解く。ただし $q = (1+r)^N$ とおく。")
    st.latex(r"\left(V - \frac{P}{r}\right)q + \frac{P}{r} = S \;\Longrightarrow\; P = \frac{r\,(Vq - S)}{q - 1}")
    st.write("別の見方:$P = \\dfrac{r\\,q}{q-1}\\left(V - \\dfrac{S}{q}\\right)$ は、通常ローンの公式で "
             "**「$V - S/q$ だけ借りた」** と考えた式です($S/q$ は残価の現在価値)。")

    a_N_check = (rc_V - P_balloon / rc_r) * rc_q + P_balloon / rc_r
    st.write(f"確認:一般項で $a_N$ = **{a_N_check:,.0f} 円**(残価 S = {rc_S:,.0f} 円 と一致)")

    # ---------- グラフ ----------
    st.divider()
    st.subheader("ローン残高と車の価値の推移")
    ns = list(range(rc_N + 1))
    bal_b = [(rc_V - P_balloon / rc_r) * (1 + rc_r) ** n + P_balloon / rc_r for n in ns]
    bal_n = [(rc_V - P_normal / rc_r) * (1 + rc_r) ** n + P_normal / rc_r for n in ns]
    car_v = [rc_V * (1 - rc_dep) ** (n / 12) for n in ns]
    st.line_chart(
        pd.DataFrame(
            {
                "残クレのローン残高(万円)": [x / 1e4 for x in bal_b],
                "通常ローンの残高(万円)": [max(x, 0) / 1e4 for x in bal_n],
                "車の実際の価値(万円)": [x / 1e4 for x in car_v],
            },
            index=ns,
        )
    )
    st.caption("車の価値は等比数列 $v_n = V(1-d)^n$ のように下がります。"
               "グラフで、ローン残高が車の価値を上回っている期間に注目しましょう。")

    # ---------- 契約終了時 ----------
    st.divider()
    st.subheader("契約終了時、いくらかかる?")
    st.write(f"{rc_years}年後の車の実際の価値 M = V(1−d)^{rc_years} = **{rc_M:,.0f} 円**"
             f"(設定した残価 S = {rc_S:,.0f} 円)")
    gap = max(rc_S - rc_M, 0)
    if gap > 0:
        st.warning(f"実際の価値が残価を **{gap:,.0f} 円** 下回っています。"
                   "返却時にこの差額を精算(自己負担)になる契約が一般的です。")
    else:
        st.success("実際の価値が残価以上なので、返却時の差額精算は発生しません。")

    pay_total = P_balloon * rc_N
    plans = [
        ("① 残クレ → 返却", pay_total + gap, "車は手元に残らない"),
        ("② 残クレ → 買取", pay_total + rc_S - rc_M, "残価 S を支払い、価値 M の車が手元に残る"),
        ("③ 通常ローン(車は自分のもの)", P_normal * rc_N - rc_M, "価値 M の車が手元に残る"),
    ]
    st.dataframe(
        pd.DataFrame(
            {
                "プラン": [p[0] for p in plans],
                "実質の負担額": [f"{p[1]:,.0f} 円" for p in plans],
                "備考": [p[2] for p in plans],
            }
        ),
        hide_index=True,
    )
    st.caption("実質の負担額 = 支払った総額 − 手元に残る車の価値。")

    int_b = pay_total + rc_S - rc_V
    int_n = P_normal * rc_N - rc_V
    st.write(
        f"利息の総額で比べると、残クレ **{int_b:,.0f} 円** / 通常ローン **{int_n:,.0f} 円**。"
        f"差の **{int_b - int_n:,.0f} 円** は、**残価 S にも毎月利息がかかり続けるため**です。"
    )

    # ---------- まとめ ----------
    st.divider()
    st.subheader("通常ローンとの違いまとめ")
    st.markdown(
        """
| | 通常ローン | 残クレ |
|---|---|---|
| 漸化式 | $a_{n+1}=(1+r)a_n-P$ | **同じ** |
| 終わりの条件 | $a_N = 0$ | $a_N = S$(残価) |
| 月々の返済 | 高い | **安い** |
| 利息がかかる元金 | $V$ のみ(0に向かって減る) | $V$ から始まり、$S$ までしか減らない(**$S$ には最後までかかる**) |
| 契約終了時 | 完済・車は自分のもの | 返却/買取/乗り換えを選ぶ |
| 注意点 | — | 実際の価値が残価を下回ると差額が出る。走行距離・傷の条件がつくことも |
"""
    )
    st.caption("※ 学習用の簡易モデルです。頭金、ボーナス払い、手数料、返却時の査定条件などは含めていません。"
               "実際の契約内容は、各社の契約書で確認してください。")

    # ---------- 練習問題 ----------
    with st.expander("練習問題"):
        st.markdown("**問10** 車両価格300万円、3年契約、残価150万円、金利0%のとき、月々の支払いはいくらか。")
        st.write("利息がないので、払うのは $V - S$ = 150万円 を36回で割った額。")
        st.latex(r"P = \frac{V - S}{N} = \frac{1{,}500{,}000}{36} \approx 41{,}667\text{ 円}")
        st.write("この場合、残高は**等差数列**(公差 $-P$)です。金利があると等比数列が絡み、公式が複雑になります。")

        st.markdown("**問11（残価精算の罠）** 車の価値が毎年20%ずつ下がるとする。3年後の価値は、元の価格の何%か。"
                    "残価率が40%なら、差額は出るか。")
        st.latex(r"v_3 = V\times 0.8^3 = 0.512\,V")
        st.write("答え:**51.2%**。残価率40%を上回るので、差額は出ません(追加の支払いがありません)。"
                 "もし年25%下がるなら $0.75^3 \\approx 0.422$ で 42.2%(40%をわずかに上回る)、"
                 "年30%なら $0.7^3 = 0.343$ で 34.3% となり、残価を下回って差額が出ます(契約者が現金で追加払いして補填する必要があります※車に傷をつけたり、制限走行距離をオーバーするときに数十万の差額を請求されることがあります)。")

        st.markdown("**問12 (総利息の罠)** 残クレの月々は安いのに、総利息が通常ローンより増えるのはなぜか。")
        st.write("通常ローンは元金が毎月減るので、利息も減っていく。残クレは**残価 S がずっと据え置き**なので、"
                 "S に対する利息(おおよそ $rS$ × 月数)が最後まで毎月かかり続ける。")

# ---------- ⑪ まとめ ----------
with t11:
    st.info("ここまでの3つの返し方を、1枚にまとめて振り返ります。")

    # ---------- 1. すべて同じ漸化式 ----------
    st.subheader("① 3つとも、同じ漸化式")
    st.latex(
        r"a_{n+1} = (1+r)\,a_n - P"
        r"\Longrightarrow "
        r"a_n = \left(a_0 - \frac{P}{r}\right)(1+r)^n + \frac{P}{r}"
    )
    st.write("**1か月ごとに残高が $(1+r)$ 倍になり、そこから P 円ずつ返す**。これは3つに共通です。"
             "違うのは、**何を決めて、何を求めるか**だけです。")

    st.markdown(
        r"""
| | 通常ローン(元利均等) | リボ払い(定額方式) | 残クレ |
|---|---|---|---|
| 最初の残高 $a_0$ | 借入額 $A$ | 利用額 $B$ | 車両価格 $V$ |
| 先に決めるもの | 回数 $N$ | 毎月の返済額 $P$ | 回数 $N$ と残価 $S$ |
| 終わりの条件 | $a_N = 0$ | $a_N = 0$ | $a_N = S$ |
| 求めるもの | $P$ | $N$ | $P$ |
| 結果の式 | $P=\dfrac{A\,r\,q}{q-1}$ | $N=\dfrac{\log\frac{P}{P-rB}}{\log(1+r)}$ | $P=\dfrac{r\,(Vq-S)}{q-1}$ |
| 金利の目安 | 年1〜3% | 年15%前後 | 契約による |
| 主に使う数学 | 等比数列 | 対数 | 等比数列 |
| 気をつける点 | 収入が減ると返せない | $P \le rB$ だと終わらない | $S$ にも利息がかかる。差額精算 |
"""
    )
    st.caption("$q = (1+r)^N$。リボ払いでは $P$ を固定するので、$N$ のほうが答えになります。")

    # ---------- 2. いまの設定での比較 ----------
    st.divider()
    st.subheader("② いまの設定で比べる")

    rows = [
        {
            "種類": "通常ローン(サイドバーの設定)",
            "借りた額": f"{A:,} 円",
            "毎月の支払い": f"{P:,.0f} 円",
            "総利息": f"{total_interest:,.0f} 円",
            "利息 ÷ 借りた額": f"{total_interest / A:.1%}",
        }
    ]
    if res["repayable"] and res["n"]:
        rows.append(
            {
                "種類": f"リボ払い(⑨の設定、完済まで{ym(res['n'])})",
                "借りた額": f"{rv_B:,} 円",
                "毎月の支払い": f"{rv_P:,} 円",
                "総利息": f"{res['interest']:,.0f} 円",
                "利息 ÷ 借りた額": f"{res['interest'] / rv_B:.1%}",
            }
        )
    else:
        rows.append(
            {
                "種類": "リボ払い(⑨の設定)",
                "借りた額": f"{rv_B:,} 円",
                "毎月の支払い": f"{rv_P:,} 円",
                "総利息": "完済できない/非常に長い",
                "利息 ÷ 借りた額": "-",
            }
        )
    rows.append(
        {
            "種類": "残クレ(⑩の設定、残価を払う場合)",
            "借りた額": f"{rc_V:,} 円",
            "毎月の支払い": f"{P_balloon:,.0f} 円",
            "総利息": f"{int_b:,.0f} 円",
            "利息 ÷ 借りた額": f"{int_b / rc_V:.1%}",
        }
    )
    st.dataframe(pd.DataFrame(rows), hide_index=True)
    st.caption("借りた額・期間・金利が違うので、あくまで「利息の重さ」の目安です。"
               "「利息 ÷ 借りた額」が大きいほど、借りたこと自体のコストが重くなります。")

    # ---------- 3. 学んだ数学 ----------
    st.divider()
    st.subheader("③ ここで使った数学")
    st.markdown(
        r"""
- **漸化式** $a_{n+1}=pa_n+q$ 型 → **不動点 $\alpha$ を引いて等比数列に変える**(②)
- **等比数列の一般項** → いきなり $a_n$ を求める(③、⑩)
- **等比数列の和** → 元金部分の合計が借入額 $A$ になる(⑥)
- **対数** → 完済までの回数 $N$ を求める(⑨)
- **等差数列** → 手元資金の増減(⑦)、元金均等返済(⑤)、金利0%のとき(⑩問10)
- **不等式の条件** → $P > rB$(元金が減る条件)、$c_k + j\,d_s < 0$(資金が尽きる条件)
"""
    )

    # ---------- 4. チェックリスト ----------
    st.divider()
    st.subheader("④ お金を借りる前の5つのチェック")
    st.markdown(
        """
1. **総支払額はいくら?** 月々の安さではなく、トータルで比べる(⑥)
2. **利息は何にかかっている?** 残価のように、返さない部分にもかかっていないか(⑩)
3. **元金は減っている?** 利息より多く返せているか($P > rB$)(⑨)
4. **収入が減ったら?** 返済負担率は?貯金は何か月もつか?(⑦)
5. **終わりの条件は?** 完済・返却・買取、それぞれ最後にいくら必要か(⑩)
"""
    )
    st.caption("どれも、漸化式を立てて数値を入れてみれば確かめられます。")

    # ---------- 5. 確認クイズ ----------
    st.divider()
    st.subheader("⑤ 確認クイズ")

    st.markdown("**Q1** 3つのうち、「回数 N を答えとして求める」のはどれか。")
    with st.expander("答え"):
        st.write("**リボ払い**。返済額 $P$ を固定しているので、$a_N=0$ を $N$ について解く(対数を使う)。")

    st.markdown("**Q2** リボ払いで $P \\le rB$ のとき、残高はどうなるか。")
    with st.expander("答え"):
        st.write("元金は減らず、$P < rB$ なら**増えていく**。毎月の利息 $rB$ を払うだけで精一杯になる。")

    st.markdown("**Q3** 残クレの月々が通常ローンより安いのに、総利息が増えるのはなぜか。")
    with st.expander("答え"):
        st.write("残価 $S$ を据え置いて元金が小さく見えるので月々は安い。しかし $S$ には最後まで利息がかかり続け、"
                 "元金が減る通常ローンより利息の総額が増える。")

    st.markdown("**Q4** どの返し方でも「$a_n$ の一般項」の形は同じ。変わるのは何か。")
    with st.expander("答え"):
        st.write("**初項 $a_0$ と、終わりの条件**(完済なら $a_N=0$、残クレなら $a_N=S$)。"
                 "また、リボ払いでは $P$ が先に決まり、$N$ が答えになる。")

    st.caption("※ 学習用の簡易モデルです。実際の契約内容や手数料は、各社の契約書で確認してください。")

# ---------- ⑫ 設備投資 ----------
with t12:
    st.subheader("企業の設備投資で考える「ローンのメリット」")
    st.info(
        "工場の機械や店舗など、**お金を生み出す設備**を借金で買うとどうなるか。"
        "借りたお金より多くの利益が得られれば、利息を払ってもプラスになります。"
        "「借りる=悪いこと」とは限らない例です。"
    )

    # ---------- 入力 ----------
    st.markdown("**設備投資の条件**")
    e1, e2, e3 = st.columns(3)
    cx_I = e1.number_input("設備投資額 $I$ (万円)", 100, 100000, 3000, step=100, key="cx_I") * 10_000
    cx_rate = e2.number_input("借入の年利(%)", 0.1, 10.0, 2.0, step=0.1, key="cx_rate")
    cx_Ny = e3.number_input("返済年数(年)", 1, 30, 10, key="cx_Ny")

    f1, f2, f3 = st.columns(3)
    cx_y1 = f1.number_input("設備による年間の追加利益 $\\pi$ (万円・初年度)", 10, 50000, 480, step=10, key="cx_y1") * 10_000
    cx_g = f2.slider(
        "利益が毎年増える割合 g(%)", 0, 10, 3, key="cx_g",
        help="設備を使ううちに、利益が毎年どれだけ増えるか。"
             "3%なら 480万円 → 494.4万円 → 509.2万円 と、毎年1.03倍。0%なら毎年同じ。",
    ) / 100
    cx_L = f3.slider("設備の使用年数(年)", 3, 20, 10, key="cx_L")

    g1, g2 = st.columns(2)
    cx_x = g1.slider(
        "実際の利益は計画の何%か 達成率 x(%)", 20, 150, 100, key="cx_x",
        help="100%=計画どおり。80%=計画の8割しか稼げなかった。うまくいかない場合を試すためのスライダー。",
    ) / 100
    cx_save = g2.number_input("自己資金を貯める場合の積立額(万円/月)", 5, 1000, 40, step=5, key="cx_save") * 10_000
    st.caption("「追加利益」は、設備によって増える年間の利益(返済前)。"
               "税金・減価償却・運転資金などは省いた簡易モデルです。")
    with st.expander("この2つの設定の意味(いまの値で確認)"):
        st.markdown(
            "- **利益が毎年増える割合 g**:毎年 (1+g) 倍になる(等比数列)\n"
            "- **達成率 x**:計画に対して、実際に何%の利益が出たか(全期間に一律でかかる)"
        )
        show_years = list(range(1, min(cx_L, 5) + 1))
        st.dataframe(
            pd.DataFrame(
                {
                    "年": [f"{k}年目" for k in show_years],
                    "計画の利益(万円)": [cx_y1 * (1 + cx_g) ** (k - 1) / 1e4 for k in show_years],
                    "実際の利益(万円)": [cx_x * cx_y1 * (1 + cx_g) ** (k - 1) / 1e4 for k in show_years],
                }
            ),
            column_config={
                "計画の利益(万円)": st.column_config.NumberColumn(format="%.1f"),
                "実際の利益(万円)": st.column_config.NumberColumn(format="%.1f"),
            },
            hide_index=True,
        )
        st.caption("「計画の利益」は g だけで決まり、「実際の利益」はそれに達成率 x をかけたものです。")
    r_c = cx_rate / 12 / 100
    N_c = 12 * cx_Ny
    P_c = monthly_payment(cx_I, r_c, N_c)  # 毎月の返済額
    T = 12 * max(cx_L, cx_Ny)  # 見る期間(月)

    def cx_profit(n, x):
        """n か月目の追加利益(円)。年ごとに (1+g) 倍 = 等比数列"""
        if n < 1 or n > 12 * cx_L:
            return 0.0
        return x * cx_y1 * (1 + cx_g) ** ((n - 1) // 12) / 12

    def cx_cum(x):
        """借入ルート:手元の現金収支の累計 c_n = c_(n-1) + 利益 - 返済"""
        c = [0.0]
        for n in range(1, T + 1):
            c.append(c[-1] + cx_profit(n, x) - (P_c if n <= N_c else 0.0))
        return c

    cum = cx_cum(cx_x)
    total_profit = sum(cx_profit(n, cx_x) for n in range(1, T + 1))
    total_pay = P_c * N_c
    interest = total_pay - cx_I
    net_gain = cum[-1]  # = 総利益 − 投資額 − 利息

    # ---------- 結果 ----------
    st.divider()
    st.subheader("借りて、今すぐ設備を買った場合")

    rho = cx_x * cx_y1 / cx_I  # 投資利益率(年)
    first_month = cx_profit(1, cx_x)
    dscr = first_month / P_c  # 返済余裕率

    m1, m2, m3 = st.columns(3)
    m1.metric("毎月の返済額 $P$", f"{P_c / 1e4:,.1f} 万円")
    m2.metric("投資利益率 $\\rho$ (年)", f"{rho:.1%}", f"借入金利 {cx_rate}%", delta_color="off")
    m3.metric(
        "返済余裕率", f"{dscr:.2f} 倍", "1倍を下回ると赤字", delta_color="off",
        help="返済余裕率 = 毎月の追加利益(返済前)÷ 毎月の返済額。初年度の値。"
             "1倍なら利益と返済額がちょうど同じ。",
    )
    if rho > cx_rate / 100:
        st.success(f"設備の収益率 {rho:.1%} が借入金利 {cx_rate}% を上回っています。"
                   "借りて投資するメリットが出る条件です。")
    else:
        st.warning("設備の収益率が借入金利以下です。借りて投資しても利益が出にくい状態です。")

    n1, n2 = st.columns(2)
    n1.metric("設備投資の最終損益", f"{net_gain / 1e4:,.0f} 万円")
    n2.metric("支払う利息の総額", f"{interest / 1e4:,.0f} 万円")

    min_cum = min(cum)
    if net_gain < 0:
        st.error("**投資を回収できませんでした。** 収益が計画を大きく下回ると、借入だけが残ります。")
    elif min_cum < 0:
        st.warning(f"最終的には黒字ですが、途中で最大 **{-min_cum / 1e4:,.0f} 万円** の資金不足が出ます"
                   "(返済が先に始まり、収益があとから増えるため)。手元資金で補う必要があります(⑦と同じ考え方)。")
    else:
        st.success("返済しながら、最初から黒字を保てます。")

    # ---------- 自己資金で貯める場合との比較 ----------
    st.divider()
    st.subheader("借りない場合(自己資金を貯めてから買う)と比べる")
    W = math.ceil(cx_I / cx_save)  # 貯まるまでの月数
    st.write(f"毎月 {cx_save / 1e4:g} 万円ずつ貯めると、{cx_I / 1e4:,.0f} 万円に届くのは "
             f"**{W} か月後({ym(W)})**。積立は**等差数列** $c_n = n \\times$ 積立額 です。")

    cum_self, acc = [], 0.0
    for n in range(0, T + 1):
        if n < W:
            cum_self.append(0.0)
        else:
            acc = -cx_I if n == W else acc + cx_profit(n - W, cx_x)
            cum_self.append(acc)

    st.line_chart(
        pd.DataFrame(
            {
                "借りて今すぐ買う(万円)": [v / 1e4 for v in cum],
                "貯めてから買う(万円)": [v / 1e4 for v in cum_self],
            },
            index=list(range(T + 1)),
        ),
        color=["#1f77b4", "#ff7f0e"],  # 1列目=青、2列目=オレンジ(DataFrameの列の順)
    )
    st.caption("横軸は月数。縦軸は「設備投資がもたらした損益の累計」。"
               "貯めてから買う場合は、買った瞬間に投資額ぶんマイナスになり、そこから利益で取り戻します。")

    diff = cum[-1] - cum_self[-1]
    if W >= T:
        st.write("自己資金では、見ている期間内に設備を買えません。")
    elif diff > 0:
        st.success(f"{ym(T)} 後の損益は、借りた場合のほうが **{diff / 1e4:,.0f} 万円** 有利です。"
                   f"利息 {interest / 1e4:,.0f} 万円を払っても、**{W} か月早く稼ぎ始めた**ぶんが上回ります。")
    else:
        st.warning(f"{ym(T)} 後の損益は、貯めてから買うほうが **{-diff / 1e4:,.0f} 万円** 有利です。"
                   "利益が小さいか、金利が高いと、借りるメリットは薄れます。")

    # ---------- 計画がはずれたら ----------
    st.divider()
    st.subheader("計画どおりにいかなかったら?(感度分析)")
    sens_rows = []
    for xx in [1.0, 0.8, 0.6, 0.4]:
        c = cx_cum(xx)
        sens_rows.append(
            {
                "計画の達成率": f"{xx:.0%}",
                "返済余裕率": f"{cx_profit(1, xx) / P_c:.2f} 倍",
                "資金不足の最大額": f"{max(-min(c), 0) / 1e4:,.0f} 万円",
                "最終損益": f"{c[-1] / 1e4:,.0f} 万円",
            }
        )
    st.dataframe(pd.DataFrame(sens_rows), hide_index=True)
    x_b = P_c / (cx_y1 / 12)
    st.write(f"初年度の収益で毎月の返済をまかなえる**最低の達成率**は、"
             f"P ÷ 月の追加利益 = **{x_b:.1%}**(増益率を考えない目安)。")

    # ---------- 数列で考える ----------
    st.divider()
    st.subheader("数列で考える")
    st.markdown("**① 手元の現金収支(漸化式)**")
    st.latex(r"c_0 = 0,\qquad c_n = c_{n-1} + \pi_n - P")
    st.write("$\\pi_n$ は n か月目の追加利益、P は毎月の返済額。増益がなく $\\pi_n$ が一定なら、")
    st.latex(r"c_n = n\,(\pi - P)\quad(\text{公差 } \pi - P \text{ の等差数列})")

    st.markdown("**② 年間利益は等比数列、累計はその和**")
    st.write("年間利益が毎年 $(1+g)$ 倍で増えるとき、k 年目の利益 $y_k$ と L 年間の累計は")
    st.latex(r"y_k = y_1(1+g)^{k-1},\qquad \sum_{k=1}^{L} y_k = \frac{y_1\{(1+g)^L - 1\}}{g}")

    st.markdown("**③ 設備投資の最終損益**")
    st.latex(r"\text{最終損益} = \sum y_k - \underbrace{(\text{設備投資額}I + \text{利息})}_{\text{総返済額}}")
    st.write(f"いまの設定:累計利益 {total_profit / 1e4:,.0f} 万円 − 総返済額 {total_pay / 1e4:,.0f} 万円 "
             f"= **{(total_profit - total_pay) / 1e4:,.0f} 万円**")

    st.markdown("**④ 借りるメリットが出る条件(目安)**")
    st.latex(r"\text{設備の収益率 } \rho = \frac{y_1}{I} \;>\; \text{借入金利}")
    st.caption("ρ が金利を大きく上回るほど、借りる効果(レバレッジ)が大きくなります。")

    st.markdown("**⑤ 返済余裕率**")
    st.latex(r"\text{返済余裕率} = \frac{\pi}{P} \qquad \left(\text{損益分岐の達成率} = \frac{P}{\pi} = \frac{1}{\text{返済余裕率}}\right)")
    st.caption("π は毎月の追加利益(初年度)、P は毎月の返済額。")

    # ---------- ローンの見え方の整理 ----------
    st.divider()
    st.subheader("⑥〜⑩との違い")
    st.markdown(
        """
| | 住宅・リボ・残クレ | 企業の設備投資 |
|---|---|---|
| 借りたお金の使い道 | 消費(使って終わり) | **利益を生む設備** |
| お金の流れ | 返済だけが出ていく | 返済が出ていくが、**収益も入ってくる** |
| 成功の条件 | 返済額が収入に収まること | **収益率 > 金利**、かつ**資金繰りがもつこと** |
"""
    )
    st.caption("※ 学習用の簡易モデルです。実際の投資判断では、税金・減価償却・運転資金・"
               "正味現在価値(NPV)などを使って慎重に検討します。")

    # ---------- 練習問題 ----------
    with st.expander("練習問題: 以下, 設備投資3,000万円を全額借入(年2%・10年=120ヶ月)し、月の追加利益が35万円(増益なし)で一定とする。月々の返済額は約27.6万円となる。"):
        st.markdown("**問13 (借入投資の最終損益)** 10年間の損益はいくらか。")
        st.latex(r"c_{120} = 120\,(\pi - P) = 120\times(35 - 27.6) \approx 888\text{ 万円}")
        st.write("答え:**888万円の黒字**。(総利益4,200万円 − 総返済額約3,312万円 ≒ 888万円 でも確かめられる)")

        st.markdown("**問14 (赤字転落のリスク分析)** 収益が計画の何%を下回ると、毎月の返済をまかなえなくなるか。")
        st.latex(r"x \cdot 35 \ge 27.6 \;\Longrightarrow\; x \ge 0.79")
        st.write("答え:**約79%**。計画の約8割を下回る状態が続くと、毎月の収支が赤字になる。")

        st.markdown("**問15 (比較：積立と借入の機会損失)** 借りずに、毎月40万円ずつ積み立てて3,000万円を用意するには何か月かかるか。"
                    "その間、設備を使えないことで、増えなかった利益はいくらか。")
        st.latex(r"3000 \div 40 = 75\text{ か月},\qquad 35\times 75 = 2625\text{ 万円}")
        st.write("答え:**75か月**。待つ間に得られなかった利益は約**2625万円**。"
                 "借りた場合の利息(約312万円)より、はるかに大きな機会損失になる。")

        st.markdown("**問16(収益率と金利の大小関係)** 問15で、設備の収益率が金利より低かったら、結論はどう変わるか。")
        st.write("待つ間に失う利益より、払う利息のほうが大きくなり得る。"
                 "**収益率と金利の大小**が、借りるかどうかの分かれ目になる。")
