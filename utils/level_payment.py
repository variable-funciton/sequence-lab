"""元利均等返済（月次・実務版）の計算クラス（旧 LevelPayment.py から移動）"""

import math
import pandas as pd


class LoanSimulator:
    """元利均等返済シミュレータ(月次ループで円未満切り捨て)"""

    def __init__(self, annual_rate: float, loan_amount: int, term_year: int):
        self.annual_rate = annual_rate
        self.loan_amount = loan_amount
        self.term_year = term_year
        self.total_months = 12 * term_year
        self.monthly_rate = annual_rate / 12 / 100
        self.monthly_payment = self._calc_monthly_payment()
        self.schedule = self._build_schedule()

    def _calc_monthly_payment(self) -> int:
        """毎月の支払額(円未満切り上げ。最終回で調整するため不足が出ないようにする)"""
        if self.loan_amount == 0:
            return 0
        if self.monthly_rate > 0:
            factor = (1 + self.monthly_rate) ** self.total_months
            payment = self.loan_amount * self.monthly_rate * factor / (factor - 1)
        else:
            payment = self.loan_amount / self.total_months
        return math.ceil(payment)

    def _build_schedule(self) -> pd.DataFrame:
        """月ごとの返済表を作成"""
        rows = []
        balance = self.loan_amount

        for month in range(1, self.total_months + 1):
            interest = math.floor(balance * self.monthly_rate)
            # 最終回は残高+利息を全額支払う
            if month == self.total_months:
                payment = balance + interest
            else:
                payment = min(self.monthly_payment, balance + interest)
            principal = payment - interest
            balance -= principal
            rows.append({
                "回数": month,
                "年": (month - 1) // 12 + 1,
                "支払額": payment,
                "元金": principal,
                "利息": interest,
                "残高": balance,
            })

        return pd.DataFrame(rows)

    @property
    def total_paid(self) -> int:
        return int(self.schedule["支払額"].sum())

    @property
    def total_interest(self) -> int:
        return int(self.schedule["利息"].sum())

    @property
    def final_payment(self) -> int:
        return int(self.schedule["支払額"].iloc[-1])

    def yearly_summary(self) -> pd.DataFrame:
        """年ごとの集計(年末残高つき)"""
        grouped = self.schedule.groupby("年").agg(
            支払額=("支払額", "sum"),
            元金=("元金", "sum"),
            利息=("利息", "sum"),
            年末残高=("残高", "last"),
        )
        return grouped.reset_index()
