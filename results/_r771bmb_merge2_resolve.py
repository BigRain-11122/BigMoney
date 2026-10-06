# r771 bm-b merge-mode resolver (canonical recipes per bigmoney-conflict-resolve skill; lineage _r771bmb_resolve.py verbatim)
# MERGE context stages: stage2 = ours (HEAD = bm-b absorb commits), stage3 = theirs (origin/main).
# Tie/unknown -> stage3 (origin side, conservative; dead-session rebase script had origin=stage2, flipped here).
import subprocess, json, re, sys, os

REPO = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"

def stage_bytes(path, n):
    r = subprocess.run(["git", "-C", REPO, "show", ":%d:%s" % (n, path)], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout

def load_json(b):
    return json.loads(b.decode("utf-8-sig"))

TS_KEY_RE = re.compile(r"(generated|updated|scanned|scan_ts|asof|last_run|_ts$|^ts$|_at$)", re.I)
ISO_RE = re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}")

def probe_ts(obj, depth=0):
    best = None
    fallback = None
    def walk(o, d):
        nonlocal best, fallback
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str) and ISO_RE.search(v):
                    if TS_KEY_RE.search(k) and (best is None or v > best):
                        best = v
                    if d <= 1 and (fallback is None or v > fallback):
                        fallback = v
                if d <= 2 and isinstance(v, (dict, list)):
                    walk(v, d + 1)
        elif isinstance(o, list):
            for v in o[:5]:
                if d <= 2:
                    walk(v, d + 1)
    walk(obj, 0)
    return best or fallback

def detect_eol(b):
    return "\r\n" if b.count(b"\r\n") > b.count(b"\n") - b.count(b"\r\n") else "\n"

def detect_indent(b):
    m = re.search(rb'\n(\x20+)"', b)
    return len(m.group(1)) if m else 1

def detect_ensure_ascii(b):
    try:
        b.decode("ascii")
        return True
    except UnicodeDecodeError:
        return False

log = []

def resolve_raw(path, side, why):
    b = stage_bytes(path, side)
    assert b is not None, "stage%d missing for %s" % (side, path)
    with open(os.path.join(REPO, path), "wb") as f:
        f.write(b)
    log.append("RESOLVED %s recipe=take-raw side=%d why=%s" % (path, side, why))
    return side

def resolve_ts_new(path):
    b2, b3 = stage_bytes(path, 2), stage_bytes(path, 3)
    assert b2 is not None and b3 is not None, "stage missing for %s" % path
    t2 = probe_ts(load_json(b2)) if path.endswith(".json") else None
    t3 = probe_ts(load_json(b3)) if path.endswith(".json") else None
    if t3 is not None and (t2 is None or t3 > t2):
        side = 3
    elif t2 is not None and (t3 is None or t2 > t3):
        side = 2
    else:
        side = 3  # tie/unknown: origin side (conservative) in merge context
    with open(os.path.join(REPO, path), "wb") as f:
        f.write(b2 if side == 2 else b3)
    log.append("RESOLVED %s recipe=ts-new side=%d ts2=%s ts3=%s" % (path, side, t2, t3))
    return side

def resolve_union_ledger(path):
    b2, b3 = stage_bytes(path, 2), stage_bytes(path, 3)
    o2, o3 = load_json(b2), load_json(b3)
    eol = detect_eol(b2)
    indent = detect_indent(b2)
    ea = detect_ensure_ascii(b2)
    keys = set(o2) | set(o3)
    out = {}
    for k in sorted(keys):
        v2, v3 = o2.get(k), o3.get(k)
        if isinstance(v2, list) and isinstance(v3, list) and v2 and v3 and isinstance(v2[0], dict):
            seen = set()
            merged = []
            for e in v2 + v3:
                c = json.dumps(e, sort_keys=True, ensure_ascii=False)
                if c not in seen:
                    seen.add(c)
                    merged.append(e)
            out[k] = merged
            log.append("  %s.%s union %d+%d -> %d" % (path, k, len(v2), len(v3), len(merged)))
        elif v3 is None:
            out[k] = v2
        elif v2 is None:
            out[k] = v3
        else:
            t2, t3 = probe_ts(v2), probe_ts(v3)
            if isinstance(v2, dict) and isinstance(v3, dict):
                m = dict(v2)
                for kk in v3:
                    if kk not in m or (isinstance(v3[kk], (str, int, float)) and str(v3[kk]) > str(m.get(kk, ""))):
                        m[kk] = v3[kk]
                out[k] = m
            else:
                out[k] = v3 if (t3 is not None and (t2 is None or t3 >= t2)) else v2
    text = json.dumps(out, indent=indent, ensure_ascii=ea)
    with open(os.path.join(REPO, path), "wb") as f:
        f.write((text + eol).encode("utf-8"))
    log.append("RESOLVED %s recipe=union-ledger indent=%d eol=%s" % (path, indent, repr(eol)))

# ---- recipe table (r771 merge-2 face: 14 UU) ----
TS_NEW = [
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/update_status.json",
    "results/token_usage.json",
    "results/prospect_promotion/_summary.json",
    "docs/daily_report/REPORT-2026-10-06.json",
    "docs/live_usage/LIVE-2026-10-06.json",
    "docs/live_usage/LIVE-latest.json",
]
MD_TWINS = {
    "docs/daily_report/REPORT-2026-10-06.md": "docs/daily_report/REPORT-2026-10-06.json",
    "docs/live_usage/LIVE-2026-10-06.md": "docs/live_usage/LIVE-2026-10-06.json",
    "docs/live_usage/LIVE-latest.md": "docs/live_usage/LIVE-latest.json",
}

for p in ["results/compute_audit.json", "results/regime_state.json"]:
    resolve_union_ledger(p)
for p in TS_NEW:
    resolve_ts_new(p)
for md, js in MD_TWINS.items():
    b2, b3 = stage_bytes(js, 2), stage_bytes(js, 3)
    with open(os.path.join(REPO, js), "rb") as f:
        cur = f.read()
    side = 2 if cur == b2 else 3
    resolve_raw(md, side, "md twin follows json side=%d" % side)

# ---- validation pass (r609 laws: json parse + no conflict markers) ----
fails = []
for p in TS_NEW + list(MD_TWINS.values()) + ["results/compute_audit.json", "results/regime_state.json"]:
    full = os.path.join(REPO, p)
    if p.endswith(".json"):
        try:
            load_json(open(full, "rb").read())
        except Exception as e:
            fails.append("%s: %s" % (p, e))
for p in TS_NEW + list(MD_TWINS.keys()) + list(MD_TWINS.values()) + ["results/compute_audit.json", "results/regime_state.json"]:
    raw = open(os.path.join(REPO, p), "rb").read()
    for marker in (b"<<<<<<< ", b"=======", b">>>>>>> "):
        if marker in raw:
            fails.append("%s: leftover marker %r" % (p, marker))
for l in log:
    print(l)
print("VALIDATION:", "ALL-PASS" if not fails else fails)
sys.exit(1 if fails else 0)
