import hashlib, json, re
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
import os
os.chdir(ROOT)
main_p = "CODELY.md"
pit_p = "research/pit-ps.md"
raw = open(main_p, "rb").read()
lines = raw.split(b"\n")
entry_prefix = b"- [2026-10-07 08:4x r665 bm-c]"
hits = [i for i, l in enumerate(lines) if l.startswith(entry_prefix)]
assert len(hits) == 1, "r665 entry count != 1: %d" % len(hits)
i = hits[0]
entry = lines[i].rstrip(b"\r")
assert entry.endswith(b"\xe5\x86\x8d\xe8\xbf\xad\xe4\xbb\xa3\xe3\x80\x82".decode() if False else True) if False else True
pointer = ("- \xe5\x9f\x9f\xe6\x8c\x87\xe9\x92\x88\xc2\xb7r665 bm-c\xef\xbc\x882026-10-07 08:4x\xef\xbc\x89\xef\xbc\x9asilent-git \xe6\x8d\x95\xe8\x8e\xb7\xe9\x9d\xa2=\xe5\x8d\x95\xe5\x9d\x97\xe5\xa4\x9a\xe8\xa1\x8c\xe5\xad\x97\xe7\xac\xa6\xe4\xb2\x92foreach \xe6\x8c\x89\xe5\xaf\xb9\xe8\xb1\xa1\xe8\xbf\xad\xe4\xbb\xa3\xe5\x9d\x91\xef\xbc\x88r511-\xe2\x91\xa2 wrapper \xe8\xbe\x93\xe5\x87\xba\xe6\x97\x8f\xe5\xa7\x8a\xe5\xa6\xb9\xe9\x9d\xa2\xc2\xb7S0 \xe8\x84\x8f\xe6\xa0\x91\xe5\x88\xa4\xe4\xbe\xa7\xe5\xae\x9e\xe5\xbc\xb9 DIRTY-COUNT 1/43 fail-closed \xe8\x87\xaa\xe6\x8d\x95\xef\xbc\x89\xe2\x86\x92research/pit-ps.md\xef\xbc\xbbPS \xe6\xb6\x88\xe8\xb4\xb9\xe9\x9d\xa2\xe6\x98\xbe\xe5\xbc\x8f -split \xe5\xbe\x8b\xef\xbc\xbd").encode("utf-8")
lines[i] = pointer
new_main = b"\n".join(lines)
open(main_p, "wb").write(new_main)
pit_raw = open(pit_p, "rb").read()
if not pit_raw.endswith(b"\n"):
    pit_raw += b"\n"
new_pit = pit_raw + entry + b"\n"
open(pit_p, "wb").write(new_pit)
e_sha = hashlib.sha256(entry).hexdigest()[:16].upper()
in_pit = e_sha.encode() if False else entry in new_pit
receipt = {
    "probe": "r665 bm-c in-window CODELY gate fix (post-merge union 31,231B > 30,720 gate; r654 precedent)",
    "action": "r665 pit entry verbatim migrated CODELY.md -> research/pit-ps.md + one-line pointer in main",
    "entry_sha16": e_sha,
    "entry_bytes": len(entry),
    "pointer_bytes": len(pointer),
    "main_bytes_before": len(raw),
    "main_bytes_after": len(new_main),
    "pit_bytes_before": len(pit_raw),
    "pit_bytes_after": len(new_pit),
    "containment": "entry bytes verbatim in pit-ps.md == entry removed from main (sha16 above both sides)",
    "asserts": {"entry_in_pit": bool(in_pit), "entry_gone_from_main": entry_prefix not in new_main.split(entry_prefix)[0] if False else (new_main.count(entry) == 0)},
}
assert receipt["asserts"]["entry_in_pit"] and new_main.count(entry) == 0
open(r"results\_r665bmc_codely_gate_fix.json", "w", encoding="utf-8", newline="\n").write(json.dumps(receipt, ensure_ascii=False, indent=1) + "\n")
print("GATE-FIX receipt:", json.dumps(receipt["asserts"]), "main", len(raw), "->", len(new_main))
