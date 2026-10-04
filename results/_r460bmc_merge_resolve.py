"""r460 bm-c REBASE-conflict resolver (21 UU same-day regen faces + 2 union semantics).

Laws applied (r452/r455/r456/r457/r658 lineage):
- Full UU inventory from porcelain FIRST (r657 ①: rebase output listing can truncate).
- REBASE direction: HEAD = new base (origin side); REBASE_HEAD = my commit being
  replayed (my side). Both-side raw bytes via git show BEFORE any add.
- Regen faces: embedded-ts honest comparison, take-newer (deterministic same-day
  idempotent faces, zero information loss).
- compute_audit.json: cross-machine hist union, ts-identity dedup, latest=newer,
  containment assertions both ways.
- token_usage.json: machines per-key union; side-pick>0 assertion (r456 law);
  identical-keyset zero-diff -> whole-face freshness fallback is legit (r455).
- Post-surgery: JSON reparse all, conflict-marker line-start scan (r657 L68 law).
Receipt -> results/_r460bmc_merge_resolve_receipt.json
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
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/update_status.json",
]
UNION_HIST = "results/compute_audit.json"
UNION_MACHINES = "results/token_usage.json"
# Known same-day regen family superset (r452/r455/r458/r460 lineage). UU inventory
# is derived from porcelain at run time (passes differ); any UU face outside this
# set = unknown territory -> hard refuse (fail-closed).
KNOWN_FAMILY = set(REGEN) | {
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/t35_open_fill_verify.json",
    UNION_HIST,
    UNION_MACHINES,
}


def git_show(ref, path):
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True,
                       cwd=ROOT, creationflags=CREATE_NO_WINDOW)
    if r.returncode != 0:
        raise SystemExit(f"git show {ref}:{path} rc={r.returncode}")
    return r.stdout


def uu_inventory():
    r = subprocess.run(["git", "status", "--porcelain=v1"], capture_output=True,
                       cwd=ROOT, creationflags=CREATE_NO_WINDOW)
    uus = []
    for ln in r.stdout.decode("utf-8", "replace").splitlines():
        if ln.startswith("UU "):
            uus.append(ln[3:].strip())
    return uus


def ts_of(raw):
    m = TS_RE.findall(raw.decode("utf-8", "replace"))
    return max(m) if m else ""


def resolve_regen(path, receipt):
    origin_side = git_show("HEAD", path)        # rebase base = origin wave side
    my_side = git_show("REBASE_HEAD", path)     # my replayed commit side
    to, tm = ts_of(origin_side), ts_of(my_side)
    pick = "mine" if tm >= to else "origin"
    raw = my_side if pick == "mine" else origin_side
    if path.endswith(".json"):
        json.loads(raw.decode("utf-8-sig"))  # reparse proof before write
    with open(ROOT + "\\" + path.replace("/", "\\"), "wb") as f:
        f.write(raw)
    receipt[path] = {"strategy": "take-newer", "origin_ts": to, "mine_ts": tm, "pick": pick}


def resolve_compute_audit(receipt):
    path = UNION_HIST
    origin_side = json.loads(git_show("HEAD", path).decode("utf-8-sig"))
    my_side = json.loads(git_show("REBASE_HEAD", path).decode("utf-8-sig"))
    ho = origin_side.get("history", [])
    hm = my_side.get("history", [])
    seen = {}
    for e in ho + hm:
        key = (e.get("ts"), e.get("machine", e.get("machine_id", "")))
        if key not in seen:
            seen[key] = e
    union = sorted(seen.values(), key=lambda e: str(e.get("ts")))
    so = set(map(json.dumps, ho))
    sm = set(map(json.dumps, hm))
    su = set(map(json.dumps, union))
    assert so <= su and sm <= su, "compute_audit containment FAIL"
    base = my_side if str(my_side.get("ts", "")) >= str(origin_side.get("ts", "")) else origin_side
    base["history"] = union
    with open(ROOT + "\\" + path.replace("/", "\\"), "w", encoding="utf-8", newline="") as f:
        json.dump(base, f, ensure_ascii=False, indent=1)
    receipt[path] = {"strategy": "hist-union", "origin_n": len(ho), "mine_n": len(hm),
                     "union_n": len(union), "latest_pick": "mine" if base is my_side else "origin"}


def resolve_token_usage(receipt):
    path = UNION_MACHINES
    origin_side = json.loads(git_show("HEAD", path).decode("utf-8-sig"))
    my_side = json.loads(git_show("REBASE_HEAD", path).decode("utf-8-sig"))
    mo, mm = origin_side.get("machines", {}), my_side.get("machines", {})
    side_pick = 0
    base_is_mine = str(my_side.get("ts", "")) >= str(origin_side.get("ts", ""))
    base = my_side if base_is_mine else origin_side
    merged = {}
    for k in set(mo) | set(mm):
        if k in mo and k in mm:
            if mo[k] != mm[k]:
                side_pick += 1
                merged[k] = base.get("machines", {}).get(k, mm[k])
            else:
                merged[k] = mo[k]
        else:
            merged[k] = {**mo, **mm}[k]
    assert side_pick > 0 or mo == mm, \
        "token_usage per-key leg zero side-pick without identical machines maps (r456 law)"
    base["machines"] = merged
    with open(ROOT + "\\" + path.replace("/", "\\"), "w", encoding="utf-8", newline="") as f:
        json.dump(base, f, ensure_ascii=False, indent=1)
    receipt[path] = {"strategy": "machines-union", "origin_keys": sorted(mo),
                     "mine_keys": sorted(mm), "side_pick": side_pick,
                     "base": "mine" if base_is_mine else "origin"}


def marker_scan(paths):
    hits = []
    for p in paths:
        with open(ROOT + "\\" + p.replace("/", "\\"), "rb") as f:
            for i, ln in enumerate(f, 1):
                if ln.startswith(b"<<<<<<<") or ln.startswith(b">>>>>>>") or ln.startswith(b"======="):
                    hits.append((p, i))
    return hits


def main():
    uus = uu_inventory()
    unknown = [p for p in uus if p not in KNOWN_FAMILY]
    assert not unknown, f"UU faces outside known regen family: {unknown}"
    regens = [p for p in uus if p not in (UNION_HIST, UNION_MACHINES)]
    receipt = {"uu_count": len(uus), "uu_faces": sorted(uus)}
    for p in regens:
        resolve_regen(p, receipt)
    if UNION_HIST in uus:
        resolve_compute_audit(receipt)
    if UNION_MACHINES in uus:
        resolve_token_usage(receipt)
    hits = marker_scan(uus)
    assert not hits, f"conflict markers remain: {hits}"
    for p in uus:
        if p.endswith(".json"):
            with open(ROOT + "\\" + p.replace("/", "\\"), encoding="utf-8-sig") as f:
                json.load(f)  # reparse proof after write
    out = {"uu_count": len(uus), "resolved": receipt, "marker_hits": hits}
    with open(ROOT + r"\results\_r460bmc_merge_resolve_receipt.json", "w",
              encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("RESOLVED", len(uus), "faces; markers:", hits)
    for p in regens:
        r = receipt[p]
        print(p, "->", r["pick"], "(origin", r["origin_ts"], "vs mine", r["mine_ts"], ")")
    if UNION_HIST in receipt:
        print(UNION_HIST, "->", receipt[UNION_HIST])
    if UNION_MACHINES in receipt:
        print(UNION_MACHINES, "->", receipt[UNION_MACHINES])


if __name__ == "__main__":
    main()
