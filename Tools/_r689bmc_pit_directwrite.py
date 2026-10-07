# -*- coding: utf-8 -*-
"""r689 bm-c pit direct-write append: churn-absorb -F message-file stale
reuse pit (r620 kin, message-content face) -> research/pit-git-staged.md
(commit entry-gate family; racewin home 822B margin too tight per domain
<=30KB law). Receipt results/_r689bmc_pit_directwrite.json.
Pattern credit: r685/r673 direct-write receipts."""
import datetime
import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = os.path.join(ROOT, "research", "pit-git-staged.md")
ENTRY = (
 "- [2026-10-07 16:4x r689 bm-c] **churn-absorb -F 消息件陈旧复用坑（r620 姊妹面"
 "·消息内容级非轮号级·当场 amend 零 origin 伤害）**：S0 脏窗处置序=写消息件→"
 "commit -F 消费→checkout -- 还原消息件（消息已消费零损失）→同窗第二段 daemon "
 "churn absorb 再 commit -F 时未重写件=捡回 HEAD 陈旧内容（实弹：吸收提交误标 "
 "r680 旧轮整句消息·log --oneline 自检当场抓回→amend 916887832 正名→零误标达 "
 "origin）。正法=**-F 消息件每次 commit 前必重写**（工作树现存内容一律视为陈旧"
 "·r620 轮号前置读律的消息件扩展面）；多段提交窗=每段「写-提-log 验」三步序。"
 "How to apply：absorb/收口多段提交后必 log --oneline -3 核对消息与提交内容一致"
 "；已推禁 amend（r620 律）。\r\n"
)

raw = open(TARGET, "rb").read()
assert raw.endswith(b"\r\n"), "tail EOL gate"
guard = "r689 bm-c] **churn-absorb -F".encode("utf-8")
assert raw.count(guard) == 0, "rerun guard"
new = raw + ENTRY.encode("utf-8")
open(TARGET, "wb").write(new)
post = open(TARGET, "rb").read()
assert post.count(guard) == 1, "post-verify count==1"
assert post[: len(raw)] == raw, "prefix invariance"

receipt = {
    "round": 689,
    "machine": "bm-c",
    "action": "pit direct-write append",
    "target": "research/pit-git-staged.md",
    "entry_bytes": len(ENTRY.encode("utf-8")),
    "entry_md5": hashlib.md5(ENTRY.encode("utf-8")).hexdigest(),
    "size_after": len(post),
    "law_refs": ["r620 churn-absorb commit round-label pre-read (racewin kin)",
                 "amend-before-push window"],
    "main_file_margin_note": "CODELY.md 30335B margin 385B -> direct-write to domain file per r672 pattern; racewin home 29898B margin 822B too tight -> staged (entry-gate family) chosen",
    "ts": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
}
rp = os.path.join(ROOT, "results", "_r689bmc_pit_directwrite.json")
with open(rp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(receipt, fh, ensure_ascii=False, indent=1)
print("pit entry appended:", len(post), "B; receipt ->", rp)
