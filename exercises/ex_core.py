"""演習(自習用の類題)の共通部品:問題の型、4択の表示、ヒント、解答、LaTeX 出力

応用数学ラボ(variable-funciton/applied-mathematics)の ex_core.py を数学IB 用に移植したもの。

問題を増やすときは、各章のファイル(ex_trig1.py など)に「生成関数」を書き、REGISTRY に登録する。
生成関数は random.Random を受け取り、Problem を返す。条件に合わない数値が出たら Retry を投げる。

応用数学ラボからの主な変更点
  - ProblemType に試験用の情報(大問の共通の問題文 intro、配点 points、並べ方 layout、
    1題が占めるページの割合 height、格子の列数 cols)を持たせた。配点は1題10点に固定しない。
  - Problem に exam_short(大問の中で使う短い問題文)と exam_choices(試験でも選択肢を残す)を足した。
  - streamlit は画面を出す関数の中でだけ使う(生成関数・LaTeX 出力は streamlit なしでテストできる)。
"""
import random
import re
from dataclasses import dataclass, field

LABELS = ["(1)", "(2)", "(3)", "(4)"]
KANA = ["ア", "イ", "ウ", "エ"]


class Retry(Exception):
    """数値がよくない(答えが自明・選択肢が重なる等)ので作り直す"""


@dataclass
class Choice:
    tex: str                 # 選択肢(LaTeX、$ なし)
    correct: bool = False
    why: str = ""            # 誤答を選んだときの指摘
    value: object = None     # 自動テスト用の値


@dataclass
class Problem:
    title: str
    level: str               # "基本" / "標準"
    statement: str           # 問題文(Markdown。数式は $..$ / $$..$$。** は使わない)
    choices: list
    hints: list = field(default_factory=list)
    solution: list = field(default_factory=list)   # 解答の途中式(段落ごと)
    meta: dict = field(default_factory=dict)       # 自動テスト用の元データ
    # 試験(記述式)で使うとき
    exam_short: str = None       # 大問の中の小問としての問題文(例: 「$\sin 210^\circ$」)。None なら statement
    exam_answer: str = None      # None なら正解の選択肢、"" なら「答」の行を出さない(証明問題など)
    exam_solution: list = None   # None なら solution をそのまま使う
    exam_choices: bool = False   # True なら試験でも選択肢(ア〜エ)を残す(グラフを選ぶ問題など)
    figure: dict = None          # 図の仕様(ex_fig.py)。問題文の下と解答に表示する
    answer_figure: dict = None   # 解答だけに入れる図
    figure_side: bool = False    # 試験で図を問題文の右に置く(扇形など)


@dataclass
class ProblemType:
    key: str
    name: str
    level: str
    gen: object                  # gen(rng) -> Problem
    intro: str = "次の問いに答えよ。"   # 大問の共通の問題文(同じ intro の型どうしは1つの大問にまとめられる)
    points: int = 5              # 試験での標準の配点(1題あたり)
    layout: str = "list"         # "list"(小問を縦に並べる)/ "grid"(小問集合:格子状に並べる)
    height: float = 1 / 3        # list のとき1題が占める問題用紙の割合
    cols: int = 5                # grid のときの列数
    unit: str = ""               # 単元名(画面の表示用)


def build(ptype, rng, tries=300):
    """生成関数を、条件を満たすまで繰り返し呼ぶ。選択肢を並べかえて返す"""
    for _ in range(tries):
        try:
            p = ptype.gen(rng)
        except Retry:
            continue
        texs = [c.tex for c in p.choices]
        if len(p.choices) != 4 or len(set(texs)) != 4 or sum(c.correct for c in p.choices) != 1:
            continue
        rng.shuffle(p.choices)
        return p
    raise RuntimeError(f"{ptype.name}: 問題を生成できませんでした")


def rng_for(*parts):
    return random.Random("-".join(str(x) for x in parts))


def correct_choice(p):
    return [c for c in p.choices if c.correct][0]


