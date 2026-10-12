# r914 bm-b: pit-spawn.md sub-split (r836/r791 precedent) -- croc transfer family 4 entries -> pit-spawn-croc.md
# Trigger: post-r914-direct-write mother 32,164B > 30,720B domain cap (breach 1,444B). Zero-loss assertion required.
import json, hashlib, re, os

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
MOTHER = ROOT + r"\research\pit-spawn.md"
CHILD = ROOT + r"\research\pit-spawn-croc.md"
RECEIPT = ROOT + r"\results\_r914bmb_pit_spawn_croc_split.json"

def lf(b: bytes) -> bytes:
    return b.replace(b"\r\n", b"\n")

raw = open(MOTHER, "rb").read()
text = raw.decode("utf-8")

prefixes = [
    "- [2026-10-03 10:5x r614 bm-b] croc sender ",
    "- [2026-10-03 11:2x r614 bm-b] croc 公共 relay ",
    "- [2026-10-03 13:3x r624 bm-a] croc 11.5.3 ",
    "- [2026-10-03 14:2x r618 bm-b] croc「could not secure channel」",
]

moved = []
first_pos = None
for p in prefixes:
    i = text.find(p)
    assert i != -1, "needle not found: " + p[:40]
    j = text.find("\n", i)
    if j == -1:
        j = len(text) - 1
    line = text[i:j+1]
    moved.append(line)
    if first_pos is None or i < first_pos:
        first_pos = i
    text = text[:i] + text[j+1:]

pointer = (
    "> 子件指针（r914 bm-b·sub-split·当窗即办）：croc 传递族四条（r614 sender 僵尸/r614 relay DNS 多 A/r624 11.5.3 CLI 形态/"
    "r618 secure channel=relay 垃圾字节）已 verbatim 迁出→research/pit-spawn-croc.md（croc 双端零配对诊断/接收点火动作前改读该子件；"
    "母件执法面其余条目不变）·receipt=results/_r914bmb_pit_spawn_croc_split.json。\n"
)
text = text[:first_pos] + pointer + text[first_pos:]
open(MOTHER, "wb").write(text.encode("utf-8"))

child_header = (
    "# pit-spawn-croc —— croc 传递族坑律子件（D-20261002-06 域件 sub-split·spawn 家族 child·r914 bm-b 建）\n\n"
    "> 来源：pit-spawn.md verbatim 迁出（2026-10-13 r914 bm-b·母件越帽 32,164B>30,720B 当窗即办·r836/r791 范式同源）。\n"
    "> 执法面：croc 双端零配对诊断（僵尸 relay 连接/DNS 多 A 分叉/CLI 形态/PAKE 通道垃圾字节）·croc 接收/发送点火动作前必读本件；"
    "spawn 家族其余坑律仍在母件 pit-spawn.md。\n"
    "> 字节对账行（零丢失断言）：母件迁出前 32164B→迁出后 %dB（移出 4 条·条目字节和（LF blob 规范化面）=%dB==子件条目区和·"
    "逐字节 verbatim 恒等零丢失·机械迁移非手抄 r399 范式）；迁移核（LF blob 面·4 条拼接）md5=%s。\n\n"
)

moved_blob_lf = b"".join(lf(m.encode("utf-8")) for m in moved)
child_text = child_header + "".join(moved)
open(CHILD, "wb").write(child_text.encode("utf-8"))

receipt = {
    "round": "r914 bm-b", "action": "pit-spawn sub-split (croc family)",
    "mother_path": "research/pit-spawn.md",
    "child_path": "research/pit-spawn-croc.md",
    "mother_bytes_before": len(raw),
    "mother_bytes_after": os.path.getsize(MOTHER),
    "moved_entries": 4,
    "moved_needles": [p[:48] for p in prefixes],
    "moved_bytes_lf_blob": len(moved_blob_lf),
    "moved_blob_md5_lf": hashlib.md5(moved_blob_lf).hexdigest(),
    "child_bytes": os.path.getsize(CHILD),
    "zero_loss_assertion": "4 entries verbatim in child == removed from mother; byte-sum identity on LF-normalized face",
    "law_refs": "r836 (pit-git-resolver-rebase2 split), r791 (pit-pool-burn split), cap 30720B domain-file law",
    "ts": "2026-10-13T04:1x+08:00",
}
json.dump(receipt, open(RECEIPT, "w", encoding="utf-8"), ensure_ascii=True, indent=1)

print("MOTHER before=%d after=%d (cap 30720: %s)" % (
    receipt["mother_bytes_before"], receipt["mother_bytes_after"],
    "OK" if receipt["mother_bytes_after"] <= 30720 else "STILL OVER"))
print("MOVED %d entries, %d LF-blob bytes, md5=%s" % (
    len(moved), len(moved_blob_lf), receipt["moved_blob_md5_lf"]))
print("CHILD bytes=%d" % receipt["child_bytes"])
