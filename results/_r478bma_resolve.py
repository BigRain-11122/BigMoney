"""r478 bm-a rebase collision resolver (32-UU, skill bigmoney-conflict-resolve canon).

Rebase replay of orphan-recovery commit 706371cf6 (r477 RW-6) vs origin/main
(bm-c r276 + bm-b r469 same-window S6 lanes). Classifications from
classify_conflicts.py: 31 classified + 1 UNKNOWN (_attrition_guard_scan.json,
manually adjudicated = snapshot take-new: whole-doc scan evidence rewritten
each S7 scan, gate_attrition ledger itself already resolved via ALL_FACES).

Recipes applied:
- ALL_FACES 5 (compute_audit/regime_state/update_status/futures_update_status/
  token_usage): already resolved by merge_lane_views.py before this script.
- paper/*_paper.json 6 members: take :3: (local). Verified marks + all other
  fields byte-identical both sides; only runtime fields differ and local side
  carries the v3 REGIME_GUARD enforce wiring (r476 RW-4 flow standard with env
  set); origin side is bm-c legacy-env re-tick. Zero loss by identity proof.
- CODELY.md: origin base (bm-c r276 did r476 hot-cold archival; archive
  confirmed to hold the r476 entry) + r477 bm-a entry line inserted at
  Project-section tail (before '### Reference'), per r327 entry-level law.
- docs twins (REPORT/LIVE/LIVE-latest): json side picked by generated ts
  (deep probe), md byte-copied from SAME side (twin-side coupling r329).
- x2_watch_log.jsonl: line-level union zero-loss (r188).
- snapshots: take-new via staged-blob ts probe (r100 hardened: value must be
  ^20.. timestamp-shaped; wall-clock values carry time-of-day).
- dashboard_status.js: js-wrapper -> take :2: whole bytes (producer-mirror
  forbidden to rebuild json.dumps style; origin ts newer).
"""
import subprocess
import json
import sys

RESULTS = "results"


def raw(stage: str, path: str) -> bytes:
    r = subprocess.run(["git", "show", f"{stage}:{path}"], capture_output=True)
    if r.returncode != 0 or not r.stdout:
        raise RuntimeError(f"blob read failed {stage}:{path} rc={r.returncode} err={r.stderr[:120]}")
    return r.stdout


def write(path: str, data: bytes):
    with open(path, "wb") as f:
        f.write(data)


