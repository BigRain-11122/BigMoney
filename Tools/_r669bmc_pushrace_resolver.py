# -*- coding: utf-8 -*-
"""r669 bm-c: push-race rebase-conflict resolver (15 UU faces, r817-precedent
per-face adjudication; r663/r637 kin).

Sides in REBASE context (r309 law): :2 = origin/base side (bm-b churn-absorbs
09:19-09:24 + bm-a r818 ~10:15-10:16 regen), :3 = OUR r669 commit (S6 regen
10:17-10:25).

Adjudication (all derived from blob content, never assumed):
- runnable_pool.json -> :2 origin blob (ONLY diff = bm-b keepalive shard
  owner_since 10:22:07 vs our mirror 10:12:07; pool law owner_since
  newer-wins; single-field diff, rest byte-identical) -- restorable class,
  treasure_guard restore gate rc-cleared.
- 13 reproducible regen faces -> :3 ours (ts-newer-wins derived from each
  blob's own ts/generated fields: ours 10:23-10:25 > theirs 10:13-10:16).
- results/token_usage.json = append-only-ledger class (restore gate FORBIDDEN
  face) -> LINE-LEVEL UNION ONLY: base=:3 (later generated), assert+union the
  'machines' ledger section row-by-row (identical on both sides this window =
  zero row loss by construction, asserted), regen scalars from later derive.

All git calls CREATE_NO_WINDOW (U060). Binary-exact blob writes (no PS pipe
byte mangling). Marker scan per r637 law after resolution."""
import json
import subprocess
import sys

CREATE_NO_WINDOW = 0x08000000
ORIGIN = {  # :2
    "results/runnable_pool.json",
}
OURS = {  # :3
    "results/update_status.json",
    "results/regime_state.json",
    "results/compute_audit.json",
    "results/_attrition_guard_scan.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "docs/daily_report/REPORT-2026-10-07.json",
    "docs/daily_report/REPORT-2026-10-07.md",
    "docs/live_usage/LIVE-2026-10-07.json",
    "docs/live_usage/LIVE-2026-10-07.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
}
LEDGER = "results/token_usage.json"
ALL = ORIGIN | OURS | {LEDGER}
assert len(ALL) == 15, "face count gate: %d" % len(ALL)


def gshow(slot, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (slot, path)],
                        capture_output=True, creationflags=CREATE_NO_WINDOW)
    assert r.returncode == 0 and r.stdout, "git show %d:%s failed" % (slot, path)
    return r.stdout


def gadd(path):
    r = subprocess.run(["git", "add", "--", path], capture_output=True,
                       creationflags=CREATE_NO_WINDOW)
    assert r.returncode == 0, "git add %s failed: %s" % (path, r.stderr.decode("utf-8", "replace")[:200])


def main():
    # 1) blob-exact side picks
    for path in ORIGIN:
        blob = gshow(2, path)
        if path.endswith(".json"):
            json.loads(blob.decode("utf-8-sig"))
        with open(path, "wb") as fh:
            fh.write(blob)
        gadd(path)
        print("RESOLVED(origin) %s %dB" % (path, len(blob)))
    for path in OURS:
        blob = gshow(3, path)
        if path.endswith(".json"):
            json.loads(blob.decode("utf-8-sig"))
        with open(path, "wb") as fh:
            fh.write(blob)
        gadd(path)
        print("RESOLVED(ours)   %s %dB" % (path, len(blob)))

    # 2) token_usage.json line-level union (ledger class, forbidden wholesale)
    a = json.loads(gshow(2, LEDGER).decode("utf-8-sig"))   # origin
    b = json.loads(gshow(3, LEDGER).decode("utf-8-sig"))   # ours (later generated)
    assert str(b.get("generated", "")) >= str(a.get("generated", "")), "ours-not-later gate"
    ma, mb = a.get("machines"), b.get("machines")
    assert isinstance(ma, dict) and isinstance(mb, dict), "machines section shape gate"
    if ma == mb:
        print("machines ledger rows: IDENTICAL both sides (%d keys) = zero row loss by construction" % len(mb))
    else:
        # row-level union: per-machine row merge, list rows by identity union
        for mk in set(ma) | set(mb):
            ra, rb = ma.get(mk), mb.get(mk)
            if ra == rb:
                continue
            if isinstance(ra, list) and isinstance(rb, list):
                seen = {json.dumps(x, sort_keys=True, ensure_ascii=False) for x in ra}
                for x in rb:
                    if json.dumps(x, sort_keys=True, ensure_ascii=False) not in seen:
                        ra.append(x)
                mb[mk] = ra
                print("machines.%s: list union -> %d rows" % (mk, len(ra)))
            elif isinstance(ra, dict) and isinstance(rb, dict):
                for k in sorted(set(ra) | set(rb)):
                    va, vb = ra.get(k), rb.get(k)
                    if va == vb:
                        continue
                    if isinstance(va, (int, float)) and isinstance(vb, (int, float)):
                        ra[k] = max(va, vb)   # counters max-wins
                        print("machines.%s.%s: counter max-wins -> %s" % (mk, k, ra[k]))
                    else:
                        ra[k] = vb if str(b.get("generated", "")) >= str(a.get("generated", "")) else va
                mb[mk] = ra
            else:
                raise SystemExit("machines.%s unhandled merge shape" % mk)
    merged = b
    merged["machines"] = mb
    with open(LEDGER, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(merged, fh, ensure_ascii=False, indent=1)
    gadd(LEDGER)
    print("RESOLVED(union)   %s generated=%s machines=%d keys" % (LEDGER, merged.get("generated"), len(merged["machines"])))

    # 3) marker scan on all 15 (r637 law: no leftover conflict markers)
    bad = []
    for path in ALL:
        with open(path, "rb") as fh:
            body = fh.read()
        for marker in (b"<<<<<<<", b">>>>>>>", b"======="):
            if marker in body:
                bad.append((path, marker.decode()))
    assert not bad, "conflict-marker residue: %s" % bad
    print("MARKER SCAN: 15/15 clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