def fill_choices(correct_tex, wrongs, pool, rng, correct_value=None):
    """正解 + 誤答(典型的な間違い)で4択を作る。
    wrongs: [(tex, why)]。重なりを除き、足りなければ pool([(tex, why)])から補う。"""
    out = [Choice(correct_tex, True, value=correct_value)]
    seen = {correct_tex}
    for tex, why in wrongs:
        if tex not in seen and len(out) < 4:
            out.append(Choice(tex, False, why))
            seen.add(tex)
    pool = list(pool)
    rng.shuffle(pool)
    for tex, why in pool:
        if tex not in seen and len(out) < 4:
            out.append(Choice(tex, False, why))
            seen.add(tex)
    if len(out) < 4:
        raise Retry
    return out


# ------------------------------------------------------------
# 表記
# ------------------------------------------------------------
def punct(s):
    """句読点を「, 」「. 」(小文字のコンマ・ピリオドと半角スペース)にそろえる(数式の外だけ)"""
    if not s:
        return s
    parts = re.split(r"(\$\$.+?\$\$|\\\[.+?\\\]|\$[^$]+\$)", s, flags=re.S)
    for k in range(0, len(parts), 2):
        parts[k] = parts[k].replace("、", ", ").replace("。", ". ").replace("，", ", ").replace("．", ". ")
    return "".join(parts).rstrip()


def jp_punct(s):
    """試験の書式(「，」「．」)にそろえる(数式の外だけ)"""
    if not s:
        return s
    parts = re.split(r"(\$\$.+?\$\$|\\\[.+?\\\]|\$[^$]+\$)", s, flags=re.S)
    for k in range(0, len(parts), 2):
        parts[k] = parts[k].replace("、", "，").replace("。", "．")
    return "".join(parts).rstrip()


def md_to_tex(s):
    """問題文・解答の Markdown を LaTeX に(数式はそのまま、$$..$$ は \\[..\\])"""
    s = re.sub(r"\$\$(.+?)\$\$", lambda m: r"\[" + m.group(1) + r"\]", s, flags=re.S)
    s = s.replace("**", "")
    return jp_punct(s)


def displaystyle_fracs(text):
    """$...$ 内の分数をすべて \\displaystyle に統一(\\dfrac も \\frac + \\displaystyle に)"""
    def fix(m):
        c = m.group(1).replace(r"\dfrac", r"\frac")
        if r"\frac" in c and not c.lstrip().startswith(r"\displaystyle"):
            c = r"\displaystyle " + c
        return "$" + c + "$"
    text = re.sub(r"(?<!\\)\$([^$]+)\$", fix, text)
    return text.replace(r"\dfrac", r"\frac")      # \[ \] の中(もともと displaystyle)


# ------------------------------------------------------------
# 画面表示(streamlit)
# ------------------------------------------------------------
def _st():
    import streamlit as st
    return st


def _inc(key, reset=None):
    st = _st()
    st.session_state[key] = st.session_state.get(key, 0) + 1
    for r in reset or []:
        st.session_state.pop(r, None)


def _new_seed(key):
    st = _st()
    st.session_state[key] = random.randint(1, 9999)


def make_set(registry, names, n, seed):
    """出題セット:型を順にくり返して n 問。各問の数値はセット番号と問番号から決まる"""
    types = [t for t in registry if t.name in names]
    return [(i, types[i % len(types)]) for i in range(n)]


def show_fig(spec, key, height=360):
    st = _st()
    from .ex_fig import plotly_fig
    st.plotly_chart(plotly_fig(spec, height=height), width="stretch", key=key)


