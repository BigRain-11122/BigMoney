# -*- coding: utf-8 -*-
"""r682 bm-c S4 pit direct-write: r681 close-narrative predicted-as-realized
misreport pit (CA flags face). Main CODELY.md at 30,705B = 15B under the
30,720B hard line -> red-line-margin direct-write convention (r666/r672
precedent): write the pit verbatim into the domain file (pit-lineage.md =
close/bookkeeping-script family) + byte-accounting receipt. Pure append,
zero deletion -> treasure_guard prescan not applicable (no removal face)."""
import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = os.path.join(ROOT, "research", "pit-lineage.md")
RECEIPT = os.path.join(ROOT, "results", "_r682bmc_pit_directwrite.json")

ENTRY = (
    "- [2026-10-07 15:0x r682 bm-c] **\u6536\u53e3\u53d9\u8ff0\u628a\u300c\u9884\u6d4b\u300d\u5f53\u300c\u5df2\u5151\u73b0\u300d\u8bef\u62a5\u5751"
    "\uff08r681 CA \u65d7\u7a7a\u8bef\u62a5\u5b9e\u5f39\u00b7\u53d9\u8ff0\u9762 vs \u81ea\u5bb6\u6301\u4e45\u5316\u65e5\u5fd7\u77db\u76fe\u00b7r682 \u4ea4\u53c9\u6838\u5f53\u8f6e\u52d8\u6b63\uff09**\uff1a"
    "r681 \u6536\u53e3\u53d9\u8ff0/RR/state \u4e09\u9762\u5199\u300cCA \u65d7=\u7a7a\uff08supply_gap/supply_floor \u81ea\u7136\u6e05\u00b7r678 \u9884\u6d4b\u5151\u73b0\uff09\u300d\uff0c"
    "\u4f46\u5176\u540c\u8f6e\u6301\u4e45\u5316\u8bc1\u636e results/_r681bmc_s6_log.txt\uff0814:30:35 compute_audit\uff09flags=[supply_gap,supply_floor] "
    "\u5728\u573a\uff1br682 \u590d\u8dd1 14:47:30 \u540c\u65d7\u5728\u573a=\u590d\u8bc1\u4f2a\u3002\u771f\u5b9e\u673a\u7406=W175 freezer\uff08bm-a \u8f66\u9053\uff09\u672a\u8dd1"
    "+\u6c60 1 live \u5df2\u4ed6\u673a\u6301\uff08FUND-DIVLOWVOL-P1-NULLS owner=bm-b\uff09\u2192supply \u5e95\u7ebf\u5728 O-2115 \u00a72 N1 "
    "\u6536\u53e3\u7a97\u5185\u672c\u5c31\u6301\u7eed\u5728\u573a\u81f3\u4e0b\u4e00 freezer \u8865\u6c60\uff0c\u975e finalize \u5373\u6e05\u3002"
    "\u6b63\u6cd5=\u6536\u53e3/RR \u53d9\u8ff0\u4e2d\u4e00\u5207\u300c\u9884\u6d4b\u5151\u73b0/\u81ea\u7136\u6e05\u300d\u7c7b\u65ad\u8a00=\u5148\u5bf9\u672c\u8f6e\u6301\u4e45\u5316\u65e5\u5fd7\u5b9e\u6d4b\u590d\u8ff0"
    "\uff08r583 facts-driven \u5f8b\u7684\u53d9\u8ff0\u9762\u5ef6\u91ca\uff09\uff1b\u53d9\u8ff0\u4e0e\u81ea\u5bb6\u65e5\u5fd7\u77db\u76fe=\u4ee5\u65e5\u5fd7\u4e3a\u51c6\u5f53\u8f6e\u52d8\u8bef\u7559\u75d5\u3002"
    "How to apply\uff1a\u590d\u5236 close \u8840\u7edf\u7ec4\u7a3f\u51e1\u5f15\u7528 rN \u9884\u6d4b\u884c\u5fc5\u9644\u672c\u8f6e\u5b9e\u6d4b\u884c\uff1b"
    "\u89c1\u300c\u81ea\u7136\u6e05/\u5982\u671f\u5151\u73b0\u300d\u7c7b\u8bcd\u5148 grep \u672c\u8f6e S6 \u65e5\u5fd7 flags \u9762\u3002| dept:\u5de5\u7a0b\n"
)

with open(TARGET, "rb") as fh:
    raw = fh.read()
crlf = raw.count(b"\r\n")
lf_only = raw.count(b"\n") - crlf
eol = b"\r\n" if crlf >= lf_only else b"\n"
pre_size = len(raw)
assert ENTRY.encode("utf-8") not in raw, "entry already present"
block = ENTRY.encode("utf-8").replace(b"\n", eol)
assert raw.endswith(eol) or not raw, "tail EOL guard"
with open(TARGET, "ab") as fh:
    fh.write(block)
with open(TARGET, "rb") as fh:
    post = fh.read()
receipt = {
    "round": 682,
    "machine": "bm-c",
    "action": "pit direct-write (main CODELY 30,705B = 15B under 30,720B hard line; r666/r672 red-line-margin convention)",
    "target": "research/pit-lineage.md",
    "entry_bytes": len(block),
    "entry_sha16": hashlib.sha256(block).hexdigest()[:16],
    "bytes_in_target_verbatim": block in post,
    "pre_size": pre_size,
    "post_size": len(post),
    "size_identity": len(post) == pre_size + len(block),
    "eol_used": eol.decode(),
    "pit": "r681 close-narrative predicted-as-realized misreport (CA flags face)",
}
assert receipt["bytes_in_target_verbatim"] and receipt["size_identity"]
with open(RECEIPT, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(receipt, fh, ensure_ascii=False, indent=1)
print("pit direct-write ok:", json.dumps({k: receipt[k] for k in ("entry_bytes", "entry_sha16", "pre_size", "post_size", "eol_used")}))
