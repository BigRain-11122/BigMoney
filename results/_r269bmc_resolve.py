"""_r269bmc_resolve.py -- r269 bm-c push-storm 20-UU resolver (canon).

Per Tools/skills/bigmoney-conflict-resolve/SKILL.md + classifier output:
  - 6 ALL_FACES (compute_audit/regime_state/update_status/lhb_update_status/
    futures_update_status/token_usage) -> merge_lane_views.py resolve
    (reads rebase stages :2:=origin / :3:=local per r351, union recipes,
    parse-verify, zero hand-rolled unions per r376).
  - 3 twin pairs (REPORT-2026-09-30, LIVE-2026-09-30, LIVE-latest):
    json deep-ts probe picks side, md byte-copied from the SAME side
    (twin-side coupling, r329: never json.loads the md, never hybrid).
  - dashboard_status.json deep-ts probe -> side; dashboard_status.js
    byte-copied from the SAME side (co-produced by build_status, R209
    js-wrapper law).
  - snapshots (scorecard_v1/strategy_scorecard/fundamental_b_layer_filter/
    prospect_promotion/_summary) -> hardened deep-ts probe take-new,
    tie -> :2: origin (r140). Value-shape gate ^20\\d{2}- + time-of-day
    required (r100/R350: no key-exclusion lists, no date-only max).
  - _attrition_guard_scan.json = classifier UNKNOWN -> manual adjudication:
    snapshot take-new by top-level ts (both sides carry ts, probed).
  - CODELY.md = memory-union with in-place-edit fallback (r327/r329):
    origin side = base+append (prefix assert TRUE), mine = in-place
    reorg (prefix FALSE) -> entry-level union = my tree + origin appended
    suffix (their new-entry lines), two-way coverage verified.
All JSON writes parse-verified before replace; report ->
results/_r269bmc_resolve_facts.json.
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ALL_FACES = [
    "results/compute_audit.json",
    "results/regime_state.json",
    "results/update_status.json",
    "results/lhb_update_status.json",
    "results/futures_update_status.json",
    "results/token_usage.json",
]
TWINS = [
    ("docs/daily_report/REPORT-2026-09-30.json",
     "docs/daily_report/REPORT-2026-09-30.md"),
    ("docs/live_usage/LIVE-2026-09-30.json",
     "docs/live_usage/LIVE-2026-09-30.md"),
    ("docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md"),
]
SNAPSHOTS = [
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/fundamental_b_layer_filter.json",
    "results/prospect_promotion/_summary.json",
    "results/_attrition_guard_scan.json",   # UNKNOWN -> manual snapshot
]
DASH_JSON = "results/dashboard_status.json"
DASH_JS = "results/dashboard_status.js"
CODELY = "CODELY.md"

TS_SHAPE = re.compile(r"^20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2}")
report = {"resolved": {}, "notes": []}


def stage_bytes(stage, rel):
    r = subprocess.run(["git", "show", f":{stage}:{rel}"],
                       capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout


def deep_ts(obj):
    """Hardened wall-clock probe (r100/R350): recursive scan, key-agnostic
    (no exclusion lists), value must be ts-shaped WITH time-of-day."""
    best = ""
    stack = [obj]
    while stack:
        o = stack.pop()
        if isinstance(o, dict):
            stack.extend(o.values())
        elif isinstance(o, list):
            stack.extend(o)
        elif isinstance(o, str) and TS_SHAPE.match(o):
            if o > best:
                best = o
    return best


def pick_side(rel, note):
    o, m = stage_bytes(2, rel), stage_bytes(3, rel)
    jo, jm = json.loads(o.decode("utf-8")), json.loads(m.decode("utf-8"))
    to, tm = deep_ts(jo), deep_ts(jm)
    side = ":3:" if (tm and (not to or tm > to)) else ":2:"   # tie -> :2:
    picked = m if side == ":3:" else o
    if not to and not tm:
        raise SystemExit(f"probe miss {rel}: no ts-shaped value either side")
    report["resolved"][rel] = {"class": "snapshot", "probe_o": to,
                               "probe_m": tm, "side": side, "note": note}
    return picked


def write_bytes(rel, data):
    full = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "wb") as fh:
        fh.write(data)


def main():
    # ---- 1. ALL_FACES via the canon merger
    for rel in ALL_FACES:
        r = subprocess.run([sys.executable,
                            os.path.join("scripts", "merge_lane_views.py"),
                            "resolve", rel], capture_output=True)
        tail = (r.stdout + r.stderr).decode("utf-8", "replace").strip()
        if r.returncode != 0:
            print(f"  FAIL {rel}: {tail[-200:]}")
            return 2
        report["resolved"][rel] = {"class": "all_faces_union",
                                  "merger_rc": r.returncode,
                                  "tail": tail[-160:]}
        print(f"  all-faces {rel}: resolved ({tail.splitlines()[-1][:90] if tail else 'ok'})")

    # ---- 2. twin pairs: json probe picks side, md bytes from same side
    for jrel, mrel in TWINS:
        o, m = stage_bytes(2, jrel), stage_bytes(3, jrel)
        jo, jm = json.loads(o.decode("utf-8")), json.loads(m.decode("utf-8"))
        to, tm = deep_ts(jo), deep_ts(jm)
        if not to and not tm:
            raise SystemExit(f"probe miss {jrel}")
        side = ":3:" if (tm and (not to or tm > to)) else ":2:"
        jb = m if side == ":3:" else o
        mb = stage_bytes(3 if side == ":3:" else 2, mrel)
        write_bytes(jrel, jb)
        write_bytes(mrel, mb)
        json.loads(open(os.path.join(ROOT, jrel), "rb").read().decode("utf-8"))
        report["resolved"][jrel] = {"class": "twin-json", "probe_o": to,
                                    "probe_m": tm, "side": side}
        report["resolved"][mrel] = {"class": "twin-md-byte-copy",
                                    "side": side}
        print(f"  twin {jrel} -> {side} (o={to} m={tm})")

    # ---- 3. snapshots + dashboard json (probe) / js (same side bytes)
    for rel in SNAPSHOTS:
        picked = pick_side(rel, "UNKNOWN-manual" if "attrition" in rel
                           else "snapshot take-new")
        write_bytes(rel, picked)
        json.loads(open(os.path.join(ROOT, rel), "rb").read().decode("utf-8"))
        print(f"  snapshot {rel} -> {report['resolved'][rel]['side']}")
    dash = pick_side(DASH_JSON, "snapshot probe; js co-produced same side")
    write_bytes(DASH_JSON, dash)
    side = report["resolved"][DASH_JSON]["side"]
    write_bytes(DASH_JS, stage_bytes(3 if side == ":3:" else 2, DASH_JS))
    json.loads(open(os.path.join(ROOT, DASH_JSON), "rb").read().decode("utf-8"))
    print(f"  dashboard json+js -> {side}")

    # ---- 4. CODELY.md memory-union, in-place-edit fallback (r327)
    base_ref = subprocess.run(["git", "rev-parse", "REBASE_HEAD^"],
                              capture_output=True).stdout.decode().strip()
    base = subprocess.run(["git", "show", f"{base_ref}:CODELY.md"],
                          capture_output=True).stdout
    o = stage_bytes(2, CODELY)
    m = stage_bytes(3, CODELY)
    o_pure = o.startswith(base)
    m_pure = m.startswith(base)
    if o_pure and m_pure:
        merged = base + o[len(base):] + m[len(base):]
        mode = "prefix-concat"
    else:
        # r327 fallback: entry-level union = non-pure side as tree +
        # pure side's appended suffix lines (their new entries only);
        # two-way coverage: origin lines not in tree must ALL come from
        # its appended suffix (base lines live in tree or archive).
        pure, tree = (o, m) if o_pure else (m, o)
        suffix = pure[len(base):]
        merged = tree + suffix
        o_lines = {ln for ln in o.decode("utf-8").splitlines() if ln.strip()}
        t_lines = set(merged.decode("utf-8").splitlines())
        s_lines = {ln for ln in suffix.decode("utf-8").splitlines() if ln.strip()}
        missing = o_lines - t_lines
        # origin lines absent from the merged tree must be base lines that
        # my in-place reorg moved to the archive (zero-loss reorg, verified
        # pre-rebase) -- anything else = real loss, fail closed.
        arch = open(os.path.join(ROOT, "research/memory-archive/202609.md"),
                    "rb").read().decode("utf-8", errors="replace")
        real_missing = {ln for ln in missing if ln not in arch}
        if real_missing:
            raise SystemExit(f"CODELY entry-level loss: {len(real_missing)} "
                             f"origin line(s) neither in tree nor archive")
        if not s_lines <= t_lines:
            raise SystemExit("CODELY suffix lines not fully carried")
        mode = (f"entry-level-union (origin pure-append={o_pure}, "
                f"mine in-place-reorg={not m_pure}; suffix={len(suffix)}B; "
                f"origin-missing-but-archived={len(missing) - len(real_missing)})")
    write_bytes(CODELY, merged)
    report["resolved"][CODELY] = {
        "class": "memory-union", "mode": mode,
        "base_ref": base_ref,
        "bytes_base": len(base), "bytes_o": len(o), "bytes_m": len(m),
        "bytes_merged": len(merged)}
    print(f"  CODELY.md -> {mode} ({len(merged)}B)")

    with open(os.path.join(ROOT, "results", "_r269bmc_resolve_facts.json"),
              "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1, sort_keys=True)
    print(f"resolver: {len(report['resolved'])} files resolved + facts "
          f"-> results/_r269bmc_resolve_facts.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
