# r448 bm-a forensic repair: gate_attrition.bm-a.json blob-union restore (r446 law: append-only ledger shrink = union/blob rebuild, never take-side)
# Incident: work-tree clobber 75->71 between r446 close (e62e0e9c8, 21:23) and r447 pre-pull absorb (299530314, 21:40)
# dropped the 4 forensic-restored rows A10/A11/A12/A13; a 22:27:33 foreign write then appended HIGHERMOM_TIMING_P1 (72).
# Repair: union of current work entries + missing rows from e62e0e9c8 blob, chronological insert (blob-tail order, HIGHERMOM stays last).
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ATT = os.path.join(ROOT, "results", "gate_attrition.bm-a.json")
BLOB_REV = "e62e0e9c8"  # r446 close commit = authoritative 75-entry repaired state

def load_blob(rev):
    out = subprocess.run(["git", "show", rev + ":results/gate_attrition.bm-a.json"],
                         capture_output=True, cwd=ROOT)
    if out.returncode != 0:
        raise SystemExit(f"blob read fail {rev}: {out.stderr[:200]}")
    return json.loads(out.stdout.decode("utf-8"))

def key(e):
    # (batch, ts) composite: same batch name may legitimately carry multiple measurement rows (REPO_CALENDAR_P2 x2 precedent)
    return (e.get("batch"), e.get("ts"))

work = json.load(open(ATT, encoding="utf-8"))
blob = load_blob(BLOB_REV)
we, be = work.get("entries", []), blob.get("entries", [])
wkeys = [key(e) for e in we]
bkeys = [key(e) for e in be]
missing = [e for e in be if key(e) not in wkeys]

print(f"work entries={len(we)} blob({BLOB_REV}) entries={len(be)} missing-in-work={len(missing)}")
for e in missing:
    print(f"  RESTORE: {key(e)}")

if not missing:
    print("nothing to restore; file already superset of blob")
else:
    dupes = len(wkeys) != len(set(wkeys))
    assert not dupes, "work file has duplicate (batch,ts) keys; manual review required"

    # chronological union: missing rows inserted before the later-appended foreign row
    # (A-rows are blob-tail order; HIGHERMOM physically hit this file at 22:27:33, after the blob state)
    last = we[-1]
    hm_last = key(last)[0] == "HIGHERMOM_TIMING_P1"
    if hm_last:
        head_rows, tail_rows = we[:-1], [last]
    else:
        head_rows, tail_rows = we, []

    merged = head_rows + missing + tail_rows
    assert len(merged) == len(we) + len(missing), "merge count mismatch"
    mkeys = [key(e) for e in merged]
    assert len(mkeys) == len(set(mkeys)), "duplicate after merge"
    work["entries"] = merged

# idempotent ordering pass: foreign-appended HIGHERMOM row must sit after the restored blob-tail rows
ent = work["entries"]
hm_idx = [i for i, e in enumerate(ent) if key(e)[0] == "HIGHERMOM_TIMING_P1"]
restored = {"T-101-V4-A10-REGIMECOMBO", "T-101-V4-A11-XSELECT", "T-101-V4-A12-PREDCOND", "T-101-V4-A13-PREDFACE"}
if hm_idx and any(key(e)[0] in restored for e in ent[hm_idx[0] + 1:]):
    hm_row = ent.pop(hm_idx[0])
    ent.append(hm_row)
    work["entries"] = ent
    print("order fix: HIGHERMOM_TIMING_P1 moved after restored blob-tail rows")

# history union (append-only chain): add any blob history rows absent in work
wh = work.get("history", [])
bh = blob.get("history", [])
wht = {json.dumps(h, sort_keys=True, ensure_ascii=False) for h in wh}
hist_add = [h for h in bh if json.dumps(h, sort_keys=True, ensure_ascii=False) not in wht]
work["history"] = wh + hist_add

tmp = ATT + ".tmp"
with open(tmp, "w", encoding="utf-8") as fh:
    json.dump(work, fh, ensure_ascii=False, indent=1)
os.replace(tmp, ATT)

# reconcile: declared vs measured (r446 law)
final = json.load(open(ATT, encoding="utf-8"))
fe = final.get("entries", [])
print(f"post-write verification: entries={len(fe)} (declared {len(we)+len(missing)})")
assert len(fe) == len(we) + len(missing), "declared != measured"
print(f"history rows: {len(wh)} -> {len(final.get('history', []))} (+{len(hist_add)})")
print(f"restored batches now present: {[key(e) for e in missing]}")
print(f"tail order: {[key(e) for e in fe[-6:]]}")
print(f"RESTORE OK zero-loss union")
