# -*- coding: utf-8 -*-
"""r763 bm-c race-window addendum: append one 补记 line to the CANONICAL round
report face documenting the post-close push race + r747-canon merge two-piece
resolution (process-visibility law P-2026-09-29-07; race disclosed in git
history + receipts, this line carries it to the CEO-visible face). Binary
EOL-matched append + write-then-grep self-verify (r865 law)."""
import datetime

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
RPT = ROOT + r"\logs\iteration-loop\round_reports-bm-c.md"
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

LINE = (
    NOW + " | r763 补记 | dept:工程 | "
    "push 竞窗实录：主 commit 1c1a89099 推送撞 bm-a r880 closeout（W186 buildgen facts+5x HANDOVER 回填+"
    "S6 41 腿再生）同窗竞速（non-FF 拒收）→churn absorb 5253d7318 前置（r642 净树律）→"
    "pull --rebase 停于 round commit pick 14 UU 共享 S6 再生面（r742/r762 同族同构）→"
    "按 r747 正典弃 rebase 转 merge ORT 两件套（_r763bmc_merge_clone/resolve/finish·stale747=0×2·"
    "compile OK×2·resolver 已中止前置容错小改〔本窗 abort 已手动先行·rc128 no-rebase-in-progress 仅在 "
    "main 分支无 MERGE_HEAD 时放行·r753 适配先例收据留痕〕·"
    "逐面 embedded-ts newer-wins〔deep-ts r738·tie→theirs r440〕+五门"
    "〔G1 UU 清零/G2 splice 零命中/G3 零标记/G4 origin-exclusive 52 面/G5 JSON 全过〕·"
    "G4 假红 2 面=daemon-live 族〔daily_scorecard/dashboard_status·CRLF 比对假阳性 r417 族〕→"
    "finisher G4' live-wins 采纳〔三 live face disk ts≥origin ts 全过〕）→"
    "merge commit 100a9df26+push DELIVERED（ahead=0 behind=0）→"
    "closeout absorb d9c0c3941（两件套+双收据+mergemsg+satengine daemon tick·"
    "add -A 无条件吸收正法 r751 律·untrackedCache 陈旧窗 r549 族如实注记）| "
    "收据 results/_r763bmc_merge_gates.json+results/_r763bmc_merge_clone.json | "
    "[via bm-c r763]")

raw = open(RPT, "rb").read()
eol = b"\r\n" if b"\r\n" in raw[-200:] else b"\n"
if not raw.endswith(eol):
    with open(RPT, "wb") as fh:
        fh.write(raw + eol)
with open(RPT, "ab") as fh:
    fh.write(LINE.encode("utf-8") + eol)
back = open(RPT, "rb").read()
assert back.count("r763 补记".encode("utf-8")) == 1, "addendum not exactly-once"
assert "r763 补记".encode("utf-8") in back.split(eol)[-2] + back.split(eol)[-3], "addendum not in tail"
print("addendum ok:", NOW, "tail rows verified")
