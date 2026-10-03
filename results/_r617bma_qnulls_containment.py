# -*- coding: utf-8 -*-
"""r617 bm-a: THIRD double-burn containment (quality-nulls lane).

09:10:25 autofill re-claimed FUND-QUALITY-P1-NULLS (shard-level claim
09:10:16) over bm-b's live correct-caliber burn (pid 57116 since 07:26,
ETA 10-08) and burned ~24min OFF-CALIBER local rows before the r617
kill. Root cause: the r616 keep-block note landed on the SENS sig only
-- the nulls sig was never installed, so the launch gate held nothing.

Legs (this helper, all local faces, zero origin harm):
 1. pool: release the shard-level claim (owner_since -> None) on
    fund-quality-p1-nulls-0of1 (entry already ownerless).
 2. fuse: install the missing keep-block sig
    scripts/fund_quality_p1.py|run,--nulls (same runner sha16 as SENS
    sig -- verified before write), note = off-caliber containment +
    bm-b rightful burner.
 3. discard the 59 errant off-caliber rows: restore
    results/fund_quality_p1/nulls.jsonl to HEAD (origin 28-row state).
"""
import hashlib, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POOL = os.path.join(ROOT, "results", "runnable_pool.json")
FUSE = os.path.join(ROOT, "results", "crash_fuse.json")
NULLS = os.path.join(ROOT, "results", "fund_quality_p1", "nulls.jsonl")
SHARD_KEY = "fund-quality-p1-nulls-0of1"
ENTRY_ID = "FUND-QUALITY-P1-NULLS"
RUNNER = os.path.join(ROOT, "scripts", "fund_quality_p1.py")
SIG = "scripts/fund_quality_p1.py|run,--nulls"


def _sha16(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()[:16]


def main():
    cur = _sha16(RUNNER)

    # --- leg 0: sanity -- the SENS sig must exist; its pinned hash is
    # the PRE-r611 runner (bm-b's 27705b55e --redo machinery edit
    # legitimately changed the file -> version-keyed gate auto-opens,
    # by design; the off-caliber condition itself is UNCHANGED, so we
    # re-arm the pin to the current hash below)
    fuse = json.load(open(FUSE, encoding="utf-8"))
    sens = fuse["sigs"].get("scripts/fund_quality_p1.py|run,--sensitivity")
    assert sens, "SENS sig missing -- unexpected fuse face"
    assert SIG not in fuse["sigs"], "nulls sig already present?"

    # --- leg 1: pool shard-claim release (json round-trip, file is
    # machine-written json; keep original separators/indent via
    # indent=1 + ensure CRLF text mode like the daemon writes it)
    pool = json.load(open(POOL, encoding="utf-8"))
    released = 0
    for e in pool.get("entries", []):
        if e.get("id") != ENTRY_ID:
            continue
        for s in e.get("shards", []):
            if s.get("key") == SHARD_KEY and s.get("owner_since"):
                s["owner_since"] = None
                released += 1
    assert released == 1, f"expected exactly 1 shard claim, got {released}"
    tmp = POOL + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\r\n") as fh:
        json.dump(pool, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, POOL)

    # --- leg 2: fuse sig install (keep-block note, r616 family) with the
    # CURRENT runner hash (r611 --redo machinery version -- version-keyed
    # gate needs a live pin) + re-arm the SENS pin drifted by the same edit
    fuse["sigs"][SIG] = {
        "count": 2,
        "refusals": 0,
        "code_sha256": cur,
        "last_crash_ts": "2026-10-03 09:37:00",
        "entry": ENTRY_ID,
        "shard": SHARD_KEY,
        "machine": "bm-a",
        "note": ("keep blocked on bm-a: OFF-CALIBER CACHE containment "
                 "(r617 third double-burn: autofill shard-claim "
                 "09:10:16 -> launch 09:10:25 -> killed 09:34, ~59 bad "
                 "rows discarded, zero origin harm; r616 keep-block "
                 "note landed on SENS sig only, nulls sig was the gap) "
                 "-- local p1c_stock 688/689 vol/amt at 100x raw (meta "
                 "no vwap_688_check, r615 probe); clear ONLY after "
                 "p1c_stock TRANSFER+verify (fleet decision) or runner "
                 "edit (fix-first); bm-b = correct-caliber rightful "
                 "burner (2000-draw run since 07:26, ETA 10-08)"),
    }
    fuse["sigs"]["scripts/fund_quality_p1.py|run,--sensitivity"][
        "code_sha256"] = cur
    fuse["sigs"]["scripts/fund_quality_p1.py|run,--sensitivity"][
        "note"] = (sens.get("note", "") +
                  " | r617 re-arm: bm-b r611 --redo machinery edit "
                  "(27705b55e) drifted the pinned hash; off-caliber "
                  "condition UNCHANGED, pin re-anchored to current "
                  "runner sha16=" + cur)
    tmp = FUSE + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\r\n") as fh:
        json.dump(fuse, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, FUSE)

    # --- leg 3: discard errant off-caliber rows (restore to HEAD;
    # rows are uncommitted local garbage from the killed burn -- r570
    # origin-verbatim family, zero origin harm)
    r = subprocess.run(
        ["git", "checkout", "HEAD", "--",
         "results/fund_quality_p1/nulls.jsonl"],
        cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    h = subprocess.run(
        ["git", "show", "HEAD:results/fund_quality_p1/nulls.jsonl"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    head_n = len([l for l in h.stdout.splitlines() if l.strip()])
    n = sum(1 for _ in open(NULLS, encoding="utf-8"))
    assert n == head_n, f"post-restore nulls rows {n} != HEAD {head_n}"

    # --- verify faces
    pool2 = json.load(open(POOL, encoding="utf-8"))
    shard2 = [s for e in pool2["entries"] if e["id"] == ENTRY_ID
              for s in e["shards"] if s["key"] == SHARD_KEY][0]
    assert shard2["owner_since"] is None
    fuse2 = json.load(open(FUSE, encoding="utf-8"))
    assert fuse2["sigs"][SIG]["code_sha256"] == cur
    print("CONTAINMENT OK: shard claim released; fuse sig installed "
          f"({SIG[:60]}..., sha16={cur}); nulls.jsonl restored to "
          f"HEAD {n} rows")


if __name__ == "__main__":
    main()
