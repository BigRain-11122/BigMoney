"""r688 bm-c rebase-conflict resolver: results/compute_audit.json =
append-history union (ts-keyed dedup, sort asc, latest = max-ts entry;
origin carries 13 early entries mine lacks, mine carries 1 fresh sample
16:27:50 origin lacks -- pure pick either side = active loss, r570/r806
union law) + results/lhb_update_status.json = single-state face
newer-wins (same cutoff/last_attempt, mine updated 16:29:26 > 16:08:27).
REBASE ours/theirs INVERSION observed: REBASE_HEAD blob = mine.
Validates JSON parse + zero conflict markers before returning."""
import json
import re
import subprocess

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"


def blob(rev, path):
    r = subprocess.run(["git", "-C", REPO, "show", f"{rev}:{path}"],
                       capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"blob read fail {rev}:{path}: {r.stderr[:200]}")
    return json.loads(r.stdout)


def main():
    ca_path = "results/compute_audit.json"
    mine = blob("REBASE_HEAD", ca_path)
    theirs = blob("origin/main", ca_path)
    by_ts = {}
    for e in theirs.get("history", []):
        by_ts[e.get("ts")] = e
    for e in mine.get("history", []):
        by_ts[e.get("ts")] = e
    merged = sorted(by_ts.values(), key=lambda x: x.get("ts") or "")
    latest = merged[-1]
    assert latest.get("ts") == "2026-10-07 16:27:50", "latest anchor mismatch"
    union = {"latest": latest, "history": merged}
    with open(REPO + "\\" + ca_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(union, fh, ensure_ascii=False, indent=2)

    lhb_path = "results/lhb_update_status.json"
    lhb_mine = blob("REBASE_HEAD", lhb_path)
    assert lhb_mine.get("updated") == "2026-10-07 16:29:26", "lhb anchor"
    with open(REPO + "\\" + lhb_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(lhb_mine, fh, ensure_ascii=False, indent=2)

    # post-validate: parse + zero markers on both resolved files
    for p in (ca_path, lhb_path):
        txt = open(REPO + "\\" + p, encoding="utf-8").read()
        assert not re.search(r"^(<<<<<<<|=======|>>>>>>>)", txt, re.M), \
            "marker pollution: " + p
        json.loads(txt)
    print("resolver done: compute_audit history union n=%d (theirs=%d mine=%d), "
          "latest=%s; lhb newer-wins updated=%s"
          % (len(merged), len(theirs["history"]), len(mine["history"]),
             latest["ts"], lhb_mine["updated"]))


if __name__ == "__main__":
    main()
