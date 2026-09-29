# r449 bm-a attrition clobber repair (3rd occurrence of r448 external-writer pit, this
# window 23:25->23:48 CLEAN->ACTIVE-LOSS): union work with HEAD blob (authoritative
# superset per guard verdict "work missing 4 rows present in HEAD"), r446/r448 recipe:
# blob-tail chronological insert + history union + declared==measured assert.
import json, os, subprocess, sys, io

try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ATT = os.path.join(ROOT, "results", "gate_attrition.bm-a.json")

def load_blob(rev):
    out = subprocess.run(["git", "show", rev + ":results/gate_attrition.bm-a.json"],
                         capture_output=True, cwd=ROOT)
    if out.returncode != 0:
        raise SystemExit(f"blob read fail {rev}: {out.stderr[:200]}")
    return json.loads(out.stdout.decode("utf-8"))

def key(e):
    return (e.get("batch"), e.get("ts"))

work = json.load(open(ATT, encoding="utf-8"))
blob = load_blob("HEAD")
we, be = work.get("entries", []), blob.get("entries", [])
wkeys = {key(e) for e in we}
missing = [e for e in be if key(e) not in wkeys]
work_only = [e for e in we if key(e) not in {(x.get("batch"), x.get("ts")) for x in be}]
print(f"work={len(we)} HEAD={len(be)} missing-in-work={len(missing)} work-only-vs-HEAD={len(work_only)}")
for e in missing:
    print("  RESTORE:", key(e))

if missing:
    assert len(we) == len({key(e) for e in we}), "work has dup keys; manual review"
    # chronological union: HEAD rows are the authoritative append order; any work-only
    # rows (legit newer appends by a live writer) keep their tail position.
    bkeys_ordered = [key(e) for e in be]
    if work_only:
        merged = [e for e in be] + work_only
    else:
        merged = list(be)
    mkeys = [key(e) for e in merged]
    assert len(mkeys) == len(set(mkeys)), "dup after union"
    assert set(mkeys) == set(list(wkeys) + [key(e) for e in missing]), "union not exhaustive"
    work["entries"] = merged
    print("union rebuilt: HEAD order + work-only tail")

# history union (append-only chain)
wh = work.get("history", [])
bh = blob.get("history", [])
wht = {json.dumps(h, sort_keys=True, ensure_ascii=False) for h in wh}
hist_add = [h for h in bh if json.dumps(h, sort_keys=True, ensure_ascii=False) not in wht]
work["history"] = wh + hist_add

declared = len(work["entries"])
tmp = ATT + ".tmp"
with open(tmp, "w", encoding="utf-8") as fh:
    json.dump(work, fh, ensure_ascii=False, indent=1)
os.replace(tmp, ATT)

final = json.load(open(ATT, encoding="utf-8"))
assert len(final.get("entries", [])) == declared, "declared != measured"
print(f"post-write: entries={declared} history={len(final.get('history', []))}")
print("RESTORE OK zero-loss union vs HEAD")
