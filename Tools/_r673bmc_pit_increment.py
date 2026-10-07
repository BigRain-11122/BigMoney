# -*- coding: utf-8 -*-
"""r673 bm-c pit-tooling.md direct-write increment + receipt.

Main-file margin law: CODELY.md 30,398B, hard line 30,720B, margin 322B <
entry size -> direct-to-domain-file per r672 increment precedent (same
window form). Append-only, byte-level, rerun guard count==0, post-verify
count==1, EOL mirroring r503 v2 law."""
import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIT = os.path.join(ROOT, "research", "pit-tooling.md")
RECEIPT = os.path.join(ROOT, "results", "_r673bmc_pit_tooling_increment.json")

ENTRY = (
 "- [2026-10-07 11:5x r673 bm-c] **机器自适应脚本的机感模块常量泄漏进 hermetic selftest fixture 坑（open_market_readiness r673 扩展实弹·当场治愈）**："
 "模块级 MACHINE=fleet/machine.json 机感探测落地后，fixture 若仍从机感派生的模块常量（LOCAL_PANELS）建面板集=selftest 测试面随宿主机漂移"
 "（bm-c 跑腿时 bm-a 十面板全缺→L4/L5b 假红两连）——正法三件套：①face 函数一律 machine 参数化（默认=机感值·显式传参覆盖）；"
 "②fixture 建集合钉死显式 lane 元组（PANEL_LANES[\"bm-a\"]）勿引机感模块常量；③新腿用显式 machine= 覆盖测未知机"
 "（bm-z 无假红+lane_map_missing 诚实旗）+bm-a 标题无后缀字节保持腿。"
 "How to apply：共享脚本做 machine-adaptive 扩展（S0-1 锚律消费）时三件套同窗落地；见「面板明明全建仍报缺件」假红先查 fixture 是否引用机感常量。"
)

pre = open(PIT, "rb").read()
pre_size = len(pre)
needle = "机感模块常量泄漏进 hermetic selftest fixture 坑".encode("utf-8")
assert pre.count(needle) == 0, "rerun guard"
eol = b"\r\n" if pre.count(b"\r\n") >= 10 else b"\n"
assert pre.endswith(eol), "tail EOL gate"
block = eol + ENTRY.encode("utf-8") + eol   # blank-line separator form
new = pre + block
open(PIT, "wb").write(new)
post = open(PIT, "rb").read()
assert post.count(needle) == 1, "post-verify count==1"
entry_bytes = len(ENTRY.encode("utf-8"))
sha16 = hashlib.sha256(ENTRY.encode("utf-8")).hexdigest()[:16]
receipt = {
    "event": "r673 bm-c pit direct-write increment (main-margin law)",
    "main_note": "CODELY.md 30,398B, hard line 30,720B, margin 322B < entry size -> direct-to-domain per r672 precedent",
    "pit_file": "research/pit-tooling.md",
    "pre_size": pre_size,
    "post_size": len(post),
    "entry_bytes": entry_bytes,
    "entry_sha16": sha16,
    "append_only": True,
    "zero_loss_assert": "entry bytes verbatim in target, count==1",
    "needle": needle.decode("utf-8"),
}
with open(RECEIPT, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(receipt, fh, ensure_ascii=False, indent=1)
print("PIT increment: %d -> %dB (+%d entry) sha16=%s receipt=%s" % (
    pre_size, len(post), entry_bytes, sha16, RECEIPT))
