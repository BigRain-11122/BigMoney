# r264 bm-b: post_review git_log_file re-anchor per R256 law (hot-ticket window rot, second strike).
# Facts verified pre-edit: d8be0cb8 (msg contains CN-REV-TILT) is the ONLY commit touching
# results/_r248bma_cnrev_harvest.py; e43bc613 (msg contains CN-DIV-LOWVOL-ROT) is the ONLY commit
# touching results/_r252bma_rot_harvest.py -> stable anchors, window can never rot.
# Same frozen fact (delivery commit exists) durably re-encoded per r71/r223 precedent;
# checks NOT deleted (禁删检查翻绿); _reconciled note appended.
import json

P = "results/post_review_criteria.json"
raw = open(P, "rb").read()
assert not raw.startswith(b"\xef\xbb\xbf"), "BOM drift"
txt = raw.decode("utf-8")
assert "\r\n" not in txt, "EOL drift"
assert not txt.endswith("\n"), "tail newline drift"
d = json.loads(txt)

REANCHOR = {
    "T-73-CN-REV-TILT-P1": ("fleet/tasks/T-2026-09-26-73-P1.json",
                            "results/_r248bma_cnrev_harvest.py"),
    "T-73-CN-DIV-LOWVOL-ROT-P1": ("fleet/tasks/T-2026-09-26-73-P1.json",
                                  "results/_r252bma_rot_harvest.py"),
}
n = 0
for it in d["items"]:
    tid = it.get("id")
    if tid not in REANCHOR:
        continue
    for c in it.get("checks", []):
        if c.get("kind") == "git_log_file" and c["args"][0] == REANCHOR[tid][0]:
            c["args"][0] = REANCHOR[tid][1]
            n += 1
assert n == 2, f"expected 2 re-anchors, did {n}"

rec = ("2026-09-26 17:5x r264 bm-b: two T-73 git_log_file checks re-anchored from hot ticket face "
       "(depth-30 window pushed out by per-round dual-machine progress appends, second R256 strike) "
       "to stable one-commit harvest scripts (_r248bma_cnrev_harvest.py=d8be0cb8, "
       "_r252bma_rot_harvest.py=e43bc613; facts git-verified pre-edit); same frozen delivery-commit "
       "fact, checks preserved not deleted")
d["_reconciled"] = (d.get("_reconciled", "") + " | " + rec).strip(" |")
out = json.dumps(d, ensure_ascii=False, indent=1)
assert not out.endswith("\n")
open(P, "wb").write(out.encode("utf-8"))
print("re-anchored 2 checks + reconciled note; bytes:", len(out.encode("utf-8")))
