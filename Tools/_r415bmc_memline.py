# -*- coding: utf-8 -*-
"""r415 bm-c S4 pit capture: append ONE hot-layer line to CODELY.md via python
(r407 law: CJK file edits never through CLI replace tool), mojibake-gated."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODELY = os.path.join(ROOT, "CODELY.md")
LINE = (
    "- [2026-10-03 13:0x r415 bm-c] HANDOVER 5x 行插入唯一性断言须机号限定（本窗两次实弹·当场自愈零外泄）："
    "断言 b\"round 415 not in body\" 被 bm-a/bm-b 各自机号命名空间的历史同名行（2026-09-29 bm-b round 415/bm-a round 415 "
    "五倍数核对行——三机轮号独立计数）误中=幂等门自拒合法插入；正法=锚改机限定 b\"bm-c round 415\"（HANDOVER 5x 行首前缀即机号面）"
    "+插入器对首行/BOM 有无/CRLF-vs-LF 三态自适应（r407 落盘通道律同窗再证：CJK 台账手术一律 python 通道禁 CLI replace）。"
    "How to apply：一切按轮号做唯一性/幂等断言的共享台账工具（5x 行插入器/轮报告去重/心跳 round_no 门）锚一律带 machine_id 限定禁裸轮号"
    "——三机轮号=三个独立命名空间；close 脚本逐窗改锚时改的是「机号+轮号」整串。\r\n"
)


def main():
    raw = open(CODELY, "rb").read()
    assert raw.count(b"\r\n") >= 10 and b"\n" not in raw.replace(b"\r\n", b""), "face"
    assert b"r415 bm-c] HANDOVER 5x" not in raw, "already appended"
    if not raw.endswith(b"\r\n"):
        raw += b"\r\n"
    out = raw + LINE.encode("utf-8")
    t = out.decode("utf-8")                      # strict utf-8 gate
    assert t.count("????") == 0, "mojibake gate"
    tmp = CODELY + ".tmp_r415"
    with open(tmp, "wb") as fh:
        fh.write(out)
    os.replace(tmp, CODELY)
    print("MEMLINE PASS: CODELY.md %dB (append r415 pit line)" % len(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
