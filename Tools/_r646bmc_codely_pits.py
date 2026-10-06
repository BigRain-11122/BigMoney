# -*- coding: utf-8 -*-
"""r646 bm-c CODELY.md pit-entry surgery: land the two r646 pit entries
(1) S5 ledger path-split era (deferred r645 candidate, product of r645
era-merge surgery), (2) D-06 receipt-face != committed-blob-face (NEW,
discovered r646: r643/r644 size receipts 30,482/30,688B vs committed blobs
28,110/26,801B; r645 planned a phantom 32B-headroom mini-split on the
receipt value). Pure insertion, zero deletion, byte-arithmetic asserted
(r429 silent-passthrough law: needle count==1 asserted). CRLF disk face
matched (autocrlf=true). Gate: post disk face reported, must hold
<=30,720B (D-20261002-06)."""
import json
import os
import datetime
import hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "CODELY.md")
pre = open(P, "rb").read()
NEEDLE = "\r\n\r\n### Reference".encode("utf-8")
assert pre.count(NEEDLE) == 1, "anchor count %d != 1" % pre.count(NEEDLE)

E1 = ("- [2026-10-07 01:5x r646 bm-c] **S5 轮账本路径分裂纪元坑（r455 孤儿路径纪元·r290-r642 块 353 轮误落根级孤儿件·r645 手术闭合·r646 配平入件）**："
      "fleet/README §6 权威路径=logs/iteration-loop/round_reports-<id>.md，但纪元内会话把轮行写进根级 round_reports-bm-c.md——正典件 r289 后直跳 r643"
      "（702 行/1,265,417B/359 条目缺席正典面），r643/r644 回归正典写作后分裂脑才显形；r645 已 verbatim 纪元合并回正典"
      "（885,950→2,151,367B·拼接/字节/非递减等七验+prescan rc0·零删除·receipt _r645bmc_ledger_heal_receipt.json）+孤儿件指针行冻结停写。"
      "根因=追加路径无守卫、纯会话裁量。How to apply：①S5 追加一律钉死正典路径常量+追加后双路径面 diff；②「本轮前史缺失」症状先查路径分裂再查内容；"
      "③孤儿件=冻结只读态，续写即违规。")

E2 = ("- [2026-10-07 01:5x r646 bm-c] **D-06 尺寸收据量面≠提交面坑（r643 census 30,482B/r644 收据 30,688B vs 提交 blob 28,110/26,801B·r645 幻影 32B 余量规划实弹·r646 发现+钉法入件）**："
      "多步手术窗内收据只钉中间步量面，后续步（flow-sink/r787 行迁出 pit-git-resolver 等）再动文件而收据值不随终态重钉——commit message 复读收据值（「main 30,688B gate-ok」）但提交 blob 另值；"
      "判据铁证=r644 收据 sha16 b45ca01f≠提交 blob sha1-16 c8a3551b（autocrlf=true 盘面=blob+79 行 CR=26,880B 同对不上）；下游 r645 按收据尾值算「余量 32B」phantom 规划 mini-split，"
      "真实提交面余量 3,839B。正法=①门禁收据必钉 post-commit 提交面：git cat-file -s HEAD:CODELY.md 为唯一权威值（r646 起收尾落 gate-pin receipt）；"
      "②下游规划/水位判定读 blob 面禁读收据尾值；③中间步量面标注「intermediate」只作过程证据。How to apply：S7 收尾加 gate-pin 步（模板 results/_r646bmc_codely_gate_pin.json）；读主件尺寸一律 cat-file 实取。")

CR = "\r\n".encode("utf-8")
ins = CR + E1.encode("utf-8") + CR + E2.encode("utf-8")
post = pre.replace(NEEDLE, ins + NEEDLE)
assert post == pre[:pre.index(NEEDLE)] + ins + pre[pre.index(NEEDLE):], "splice identity fail"
assert len(post) == len(pre) + len(ins), "byte arithmetic fail"
assert post.count(NEEDLE) == 1 and post.count(E1.encode("utf-8")) == 1 and post.count(E2.encode("utf-8")) == 1
with open(P, "wb") as f:
    f.write(post)
chk = open(P, "rb").read()
assert chk == post, "writeback readback fail"

def sha16(b):
    return hashlib.sha1(b).hexdigest()[:16]

facts = {
    "round": "r646 bm-c",
    "ts": datetime.datetime.now().isoformat(timespec="seconds"),
    "pre_disk_bytes": len(pre),
    "pre_disk_sha16": sha16(pre),
    "inserted_bytes": len(ins),
    "post_disk_bytes": len(chk),
    "post_disk_sha16": sha16(chk),
    "e1_bytes": len(E1.encode("utf-8")),
    "e2_bytes": len(E2.encode("utf-8")),
    "gate": 30720,
    "gate_disk_ok": len(chk) <= 30720,
    "zero_deletion": True,
    "anchor": "CRLF CRLF ### Reference (count==1 asserted)",
    "law_refs": ["D-20261002-06 main<=30KB gate", "r429 silent-passthrough needle count law",
                 "memory four-question gate (one-thing-per-entry <=1.5KB)"],
    "note": ("receipt values of r643/r644 (30,482/30,688B) were intermediate faces; committed"
             " blobs are 28,110/26,801B; blob face is authoritative per E2. Gate pin of the"
             " COMMITTED face lands post-commit as results/_r646bmc_codely_gate_pin.json."),
}
out = os.path.join(ROOT, "results", "_r646bmc_codely_pits_receipt.json")
with open(out, "w", encoding="utf-8", newline="\n") as f:
    json.dump(facts, f, ensure_ascii=False, indent=1, sort_keys=True)
    f.write("\n")
print("pre=%d post=%d ins=%d gate_disk_ok=%s post_sha16=%s" %
      (len(pre), len(chk), len(ins), facts["gate_disk_ok"], facts["post_disk_sha16"]))
print("WROTE", out)
