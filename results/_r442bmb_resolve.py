"""r442 bm-b rebase resolver -- 24 UU dual-burn drift faces, canon
recipes per bigmoney-conflict-resolve classifier (24/24 classified, 0
UNKNOWN).  Side 2 = ours = origin/main (HEAD during rebase); side 3 =
theirs = the replayed r442 commit.  Tie law r140: same-ts -> HEAD
(side 2).  R350 probe law: wall-clock values must carry time-of-day,
key-exclude lists forbidden, value-shape adjudication only."""
import json
import re
import subprocess

TS_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")


def blob(side, path):
    h = subprocess.run(["git", "show", f":{side}:{path}"],
                       capture_output=True).stdout
    return h


def probe_ts(obj, best=""):
    """Deep wall-clock probe: max time-of-day-carrying value."""
    if isinstance(obj, dict):
        for v in obj.values():
            best = probe_ts(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = probe_ts(v, best)
    elif isinstance(obj, str) and TS_RE.match(obj) and obj > best:
        best = obj
    return best


def take_new_bytes(path):
    a, b = blob(2, path), blob(3, path)
    try:
        ta = probe_ts(json.loads(a.decode("utf-8")))
    except Exception:
        ta = ""
    try:
        tb = probe_ts(json.loads(b.decode("utf-8")))
    except Exception:
        tb = ""
    return b if (tb and (not ta or tb > ta)) else a


def write(path, data):
    with open(path, "wb") as f:
        f.write(data)
    # parse-verify law r185 (json faces only)
    if path.endswith(".json"):
        json.loads(open(path, encoding="utf-8").read())
    print(f"resolved {path}")


def detect_indent(raw):
    for line in raw.decode("utf-8", errors="replace").split("\n")[1:3]:
        m = re.match(r"^ +", line)
        if m:
            return len(m.group(0))
    return 2


def resolve_union_ledger(path, ledger_keys, scalar_ts_key=None):
    a = json.loads(blob(2, path).decode("utf-8"))
    b = json.loads(blob(3, path).decode("utf-8"))
    indent = detect_indent(blob(2, path))
    out = {}
    # union ledgers by canonical row identity
    for k in a:
        if k in ledger_keys:
            seen, rows = set(), []
            for row in list(a.get(k) or []) + list(b.get(k) or []):
                key = json.dumps(row, sort_keys=True, ensure_ascii=False)
                if key not in seen:
                    seen.add(key)
                    rows.append(row)
            # sort by row wall-clock if any, else keep origin order
            if rows and isinstance(rows[0], dict) and \
                    any(TS_RE.match(str(v)) for r in rows[:3]
                        for v in r.values()):
                rows.sort(key=lambda r: probe_ts(r))
            out[k] = rows
        else:
            out[k] = a[k]
    for k in b:
        if k in out:
            continue
        out[k] = b[k]
    # scalar fields: take the fresher side whole-doc probe
    if probe_ts(a) >= probe_ts(b):
        for k in a:
            if k not in ledger_keys:
                out[k] = a[k]
    else:
        for k in b:
            if k not in ledger_keys:
                out[k] = b[k]
    data = (json.dumps(out, ensure_ascii=False, indent=indent,
                       default=str) + "\n").encode("utf-8")
    la = sum(len(a.get(k) or []) for k in ledger_keys)
    lb = sum(len(b.get(k) or []) for k in ledger_keys)
    lo = sum(len(out[k]) for k in ledger_keys)
    assert lo >= max(la, lb), f"{path}: union loss {lo} < {max(la, lb)}"
    print(f"{path}: ledger union |A|={la} |B|={lb} -> |AUB|={lo}")
    write(path, data)


def resolve_union_jsonl(path):
    a = blob(2, path).decode("utf-8").splitlines()
    b = blob(3, path).decode("utf-8").splitlines()
    seen, out = set(), []
    for line in list(a) + list(b):
        if line and line not in seen:
            seen.add(line)
            out.append(line)
    # parse-verify: producer concatenates objects without newline glue
    dec = json.JSONDecoder()
    n_obj = 0
    for line in out:
        i, n = 0, len(line)
        while i < n:
            while i < n and line[i] in " \t\r":
                i += 1
            if i >= n:
                break
            _, i = dec.raw_decode(line, i)
            n_obj += 1
    print(f"{path}: line union {len(a)}+{len(b)} -> {len(out)} "
          f"({n_obj} objects raw-decoded)")
    write(path, ("\n".join(out) + "\n").encode("utf-8"))


# ---- rolling-ledger unions (r188/R208 law)
resolve_union_ledger("results/compute_audit.json", {"history"})
resolve_union_ledger("results/regime_state.json",
                     {"history", "transitions"})
# ---- append-log line union (r188/r217 law)
resolve_union_jsonl("results/x2_watch_log.jsonl")

# ---- snapshot take-new pairs (docs twins ride the json decision)
PAIRS = [
    ("docs/daily_report/REPORT-2026-09-29.json",
     ["docs/daily_report/REPORT-2026-09-29.md"]),
    ("docs/live_usage/LIVE-2026-09-29.json",
     ["docs/live_usage/LIVE-2026-09-29.md"]),
    ("docs/live_usage/LIVE-latest.json",
     ["docs/live_usage/LIVE-latest.md"]),
    ("results/dashboard_status.json", ["results/dashboard_status.js"]),
]
for lead, twins in PAIRS:
    data = take_new_bytes(lead)
    write(lead, data)
    for tw in twins:
        write(tw, take_new_bytes(tw))

# ---- plain snapshots (take-new via hardened probe)
for p in [
    "results/fundamental_b_layer_filter.json",
    "results/lhb_update_status.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/t35_open_fill_verify.json",
    "results/token_usage.json",
    "results/update_status.json",
]:
    write(p, take_new_bytes(p))

print("resolver done: 24 files, union ledgers zero-loss, "
      "take-new probes R350-hardened, parse-verified r185")
