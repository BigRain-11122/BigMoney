"""r454 bm-a rebase conflict resolver (canon: bigmoney-conflict-resolve skill).

Storm face: my adoption commit 8da57a5e9 (dead-tick r453 S6 sweep, 77 artifacts
02:41-42) replayed onto origin/main which holds bm-c r247 S6 artifact face ->
31 UU + 1 UNKNOWN (guard scan). Stage law r351: :2: = origin side, :3: = local
(bm-a) side; tie -> :2: (r140). Host-guarded faces (r378 D-03 batch3 C-family:
daily_scorecard / strategy_scorecard / dashboard_status json+js) -> take :3:
whole bytes per R31 non-host-write-non-authoritative law. ALL_FACES conflicts
delegated to scripts/merge_lane_views.py resolve (union/take-new per face with
parse-verify; hand-written union FORBIDDEN per r376). x2_watch_log.jsonl =
line-level union + r443 raw_decode acceptance (line count == object count).
UNKNOWN _attrition_guard_scan.json = r444 manual adjudication (deep key-compare,
take-new by ts only when files face identical / superset monotone).

Hardened deep-ts probe (r100 + R350): key normalized by stripping '_'/'-'
before prefix match; value MUST be ^20\\d{2}- AND contain time-of-day (':')
-- date-only values never feed the max; key-EXCLUDE tables forbidden; probe
reads STAGED blobs, never the working tree.
"""
import json
import subprocess
import sys

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
HOST_TAKE_LOCAL = [  # r378 host=bm-a single-writer guard faces -> :3: whole bytes
    "results/dashboard_status.json",
    "results/dashboard_status.js",
    "results/daily_scorecard.json",
    "results/strategy_scorecard.json",
]
PROBE_TAKE_NEW = [  # snapshot regen faces -> hardened probe on staged blobs
    "results/scorecard_v1.json",
    "results/t35_open_fill_verify.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-09-29.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
]
ALL_FACES_DELEGATED = [  # handled first via merge_lane_views.py resolve
    "results/compute_audit.json",
    "results/regime_state.json",
    "results/update_status.json",
    "results/lhb_update_status.json",
    "results/futures_update_status.json",
    "results/token_usage.json",
    "results/fundamental_b_layer_filter.json",
]
TWIN_GROUPS = {  # probe the json member, byte-copy every member from SAME side
    "docs/daily_report/REPORT-2026-09-30.json": [
        "docs/daily_report/REPORT-2026-09-30.json",
        "docs/daily_report/REPORT-2026-09-30.md",
    ],
    "docs/live_usage/LIVE-2026-09-30.json": [
        "docs/live_usage/LIVE-2026-09-30.json",
        "docs/live_usage/LIVE-2026-09-30.md",
        "docs/live_usage/LIVE-latest.json",
        "docs/live_usage/LIVE-latest.md",
    ],
}
X2_LOG = "results/x2_watch_log.jsonl"
GUARD_SCAN = "results/_attrition_guard_scan.json"  # UNKNOWN -> manual law r444
PROBE_PREFIXES = ("generated", "updated", "asof", "stateupdated",
                  "generatedfromstateupdated", "scannedat", "lastrun")


def blob(stage, path):
    spec = f"{stage.rstrip(':')}:{path}"  # stage ':2:' -> ':2:path' (no double colon)
    r = subprocess.run(["git", "-C", ROOT, "show", spec], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"git show {spec} rc={r.returncode}: {r.stderr[:200]!r}")
    return r.stdout


def deep_ts(obj):
    best = None

    def rec(o):
        nonlocal best
        if isinstance(o, dict):
            for k, v in o.items():
                nk = k.lower().replace("_", "").replace("-", "")
                if (isinstance(v, str) and any(nk.startswith(p) for p in PROBE_PREFIXES)
                        and v[:2] == "20" and "-" in v and ":" in v):  # R350 time-of-day gate
                    if best is None or v > best:
                        best = v
                rec(v)
        elif isinstance(o, list):
            for it in o:
                rec(it)

    rec(obj)
    return best


def write_bytes(path, data):
    with open(ROOT + "\\" + path.replace("/", "\\"), "wb") as f:
        f.write(data)


def verify_json(path, data=None):
    raw = data if data is not None else open(ROOT + "\\" + path.replace("/", "\\"), "rb").read()
    json.loads(raw.decode("utf-8"))
    return True


