import hashlib, json, os
os.chdir(r"K:\Fluxgroup\FluxGroup\quant\bigmoney")
main_p = "CODELY.md"
pit_p = "research/pit-ps.md"
raw = open(main_p, "rb").read()
lines = raw.split(b"\n")
prefix = b"- [2026-10-07 07:4x r662 bm-c]"
hits = [i for i, l in enumerate(lines) if l.startswith(prefix)]
assert len(hits) == 1, "r662 entry count != 1: %d" % len(hits)
i = hits[0]
entry = lines[i].rstrip(b"\r")
pointer = ("\xe5\x9f\x9f\xe6\x8c\x87\xe9\x92\x88\xc2\xb7r662 bm-c\xef\xbc\x882026-10-07 07:4x\xef\xbc\x89\xef\xbc\x9a\xe8\xbd\xae\xe5\x8f\xb7\xe8\x84\x9a\xe6\x9c\xac\xe5\x85\x8b\xe9\x9a\x86\xe8\xa3\xb8\xe6\x95\xb0\xe5\xad\x97\xe9\x80\x83\xe9\x80\xb8\xe5\x89\x8d\xe7\xbc\x80 replace \xe5\x9d\x91\xef\xbc\x88r758/r640/r644 \xe6\x97\x8f\xe6\x96\xb0\xe6\x9c\xba\xe6\xa2\xb0\xe9\x9d\xa2\xef\xbc\x89\xe2\x86\x92research/pit-ps.md\xef\xbc\xbb\xe8\xa3\xb8\xe6\x95\xb0\xe5\xad\x97 replace+\xe5\x85\x8b\xe9\x9a\x86\xe5\x90\x8e\xe6\xae\x8b\xe5\x8f\xb7\xe9\x97\xa8\xe5\xbc\xba\xe5\x88\xb6\xe6\xad\xa5+\xe7\x82\xb9\xe7\x81\xab\xe9\xa6\x96\xe8\xa1\x8c\xe6\xa0\xb8\xe9\xaa\x8c\xe5\xbe\x8b\xef\xbc\xbd").encode("utf-8")
lines[i] = pointer
new_main = b"\n".join(lines)
open(main_p, "wb").write(new_main)
pit_raw = open(pit_p, "rb").read()
if not pit_raw.endswith(b"\n"):
    pit_raw += b"\n"
new_pit = pit_raw + entry + b"\n"
open(pit_p, "wb").write(new_pit)
e_sha = hashlib.sha256(entry).hexdigest()[:16].upper()
receipt = {
    "probe": "r665 bm-c in-window CODELY gate fix #2 (post-merge commit blob 30,801B > 30,720 by 81B; r654 post-push precedent)",
    "action": "r662 pit entry verbatim migrated CODELY.md -> research/pit-ps.md + one-line pointer in main",
    "entry_sha16": e_sha,
    "entry_bytes": len(entry),
    "pointer_bytes": len(pointer),
    "main_bytes_before": len(raw),
    "main_bytes_after": len(new_main),
    "pit_bytes_after": len(new_pit),
    "asserts": {"entry_in_pit": entry in new_pit, "entry_gone_from_main": new_main.count(entry) == 0},
}
assert receipt["asserts"]["entry_in_pit"] and new_main.count(entry) == 0
open(r"results\_r665bmc_codely_gate_fix2.json", "w", encoding="utf-8", newline="\n").write(json.dumps(receipt, ensure_ascii=False, indent=1) + "\n")
print("GATE-FIX2 receipt:", json.dumps(receipt["asserts"]), "main", len(raw), "->", len(new_main))
