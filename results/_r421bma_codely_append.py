# -*- coding: utf-8 -*-
"""_r421bma_codely_append.py -- one-shot: append r421 pit entry to root CODELY.md.

File-face write per r406bm-b file-face law (CJK never through PS command channel).
Idempotent: refuses if the r421 marker already present.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "CODELY.md"
MARKER = "[2026-09-29 09:4x r421 bm-a] 坑律（W7 TSTATE 探针实弹·九十五批）"

ENTRY = (
    "- [2026-09-29 09:4x r421 bm-a] 坑律（W7 TSTATE 探针实弹·九十五批）："
    "**pandas 门探针双伪影——①NaN 参与比较产 False 非 NaN**"
    "（`series < rolling_quantile` 型门在预热窗内=「False 但非可判」≠gate-closed NaN："
    "可判面必须从底层分位/threshold 序列 notna 派生·勿用门 bool 面）；"
    "**②bool dtype 序列 first_valid_index()==0 全真伪影**"
    "（False 是合法值非 NA→首真必须 values.argmax() 或布尔索引）。"
    "当窗自纠实录：decidable_days 3,305 与 first_decidable 0 互斥露馅→修正后 "
    "mad60 首可判 bar-178/rsv60 bar-59 如实。How to apply：一切 rolling 分位/阈值门探针"
    "（W8+ 新轴同族）必带「底层 notna 派生 decidable+argmax 取首真」双腿+prereg §6 "
    "selftest 伪影腿（W7 已接）。指针=results/_r421bma_tstate_probe.py+"
    "TRIAL_LABOR_W7_PREREG §2/§6。\n"
)


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")
    if MARKER in text:
        print("already-present: no-op")
        return 0
    if not text.endswith("\n"):
        text += "\n"
    text += ENTRY
    TARGET.write_text(text, encoding="utf-8")
    size = TARGET.stat().st_size
    print("appended; new size bytes=%d (hard-line 10240: %s)" % (size, "OK" if size <= 10240 else "OVER"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