def main():
    log = []

    def say(msg):
        log.append(msg)
        print(msg)

    # 1) ALL_FACES -> merge_lane_views resolve (canon engine, parse-verified)
    for p in ALL_FACES_DELEGATED:
        r = subprocess.run(["python", "-X", "utf8", "scripts\\merge_lane_views.py",
                            "resolve", p], capture_output=True, cwd=ROOT)
        out = (r.stdout + r.stderr).decode("utf-8", "replace").strip().splitlines()
        tail = out[-1] if out else ""
        if r.returncode != 0:
            say(f"FALLBACK-PROBE {p}: mlv rc={r.returncode} tail={tail!r}")
            sides = []
            for st in (":2:", ":3:"):
                d = blob(st, p)
                verify_json(p, d)
                sides.append((deep_ts(json.loads(d)) or "", st, d))
            sides.sort(key=lambda x: x[0])
            pick = sides[-1][2] if sides[-1][0] != sides[0][0] else blob(":2:", p)  # tie->HEAD/origin r140
            write_bytes(p, pick)
            verify_json(p)
            say(f"  -> probe take-new {p} done")
        else:
            say(f"MLV-RESOLVE {p}: {tail}")

    # 2) host-guarded faces -> :3: whole bytes (R31 authority law)
    for p in HOST_TAKE_LOCAL:
        d = blob(":3:", p)
        if p.endswith(".json"):
            verify_json(p, d)
        write_bytes(p, d)
        say(f"HOST-LOCAL {p} ({len(d)}B)")

    # 3) snapshot probe take-new on staged blobs
    for p in PROBE_TAKE_NEW:
        o = json.loads(blob(":2:", p))
        m = json.loads(blob(":3:", p))
        ot, mt = deep_ts(o), deep_ts(m)
        if mt and (not ot or mt > ot):
            side, data = ":3:", blob(":3:", p)
        elif ot and (not mt or ot > mt):
            side, data = ":2:", blob(":2:", p)
        else:
            side, data = ":2:", blob(":2:", p)  # tie -> origin/HEAD r140
        verify_json(p, data)
        write_bytes(p, data)
        say(f"TAKE-NEW {p} side={side} origin_ts={ot} mine_ts={mt}")

    # 4) twin groups: probe json member once, byte-copy ALL members same side
    for probe_path, members in TWIN_GROUPS.items():
        o = json.loads(blob(":2:", probe_path))
        m = json.loads(blob(":3:", probe_path))
        ot, mt = deep_ts(o), deep_ts(m)
        side = ":3:" if (mt and (not ot or mt > ot)) else ":2:"
        for mem in members:
            d = blob(side, mem)
            if mem.endswith(".json"):
                verify_json(mem, d)
            write_bytes(mem, d)
        say(f"TWIN {probe_path} side={side} origin_ts={ot} mine_ts={mt} ({len(members)} members)")

    # 5) x2_watch_log.jsonl: line-level union (base + origin-adds + mine-adds), r443 acceptance
    base = blob(":1:", X2_LOG).decode("utf-8", "replace").splitlines()
    orig = blob(":2:", X2_LOG).decode("utf-8", "replace").splitlines()
    mine = blob(":3:", X2_LOG).decode("utf-8", "replace").splitlines()
    seen = set()
    merged = []
    for src in (base, orig, mine):
        for ln in src:
            t = ln.strip()
            if not t or t in seen:
                continue
            seen.add(t)
            merged.append(ln)
    # r443 acceptance: every line must decode as exactly one JSON object
    ok = 0
    for ln in merged:
        t = ln.strip()
        if not t:
            continue
        dec = json.JSONDecoder()
        obj, idx = dec.raw_decode(t)
        if idx != len(t):
            raise RuntimeError(f"x2 union line not single object: {t[:80]!r}")
        ok += 1
    write_bytes(X2_LOG, ("\n".join(merged) + "\n").encode("utf-8"))
    say(f"X2-UNION lines={ok} (base={len(base)} origin={len(orig)} mine={len(mine)}) raw_decode=OK")

    # 6) UNKNOWN guard scan: r444 manual adjudication
    o = json.loads(blob(":2:", GUARD_SCAN))
    m = json.loads(blob(":3:", GUARD_SCAN))
    ot, mt = deep_ts(o), deep_ts(m)
    ok2, om2 = set(o.get("files", {})), set(m.get("files", {}))
    if o.get("files") == m.get("files"):
        side = ":3:" if (mt and (not ot or mt > ot)) else ":2:"
        verdict = "files-identical take-new by ts"
    elif om2 >= ok2 and mt and (not ot or mt > ot):
        side, verdict = ":3:", "mine superset+newer (monotone keep)"
    elif ok2 >= om2 and ot and (not mt or ot >= mt):
        side, verdict = ":2:", "origin superset+newer (monotone keep)"
    else:
        raise RuntimeError(f"guard scan files diverge both ways: origin={len(ok2)} mine={len(om2)} ts {ot}/{mt} -- manual adjudication required")
    d = blob(side, GUARD_SCAN)
    verify_json(GUARD_SCAN, d)
    write_bytes(GUARD_SCAN, d)
    say(f"GUARD-SCAN {GUARD_SCAN} side={side} verdict={verdict} origin_ts={ot} mine_ts={mt}")

    # 7) final parse-verify sweep over every resolved path
    all_paths = (HOST_TAKE_LOCAL + PROBE_TAKE_NEW + list(TWIN_GROUPS) +
                 [mem for ms in TWIN_GROUPS.values() for mem in ms] +
                 [X2_LOG, GUARD_SCAN])
    for p in all_paths:
        if p.endswith(".json"):
            verify_json(p)
    say(f"FINAL SWEEP: {len(all_paths)} paths parse-verified ({sum(1 for p in all_paths if p.endswith('.json'))} json)")
    print("RESOLVER-DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
