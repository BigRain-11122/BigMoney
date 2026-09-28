"""r391 bm-b rebase resolver -- results/runnable_pool.json UU (r312 recipe).

Sides:
  stage2 (ours, origin-side after bm-c push 2a59e874): TRIAL-LABOR-W3-JUDGE
    shard claim owner=bm-c @15:50:05 (transient autofill claim,
    non-authoritative per classifier law)
  stage3 (theirs, my replayed harvest commit): entry+shard DONE with
    finalize receipt (w3_judge.json 15:51:55, 513 cells, G2 eligible 0)

r312 pool-entry-done-union: per entry id union; done ABSORBS claim;
one-side-only entries kept; done side's shard fields = completing
machine's record (the flip evidence gate is the authority).
"""
import json
import subprocess

PATH = "results/runnable_pool.json"


def blob(stage):
    return subprocess.run(
        ["git", "show", f":{stage}:{PATH}"], capture_output=True
    ).stdout.decode("utf-8")


def entries(d):
    lst = d.get("entries") if isinstance(d, dict) else d
    return lst, {x["id"]: x for x in lst}


ours_raw, theirs_raw = blob(2), blob(3)
ours, theirs = json.loads(ours_raw), json.loads(theirs_raw)
ol, o = entries(ours)
tl, t = entries(theirs)
print(f"side sizes: origin={len(o)} mine={len(t)}")

assert set(o) == set(t), (
    f"entry-set drift: only-origin={sorted(set(o)-set(t))} "
    f"only-mine={sorted(set(t)-set(o))}")

# per-entry union with done-absorb; list order preserved from origin side
merged, diffs = [], []
for e in ol:
    k = e["id"]
    if json.dumps(e, sort_keys=True, ensure_ascii=False) == json.dumps(
            t[k], sort_keys=True, ensure_ascii=False):
        merged.append(e)
        continue
    diffs.append(k)
    a, b = e, t[k]
    # done absorbs (r312): authoritative done side wins entry+shard record
    if b.get("status") == "done" and a.get("status") != "done":
        pick, why = b, "done(theirs) absorbs claim(ours)"
    elif a.get("status") == "done" and b.get("status") != "done":
        pick, why = a, "done(ours) absorbs claim(theirs)"
    else:
        # both non-done: same-status -> shard-level union (done absorbs)
        pick = {**a, **{k2: v2 for k2, v2 in b.items() if k2 not in a}}
        for sh_b in b.get("shards", []):
            for i, sh_a in enumerate(pick.get("shards", [])):
                if sh_a.get("key") == sh_b.get("key"):
                    pick["shards"][i] = (
                        sh_b if sh_b.get("status") == "done"
                        and sh_a.get("status") != "done" else sh_a)
                    break
            else:
                pick.setdefault("shards", []).append(sh_b)
        why = "same-status shard union"
    merged.append(pick)
    print(f"  {k}: {why}")

# top-level keys: union, origin side authoritative for non-entries scalars
out = dict(ours) if isinstance(ours, dict) else merged
if isinstance(ours, dict):
    out["entries"] = merged
    for k2, v2 in (theirs.items() if isinstance(theirs, dict) else []):
        if k2 != "entries" and k2 not in out:
            out[k2] = v2

# verify: json round-trip + done-absorb assertion
txt = json.dumps(out, ensure_ascii=False, indent=1)
back = json.loads(txt)
bl, bmap = entries(back)
w3 = bmap["TRIAL-LABOR-W3-JUDGE"]
assert w3["status"] == "done" and w3["shards"][0]["status"] == "done", w3
assert w3["shards"][0]["owner"] == "bm-b", w3["shards"][0]
assert len(bl) == len(ol) == len(tl)
assert diffs == ["TRIAL-LABOR-W3-JUDGE"], diffs

with open(PATH, "w", encoding="utf-8", newline="") as f:
    f.write(txt + "\n")
final = json.loads(open(PATH, encoding="utf-8").read())
fl, fmap = entries(final)
assert fmap["TRIAL-LABOR-W3-JUDGE"]["status"] == "done"
print(f"write-back OK: {len(fl)} entries, W3-JUDGE done-absorbed "
      f"(diffs confined to {diffs})")
