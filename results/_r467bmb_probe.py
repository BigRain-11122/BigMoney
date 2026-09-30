# r467 bm-b S0 rebase replay conflict probe: classify 19 UNKNOWN faces (stage2 vs stage3 structure+ts)
import subprocess, json, re, sys

TS_RE = re.compile(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}(?::\d{2})?")

def stage_bytes(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    if r.returncode != 0:
        sys.exit(f"stage read fail {stage} {path}: {r.stderr[:200]}")
    return r.stdout

def deep_ts(obj, best=""):
    if isinstance(obj, dict):
        for v in obj.values():
            best = deep_ts(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = deep_ts(v, best)
    elif isinstance(obj, str):
        for m in TS_RE.finditer(obj):
            c = m.group(0)
            if len(c) >= 16 and c > best:
                best = c
    return best

def shape(obj, depth=0):
    if depth > 2:
        return "..."
    if isinstance(obj, dict):
        return {k: shape(v, depth+1) for k, v in list(obj.items())[:14]}
    if isinstance(obj, list):
        return [f"list[{len(obj)}]", shape(obj[0], depth+1) if obj else None]
    return type(obj).__name__

FILES = [
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/daily_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/strategy_scorecard.json",
    "results/scorecard_v1.json",
    "results/paper/marks/marks-20260930.jsonl",
    "results/x2_watch_log.jsonl",
]
for p in FILES:
    try:
        b2, b3 = stage_bytes(2, p), stage_bytes(3, p)
    except SystemExit as e:
        print(f"[{p}] STAGE READ FAIL: {e}")
        continue
    if p.endswith(".jsonl"):
        l2 = b2.decode("utf-8").splitlines()
        l3 = b3.decode("utf-8").splitlines()
        s2, s3 = set(l2), set(l3)
        print(f"[{p}] :2={len(l2)}lines :3={len(l3)}lines only2={len(s2-s3)} only3={len(s3-s2)} superset3={not (s2-s3)}")
        continue
    try:
        j2 = json.loads(b2.decode("utf-8"))
        j3 = json.loads(b3.decode("utf-8"))
    except Exception as e:
        print(f"[{p}] PARSE FAIL: {e}; :2 {len(b2)}B :3 {len(b3)}B")
        continue
    t2, t3 = deep_ts(j2), deep_ts(j3)
    same = "IDENTICAL" if b2 == b3 else "DIFF"
    print(f"[{p}] {same} ts2={t2!r} ts3={t3!r} newer={'s3' if t3 > t2 else ('s2' if t2 > t3 else 'TIE')}")
    if same == "DIFF":
        print(f"  :2 shape {json.dumps(shape(j2))[:400]}")
        print(f"  :3 shape {json.dumps(shape(j3))[:400]}")
