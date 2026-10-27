# 数列のシミュレーション（数学B 後期）

Streamlit Community Cloud で公開する、数列の学習用 Web アプリです。
**Main file path は従来どおり `LevelPayment.py`** のままで動きます（中身はページ一覧に変わりました）。

## ページ構成

| ページ | 内容 | 関連課題 |
|---|---|---|
| 等差数列とその和 | 項と和のグラフ、和が最大になる n、初めて負になる項、和の公式の図解 | 後期課題9 |
| 等比数列とその和 | 一般項と和の公式。公比 r の 6 つの場合（0<r<1, r=1, r>1, −1<r<0, r=−1, r<−1）を強調表示・一覧比較。和の公式の導き方 | 後期課題10 |
| 単利と複利 | 単利（等差数列）と複利（等比数列）の比較、毎年減る投資、72 の法則 | 後期課題10 |
| 漸化式で見るローン返済 | `a_{n+1} = (1+r)a_n − P` を 1 年ずつ進める。完済・残クレ・返済額固定、特性方程式と一般項 | 後期課題12 |
| ローン返済で学ぶ漸化式（月次・総合） | 元利均等返済の解法、一般項と数値の比較、総支払額、返済不能シナリオ、用語集、リボ払い、残クレ、まとめ、設備投資（12 タブ。loan_recurrence_app_v2.py を移植） | 後期課題12（発展） |
| 元利均等返済（月次・実務版） | 旧 LevelPayment.py の画面（変更なし） | 発展 |

各ページの「例題を読み込む」で、課題と同じ数値を読み込めます。

## ファイル構成

```
LevelPayment.py        エントリーポイント（ページ一覧はここで管理）
views/                 各ページ
utils/sequences.py     数列の計算（Fraction で厳密計算、Streamlit に依存しない）
utils/level_payment.py 月次ローンの計算クラス（旧 LevelPayment.py から移動）
tests/test_sequences.py 課題9・10・12 の数値で検証するテスト
```

## ローカルでの確認

```bash
pip install -r requirements.txt
streamlit run LevelPayment.py
python -m tests.test_sequences
```
