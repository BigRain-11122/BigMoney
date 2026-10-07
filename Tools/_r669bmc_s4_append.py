# -*- coding: utf-8 -*-
"""r669 bm-c S4: append new pit entry to main CODELY.md tail (gated).
Law: 新坑律先入主件后回扫; cap 30,720B; CRLF face preserved; needle
uniqueness + size equation + cap gates fail-closed before write."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(ROOT, "CODELY.md")
CAP = 30720
NEEDLE = "[2026-10-07 10:4x r669 bm-c]"

NEW_LINE = (
    "- [2026-10-07 10:4x r669 bm-c] **拆件脚本列表构成错误=逐行锚点门盲区·构造式×方程式双 derive 恒等门才抓得住（r441 电池实弹）**："
    "r669 resolver split survivors 误含 3 行头块=新母件头块重复——19 条 stay 锚点门全过（重复≠丢失=盲区）·唯一拦截=字节方程门"
    "（构造 len vs 方程 derive 差 6B·fail-closed 零写出）；连带=str/bytes 混型 join 崩+硬门手算 off-by-one（移除=len(line 含CR)+1〔LF 分隔符〕=995 非 994）。"
    "正法=拆件脚本断言电池必配「构造=方程」双路独立 derive 恒等门（逐行锚点门抓不住头块重复/漏行/错序）+硬门尺寸当场 len() derive 禁手算；修后复跑+--verify 55 checks。"
    "How to apply：r441/r669 系拆件/迁移模板电池必含此门。"
)


def main():
    raw = open(MAIN, "rb").read()
    before = len(raw)
    assert before == 29724, "main size gate: %d" % before
    assert raw.endswith(b"\n"), "trailing newline gate"
    assert raw.count(NEEDLE.encode("utf-8")) == 0, "needle already present (rerun?)"
    line = NEW_LINE.encode("utf-8") + b"\r"
    after = before + len(line) + 1
    assert after <= CAP, "cap gate: %d > %d" % (after, CAP)
    body = raw.split(b"\n")
    assert body[-1] == b"", "trailing element gate"
    new_raw = b"\n".join(body[:-1] + [line]) + b"\n"
    assert len(new_raw) == after, "size equation gate"
    n_cr, n_crlf, n_lf = new_raw.count(b"\r"), new_raw.count(b"\r\n"), new_raw.count(b"\n")
    assert n_cr == n_crlf == n_lf, "CRLF triple-count gate"
    new_raw.decode("utf-8")
    assert new_raw.count(NEEDLE.encode("utf-8")) == 1, "presence gate"
    with open(MAIN, "wb") as fh:
        fh.write(new_raw)
    print("S4 APPEND OK main %d->%d (line %dB incl CR, headroom %dB)"
          % (before, after, len(line), CAP - after))
    return 0


if __name__ == "__main__":
    sys.exit(main())
