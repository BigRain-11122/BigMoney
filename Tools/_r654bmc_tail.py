# -*- coding: utf-8 -*-
"""r654 bm-c close-tail addendum: record the close-window push-rebase surgery
(push rejected non-FF -> pull --rebase 14-face UU -> deep-ts newer-wins
= stage3 (r654 S6 04:41-42) beats stage2 (bm-a r808 S6 04:34-36) on ALL 14
S6-regenerable faces (dual probe receipts) -> first continue refused with
ls-files -u EMPTY = r613 daemon live-write variant (sat-engine MM double-face
staged + same-window continue succeeded) -> push delivered d92b1286b,
N=0 both directions. Appends one RR line + commits the resolution receipt
script. Zero new pits (all faces followed recorded laws: r794 newer-wins,
r613 continue variant, r787 atomic add+continue)."""
import json
import os
import time

now = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

RR = r"logs\iteration-loop\round_reports-bm-c.md"
row = ("{ts} | r654 bm-c close-tail | 推送窗手术补记：push 被拒 non-FF（bm-a r808 波先达）→净树 pull --rebase 停 pick-1 14 面 UU（全=S6 可再生共享面双跑撞面）→"
       "deep-ts 逐面双探针（stage2=bm-a r808 S6 04:34-36 vs stage3=bm-c r654 S6 04:41-42）=14/14 我方更新→newer-wins 全取 stage3（r794 律·逐面 checkout --theirs+JSON 重解析门+marker 零泄漏+定向 add 禁 add -u 循环）→"
       "首次 continue 拒发而 ls-files -u 空=r613 daemon 活写变体实锤（sat-engine 双面 MM=add 后再 tick）→按正法 staged 活写面+同窗 continue=成功（Successfully rebased·refs/heads/main 落位·symbolic-ref 验证）→"
       "push 送达 d92b1286b（e7bfd21c8..d92b1286b）+fetch 双向 rev-list 0/0=本地未达 origin commit 数 0 自证成立→REBASE_HEAD 残留已清。零新坑（全程按在册律执行：r794 newer-wins/r613 变体/r787 原子化/r653 哈希域核销）。"
       " | 证据=Tools/_r654bmc_rebase_resolve.py（14 面收口器）+git log d92b1286b（消息净·46 files）| 下轮指针：r655=5x HANDOVER 窗\n").format(ts=now)
with open(RR, "ab") as fh:
    fh.write(row.encode("utf-8") + b"\r\n")
print("RR close-tail appended")

# state note augmentation (measured-face law: keep claims true, add tail fact)
SP = r"state-bm-c.json"
st = json.load(open(SP, encoding="utf-8-sig"))
assert st["round_no"] == 655
st["note"] = (st["note"] + " Close-tail: push-rebase surgery (14 UU S6 faces newer-wins stage3, r613 daemon-variant continue, delivered d92b1286b N=0; REBASE_HEAD cleaned).")
json.dump(st, open(SP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("state note augmented")