def deep_ts(obj, out, prefix=""):
    """r100/R350 hardened probe: strip _/- from keys, value must look like a timestamp."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            kl = k.lower().replace("_", "").replace("-", "")
            if isinstance(v, str) and v[:2] == "20" and (
                "ts" in kl or "generated" in kl or "updated" in kl or "asof" in kl or "at" == kl[-2:]
            ):
                # wall-clock values must carry time-of-day for max-compare
                if "T" in v or " " in v[10:]:
                    out[f"{prefix}/{k}"] = v
            deep_ts(v, out, f"{prefix}/{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:5]):
            deep_ts(v, out, f"{prefix}[{i}]")


def take_new_snapshot(path: str):
    o = json.loads(raw(':2', path))
    l = json.loads(raw(':3', path))
    to, tl = {}, {}
    deep_ts(o, to)
    deep_ts(l, tl)
    if not to and not tl:
        # no timestamp probe available: byte-identity check, else take origin (newest S6 chain by assumption) -- fail loudly
        if raw(':2', path) == raw(':3', path):
            write(path, raw(':2', path))
            return "identical"
        raise RuntimeError(f"{path}: no ts probe, sides differ -- manual adjudication required")
    omax = max(to.values()) if to else ""
    lmax = max(tl.values()) if tl else ""
    side = ":2" if omax >= lmax else ":3"
    write(path, raw(side, path))
    return f"take {side} (o={omax} l={lmax})"


def twin(base_dir: str, stem: str):
    j, m = f"{base_dir}/{stem}.json", f"{base_dir}/{stem}.md"
    oj, lj = json.loads(raw(':2', j)), json.loads(raw(':3', j))
    og, lg = oj.get("generated_at", oj.get("generated", "")), lj.get("generated_at", lj.get("generated", ""))
    if not og or not lg:
        raise RuntimeError(f"twin {j}: no generated/generated_at probe on one side -- manual adjudication")
    side = ":2" if og >= lg else ":3"
    write(j, raw(side, j))
    write(m, raw(side, m))
    return f"twin {side} (o={og} l={lg})"


def main():
    log = []

    # 1) paper 6 members: take local (identity proof done pre-script)
    for mem in ["COMPOSITE-CE-01", "COMPOSITE-CE-02", "DROUGHT-CE-01",
                "ENGULF-CE-01", "NEEDLE-DE-01", "VOLATILITY-CE-01"]:
        p = f"results/paper/{mem}_paper.json"
        o, l = raw(':2', p), raw(':3', p)
        if o == l:
            write(p, l)
            log.append(f"{p}: identical")
            continue
        # safety re-verify: marks + all fields except runtime trio identical
        oj, lj = json.loads(o), json.loads(l)
        fo = {k: v for k, v in oj.items() if k not in ("forward_guard", "regime_guard", "updated")}
        fl = {k: v for k, v in lj.items() if k not in ("forward_guard", "regime_guard", "updated")}
        assert json.dumps(fo, sort_keys=True) == json.dumps(fl, sort_keys=True), f"{p} field drift beyond runtime trio!"
        write(p, l)
        log.append(f"{p}: take :3: (v3 flow-state, fields identical beyond runtime trio)")

    # 2) CODELY.md: origin base + r477 entry insert at Project tail
    o = raw(':2', "CODELY.md").decode("utf-8")
    l = raw(':3', "CODELY.md").decode("utf-8")
    b = raw(':1', "CODELY.md").decode("utf-8")
    bl, ol, ll = b.splitlines(), o.splitlines(), l.splitlines()
    new_local = [x for x in ll if x not in set(bl) and x.strip().startswith("- [") and "r477" in x]
    assert len(new_local) == 1, f"expected exactly 1 r477 entry line, got {len(new_local)}"
    marker = "### Reference"
    idx = ol.index(marker)
    merged = ol[:idx] + new_local + ol[idx:]
    write("CODELY.md", ("\n".join(merged) + ("\n" if o.endswith("\n") else "")).encode("utf-8"))
    log.append(f"CODELY.md: origin base + r477 entry inserted before ### Reference "
               f"(base {len(bl)} -> merged {len(merged)} lines)")

    # 3) docs twins
    log.append(twin("docs/daily_report", "REPORT-2026-09-30"))
    log.append(twin("docs/live_usage", "LIVE-2026-09-30"))
    log.append(twin("docs/live_usage", "LIVE-latest"))

    # 4) x2_watch_log.jsonl: line-level union
    p = "results/x2_watch_log.jsonl"
    o_lines = raw(':2', p).decode("utf-8").splitlines()
    l_lines = raw(':3', p).decode("utf-8").splitlines()
    seen, union = set(), []
    for line in o_lines + l_lines:
        if line not in seen:
            seen.add(line)
            union.append(line)
    write(p, ("\n".join(union) + "\n").encode("utf-8"))
    log.append(f"{p}: union {len(o_lines)}+{len(l_lines)} -> {len(union)} lines zero-loss")

    # 5) snapshots take-new
    for p in ["results/daily_scorecard.json", "results/dashboard_status.json",
              "results/fundamental_b_layer_filter.json", "results/lhb_update_status.json",
              "results/paper_export/latest.json", "results/paper_export/export-2026-09-29.json",
              "results/prospect_paper/_summary.json", "results/prospect_promotion/_summary.json",
              "results/scorecard_v1.json", "results/strategy_scorecard.json",
              "results/t35_open_fill_verify.json", "results/_attrition_guard_scan.json"]:
        log.append(f"{p}: {take_new_snapshot(p)}")

    # 6) dashboard_status.js: js-wrapper -> take :2: whole bytes (origin ts newer)
    p = "results/dashboard_status.js"
    write(p, raw(':2', p))
    log.append(f"{p}: take :2: whole bytes (js-wrapper snapshot law R209)")

    for line in log:
        print(line)
    print(f"\nOK {len(log)} faces resolved")


if __name__ == "__main__":
    sys.exit(main())
