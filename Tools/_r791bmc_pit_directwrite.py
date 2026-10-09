# -*- coding: utf-8 -*-
"""r791 bm-c S4: direct-write one new pit entry (RAM-gate bounded-wait vs
orphan-probe three-face, W17 SCREEN-SHARD-0 live evidence) into
research/pit-pool-burn.md per r666 direct-write precedent (CODELY.md main at
77B margin). CJK append via script not CLI replace (r407 law). Atomic (r614).
Idempotent: aborts if anchor already present."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TGT = os.path.join(ROOT, "research", "pit-pool-burn.md")
CAP = 30720
ANCHOR = "- [2026-10-09 08:2x r791 bm-c]"
ENTRY = (
    "- [2026-10-09 08:2x r791 bm-c] **RAM 门有界等待池 runner 被孤儿探针三面命中=deadline 判别律"
    "（W17 SCREEN-SHARD-0 实弹·只读判正确零误杀）**：池 runner 卡在 _ram_gate_gb(wait_min=40) "
    "有界等待（free RAM 1.3GB<4GB 门下·睡眠轮询零写入）时孤儿三面全中——父死（detached spawn 族）"
    "+无活宿主祖先+CPU 停滞（20s 采样 0.0）→探针判孤儿；实况=等待帽 40min 到点自退 rc2 诚实拒收"
    "（pid 39968 07:47 点火→~08:27 自退·复跑探针 orphan_n 回落 1 实证·池面 entry 归 ready 由 autofill 复燃）。"
    "How to apply：孤儿探针命中池 runner 先核其有界等待帽（RAM 门 wait_min=40 族）——age<帽+点火 slop "
    "一律只读等待勿 --kill（杀=白弃已付出的等待+中断合法 rc2 退路）；超帽仍滞留才收编击杀；"
    "轮报告孤儿行对池 runner 须带「RAM 门等待·deadline=点火+40min」注记防下轮误判。"
)


def main() -> int:
    raw = open(TGT, "rb").read()
    txt = raw.decode("utf-8")
    assert ANCHOR not in txt, "entry already present (idempotent abort)"
    assert raw.endswith(b"\r\n"), "target must end with CRLF"
    body = ENTRY.encode("utf-8")
    assert len(raw) + len(body) + 2 <= CAP, "target over cap after append"
    tmp = TGT + ".tmp_r791dw"
    with open(tmp, "wb") as fh:
        fh.write(raw + body + b"\r\n")
    os.replace(tmp, TGT)
    new = open(TGT, "rb").read()
    assert len(new) == len(raw) + len(body) + 2
    assert new.decode("utf-8").count(ANCHOR) == 1
    print("DIRECT-WRITE PASS: pit-pool-burn %dB -> %dB (+%dB entry)"
          % (len(raw), len(new), len(body) + 2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
