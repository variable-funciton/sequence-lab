"""元利均等返済シミュレーション（月次・実務版）— 旧 LevelPayment.py の画面部分"""

import streamlit as st

from utils.level_payment import LoanSimulator

st.title("元利均等返済シミュレーション")

st.header("情報入力")
loan_amount_man = st.number_input("借入金額(万円)", min_value=0, max_value=100000, value=1000, step=10)
rate = st.number_input("年利(%)", min_value=0.0, max_value=100.0, value=3.0, step=0.1, format="%.2f")
years = st.number_input("借入年数(年)", min_value=1, max_value=50, value=20, step=1)

total_price = loan_amount_man * 10_000

if total_price == 0:
    st.warning("借入金額を1万円以上で入力してください。")
    st.stop()

loan = LoanSimulator(rate, total_price, years)

st.divider()
st.header("計算結果")

c1, c2 = st.columns(2)
c1.metric("毎月の支払額", f"{loan.monthly_payment:,} 円")
c2.metric("最終回の支払額", f"{loan.final_payment:,} 円")

c3, c4 = st.columns(2)
c3.metric("総利息", f"{loan.total_interest:,} 円")
c4.metric("累計支払額", f"{loan.total_paid:,} 円")

st.subheader("残高の推移")
yearly = loan.yearly_summary()
st.line_chart(yearly.set_index("年")["年末残高"])

st.subheader("年別の内訳")
st.dataframe(
    yearly.style.format("{:,}", subset=["支払額", "元金", "利息", "年末残高"]),
    hide_index=True,
)

with st.expander("月別の返済表を見る"):
    st.dataframe(loan.schedule, hide_index=True)

st.caption("※ 概算です。実際の返済額は金融機関の計算方法(端数処理・ボーナス払い等)により異なります。")
