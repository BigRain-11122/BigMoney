# -*- coding: utf-8 -*-
# r790 bm-c MERGE resolver (r746/r747 race-window canon) -- claim-collision reconcile:
# local undelivered daemon commits (GENERATE harvest done + screen-0 claim) vs
# origin bm-a GENERATE claim (1316ab9e7 07:20:38). MERGE semantics: stage2=ours(local),
# stage3=theirs(origin) -- NOT rebase-reversed (r782 law does not apply here).
# r648 sha-channel blob reads + marker hard-gate + r516 deep-audit + JSON validity gate.
import subprocess, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = {"round": 790, "mode": "merge", "stage_semantics": "stage2=ours(local) stage3=theirs(origin)", "files": {}}

def catfile(sha: str) -> bytes:
    r = subprocess.run(["git", "cat-file", "-p", sha], capture_output=True, cwd=ROOT)
    if r.returncode != 0 or not r.stdout:
        raise SystemExit(f"blob read FAIL {sha} rc={r.returncode} len={len(r.stdout)}")
    return r.stdout

MARKERS = (b"<<<<<<<", b">>>>>>>", b"=======")

def marker_scan(name: str, b: bytes):
    hits = [m for m in MARKERS if m in b]
    if hits:
        raise SystemExit(f"MARKER POLLUTION {name}: {hits}")

def ls_unmerged():
    r = subprocess.run(["git", "ls-files", "-u"], capture_output=True, cwd=ROOT)
    assert r.returncode == 0, f"ls-files -u rc={r.returncode}"
    m = {}
    for line in r.stdout.decode("utf-8").splitlines():
        meta, path = line.split("\t")
        f = meta.split()
        m[(path, int(f[2]))] = f[1]
    return m

UNMERGED = ls_unmerged()

# ---------- 1) runnable_pool.json per-face max-merge ----------
POOL = "results/runnable_pool.json"
assert (POOL, 2) in UNMERGED and (POOL, 3) in UNMERGED, f"pool stage pair missing; got {sorted(UNMERGED)}"
b2, b3 = catfile(UNMERGED[(POOL, 2)]), catfile(UNMERGED[(POOL, 3)])
marker_scan(POOL + ":ours", b2)
marker_scan(POOL + ":theirs", b3)
j2, j3 = json.loads(b2), json.loads(b3)
assert set(j2.keys()) == set(j3.keys()), f"top-level key drift {set(j2.keys()) ^ set(j3.keys())}"
e2, e3 = j2["entries"], j3["entries"]
assert len(e2) == len(e3) == 418, f"entry count drift {len(e2)} vs {len(e3)}"

def shard_claim_newer(sa, sb):
    # per-face newer-wins on owner_since (S0 reland law); claim beats null-claim
    ta, tb = sa.get("owner_since") or "", sb.get("owner_since") or ""
    if ta and (not tb or ta >= tb):
        return sa.get("owner"), ta
    if tb:
        return sb.get("owner"), tb
    return sa.get("owner"), ta

merged_entries, diffs = [], []
for a, b in zip(e2, e3):
    assert a.get("id") == b.get("id"), f"entry order drift at {a.get('id')} vs {b.get('id')}"
    if a == b:
        merged_entries.append(a)
        continue
    diffs.append(a["id"])
    if a["id"] == "TRIAL-LABOR-W17-GENERATE":
        # theirs carries bm-a claim fields (owner bm-a, owner_since 07:20:38);
        # ours carries the terminal done-state (products in absorb commit a4a4390e3).
        # merged = done-state (ours, terminal, cannot regress) + claim fields newer-wins.
        m = dict(b)
        for k in ("status", "done_by", "done_at"):
            if k in a:
                m[k] = a[k]
        msh = []
        for sa in a["shards"]:
            sb = next((s for s in b["shards"] if s["key"] == sa["key"]), None)
            if sb is None or sa == sb:
                msh.append(sa)
                continue
            ms = dict(sb)
            for k, v in sa.items():
                if k not in ("owner", "owner_since"):
                    ms[k] = v
            ow, os_ = shard_claim_newer(sa, sb)
            if ow is not None:
                ms["owner"], ms["owner_since"] = ow, os_
            msh.append(ms)
        m["shards"] = msh
        merged_entries.append(m)
    elif a["id"] == "TRIAL-LABOR-W17-SCREEN-SHARD-0":
        # ours carries bm-c claim (07:20:37); theirs shard owner=null (unclaimed)
        m = dict(a)
        msh = []
        for sa in a["shards"]:
            sb = next((s for s in b["shards"] if s["key"] == sa["key"]), None)
            ow, os_ = shard_claim_newer(sa, sb if sb else {})
            if ow is not None:
                sa = dict(sa)
                sa["owner"], sa["owner_since"] = ow, os_
            msh.append(sa)
        m["shards"] = msh
        merged_entries.append(m)
    else:
        raise SystemExit(f"UNEXPECTED POOL ENTRY DIFF: {a['id']} -- manual audit required (r516 deep-audit law)")

