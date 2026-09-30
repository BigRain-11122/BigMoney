# r280 bm-c rebase-wave resolver: 17-UU shared-derived-faces collision (bm-b r471 base vs bm-c r280 replay).
# Canon: r461 direction-by-ts-probe (no rebase convention), r278 wave-2 twins same-side force,
# r278 compute_audit history-union zero-loss, r140 tie -> stage2 (upstream base side).
import json
import subprocess
import sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
FILES = [
    "docs/daily_report/REPORT-2026-09-30.json",
    "docs/daily_report/REPORT-2026-09-30.md",
    "docs/live_usage/LIVE-2026-09-30.json",
    "docs/live_usage/LIVE-2026-09-30.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/prospect_promotion/_summary.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
]


def blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True,
                       cwd=ROOT)
    if r.returncode != 0:
        return None
    return r.stdout.decode("utf-8", errors="replace")


def probe_ts(obj):
    """Deepest-first shallow ts probe over dict keys."""
    if not isinstance(obj, dict):
        return ""
    for k in ("updated", "ts", "generated", "generated_at", "last_attempt",
              "updated_at", "now", "written_at", "asof"):
        v = obj.get(k)
        if isinstance(v, str) and len(v) >= 8:
            return v
    return ""


def main():
    log = []
    for path in FILES:
        s2 = blob(2, path)  # upstream base (bm-b r471)
        s3 = blob(3, path)  # my replayed r280
        if s2 is None and s3 is None:
            log.append((path, "BOTH-ABSENT", "git rm"))
            subprocess.run(["git", "rm", "-q", "--", path], cwd=ROOT)
            continue
        if s2 is None:
            log.append((path, "STAGE2-ABSENT", "take stage3"))
            open(ROOT + "\\" + path.replace("/", "\\"), "w", encoding="utf-8", newline="").write(s3)
            subprocess.run(["git", "add", "--", path], cwd=ROOT)
            continue
        if s3 is None:
            log.append((path, "STAGE3-ABSENT", "take stage2"))
            open(ROOT + "\\" + path.replace("/", "\\"), "w", encoding="utf-8", newline="").write(s2)
            subprocess.run(["git", "add", "--", path], cwd=ROOT)
            continue
        # both present
        if path.endswith(".json"):
            try:
                o2 = json.loads(s2)
                o3 = json.loads(s3)
            except Exception:
                # unparseable json face: take-new by raw ts probe fallback -> stage2 on tie
                t2, t3 = probe_ts(None), probe_ts(None)
                side = 2
                log.append((path, "JSON-PARSE-FAIL", "take stage2"))
                open(ROOT + "\\" + path.replace("/", "\\"), "w", encoding="utf-8", newline="").write(s2)
                subprocess.run(["git", "add", "--", path], cwd=ROOT)
                continue
            if path == "results/compute_audit.json":
                # rolling ledger: union history arrays by identity, latest take-new
                h2 = o2.get("history") or []
                h3 = o3.get("history") or []
                merged = {}
                for row in h2 + h3:
                    key = row.get("ts")
                    if key in merged:
                        # keep the later ts entry; identical ts -> first (stage2) wins tie
                        continue
                    merged[key] = row
                union = [merged[k] for k in sorted(merged.keys())]
                # base fields: take newer ts side
                t2, t3 = probe_ts(o2), probe_ts(o3)
                base = o2 if (t3 == "" or (t2 != "" and t2 >= t3)) else o3
                base = dict(base)
                base["history"] = union
                out = json.dumps(base, ensure_ascii=False, indent=1)
                open(ROOT + "\\" + path.replace("/", "\\"), "w", encoding="utf-8", newline="").write(out + "\n")
                subprocess.run(["git", "add", "--", path], cwd=ROOT)
                log.append((path, f"UNION {len(h2)}+{len(h3)}->{len(union)}", "history-union + latest take-new"))
                continue
            t2, t3 = probe_ts(o2), probe_ts(o3)
            if t3 != "" and (t2 == "" or t3 > t2):
                side, obj = 3, o3
            elif t2 == t3:
                side, obj = 2, o2
            else:
                side, obj = 2, o2
            out = json.dumps(obj, ensure_ascii=False, indent=1)
            open(ROOT + "\\" + path.replace("/", "\\"), "w", encoding="utf-8", newline="").write(out + "\n")
            subprocess.run(["git", "add", "--", path], cwd=ROOT)
            log.append((path, f"ts2={t2} ts3={t3}", f"take stage{side}"))
            continue
        # .md / .js faces: deterministic twins -- same-side force with their json twin when one exists,
        # else raw scan for a ts token; tie -> stage2.
        twin = None
        if path.endswith(".md"):
            twin = path[:-3] + ".json"
        forced = None
        for (p, note, act) in log:
            if p == twin and act.startswith("take stage"):
                forced = act[-1]
                break
        if forced is None:
            import re
            m2 = re.findall(r"20\d\d-\d\d-\d\d[T ]\d\d:\d\d(:\d\d)?", s2)
            m3 = re.findall(r"20\d\d-\d\d-\d\d[T ]\d\d:\d\d(:\d\d)?", s3)
            t2 = m2[-1] if m2 else ""
            t3 = m3[-1] if m3 else ""
            if t3 != "" and (t2 == "" or t3 > t2):
                forced = "3"
            else:
                forced = "2"
        side = forced
        content = s2 if side == "2" else s3
        open(ROOT + "\\" + path.replace("/", "\\"), "w", encoding="utf-8", newline="").write(content)
        subprocess.run(["git", "add", "--", path], cwd=ROOT)
        log.append((path, f"twin-force", f"take stage{side}"))
    for row in log:
        print(" | ".join(row))
    # post-verify: no UU left
    r = subprocess.run(["git", "status", "--short"], capture_output=True, cwd=ROOT)
    uu = [l for l in r.stdout.decode("utf-8", errors="replace").splitlines() if l.startswith("UU")]
    print("UU remaining:", len(uu))
    return 0 if not uu else 2


if __name__ == "__main__":
    sys.exit(main())
