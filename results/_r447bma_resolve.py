"""r447 bm-a rebase UU resolver (residual 8 files, non-ALL_FACES fail-closed faces).

Skill recipes applied (bigmoney-conflict-resolve):
- 6x results/paper/*_paper.json  : snapshot -> whole-doc take-new via hardened deep-ts probe on 'updated'
- results/scorecard_v1.json      : snapshot -> whole-doc take-new via hardened deep-ts probe
- results/strategy_scorecard.json: snapshot -> whole-doc take-new via hardened deep-ts probe
- results/x2_watch_log.jsonl      : append-log -> line-level union zero loss (|A u B|)

Probe laws: r100 (normalize key stripping '_'/'-' BEFORE prefix match; value must be
timestamp-shaped ^20\\d{2}- before max-compare), R350 (wall-clock values require time-of-day
[T ]HH:MM; date-only values must not feed the wall-clock max; key-name EXCLUDE lists forbidden),
r311/D-20260927-09 (deep-scan nested layers), r319 (probe path existence first),
r140 (same-second tie -> HEAD side = :2: origin side during replay).
Stage law r351: :2: = origin/ours (HEAD), :3: = local/replay side.
Reads git objects via subprocess bytes (r209: no PS pipe redirection on encoding-sensitive files).
"""
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PAPER = [
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
]
SNAPSHOTS = PAPER + ["results/scorecard_v1.json", "results/strategy_scorecard.json"]
APPEND_LOG = "results/x2_watch_log.jsonl"

KEY_PREFIXES = ("asof", "updated", "generated", "ts", "cutoff", "time")
TS_SHAPE = re.compile(r"^20\d{2}-")
WALLCLOCK = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")
DATE_ONLY = re.compile(r"^20\d{2}-\d{2}-\d{2}$")


def stage_blob(stage, path):
    out = subprocess.run(
        ["git", "show", f":{stage}:{path}"], capture_output=True
    ).stdout
    return out


def norm_key(k):
    return k.replace("_", "").replace("-", "").lower()


def collect_ts(obj, path="", acc=None):
    if acc is None:
        acc = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            kp = f"{path}.{k}" if path else k
            if isinstance(v, str):
                nk = norm_key(k)
                if any(nk.startswith(p) for p in KEY_PREFIXES) and TS_SHAPE.match(v):
                    acc.append((kp, v))
            collect_ts(v, kp if isinstance(v, (dict, list)) else path, acc)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            collect_ts(v, f"{path}[{i}]", acc)
    return acc


def probe_side(raw_bytes, label):
    txt = raw_bytes.decode("utf-8", errors="replace")
    try:
        doc = json.loads(txt)
    except json.JSONDecodeError as e:
        return None, f"{label}: JSONDecodeError {e}", None
    cands = collect_ts(doc)
    wall = [(p, v) for p, v in cands if WALLCLOCK.match(v)]
    dateonly = [(p, v) for p, v in cands if DATE_ONLY.match(v)]
    return doc, cands, (wall, dateonly)


def resolve_snapshot(path):
    o_doc, o_cands, o_split = probe_side(stage_blob(2, path), ":2:origin")
    l_doc, l_cands, l_split = probe_side(stage_blob(3, path), ":3:local")
    if o_doc is None and l_doc is None:
        return f"{path}: BOTH SIDES UNPARSEABLE -- manual adjudication required"
    if o_doc is None:
        picked, side = l_doc, "local(unparseable origin)"
    elif l_doc is None:
        picked, side = o_doc, "origin(unparseable local)"
    else:
        o_wall = o_split[0]
        l_wall = l_split[0]
        if o_wall and l_wall:
            o_max = max(v for _, v in o_wall)
            l_max = max(v for _, v in l_wall)
            if l_max > o_max:
                picked, side = l_doc, f"local (wallclock {l_max} > {o_max})"
            elif o_max > l_max:
                picked, side = o_doc, f"origin (wallclock {o_max} > {l_max})"
            else:
                picked, side = o_doc, f"origin (wallclock tie {o_max} -> HEAD r140)"
        elif o_wall:
            picked, side = o_doc, "origin (only-side wallclock)"
        elif l_wall:
            picked, side = l_doc, "local (only-side wallclock)"
        else:
            o_d = max((v for _, v in o_split[1]), default="")
            l_d = max((v for _, v in l_split[1]), default="")
            if l_d > o_d:
                picked, side = l_doc, f"local (dateonly fallback {l_d} > {o_d})"
            else:
                picked, side = o_doc, f"origin (dateonly fallback {o_d} >= {l_d})"
    txt = json.dumps(picked, ensure_ascii=False, indent=2)
    if not txt.endswith("\n"):
        txt += "\n"
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(txt)
    json.loads(open(path, "r", encoding="utf-8").read())  # parse-verify (r185)
    return f"{path}: took {side}"


def resolve_append_log(path):
    o_txt = stage_blob(2, path).decode("utf-8", errors="replace").splitlines()
    l_txt = stage_blob(3, path).decode("utf-8", errors="replace").splitlines()
    o_set = set(o_txt)
    l_set = set(l_txt)
    union = o_txt + [ln for ln in l_txt if ln not in o_set]
    union_set = o_set | l_set
    # chronological re-sort by per-line ts (stable) -- append ledger ts-keyed
    def ts_key(ln):
        try:
            return json.loads(ln).get("ts", "")
        except Exception:
            return ""
    union.sort(key=ts_key)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(union) + "\n")
    ok = len(union) == len(union_set)
    return (
        f"{path}: union |ours|={len(o_txt)} |theirs|={len(l_txt)} "
        f"-> {len(union)} rows (|AuB|={len(union_set)}) zero-loss={'PASS' if ok else 'FAIL'}"
    )


def main():
    out = []
    for p in SNAPSHOTS:
        out.append(resolve_snapshot(p))
    out.append(resolve_append_log(APPEND_LOG))
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