def render(chapter, registry, title):
    """章の演習ページ"""
    st = _st()
    ck = f"ex_{chapter}"
    st.info("自習用の演習です。数値を変えた類題が何度でも作れます。"
            "答えを選ぶと正誤と、誤答なら間違えやすい点が表示されます。ヒントは1段ずつ開けられます。")
    c1, c2 = st.columns([1, 2])
    level = c1.radio("難易度", ["基本", "標準", "基本+標準"], index=2, key=f"{ck}_lv")
    avail = [t for t in registry if level == "基本+標準" or t.level == level]
    names = c2.multiselect("問題の型(複数選べる)", [t.name for t in avail], default=[t.name for t in avail],
                           key=f"{ck}_types_{level}")
    if not names:
        st.warning("問題の型を1つ以上選んでください。")
        return
    d1, d2, d3 = st.columns([1, 1, 1])
    n = d1.slider("問題数", 1, 12, min(len(names), 6), key=f"{ck}_n")
    seed_key = f"{ck}_seed"
    if seed_key not in st.session_state:
        st.session_state[seed_key] = 1
    seed = int(d2.number_input("セット番号", 1, 9999, step=1, key=seed_key))
    d3.button("新しいセットを作る", on_click=_new_seed, args=(seed_key,), key=f"{ck}_new")
    d3.caption("同じセット番号なら同じ問題が出る(質問するときに番号を伝えよう)。")

    probs = []
    for i, t in make_set(registry, names, n, seed):
        vkey = f"{ck}_{seed}_{i}_v"
        v = st.session_state.get(vkey, 0)
        p = build(t, rng_for(seed, i, v, t.key))
        probs.append((i, t, v, vkey, p))

    st.divider()
    for i, t, v, vkey, p in probs:
        base = f"{ck}_{seed}_{i}_{v}"
        st.markdown(f"#### 問{i + 1}　{p.title}　〔{p.level}〕" + (f"(類題 {v})" if v else ""))
        st.markdown(punct(p.statement))
        if p.figure is not None:
            show_fig(p.figure, f"{base}_fig")
        for lab, c in zip(LABELS, p.choices):
            st.markdown(f"{lab}　${c.tex}$")
        ans = st.radio("答え", LABELS, index=None, horizontal=True, key=f"{base}_ans")
        if ans is not None:
            c = p.choices[LABELS.index(ans)]
            if c.correct:
                st.success("正解! ")
            else:
                st.error(punct("不正解. " + (c.why or "もう一度計算を確かめよう。")))
        hkey = f"{base}_h"
        k = st.session_state.get(hkey, 0)
        for j, h in enumerate(p.hints[:k], 1):
            st.markdown(punct(f"ヒント{j}:{h}"))
        b1, b2, b3 = st.columns(3)
        if k < len(p.hints):
            b1.button(f"ヒントを見る({k + 1}/{len(p.hints)})", on_click=_inc, args=(hkey,), key=f"{base}_hb")
        show = b2.checkbox("解答を表示", key=f"{base}_sol")
        b3.button("同じ型でもう一問", on_click=_inc, args=(vkey,), key=f"{base}_more")
        if show:
            correct = LABELS[[c.correct for c in p.choices].index(True)]
            with st.container(border=True):
                st.markdown(f"正解:{correct}")
                for s in p.solution:
                    st.markdown(punct(s))
                if p.answer_figure is not None:
                    show_fig(p.answer_figure, f"{base}_afig", height=340)
        st.divider()

    st.subheader("紙で解く(LaTeX・PDF でダウンロード)")
    st.caption("いま表示している問題(類題に切りかえた問題を含む)を、数学IB の試験と同じ構成の LaTeX 一式"
               "(本体2つ + problems.tex + answers.tex)にして zip でダウンロードする。uplatex + dvipdfmx でコンパイルする。")
    plist = [p for *_, p in probs]
    e1, e2 = st.columns(2)
    with e1:
        st.markdown("**LaTeX ファイル**(先生・自分で編集したい人)")
        st.download_button("LaTeX 一式をダウンロード(.zip)", latex_zip(plist, title, seed),
                           file_name=f"数学IB_{title.replace(' ', '_')}_演習_{seed}.zip", mime="application/zip",
                           key=f"{ck}_dl")
    with e2:
        st.markdown("**すぐに取り組みたい学生はこちらでダウンロード**")
        student_pdf_ui(plist, title, seed, ck)


# ------------------------------------------------------------
# LaTeX 出力(数学IB の試験と同じ構成:本体 + problems.tex / answers.tex)
# ------------------------------------------------------------
NENDO = "令和8年度"
SUBJECT = "数学IB"
CLASS_LINE = r"1年M, E, C, T 工学科 \hspace{10truemm}番\ 氏名\hspace{50truemm}"

