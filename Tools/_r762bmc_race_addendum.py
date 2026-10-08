# -*- coding: utf-8 -*-
"""r762 bm-c race-window addendum: append one 补记 line to the CANONICAL round
report face documenting the post-close push race + r747-canon merge two-piece
resolution (process-visibility law P-2026-09-29-07; race disclosed in git
history + receipts, this line carries it to the CEO-visible face). Binary
EOL-matched append + write-then-grep self-verify (r865 law)."""
import datetime

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
RPT = ROOT + r"\logs\iteration-loop\round_reports-bm-c.md"
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

LINE = (
    NOW + " | r762 补记 | dept:工程 | "
    "push 竞窗实录：主 commit 5bfea52c3 推送撞 bm-a r878/r879 同窗竞速（non-FF 拒收）→"
    "pull --rebase 撞 12 UU 同窗 S6 再生面→按 r747 正典 abort+merge ORT 两件套"
    "（_r762bmc_merge_clone/resolve/finish·stale747=0×2·compile OK×2·"
    "逐面 embedded-ts newer-wins〔deep-ts r738·tie→theirs r440〕+五门全过"
    "〔G1 UU 清零/G2 splice 零命中/G3 零标记/G4 origin-exclusive 102 面/G5 JSON 全过〕·"
    "G4 假红 11 面=daemon-live+双跑 S6 再生族→finisher G4' live-wins 采纳）→"
    "merge commit 30252b00+push DELIVERED（ahead=0 behind=0）+"
    "closeout absorb c3bce5bed（两件套+收据+satengine daemon tick）| "
    "marks lane 观察项解除：bm-a r879 closeout 携 13:39 tick 落地（marks-20261008.jsonl 5→6 行·"
    "长轮假说实证·14:0x 红标升级阈值不再触发）| "
    "收据 results/_r762bmc_merge_gates.json+results/_r762bmc_merge_clone.json | "
    "[via bm-c r762]")

raw = open(RPT, "rb").read()
eol = b"\r\n" if b"\r\n" in raw[-200:] else b"\n"
if not raw.endswith(eol):
    with open(RPT, "wb") as fh:
        fh.write(raw + eol)
with open(RPT, "ab") as fh:
    fh.write(LINE.encode("utf-8") + eol)
back = open(RPT, "rb").read()
assert back.count("r762 补记".encode("utf-8")) == 1, "addendum not exactly-once"
assert "r762 补记".encode("utf-8") in back.split(eol)[-2] + back.split(eol)[-3], "addendum not in tail"
print("addendum ok:", NOW, "tail rows verified")
