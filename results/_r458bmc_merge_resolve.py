"""r458 bm-c merge-conflict resolver (14 UU same-day regen faces + 2 union faces).

Laws applied (r452/r455/r656/r657 lineage):
- Both-side raw bytes via `git show HEAD:<p>` / `git show MERGE_HEAD:<p>` BEFORE any
  add (add wipes stage2/3; MERGE_HEAD in place during merge = equivalent).
- Regen faces: embedded-ts honest comparison, take-newer (deterministic same-day
  idempotent faces, zero information loss).
- compute_audit.json: cross-machine hist union, ts-identity dedup, latest=newer,
  containment assertions both ways.
- token_usage.json: machines per-key union; side-pick>0 assertion (r456 law);
  zero per-key hits -> whole-face freshness fallback (r455 precedent).
- Post-surgery: JSON reparse all, conflict-marker line-start scan (not substring,
  r657 L68 law), zero-loss assertions.
Receipt -> results/_r458bmc_merge_resolve_receipt.json
"""
import json
import re
import subprocess

CREATE_NO_WINDOW = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
TS_RE = re.compile(r"2026-10-\d\dT\d\d:\d\d:\d\d")

REGEN = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/daily_report/REPORT-2026-10-04.md",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/update_status.json",
]
UNION_HIST = "results/compute_audit.json"
UNION_MACHINES = "results/token_usage.json"


def git_show(ref, path):
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True,
                        cwd=ROOT, creationflags=CREATE_NO_WINDOW)
    if r.returncode != 0:
        raise SystemExit(f"git show {ref}:{path} rc={r.returncode}")
    return r.stdout


def ts_of(raw):
    m = TS_RE.findall(raw.decode("utf-8", "replace"))
    return max(m) if m else ""


def resolve_regen(path, receipt):
    ours = git_show("HEAD", path)
    theirs = git_show("MERGE_HEAD", path)
    to, tt = ts_of(ours), ts_of(theirs)
    pick = "ours" if to >= tt else "theirs"
    raw = ours if pick == "ours" else theirs
    if path.endswith(".json"):
        json.loads(raw.decode("utf-8-sig"))  # reparse proof before write
    with open(ROOT + "\\" + path.replace("/", "\\"), "wb") as f:
        f.write(raw)
    receipt[path] = {"strategy": "take-newer", "ours_ts": to, "theirs_ts": tt, "pick": pick}


def resolve_compute_audit(receipt):
    path = UNION_HIST
    ours = json.loads(git_show("HEAD", path).decode("utf-8-sig"))
    theirs = json.loads(git_show("MERGE_HEAD", path).decode("utf-8-sig"))
    ho = ours.get("history", [])
    ht = theirs.get("history", [])
    seen = {}
    for e in ho + ht:
        key = (e.get("ts"), e.get("machine", e.get("machine_id", "")))
        if key not in seen:
            seen[key] = e
    union = sorted(seen.values(), key=lambda e: str(e.get("ts")))
    so, st = set(map(json.dumps, ho)), set(map(json.dumps, ht))
    su = set(map(json.dumps, union))
    assert so <= su and st <= su, "compute_audit containment FAIL"
    base = ours if str(ours.get("ts", "")) >= str(theirs.get("ts", "")) else theirs
    base["history"] = union
    out = ROOT + "\\" + path.replace("/", "\\")
    with open(out, "w", encoding="utf-8", newline="") as f:
        json.dump(base, f, ensure_ascii=False, indent=1)
    receipt[path] = {"strategy": "hist-union", "ours_n": len(ho), "theirs_n": len(ht),
                     "union_n": len(union), "latest_pick": "ours" if base is ours else "theirs"}


def resolve_token_usage(receipt):
    path = UNION_MACHINES
    ours = json.loads(git_show("HEAD", path).decode("utf-8-sig"))
    theirs = json.loads(git_show("MERGE_HEAD", path).decode("utf-8-sig"))
    mo, mt = ours.get("machines", {}), theirs.get("machines", {})
    side_pick = 0
    merged = {}
    base_is_ours = str(ours.get("ts", "")) >= str(theirs.get("ts", ""))
    base = ours if base_is_ours else theirs
    for k in set(mo) | set(mt):
        if k in mo and k in mt:
            if mo[k] != mt[k]:
                side_pick += 1
                merged[k] = base.get("machines", {}).get(k, mo[k])
            else:
                merged[k] = mo[k]
        else:
            merged[k] = (mo | mt)[k]
    assert side_pick > 0 or set(mo) == set(mt), \
        "token_usage per-key leg zero side-pick without identical keyset (r456 law)"
    base["machines"] = merged
    out = ROOT + "\\" + path.replace("/", "\\")
    with open(out, "w", encoding="utf-8", newline="") as f:
        json.dump(base, f, ensure_ascii=False, indent=1)
    receipt[path] = {"strategy": "machines-union", "ours_keys": sorted(mo),
                     "theirs_keys": sorted(mt), "side_pick": side_pick,
                     "base": "ours" if base_is_ours else "theirs"}


def marker_scan(paths):
    hits = []
    for p in paths:
        with open(ROOT + "\\" + p.replace("/", "\\"), "rb") as f:
            for i, ln in enumerate(f, 1):
                if ln.startswith(b"<<<<<<<") or ln.startswith(b">>>>>>>") or ln.startswith(b"======="):
                    hits.append((p, i))
    return hits


def codely_dedup_check():
    p = ROOT + "\\CODELY.md"
    with open(p, "rb") as f:
        lines = f.read().decode("utf-8", "replace").splitlines()
    seen = set()
    dups = []
    for ln in lines:
        if ln.startswith("- [") and ln in seen:
            dups.append(ln[:80])
        if ln.startswith("- ["):
            seen.add(ln)
    return dups


def main():
    receipt = {}
    for p in REGEN:
        resolve_regen(p, receipt)
    resolve_compute_audit(receipt)
    resolve_token_usage(receipt)
    # post checks
    all_faces = REGEN + [UNION_HIST, UNION_MACHINES]
    hits = marker_scan(all_faces)
    assert not hits, f"conflict markers remain: {hits}"
    for p in all_faces:
        if p.endswith(".json"):
            with open(ROOT + "\\" + p.replace("/", "\\"), encoding="utf-8-sig") as f:
                json.load(f)  # reparse proof
    dups = codely_dedup_check()
    out = {"resolved": receipt, "marker_hits": hits, "codely_dup_lines": dups}
    with open(ROOT + r"\results\_r458bmc_merge_resolve_receipt.json", "w",
              encoding="utf-8", newline="") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("RESOLVED", len(receipt), "faces; markers:", hits, "; codely dups:", len(dups))
    for p, r in receipt.items():
        print(p, "->", r.get("strategy"), r.get("pick", r.get("base", "")))


if __name__ == "__main__":
    main()
