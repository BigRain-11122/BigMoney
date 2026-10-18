# r1013 bm-b CODELY.md hot-cold (10,560B > 10,240 hard line -> migrate 2 oldest
# content rows verbatim to research/memory-archive/202610.md, leave one pointer).
import json, os, io

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
CODELY = os.path.join(ROOT, "CODELY.md")
ARCHIVE = os.path.join(ROOT, "research", "memory-archive", "202610.md")
RECEIPT = os.path.join(ROOT, "results", "_r1013bmb_codely_hotcold_receipt.json")

PREFIXES = ("- [2026-10-18 11:4x r1005 bm-b]", "- [2026-10-18 16:4x r1008 bm-b]")
POINTER = ("- 冷层指针：PS Select -First 截停上游脚本坑（r1005）+ rebase-continue 幽灵拒绝死循环/stash-pop 索引毒化/"
           "per-machine 键面 union 三连坑（r1008）全文 verbatim=archive 202610.md『热冷整编 2026-10-19 r1013 bm-b 窗批』节。")

c_bytes = open(CODELY, "rb").read()
bom = c_bytes.startswith(b"\xef\xbb\xbf")
lines = c_bytes.decode("utf-8-sig").splitlines()

migrated = []
out = []
for ln in lines:
    hit = None
    for p in PREFIXES:
        if ln.startswith(p):
            hit = p
            break
    if hit:
        migrated.append(ln)
        if hit == PREFIXES[0]:
            out.append(POINTER)  # pointer takes the place of the first migrated row
    else:
        out.append(ln)

assert len(migrated) == 2, "expected exactly 2 rows, got %d" % len(migrated)
new_text = "\n".join(out) + ("\n" if c_bytes.decode("utf-8-sig").endswith("\n") else "")
new_bytes = (b"\xef\xbb\xbf" if bom else b"") + new_text.encode("utf-8")
assert len(new_bytes) <= 10240, "still over 10KB hard line: %d" % len(new_bytes)

a_bytes = open(ARCHIVE, "rb").read()
a_bom = a_bytes.startswith(b"\xef\xbb\xbf")
a_text = a_bytes.decode("utf-8-sig")
section = "\n\n## 『热冷整编 2026-10-19 r1013 bm-b 窗批』\n\n" + "\n".join(migrated) + "\n"
if not a_text.endswith("\n"):
    a_text += "\n"
a_text += section
open(ARCHIVE, "wb").write((b"\xef\xbb\xbf" if a_bom else b"") + a_text.encode("utf-8"))
open(CODELY, "wb").write(new_bytes)

receipt = {"round": "r1013", "machine": "bm-b", "migrated_rows": 2,
           "prefixes": list(PREFIXES), "codely_size_before": len(c_bytes),
           "codely_size_after": len(new_bytes), "archive_appended_bytes": len(section.encode('utf-8'))}
json.dump(receipt, open(RECEIPT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(receipt, ensure_ascii=False))
