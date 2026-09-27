# -*- coding: utf-8 -*-
"""r312 bm-b runnable_pool.json rebase-conflict union resolver (replay of
the 09:02 autofill stray claim commit onto bm-a r306 origin).

Stage semantics (rebase): stage2=ours=new base (origin/main, bm-a r306:
CN-MKTNEUTRAL-P1 done + judged-closed) -- AUTHORITATIVE for shared entry
state per fleet/README sec.4 commit-time law (bm-a claim 08:40:04 precedes
our stale 09:02 stray claim); stage3=theirs=replayed stray commit (carries
the 9 DECISION-CHAIN-E2E-X2-* entries which exist ONLY on this side).

Recipe: entries union by id -- shared ids take stage2 (origin), ids absent
on origin are appended verbatim from stage3 (zero loss of the new pool
supply). Top-level scaffolding (version/law_ref/schema) from stage2;
updated_at = now. Parse-validate before write (r185 law)."""
import json
import os
import subprocess
import sys
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
    added, kept_origin = [], 0
    for e in theirs["entries"]:
        if e["id"] in merged:
            kept_origin += 1          # origin side wins (commit-time law)
            continue
        merged[e["id"]] = e           # only-on-mine entries: keep verbatim
        added.append(e["id"])
    pool = dict(ours)
    pool["entries"] = list(merged.values())
    pool["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    # contract asserts (r301 shards + r305 workers_plan) on the added set
    for e in pool["entries"]:
        if e["id"].startswith("DECISION-CHAIN-E2E-X2"):
            assert e.get("status") == "ready" and e.get("runner")
            assert e.get("workers_plan") and e.get("shards")
    mk = [e for e in pool["entries"] if e["id"] == "CN-MKTNEUTRAL-P1"]
    assert mk and mk[0]["shards"][0]["status"] == "done", (
        "mkneutral must stay origin done-state (bm-a r306 closure)")
    text = json.dumps(pool, ensure_ascii=False, indent=1)
    json.loads(text)
    with open(os.path.join(REPO, PATH), "w", encoding="utf-8",
              newline="\n") as f:
        f.write(text + "\n")
    subprocess.run(["git", "add", "--", PATH], cwd=REPO)
    print(f"pool union: {len(pool['entries'])} entries; kept-origin(shared)="
          f"{kept_origin}; added-from-mine={len(added)} ({', '.join(added)})")


if __name__ == "__main__":
    main()
