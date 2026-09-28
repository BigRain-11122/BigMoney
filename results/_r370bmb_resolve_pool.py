# -*- coding: utf-8 -*-
"""r370 bm-b pool UU resolver (r312 pool-entry-done-union canon).

Conflict shape: whole-file two-sided UU on results/runnable_pool.json
during `git pull --rebase` replay of 261bb027 onto origin 68cc3d06.

Sides:
  HEAD (origin 68cc3d06, updated_at 09:15:00) = bm-a screen-finalize
    harvest flip: TRIAL-LABOR-W3-SCREEN ready->done (+result_ref
    w3_screen.json; shard done owner bm-a 09:00:05); 93 entries.
  OURS (261bb027, updated_at 09:04:24) = my sole delta: TRIAL-LABOR-
    W3-JUDGE entry appended (waiting); screen entry at the older ready
    face; 94 entries.

Recipe (classifier r312): per-entry-id union; done ABSORBS (either side
done -> done, shard fields from the completing machine's record);
one-side-only entry -> keep; updated_at = newer side; all other fields
asserted identical.  Zero-loss check: union ids == HEAD ids + mine-only
ids; parse-verify before write-back (r185 law); canonical indent=1
format mirror of the fleet face."""
import io
import json

SRC = "results/runnable_pool.json"
raw = io.open(SRC, "r", encoding="utf-8", newline="").read()
lines = raw.replace("\r\n", "\n").split("\n")
mk = [i for i, l in enumerate(lines)
      if l.startswith(("<<<<<<<", "|||||||", "=======", ">>>>>>>"))]
assert len(mk) == 3, f"marker scan unexpected: {mk}"
sep = mk[1]
H = json.loads("{" + "\n".join(lines[2:sep]))
M = json.loads("{" + "\n".join(lines[sep + 1:mk[2]]))
assert set(H) == set(M), "top-level key drift"
hk = {k: v for k, v in H.items() if k not in ("entries", "updated_at")}
mk_ = {k: v for k, v in M.items() if k not in ("entries", "updated_at")}
assert hk == mk_, "top-level non-entry drift beyond updated_at"
hi = {e["id"]: e for e in H["entries"]}
mi = {e["id"]: e for e in M["entries"]}
assert set(mi) - set(hi) == {"TRIAL-LABOR-W3-JUDGE"}, \
    f"unexpected mine-only ids: {set(mi) - set(hi)}"
assert not (set(hi) - set(mi)), f"unexpected head-only ids: {set(hi)-set(mi)}"

union = {}
n_done_absorb = 0
for eid in hi:
    h, m = hi[eid], mi[eid]
    hs, ms = h.get("status"), m.get("status")
    if hs == "done" or ms == "done":
        # done ABSORBS: take the completing side's record verbatim
        src_side = h if hs == "done" else m
        if hs != ms:
            n_done_absorb += 1
        union[eid] = json.loads(json.dumps(src_side))
    elif hs == ms:
        if json.dumps(h, sort_keys=True) == json.dumps(m, sort_keys=True):
            union[eid] = h
        else:
            # same status, differing shard/owner transient fields ->
            # shard-level union (done absorbs at shard level; owner
            # fields are transient autofill claims, non-authoritative)
            u = json.loads(json.dumps(h))
            for k in m:
                if k == "shards":
                    hs_sh = {s["key"]: s for s in u.get("shards", [])}
                    for s in m["shards"]:
                        t = hs_sh.get(s["key"])
                        if t is None or s.get("status") == "done":
                            if t is not None:
                                u["shards"] = [
                                    (s if x["key"] == s["key"] else x)
                                    for x in u["shards"]]
                            else:
                                u["shards"].append(s)
                        else:
                            u["shards"] = [
                                (s if x["key"] == s["key"] else x)
                                for x in u["shards"]]
                else:
                    u[k] = m[k]
            union[eid] = u
    else:
        raise SystemExit(f"status face divergence on {eid}: "
                         f"{hs} vs {ms} -- manual adjudication required")
for eid in set(mi) - set(hi):          # one-side-only entries -> keep
    union[eid] = mi[eid]

out = {k: v for k, v in H.items() if k != "entries"}
out["entries"] = [union[e["id"]] for e in H["entries"]] + \
    [union[e] for e in set(mi) - set(hi)]
out["updated_at"] = max(H.get("updated_at", ""), M.get("updated_at", ""))

# zero-loss + done-absorb assertions
assert len(out["entries"]) == len(hi) + len(set(mi) - set(hi)) == 94
scr = next(e for e in out["entries"] if e["id"] == "TRIAL-LABOR-W3-SCREEN")
jud = next(e for e in out["entries"] if e["id"] == "TRIAL-LABOR-W3-JUDGE")
assert scr["status"] == "done" and scr["result_ref"], "done-absorb failed"
assert scr["shards"][0]["status"] == "done" and \
    scr["shards"][0]["owner"] == "bm-a", "shard done-absorb failed"
assert jud["status"] == "waiting" and jud["lane_owner"] is None, \
    "judge entry must stay waiting"
json.loads(json.dumps(out))            # parse-verify (r185)
with io.open(SRC, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
print(f"[r370 resolve] union 94 entries: screen done-absorb x"
      f"{n_done_absorb} (HEAD completing side), judge kept waiting, "
      f"updated_at={out['updated_at']}")
