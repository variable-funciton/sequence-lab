"""数列のシミュレーション（数学B 後期）— エントリーポイント

Streamlit Community Cloud の Main file path は従来どおり LevelPayment.py のままで動く。
ページを増やすときは views/ にファイルを作り、下の PAGES に 1 行追加する。
"""

import streamlit as st

st.set_page_config(page_title="数列のシミュレーション", page_icon="🔢", layout="wide")

PAGES = {
    "はじめに": [
        st.Page("views/home.py", title="ホーム", icon="🏠", default=True),
    ],
    "数列": [
        st.Page("views/arithmetic.py", title="等差数列とその和", icon="📶", url_path="arithmetic"),
        st.Page("views/geometric.py", title="等比数列とその和", icon="✖️", url_path="geometric"),
        st.Page("views/interest.py", title="単利と複利（等差・等比）", icon="💹", url_path="interest"),
        st.Page("views/recurrence_loan.py", title="漸化式で見るローン返済", icon="🔁", url_path="recurrence_loan"),

        st.Page("views/loan_textbook.py", title="ローン返済で学ぶ漸化式（月次・総合）", icon="📘",
                url_path="loan_textbook"),
    ],
    "物理への応用": [
        st.Page("views/bounce.py", title="ボールの跳ね返り（無限等比級数）", icon="🏀", url_path="bounce"),
    ],
    "機械系のための数列": [
        st.Page("views/preferred_numbers.py", title="標準数（ルナール数列）", icon="📏", url_path="preferred_numbers"),
        st.Page("views/damping.py", title="減衰振動の振幅", icon="〰️", url_path="damping"),
    ],
    "電気系のための数列": [
        st.Page("views/e_series.py", title="抵抗器の E 系列", icon="🔌", url_path="e_series"),
        st.Page("views/ladder.py", title="はしご形回路の合成抵抗", icon="🪜", url_path="ladder"),
        st.Page("views/transient.py", title="過渡現象を漸化式で計算", icon="⚡", url_path="transient"),
    ],
    "化学系のための数列": [
        st.Page("views/half_life.py", title="放射性物質の半減期", icon="☢️", url_path="half_life"),
        st.Page("views/dosing.py", title="薬の繰り返し投与", icon="💊", url_path="dosing"),
        st.Page("views/extraction.py", title="溶媒抽出・段階希釈", icon="🧪", url_path="extraction"),
    ],
    "都市系のための数列": [
        st.Page("views/population.py", title="人口の変化と将来推計", icon="🏙️", url_path="population"),
        st.Page("views/repair_fund.py", title="マンションの修繕積立金", icon="🏢", url_path="repair_fund"),
        st.Page("views/magnitude.py", title="地震のマグニチュード", icon="🌏", url_path="magnitude"),
    ],
    "ビジネスのための数列": [
        st.Page("views/depreciation.py", title="減価償却（定額法・定率法）", icon="🧾", url_path="depreciation"),
        st.Page("views/saving.py", title="積立と複利", icon="🐷", url_path="saving"),
    ],
    "実務版": [
        st.Page("views/level_payment.py", title="元利均等返済（月次）", icon="🏦", url_path="level_payment"),
    ],
}

st.navigation(PAGES).run()