assert set(diffs) == {"TRIAL-LABOR-W17-GENERATE", "TRIAL-LABOR-W17-SCREEN-SHARD-0"}, f"diff set drift: {diffs}"
from collections import Counter
merged_pool = dict(j2)
merged_pool["entries"] = merged_entries
status_count = dict(Counter(e.get("status", "?") for e in merged_entries))
assert status_count == {"done": 409, "ready": 9}, f"merged status counter drift {status_count}"
gen = next(e for e in merged_entries if e["id"] == "TRIAL-LABOR-W17-GENERATE")
assert gen["status"] == "done" and gen["done_by"] == "bm-c", "GENERATE merged not done-by-bm-c"
gsh = gen["shards"][0]
assert gsh["owner"] == "bm-a" and gsh["owner_since"] == "2026-10-09 07:20:38", f"GENERATE claim fields lost: {gsh.get('owner')}/{gsh.get('owner_since')}"
assert gsh["status"] == "done" and gsh["harvested_by"] == "bm-c" and gsh["done_at"] == "2026-10-09 07:20:03"
scr = next(e for e in merged_entries if e["id"] == "TRIAL-LABOR-W17-SCREEN-SHARD-0")
assert scr["shards"][0]["owner"] == "bm-c" and scr["shards"][0]["owner_since"] == "2026-10-09 07:20:37"
pool_out = json.dumps(merged_pool, ensure_ascii=False, indent=1).encode("utf-8") + b"\n"
json.loads(pool_out.decode("utf-8"))  # r504 validity gate
(ROOT / POOL).write_bytes(pool_out)
RECEIPT["files"][POOL] = {
    "decision": "per-face max-merge", "diffs": diffs, "status_count": status_count,
    "generate_face": {"status": gen["status"], "done_by": gen["done_by"], "done_at": gen["done_at"],
                      "shard_owner": gsh["owner"], "shard_owner_since": gsh["owner_since"],
                      "harvested_by": gsh.get("harvested_by"), "shard_status": gsh["status"]},
    "screen0_face": {"owner": scr["shards"][0]["owner"], "owner_since": scr["shards"][0]["owner_since"]},
    "out_bytes": len(pool_out)}

# ---------- 2) jsonl line-union (r570 union precedent, two-pointer ts merge) ----------
import re

def union_jsonl(path):
    assert (path, 2) in UNMERGED and (path, 3) in UNMERGED, f"{path} stage pair missing"
    l2 = catfile(UNMERGED[(path, 2)]).decode("utf-8").splitlines()
    l3 = catfile(UNMERGED[(path, 3)]).decode("utf-8").splitlines()

    def tskey(ln: str) -> str:
        m = re.search(r'"ts": "([^"]+)"', ln)
        return m.group(1) if m else ""

    # two-pointer stable merge: per-side order preserved, cross-side interleaved by ts
    seen, rows, bad_lines = set(), [], []
    i = j = 0
    while i < len(l2) or j < len(l3):
        take2 = j >= len(l3) or (i < len(l2) and tskey(l2[i]) <= tskey(l3[j]))
        ln = l2[i] if take2 else l3[j]
        if take2:
            i += 1
        else:
            j += 1
        if ln and ln not in seen:
            seen.add(ln)
            rows.append(ln)
            try:
                json.loads(ln)
            except Exception:
                # known historical malformed line (e.g. 2026-10-03 concatenated
                # double-object line) -- allowed ONLY if byte-identical in both
                # sides = pre-existing committed content, preserved verbatim
                assert ln in l2 and ln in l3, f"NEW malformed line introduced by merge in {path}: {ln[:80]}"
                bad_lines.append(ln[:80])
    out = ("\n".join(rows) + "\n").encode("utf-8")
    (ROOT / path).write_bytes(out)
    RECEIPT["files"][path] = {"decision": "two-pointer ts union", "ours": len(l2), "theirs": len(l3),
                              "merged": len(rows), "known_bad_preserved": len(bad_lines),
                              "out_bytes": len(out)}

union_jsonl("results/pool_core_samples.jsonl")
union_jsonl("results/pool_red_flags.jsonl")

# ---------- 3) marker sweep on all resolved files (r705 verify-leg law) ----------
bad = [p for p in RECEIPT["files"] if any(m in (ROOT / p).read_bytes() for m in MARKERS)]
assert not bad, f"marker residue {bad}"
RECEIPT["marker_sweep"] = "CLEAN"
RECEIPT["unmerged_files_seen"] = sorted({p for (p, s) in UNMERGED})

outp = ROOT / "results/_r790bmc_merge_resolver.json"
outp.write_text(json.dumps(RECEIPT, ensure_ascii=False, indent=1), encoding="utf-8")
print("MERGE_RESOLVER_OK files=", len(RECEIPT["files"]), "pool_status=", status_count,
      "pool_entries=", len(merged_entries))
