"""ブラウザ側で動くアニメーション（assets/*.html）をページに埋め込む。

アニメーションは生徒のブラウザの中で動く（JavaScript + canvas）ので、クラス全員が同時に再生しても
サーバーには負荷がかからない。パラメータはサイドバーの値を JSON にして渡す。

HTML の中の目印を置きかえる：
  /*__COMMON__*/  assets/anim_common.js（再生ボタン・キャンバス・グラフの共通部品）
  /*__PARAMS__*/  パラメータ（JSON）
"""

from __future__ import annotations

import json
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"


def build_html(name: str, params: dict) -> str:
    page = (ASSETS / f"{name}.html").read_text(encoding="utf-8")
    common = (ASSETS / "anim_common.js").read_text(encoding="utf-8")
    return page.replace("/*__COMMON__*/", common).replace("/*__PARAMS__*/", json.dumps(params, ensure_ascii=False))


def render(name: str, params: dict, height: int) -> None:
    import streamlit.components.v1 as components

    components.html(build_html(name, params), height=height, scrolling=True)