# 先生の手元(emath あり)で使う本体のプリアンブル。後期中間の試験と同じ
PREAMBLE = r"""\documentclass[a4paper,12pt,dvipdfmx,fleqn,uplatex]{jsarticle}
\newcommand{\f}[1]{\framebox[1cm]{\textgt{\small #1}}}
\def\labelenumi{\framebox[0.8cm]{\bf\theenumi}}
\def\theenumii{\arabic{enumii}}
\usepackage[margin=0.5cm,dvipdfmx]{geometry}
\usepackage{amsmath, amssymb}
\usepackage{arydshln}
\usepackage{multicol,enumerate,multienum}
\usepackage{setspace}
\usepackage{cancel}
\usepackage{tikz}
\usetikzlibrary{intersections, calc}
\usetikzlibrary{patterns,arrows,decorations.pathmorphing}
\usetikzlibrary{decorations.markings}
\usepackage{pgfplots}
\pgfplotsset{compat=1.12}
\usepackage{emath,
emathEy,
emathMw,
emathW,emathWb,emathWs,
}
\newcommand{\Set}[1]{ \left\{ #1 \right\} }
\usepackage{ascmac}
\pagestyle{empty}
"""

# emath のないサーバー(Streamlit Community Cloud)で PDF を作るときのプリアンブル。
# emath の edaenumerate の代わりを multicol で定義する
SERVER_PREAMBLE = r"""\documentclass[a4paper,12pt,dvipdfmx,fleqn,uplatex]{jsarticle}
\def\labelenumi{\framebox[0.8cm]{\bf\theenumi}}
\def\theenumii{\arabic{enumii}}
\usepackage[margin=0.5cm,dvipdfmx]{geometry}
\usepackage{amsmath, amssymb}
\usepackage{multicol,enumerate}
\usepackage{setspace}
\usepackage{tikz}
\usepackage{ascmac}
\usepackage{xparse}
\NewDocumentEnvironment{edaenumerate}{d<>}
 {\begin{multicols}{\IfNoValueTF{#1}{4}{#1}}\begin{enumerate}\setlength{\itemsep}{0pt}}
 {\end{enumerate}\end{multicols}}
\pagestyle{empty}
"""


def choices_tex(choices, kana=False):
    """4択の選択肢。短ければ1行に4つ、長ければ1行に2つ"""
    labs = [f"（{k}）" for k in KANA] if kana else LABELS
    cells = [rf"{lab}\ ${c.tex}$" for lab, c in zip(labs, choices)]
    if max(len(c.tex) for c in choices) <= 28:
        return r"\noindent" + r"\hfill ".join(cells) + r"\hfill\null"
    rows = []
    for k in (0, 2):
        rows.append(r"\noindent\makebox[0.48\linewidth][l]{" + cells[k] + r"}\makebox[0.48\linewidth][l]{"
                    + cells[k + 1] + "}")
    return r"\\[2mm]".join(rows)


def main_tex(title, seed, inner, answer=False, preamble=PREAMBLE):
    head = rf"{NENDO} {SUBJECT} {title} 演習" + (" 解答" if answer else "")
    return (preamble + "\\makeatletter\n"
            + rf"\title{{{head}}}" + "\n"
            + rf"\author{{{CLASS_LINE}}}" + "\n"
            + rf"\date{{セット番号 {seed}}}" + "\n"
            + "\\begin{document}\n\\maketitle\n\\begin{enumerate}\n"
            + rf"\input{{{inner}}}" + "\n\\end{enumerate}\n\\end{document}\n")


def _fig(p):
    spec = getattr(p, "figure", None)
    if not spec:                      # 図のない問題では ex_fig を読み込まない(ex_fig のないアプリでも動く)
        return ""
    from .ex_fig import tikz
    return "\\begin{center}\n" + tikz(spec) + "\n\\end{center}\n"


def _afig(p):
    spec = getattr(p, "answer_figure", None)
    if not spec:
        return ""
    from .ex_fig import tikz
    return tikz(spec)


def problems_tex(problems, per_page=4):
    out = []
    for k, p in enumerate(problems, 1):
        out.append(rf"\item {md_to_tex(p.statement)}" + "\n\n" + _fig(p) + choices_tex(p.choices) + "\n\\vfill")
        if k % per_page == 0 and k < len(problems):
            out.append(r"\clearpage")
    return displaystyle_fracs("% 問題(本体から \\input する)\n" + "\n\n".join(out) + "\n")


