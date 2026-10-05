# r767 bm-b rebase-UU resolver (push-rejection path, skill-sanctioned batch resolve).
# 18-UU = same-window dual S6 chain products (bm-b r767 chain 07:31-07:35 vs bm-c r604 chain ~07:36-07:38).
# Recipes: regen twins/snapshots = ts-newer-wins (r756 strptime normalization, mixed 'T'+08:00 vs ' ' forms);
#          rolling faces (compute_audit/regime_state) = history union zero-loss + take-new scalar state;
#          md/js twins same-side bound to their json twin (r708);
#          js-wrapper = whole-side bytes, ts extracted from inner JSON (R209 no re-emit);
#          fail-closed: any unresolvable face -> exit 2, no writes.
# Stages during rebase: :2: = base (origin/main side), :3: = replayed commit (bm-b r767 side).
import subprocess, json, datetime, sys, os

REPO = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"

CONFLICTS = [
    "docs/daily_report/REPORT-2026-10-06.json",
    "docs/daily_report/REPORT-2026-10-06.md",
    "docs/live_usage/LIVE-2026-10-06.json",
    "docs/live_usage/LIVE-2026-10-06.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]

TS_KEYS = ["ts", "generated", "updated", "generated_at", "written_at", "as_of", "last_run", "time"]
ROLLING_UNION_KEYS = ["history", "launches", "transitions"]

def git_bytes(ref: str) -> bytes:
    r = subprocess.run(["git", "show", ref], capture_output=True, cwd=REPO)
    if r.returncode != 0:
        raise RuntimeError(f"git show {ref} rc={r.returncode}")
    return r.stdout

def parse_ts(v):
    if not isinstance(v, str):
        return None
    s = v.strip()
    if len(s) >= 10 and s[10] == " ":
        s = s[:10] + "T" + s[11:]  # r756: normalize space separator -> T before compare
    fmts = ["%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f%z"]
    for f in fmts:
        try:
            d = datetime.datetime.strptime(s, f)
            if d.tzinfo is None:
                d = d.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=8)))
            return d
        except ValueError:
            continue
    return None

def find_ts(obj):
    """ts probe: top-level candidate keys, then one level into common containers
    (compute_audit={'latest':{...}}, dashboard_status={'meta':{...}})."""
    if isinstance(obj, dict):
        for k in TS_KEYS:
            if k in obj:
                dt = parse_ts(obj[k])
                if dt is not None:
                    return k, dt, obj[k]
        for cont in ("latest", "meta", "info", "status", "envelope"):
            sub = obj.get(cont)
            if isinstance(sub, dict):
                for k in TS_KEYS:
                    if k in sub:
                        dt = parse_ts(sub[k])
                        if dt is not None:
                            return f"{cont}.{k}", dt, sub[k]
    return None, None, None

def load_side(path):
    a = git_bytes(":2:" + path)  # base side (origin)
    b = git_bytes(":3:" + path)  # replayed side (bm-b)
    ja, jb = None, None
    try:
        ja = json.loads(a.decode("utf-8"))
    except Exception:
        pass
    try:
        jb = json.loads(b.decode("utf-8"))
    except Exception:
        pass
    return a, ja, b, jb

def union_list(x, y):
    """Identity-dedup union preserving order: x entries then y-only entries."""
    seen = set()
    out = []
    for e in x + y:
        key = json.dumps(e, sort_keys=True, ensure_ascii=False)
        if key not in seen:
            seen.add(key)
            out.append(e)
    return out, len(x), len(y)

