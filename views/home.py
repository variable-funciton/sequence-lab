"""ホーム（各ページへの案内）"""

import streamlit as st

st.title("🔢 数列のシミュレーション")
st.markdown(
    "数列の考え方が、お金の計算（預金・投資・ローン）や、物理・工学の場面でどのように使われているかを、"
    "数値を変えながら確かめるためのアプリです。左のメニュー、または下のリンクから各ページへ移動できます。"
)

CARDS = [
    ("📶 等差数列とその和", r"一般項 $a_n$ と和 $S_n$ をグラフで確認。和が最大になる $n$ や、"
     "和の公式（逆順に並べて足す）の図解。", "後期課題9", "views/arithmetic.py"),
    ("✖️ 等比数列とその和", r"一般項 $ar^{n-1}$ と和の公式。公比 $r$ の 6 つの場合"
     r"（$0<r<1$, $r=1$, $r>1$, $-1<r<0$, $r=-1$, $r<-1$）で項と和のふるまいを比べる。",
     "後期課題10", "views/geometric.py"),
    ("💹 単利と複利", "単利（等差数列）と複利（等比数列）の増え方を比較。毎年減る投資も。",
     "後期課題10", "views/interest.py"),
    ("🔁 漸化式で見るローン返済", r"$a_{n+1} = (1+r)a_n - P$ を 1 年ずつ進めて残高を観察。"
     "完済・残クレ・返済不足で借金が増えるケース、特性方程式による一般項。", "後期課題12", "views/recurrence_loan.py"),
    ("📘 ローン返済で学ぶ漸化式（月次・総合）", "元利均等返済を漸化式で解き、一般項・総支払額・返済不能シナリオ、"
     "リボ払い・残クレ・企業の設備投資まで 12 のタブで学ぶ。", "後期課題12（発展）", "views/loan_textbook.py"),
    ("🏦 元利均等返済（月次・実務版）", "住宅ローンのような月払いの返済表。円未満の端数処理つき。",
     "発展", "views/level_payment.py"),
]
cols = st.columns(2)
for i, (title, desc, rel, path) in enumerate(CARDS):
    with cols[i % 2], st.container(border=True):
        st.subheader(title)
        st.markdown(desc)
        st.caption(f"関連: {rel}")
        st.page_link(path, label="ページを開く", icon="➡️")

st.markdown("### 物理・各学科への応用")
st.markdown("数列が、物理や機械・電気・化学・都市（土木・建築）・ビジネスの場面でどのように使われているかを見るページです。")
APPLIED = [
    ("🏀 物理", [("views/bounce.py", "ボールの跳ね返り", "はね返る高さは等比数列。無限にはね返っても、止まるまでの道のりと時間は有限。")]),
    ("⚙️ 機械系", [("views/preferred_numbers.py", "標準数（ルナール数列）", r"部品の寸法・定格を公比 $\sqrt[n]{10}$ の等比数列で段階づけ。"),
                  ("views/damping.py", "減衰振動の振幅", "抵抗なら等比数列、摩擦なら等差数列で振幅が減る。")]),
    ("🔌 電気系", [("views/e_series.py", "抵抗器の E 系列", "E6・E12・E24 は等比数列。許容差とのつながり。"),
                  ("views/ladder.py", "はしご形回路の合成抵抗", r"漸化式と極限。$R_1 = R_2$ なら黄金比とフィボナッチ数。"),
                  ("views/transient.py", "過渡現象を漸化式で計算", "RC・RL 回路を差分法で。きざみが粗いと振動・発散。")]),
    ("🧪 化学系", [("views/half_life.py", "放射性物質の半減期", "公比 1/2 の等比数列。年代測定。"),
                  ("views/dosing.py", "薬の繰り返し投与", r"$c_{n+1} = rc_n + D$。ローンと同じ形の漸化式と定常状態。"),
                  ("views/extraction.py", "溶媒抽出・段階希釈", "少しずつ何回も抽出するほうがよい理由。")]),
    ("🏙️ 都市系", [("views/population.py", "人口の変化と将来推計", "等比数列のモデルと、国の将来推計との比較。"),
                  ("views/repair_fund.py", "マンションの修繕積立金", "均等積立と段階増額積立（等差数列の和）。"),
                  ("views/magnitude.py", "地震のマグニチュード", "M が 1 違うとエネルギーは約 32 倍（等比数列）。")]),
    ("💼 ビジネス", [("views/depreciation.py", "減価償却", "定額法は等差数列、定率法は等比数列。国税庁の計算例を再現。"),
                   ("views/saving.py", "積立と複利", r"$a_{n+1} = (1 + r)a_n + P$。ローン返済の逆向き。")]),
]
cols = st.columns(3)
for i, (head, pages) in enumerate(APPLIED):
    with cols[i % 3], st.container(border=True):
        st.markdown(f"**{head}**")
        for path, label, desc in pages:
            st.page_link(path, label=label)
            st.caption(desc)

st.divider()
with st.expander("使い方のヒント"):
    st.markdown(
        "- 設定は左のサイドバーにあります（スマートフォンでは左上の **>** を押すと開きます）。\n"
        "- 「例題を読み込む」を選ぶと、課題と同じ数値が自動で入ります。\n"
        "- グラフにカーソルを合わせる（タップする）と値が表示されます。"
    )
