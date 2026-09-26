# -*- coding: utf-8 -*-
"""r306 bm-b: reconcile deepdiff(6 variant pairs) vs union(52 unique) discrepancy
on autofill_state.json stages. Read-only."""
import subprocess, json

def blob(rev, path):
    r = subprocess.run(["git", "show", "%s:%s" % (rev, path)], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("no blob %s %s" % (rev, path))
    return r.stdout

P = "results/autofill_state.json"
o = json.loads(blob("17fbbd18", P).decode("utf-8-sig"))
t = json.loads(blob("f9a01924", P).decode("utf-8-sig"))
ol, tl = o["launches"], t["launches"]
print("ours len=%d theirs len=%d" % (len(ol), len(tl)))

def key(r):
    return json.dumps(r, sort_keys=True, ensure_ascii=False)

ok, tk = {key(r) for r in ol}, {key(r) for r in tl}
print("union unique=%d | A-only=%d | B-only=%d | shared=%d" % (
    len(ok | tk), len(ok - tk), len(tk - ok), len(ok & tk)))

print("\n-- A-only entries (index, ts, machine, has_crash_flag):")
for i, r in enumerate(ol):
    if key(r) not in tk:
        print("  A[%d] ts=%s machine=%s crash_counted=%s" % (
            i, r.get("ts"), r.get("machine"), "crash_counted" in r))
print("\n-- B-only entries:")
for i, r in enumerate(tl):
    if key(r) not in ok:
        print("  B[%d] ts=%s machine=%s crash_counted=%s" % (
            i, r.get("ts"), r.get("machine"), "crash_counted" in r))

# pairwise key-presence check on the same indexes the deepdiff flagged
print("\n-- pairwise crash_counted presence at flagged indexes:")
for i in (40, 42, 44, 46, 48, 49):
    a_has = "crash_counted" in ol[i]
    b_has = "crash_counted" in tl[i]
    same_rest = {k: v for k, v in ol[i].items() if k != "crash_counted"} == \
                {k: v for k, v in tl[i].items() if k != "crash_counted"}
    print("  idx=%d A_has=%s B_has=%s rest_equal=%s ts_A=%s ts_B=%s" % (
        i, a_has, b_has, same_rest, ol[i].get("ts"), tl[i].get("ts")))

# and index-shift check: does B[i] == A[i+k] for some k in tail region?
print("\n-- cross-identity scan (B entry found in A at which index):")
for i in (38, 40, 42, 44, 46, 48, 49):
    kb = key(tl[i])
    hits = [j for j, r in enumerate(ol) if key(r) == kb]
    print("  B[%d] ts=%s matches A indexes=%s" % (i, tl[i].get("ts"), hits))