def main() -> int:
    receipt = {"round": "r767", "kind": "rebase-uu push-rejection resolve", "files": {}}
    decisions = {}   # path -> "base"|"ours"|"union" side decision for json twins
    writes = []      # (path, bytes)
    problems = []

    # --- Pass 1: JSON faces, ts-newer-wins / rolling union ---
    for p in CONFLICTS:
        if not p.endswith(".json"):
            continue
        a, ja, b, jb = load_side(p)
        if ja is None or jb is None:
            problems.append(f"{p}: unparseable side base={ja is None} replay={jb is None}")
            continue
        ka, da, ra = find_ts(ja)
        kb, db, rb = find_ts(jb)
        if da is None and db is None:
            problems.append(f"{p}: no parseable ts on either side")
            continue
        # rolling faces: union ledger keys + take-new scalars
        rolled = False
        if p in ("results/compute_audit.json", "results/regime_state.json"):
            merged = dict(jb) if (db is not None and (da is None or db >= da)) else dict(ja)
            src_new = "replay" if (db is not None and (da is None or db >= da)) else "base"
            for k in ROLLING_UNION_KEYS:
                if k in ja or k in jb:
                    xa = ja.get(k, []) if isinstance(ja.get(k, []), list) else []
                    xb = jb.get(k, []) if isinstance(jb.get(k, []), list) else []
                    merged[k], na, nb = union_list(xa, xb)
                    receipt["files"][p] = {
                        "class": "rolling-ledger", "recipe": "union+take-new",
                        "union_key": k, "base_rows": na, "replay_rows": nb,
                        "union_rows": len(merged[k]),
                        "ts_base": ra, "ts_replay": rb, "state_taken": src_new,
                    }
                    rolled = True
                    break
            if rolled:
                out = json.dumps(merged, ensure_ascii=False, indent=1).encode("utf-8")
                writes.append((p, out))
                decisions[p] = src_new
                continue
        # snapshot / regen twin: ts-newer-wins whole doc
        if db is not None and (da is None or db >= da):
            side = "replay"
            out = b
        else:
            side = "base"
            out = a
        decisions[p] = side
        receipt["files"][p] = {
            "class": "snapshot/regen-twin", "recipe": "ts-newer-wins",
            "ts_base": ra, "ts_replay": rb, "picked": side, "ts_key_base": ka, "ts_key_replay": kb,
        }
        writes.append((p, out))

    # --- Pass 2: js-wrapper (dashboard_status.js) bound to its json twin side ---
    jsp = "results/dashboard_status.js"
    json_twin = "results/dashboard_status.json"
    if decisions.get(json_twin):
        side = decisions[json_twin]  # r708 same-side bound
        raw = git_bytes((":2:" if side == "base" else ":3:") + jsp)
        # R209: verify wrapper shape, write whole side bytes, no re-emit
        head = raw[:60].decode("utf-8", errors="replace")
        if "window.DASH_DATA" not in raw.decode("utf-8", errors="replace")[:200]:
            problems.append(f"{jsp}: wrapper shape unexpected: {head!r}")
        else:
            writes.append((jsp, raw))
            receipt["files"][jsp] = {"class": "js-wrapper", "recipe": "whole-side bytes, twin-bound", "picked": side}

    # --- Pass 3: md twins bound to their json twins (r708 same-side) ---
    md_bounds = {
        "docs/daily_report/REPORT-2026-10-06.md": "docs/daily_report/REPORT-2026-10-06.json",
        "docs/live_usage/LIVE-2026-10-06.md": "docs/live_usage/LIVE-2026-10-06.json",
        "docs/live_usage/LIVE-latest.md": "docs/live_usage/LIVE-2026-10-06.json",
        "docs/live_usage/LIVE-latest.json": "docs/live_usage/LIVE-2026-10-06.json",
        "results/scorecard_v1.json": "results/strategy_scorecard.json",
    }
    for p, twin in md_bounds.items():
        if decisions.get(twin) is None:
            problems.append(f"{p}: json twin {twin} undecided")
            continue
        side = decisions[twin]
        raw = git_bytes((":2:" if side == "base" else ":3:") + p)
        writes.append((p, raw))
        receipt["files"][p] = {"class": "twin-bound", "recipe": "same-side with json twin", "picked": side}

    if problems:
        print(json.dumps({"status": "FAIL", "problems": problems}, ensure_ascii=False))
        return 2

    # --- Verify before write (r185): every JSON write parses; union counts sane ---
    for p, data in writes:
        if p.endswith(".json"):
            json.loads(data.decode("utf-8"))
    for k, v in receipt["files"].items():
        if v.get("class") == "rolling-ledger":
            assert v["union_rows"] >= max(v["base_rows"], v["replay_rows"]), f"union loss {k}"

    # --- Write + git add ---
    for p, data in writes:
        fp = os.path.join(REPO, p.replace("/", os.sep))
        with open(fp, "wb") as f:
            f.write(data)
        r = subprocess.run(["git", "add", p], capture_output=True, cwd=REPO)
        if r.returncode != 0:
            print(json.dumps({"status": "FAIL", "add": p, "err": r.stderr.decode(errors='replace')}, ensure_ascii=False))
            return 2

    # --- Readback: no conflict markers left in any of the 18 faces ---
    leftover = []
    for p in CONFLICTS:
        fp = os.path.join(REPO, p.replace("/", os.sep))
        blob = open(fp, "rb").read()
        if b"<<<<<<<" in blob or b">>>>>>>" in blob:
            leftover.append(p)
    if leftover:
        print(json.dumps({"status": "FAIL", "markers_left": leftover}, ensure_ascii=False))
        return 2

    receipt["resolved_count"] = len(writes)
    receipt["verdict"] = "PASS"
    with open(os.path.join(REPO, "results", "_r767bmb_merge2_resolve.json"), "w", encoding="utf-8") as f:
        json.dump(receipt, f, ensure_ascii=False, indent=1)
    print(json.dumps({"status": "OK", "resolved": len(writes),
                      "sides": {p: decisions.get(p, receipt["files"][p]["picked"]) for p in CONFLICTS}},
                     ensure_ascii=False))
    return 0

if __name__ == "__main__":
    sys.exit(main())
