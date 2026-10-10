# r963 inherited-rebase UU resolver (bm-a, 2026-10-10 21:5x)
# Context: r962 session died mid push-rebase (5-min auto-kill) at pick 7f3cf0c.
# This script resolves the 9 non-ALL_FACES UU files per bigmoney-conflict-resolve skill:
#   - REPORT/LIVE twin regen faces: json side decided by deep ts probe, md byte-copied SAME side (r327/r329)
#   - fundamental_b_layer_filter: snapshot take-new by ts (R216)
#   - _attrition_guard_scan: scan receipt take-new by ts (hand-classified from UNKNOWN)
#   - d19_watermark: last-run receipt take-new by ts (hand-classified; real watermark keys live in per-machine state files)
# Probe laws: deep-scan nested (r311), probe path existence (r319), key-strip normalize + wall-clock
# time-of-day + no exclude-lists (r100/r350), staged blob not working tree (r350).
import subprocess, json, re, sys, os

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
GIT = r"C:\Program Files\Git\cmd\git.exe"

def stage_bytes(path, stage):
    r = subprocess.run([GIT, "-C", REPO, "show", ":%s:%s" % (stage, path)],
                       capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout

def norm(k):
    return k.replace("_", "").replace("-", "").lower()

WALL_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?")
PREFIXES = ("generated", "updated", "ts", "asof", "cutoff")

def deep_ts(obj):
    """Return max wall-clock ts under ts-prefixed keys; fallback to max any wall-clock value."""
    best_pref, best_any = None, None

    def rec(o):
        nonlocal best_pref, best_any
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str):
                    if WALL_RE.match(v):
                        if best_any is None or v > best_any:
                            best_any = v
                        nk = norm(k)
                        if nk.startswith(PREFIXES):
                            if best_pref is None or v > best_pref:
                                best_pref = v
                rec(v)
        elif isinstance(o, list):
            for it in o:
                rec(it)

    rec(obj)
    return best_pref, best_any

def probe_side(path, stage):
    b = stage_bytes(path, stage)
    if b is None:
        return None, None
    try:
        obj = json.loads(b.decode("utf-8-sig"))
    except Exception as e:
        raise SystemExit("probe %s :%s: json parse fail: %s" % (path, stage, e))
    p, a = deep_ts(obj)
    return p, a

def pick_side(path, prefer_pref=True):
    """Return 'ours'/'theirs' by newest ts probe (prefixed first, fallback any)."""
    op, oa = probe_side(path, 2)
    tp, ta = probe_side(path, 3)
    o_key = op if (prefer_pref and op) else oa
    t_key = tp if (prefer_pref and tp) else ta
    print("  probe[%s] ours=%s theirs=%s (pref ours=%s theirs=%s)" %
          (os.path.basename(path), o_key, t_key, op, tp))
    if o_key is None and t_key is None:
        raise SystemExit("no ts on either side: %s" % path)
    if t_key is None:
        return "ours", o_key
    if o_key is None:
        return "theirs", t_key
    if o_key > t_key:
        return "ours", o_key
    if t_key > o_key:
        return "theirs", t_key
    print("  TIE -> HEAD/ours per r140")
    return "ours", o_key

def write_side(path, side):
    stage = 2 if side == "ours" else 3
    b = stage_bytes(path, stage)
    if b is None:
        raise SystemExit("stage blob missing: :%s:%s" % (stage, path))
    if b"<<<<<<<" in b or b"=======" in b:
        raise SystemExit("stage blob has conflict markers?!")
    with open(os.path.join(REPO, path), "wb") as f:
        f.write(b)
    print("  wrote %s <- %s side (%d bytes)" % (path, side, len(b)))
    return b

def verify_json(path):
    with open(os.path.join(REPO, path), "rb") as f:
        raw = f.read()
    if b"<<<<<<<" in raw:
        raise SystemExit("marker in %s" % path)
    json.loads(raw.decode("utf-8-sig"))
    print("  parse-verify OK: %s" % path)

log = []

print("=== twin family: daily_report REPORT-2026-10-10 (json decides, md same side)")
side, ts = pick_side("docs/daily_report/REPORT-2026-10-10.json")
log.append("REPORT twins <- %s (%s)" % (side, ts))
write_side("docs/daily_report/REPORT-2026-10-10.json", side)
write_side("docs/daily_report/REPORT-2026-10-10.md", side)
verify_json("docs/daily_report/REPORT-2026-10-10.json")

print("=== twin family: live_usage LIVE-2026-10-10 + LIVE-latest (dated json decides, all 4 same side)")
side, ts = pick_side("docs/live_usage/LIVE-2026-10-10.json")
log.append("LIVE 4-file family <- %s (%s)" % (side, ts))
for p in ["docs/live_usage/LIVE-2026-10-10.json", "docs/live_usage/LIVE-2026-10-10.md",
          "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md"]:
    write_side(p, side)
verify_json("docs/live_usage/LIVE-2026-10-10.json")
verify_json("docs/live_usage/LIVE-latest.json")

print("=== snapshot: fundamental_b_layer_filter")
side, ts = pick_side("results/fundamental_b_layer_filter.json")
log.append("fundamental_b_layer_filter <- %s (%s)" % (side, ts))
write_side("results/fundamental_b_layer_filter.json", side)
verify_json("results/fundamental_b_layer_filter.json")

print("=== scan receipt: _attrition_guard_scan")
side, ts = pick_side("results/_attrition_guard_scan.json")
log.append("_attrition_guard_scan <- %s (%s)" % (side, ts))
write_side("results/_attrition_guard_scan.json", side)
verify_json("results/_attrition_guard_scan.json")

print("=== d19 last-run receipt: d19_watermark")
side, ts = pick_side("results/d19_watermark.json")
log.append("d19_watermark <- %s (%s)" % (side, ts))
write_side("results/d19_watermark.json", side)
verify_json("results/d19_watermark.json")

print("=== RESOLUTION SUMMARY ===")
for l in log:
    print(l)
print("ALL 9 MANUAL FACES RESOLVED")