def answers_tex(problems, per_page=2):
    out = []
    for k, p in enumerate(problems, 1):
        j = [c.correct for c in p.choices].index(True)
        sol = "\n\n".join("    " + md_to_tex(s) for s in p.solution)
        afig = _afig(p)
        if afig:
            sol = ("    \\begin{minipage}[t]{0.56\\linewidth}\\vspace{0pt}\n" + sol + "\n    \\end{minipage}\\hfill\n"
                   "    \\begin{minipage}[t]{0.42\\linewidth}\\vspace{0pt}\\centering\n" + afig + "\n    \\end{minipage}")
        out.append(rf"\item {md_to_tex(p.statement)}" + "\n\n" + _fig(p) + choices_tex(p.choices) + "\n\n"
                   + "  \\begin{itembox}[l]{解答・解説}\n"
                   + rf"    \textbf{{答：{LABELS[j]}}}\ ${p.choices[j].tex}$\\" + "\n\n"
                   + sol + "\n" + "  \\end{itembox}\n\\vfill")
        if k % per_page == 0 and k < len(problems):
            out.append(r"\clearpage")
    return displaystyle_fracs("% 解答・解説(本体から \\input する)\n" + "\n\n".join(out) + "\n")


def latex_files(problems, title, seed):
    """{ファイル名: 内容}。本体の2ファイルは problems.tex / answers.tex を \\input する"""
    return {
        f"{SUBJECT}演習.tex": main_tex(title, seed, "problems.tex"),
        f"{SUBJECT}演習-Ans.tex": main_tex(title, seed, "answers.tex", answer=True),
        "problems.tex": problems_tex(problems),
        "answers.tex": answers_tex(problems),
    }


def zip_bytes(files):
    import io
    import zipfile
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, text in files.items():
            z.writestr(name, text)
    return buf.getvalue()


def latex_zip(problems, title, seed):
    return zip_bytes(latex_files(problems, title, seed))


# ------------------------------------------------------------
# 学生用 PDF(問題 → 解答・解説 の順に1つの PDF)
# サーバーに uplatex と dvipdfmx が必要(Streamlit Community Cloud では packages.txt で入れる)
# ------------------------------------------------------------
STUDENT_PREAMBLE = r"""\documentclass[a4paper,11pt,dvipdfmx,fleqn,uplatex]{jsarticle}
\def\labelenumi{\framebox[0.8cm]{\bf\theenumi}}
\def\theenumii{\arabic{enumii}}
\usepackage[margin=1.5cm]{geometry}
\usepackage{amsmath, amssymb}
\usepackage{ascmac}
\usepackage{tikz}
\pagestyle{empty}
"""


def student_tex(problems, title, seed):
    return (STUDENT_PREAMBLE
            + rf"\title{{{SUBJECT}　{title}　演習}}" + "\n"
            + rf"\author{{1年\hspace{{1.5cm}}科\hspace{{1.5cm}}番\ 氏名\hspace{{4cm}}}}" + "\n"
            + rf"\date{{セット番号 {seed}(同じ番号で Web の演習と同じ問題が出ます)}}" + "\n"
            + "\\begin{document}\n\\maketitle\n\\begin{enumerate}\n" + problems_tex(problems)
            + "\\end{enumerate}\n\\clearpage\n\\begin{center}{\\Large 解答・解説}\\end{center}\n"
            + "\\begin{enumerate}\n" + answers_tex(problems) + "\\end{enumerate}\n\\end{document}\n")


def latex_available():
    import shutil
    return shutil.which("uplatex") is not None and shutil.which("dvipdfmx") is not None


def _compile_pdf(tex):
    """uplatex → dvipdfmx。(PDF のバイト列, エラーの抜粋) を返す"""
    import os
    import subprocess
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        with open(os.path.join(d, "main.tex"), "w", encoding="utf-8") as f:
            f.write(tex)
        try:
            r = subprocess.run(["uplatex", "-interaction=nonstopmode", "-halt-on-error", "-kanji=utf8", "main.tex"],
                               cwd=d, capture_output=True, text=True, timeout=90)
            if r.returncode != 0:
                return None, "\n".join(l for l in r.stdout.splitlines() if l.startswith("!") or "l." in l)[-1500:]
            r = subprocess.run(["dvipdfmx", "-q", "main.dvi"], cwd=d, capture_output=True, text=True, timeout=90)
            path = os.path.join(d, "main.pdf")
            if r.returncode != 0 or not os.path.exists(path):
                return None, (r.stderr or r.stdout)[-1500:]
            with open(path, "rb") as f:
                return f.read(), ""
        except Exception as e:  # タイムアウトなど
            return None, str(e)


