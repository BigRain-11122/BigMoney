"""r699 pool conflict resolve: CONTEST-RC double-flip -> theirs (r474
per-field max-merge newer-wins; r311 latest.ts law), then semantic verify of
the auto-merged SHARD-10 face + whole-pool invariants."""
import json
import subprocess

PATH = "results/runnable_pool.json"

raw = open(PATH, "rb").read()
eol = b"\r\n" if b"\r\n" in raw[:4000] else b"\n"
lines = raw.split(eol)
out, mode = [], "keep"
for ln in lines:
    s = ln.strip()
    if s == b"<<<<<<< HEAD":
        mode = "ours"
        continue
    if s == b"=======":
        mode = "theirs"
        continue
    if s == b">>>>>>> origin/main":
        mode = "keep"
        continue
    if mode == "ours":
        continue
    out.append(ln)
data = eol.join(out)
txt = data.decode("utf-8")
assert "<<<<<<<" not in txt and ">>>>>>>" not in txt, "markers remain"
pool = json.loads(txt)
open(PATH, "wb").write(data)
print("markers resolved (CONTEST-RC -> theirs 22:32:33/bm-c)")


def side(rev):
    r = subprocess.run(["git", "show", f"{rev}:{PATH}"],
                       capture_output=True, timeout=30)
    return json.loads(r.stdout.decode("utf-8"))


ours, theirs = side("HEAD"), side("MERGE_HEAD")
ent = {}
for p in (ours, theirs, pool):
    for e in p.get("entries", []):
        ent.setdefault(e.get("id"), []).append(e)


def shard(doc, eid, key):
    for e in doc.get("entries", []):
        if e.get("id") == eid:
            for s in e.get("shards", []):
                if s.get("key") == key:
                    return e, s
    return None, None


# semantic invariants on the resolved worktree pool
e_rc, s_rc = shard(pool, "CONTEST-YTD-P1-RC-0OF1", "contest-ytd-p1-rc-0of1")
assert e_rc["status"] == "done" and s_rc["status"] == "done"
assert s_rc["owner_since"] == "2026-10-04 22:32:33", s_rc["owner_since"]
assert s_rc["harvested_by"] == "bm-c" and e_rc["done_by"] == "bm-c"

# SHARD-10 auto-merge sanity: done everywhere, ts = newer of both sides
e_10, s_10 = shard(pool, "PERPETUAL-N2-W15-SHARD-10", "n2w15-10of12")
_, s_10o = shard(ours, "PERPETUAL-N2-W15-SHARD-10", "n2w15-10of12")
_, s_10t = shard(theirs, "PERPETUAL-N2-W15-SHARD-10", "n2w15-10of12")
assert e_10["status"] == "done" and s_10["status"] == "done"
for f in ("owner_since", "done_at"):
    want = max(x for x in (s_10o.get(f), s_10t.get(f)) if x)
    got = s_10.get(f)
    assert got == want, f"SHARD-10 {f}: got {got} want {want} (max-merge)"
print("SHARD-10 max-merge sane:", {k: s_10.get(k) for k in
                                   ("status", "owner_since", "done_at",
                                    "harvested_by")})

e_2, s_2 = shard(pool, "PERPETUAL-N2-W15-SHARD-10".replace("10", "2"),
                 "n2w15-2of12")
assert e_2["status"] == "ready" and s_2["status"] == "ready"
assert s_2["owner"] == "bm-b", "SHARD-2 claim intact"
e_11, s_11 = shard(pool, "PERPETUAL-N2-W15-SHARD-11", "n2w15-11of12")
assert e_11["status"] == "done" and s_11["status"] == "done"
n_done = sum(1 for e in pool["entries"]
             if e.get("id", "").startswith("PERPETUAL-N2-W15-SHARD")
             and e.get("status") == "done")
print("N2-W15 screen shards done:", n_done, "/12")
assert n_done == 11, n_done
print("POOL RESOLVE OK")
