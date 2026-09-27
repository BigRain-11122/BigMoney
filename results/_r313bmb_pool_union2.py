# -*- coding: utf-8 -*-
"""r313 bm-b runnable_pool.json rebase-conflict union resolver (replay of
the pool-registration commit onto bm-a's x2-LA claim commit 4ffc7ad6).

Stage semantics (rebase): stage2=ours=new base (origin/main, bm-a's
autofill claim dce2-legacy-la -- AUTHORITATIVE for shared entries per
fleet/README sec.4 commit-time law; bm-b's rival claim 1f30497f was
skipped as the yielded side); stage3=theirs=my pool-registration commit
(carries the 9 PROSPECT-REGIME-SEGMENTS entries which exist ONLY on this
side).

Recipe: entries union by id -- shared ids take stage2 (origin face,
keeps bm-a's claim status verbatim), ids absent on origin are appended
verbatim from stage3 (zero loss of the new shard supply). Top-level
scaffolding from stage2; updated_at = now. Parse-validate before write
(r185 law)."""
import json
import os
import subprocess
import time

REPO = r"C:\Users\Administrator\Desktop\Bigmoney"
PATH = "results/runnable_pool.json"


def stage(n):
    r = subprocess.run(["git", "show", f":{n}:{PATH}"], capture_output=True,
                       cwd=REPO)
    assert r.returncode == 0, f"missing stage {n}"
    return json.loads(r.stdout.decode("utf-8-sig"))


def main():
    ours, theirs = stage(2), stage(3)
    merged = {e["id"]: e for e in ours["entries"]}
    added, shared = [], []
    for e in theirs["entries"]:
        if e["id"] in merged:
            shared.append(e["id"])
            continue                      # origin side wins (claim law)
        merged[e["id"]] = e                # only-on-mine: keep verbatim
        added.append(e["id"])
    pool = dict(ours)
    pool["entries"] = list(merged.values())
    pool["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    # contract asserts: my 9 registrations trio-valid (r301+r305)
    for e in pool["entries"]:
        if e["id"].startswith("PROSPECT-REGIME-SEGMENTS"):
            assert e.get("status") == "ready" and e.get("runner")
            assert e.get("workers_plan") and e.get("shards")
    # bm-a's claim must survive verbatim on the shared x2-LA entry
    x2la = [e for e in pool["entries"] if e["id"] == "DECISION-CHAIN-E2E-X2-LA"]
    assert x2la, "x2-LA entry missing"
    sh = x2la[0]["shards"][0]
    assert sh.get("owner") == "bm-a", f"x2-LA owner={sh.get('owner')!r}"
    # prior closure face intact
    mk = [e for e in pool["entries"] if e["id"] == "CN-MKTNEUTRAL-P1"]
    assert mk and mk[0]["shards"][0]["status"] == "done"
    assert len(pool["entries"]) == len({e["id"] for e in pool["entries"]})
    text = json.dumps(pool, ensure_ascii=False, indent=1)
    json.loads(text)
    with open(os.path.join(REPO, PATH), "w", encoding="utf-8",
              newline="\n") as f:
        f.write(text + "\n")
    subprocess.run(["git", "add", "--", PATH], cwd=REPO)
    print(f"pool union: {len(pool['entries'])} entries; "
          f"added-from-mine={len(added)} ({', '.join(added)}); "
          f"shared-kept-origin={len(shared)}; x2-LA owner={sh.get('owner')}")


if __name__ == "__main__":
    main()
