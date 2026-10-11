# -*- coding: utf-8 -*-
"""r884 bm-b autostash supersession assert (r642 law: assert-before-drop, no blind pop).

Stash = dying r883 session's autostash (14:56:17 daemon snapshot, 7 faces).
HEAD = 5c4f62eda (rebased pick, absorbed live tree ~15:1x).
Assert each stash face is superseded by HEAD (newer-ts for snapshots, line-superset
for jsonl, key-row superset fallback); PASS on all => caller may checkout HEAD + drop.
"""
import json, re, subprocess, sys, os, datetime

REPO = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
FACES = [
    "results/autofill_state.bm-b.json",
    "results/ext_slots_pull_status.json",
    "results/p1d_gates.json",
    "results/runnable_pool.bm-b.json",
    "results/saturation_engine/face_bm-b.json",
    "results/saturation_engine/history_bm-b.jsonl",
    "results/saturation_engine/state_bm-b.json",
]
ISO_RE = re.compile(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?")
TS_KEY_RE = re.compile(r"(ts|time|date|asof|updated|generated|last|epoch|when|cycle)", re.I)

def git(*args):
    r = subprocess.run(["git", "-C", REPO] + list(args), capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("git rc=%d: %s" % (r.returncode, r.stderr[:300].decode("utf-8", "replace")))
    return r.stdout

def parse_iso(s):
    s = s.replace(" ", "T")
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"):
        try:
            return datetime.datetime.strptime(s[:16 if fmt.endswith("%M") else 19], fmt)
        except Exception:
            pass
    return None

def deep_ts(obj, best=None):
    if best is None: best = {"v": None}
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str):
                m = ISO_RE.search(v)
                if m:
                    t = parse_iso(m.group(0))
                    if t and (best["v"] is None or t > best["v"]): best["v"] = t
            deep_ts(v, best)
    elif isinstance(obj, list):
        for v in obj: deep_ts(v, best)
    elif isinstance(obj, str):
        m = ISO_RE.search(obj)
        if m:
            t = parse_iso(m.group(0))
            if t and (best["v"] is None or t > best["v"]): best["v"] = t
    return best["v"]

def rows_keys(obj):
    keys = set()
    def walk(o, path):
        if isinstance(o, dict):
            if o and all(not isinstance(v, (dict, list)) for v in o.values()):
                keys.add(path)
            else:
                for k, v in o.items(): walk(v, path + "/" + str(k))
        elif isinstance(o, list):
            for i, v in enumerate(o): walk(v, path + "/%d" % i)
    walk(obj, "")
    return keys

verdicts = {}
ok = True
for f in FACES:
    s_blob = git("show", "stash@{0}:" + f)
    h_blob = git("show", "HEAD:" + f)
    if s_blob == h_blob:
        verdicts[f] = "byte-identical"
        continue
    if f.endswith(".jsonl"):
        sl = [l for l in s_blob.decode("utf-8", "replace").splitlines() if l.strip()]
        hl = [l for l in h_blob.decode("utf-8", "replace").splitlines() if l.strip()]
        ss, hs = set(sl), set(hl)
        if ss <= hs:
            verdicts[f] = "line-superset head=%d stash=%d" % (len(hl), len(sl))
        else:
            verdicts[f] = "FAIL line-diff stash_only=%d" % len(ss - hs); ok = False
        continue
    try:
        sj = json.loads(s_blob.decode("utf-8", "replace"))
        hj = json.loads(h_blob.decode("utf-8", "replace"))
    except Exception as e:
        verdicts[f] = "FAIL parse %s" % e; ok = False
        continue
    ts, th = deep_ts(sj), deep_ts(hj)
    if th is not None and ts is not None and th >= ts:
        verdicts[f] = "newer-ts head=%s stash=%s" % (th, ts)
        continue
    ks, kh = rows_keys(sj), rows_keys(hj)
    if ks <= kh:
        verdicts[f] = "key-superset head=%d stash=%d (ts %s vs %s)" % (len(kh), len(ks), th, ts)
        continue
    if ts is None and th is None and sj == hj:
        verdicts[f] = "payload-equal"
        continue
    verdicts[f] = "FAIL no-dominance ts_head=%s ts_stash=%s keys_stash_only=%d" % (th, ts, len(ks - kh))
    ok = False

for f in FACES:
    print("%-56s %s" % (f, verdicts[f]))
print("ASSERT-VERDICT:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
