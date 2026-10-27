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
    "実務版": [
        st.Page("views/level_payment.py", title="元利均等返済（月次）", icon="🏦", url_path="level_payment"),
    ],
}

st.navigation(PAGES).run()