def compile_pdf(tex):
    st = _st()
    return st.cache_data(show_spinner=False, max_entries=200)(_compile_pdf)(tex)


def student_html(problems, title, seed):
    """LaTeX が使えないとき用:ブラウザで開いて印刷(PDF に保存)できるページ(数式は KaTeX)"""
    import html as H

    def para(s):
        return "".join(f"<p>{H.escape(x)}</p>" for x in s.split("\n\n") if x.strip())

    body = []
    for i, p in enumerate(problems, 1):
        ch = "".join(f'<span class="ch">{lab} ${H.escape(c.tex)}$</span>' for lab, c in zip(LABELS, p.choices))
        fig = '<p class="note">(この問題には図があります。Web の演習画面で確認してください)</p>' if p.figure else ""
        body.append(f'<div class="q"><b class="n">{i}</b>{para(p.statement)}{fig}<div class="chs">{ch}</div>'
                    f'<div class="space"></div></div>')
    ans = []
    for i, p in enumerate(problems, 1):
        j = [c.correct for c in p.choices].index(True)
        ans.append(f'<div class="a"><b class="n">{i}</b><p><b>答:{LABELS[j]} ${H.escape(p.choices[j].tex)}$</b></p>'
                   + "".join(para(s) for s in p.solution) + "</div>")
    return f"""<!doctype html><html lang="ja"><head><meta charset="utf-8"><title>{SUBJECT} {H.escape(title)} 演習 {seed}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"
 onload="renderMathInElement(document.body,{{delimiters:[{{left:'$$',right:'$$',display:true}},{{left:'$',right:'$',display:false}}]}})"></script>
<style>body{{font-family:serif;max-width:46em;margin:2em auto;line-height:1.7}} .n{{border:1px solid #000;padding:0 .6em;margin-right:.6em}}
.chs{{display:flex;flex-wrap:wrap;gap:.5em 2.5em;margin:.6em 0}} .space{{height:9em}} .note{{color:#666;font-size:.9em}}
.q,.a{{break-inside:avoid;margin-bottom:1.2em}} .answers{{break-before:page}} @media print{{.noprint{{display:none}}}}</style></head><body>
<p class="noprint">ブラウザの「印刷」から「PDF に保存」を選ぶと PDF になります。</p>
<h2>{SUBJECT} {H.escape(title)} 演習</h2><p>セット番号 {seed}　　1年　　科　　番　氏名</p>
{''.join(body)}<div class="answers"><h2>解答・解説</h2>{''.join(ans)}</div></body></html>"""


def student_pdf_ui(problems, title, seed, ck):
    st = _st()
    if latex_available():
        key = f"{ck}_pdf_{seed}_" + str(abs(hash(tuple(p.statement for p in problems))) % 10 ** 8)
        if st.button("PDF を作る(問題 → 解答・解説)", key=f"{key}_make"):
            with st.spinner("PDF を作成中…"):
                st.session_state[key] = compile_pdf(student_tex(problems, title, seed))
        if key in st.session_state:
            pdf, err = st.session_state[key]
            if pdf:
                st.download_button("PDF をダウンロード", pdf, file_name=f"{SUBJECT}_{title.replace(' ', '_')}_演習_{seed}.pdf",
                                   mime="application/pdf", key=f"{key}_dl")
            else:
                st.error("PDF の作成に失敗しました。LaTeX 一式をダウンロードして手元でコンパイルしてください。")
                st.code(err)
        st.caption("印刷して解き、最後のページの解答・解説で答え合わせができます。")
    else:
        st.download_button("印刷用ページをダウンロード(.html)", student_html(problems, title, seed),
                           file_name=f"{SUBJECT}_{title.replace(' ', '_')}_演習_{seed}.html", mime="text/html",
                           key=f"{ck}_html")
        st.caption("このサーバーでは PDF を作れないため、印刷用ページを出しています。"
                   "ブラウザで開いて「印刷」→「PDF に保存」で PDF になります(図は Web 画面で確認)。")
