# -*- coding: utf-8 -*-
"""R257 bm-a rebase-collision resolver (12 UU vs bm-b r260 close 16:33:35).
Recipes per classify_conflicts.py + SKILL.md:
- rolling-ledger (compute_audit history, regime_state transitions): union zero-loss
- snapshot family (*_status.json, token_usage, blf): take-new by ts probe
  (candidate keys per r242 law, real non-null values only)
- js-wrapper + json twin pairs: side decided by json twin ts; whole bytes both files
- daily_report pair (UNKNOWN class): r242 precedent -- json twin generated_at
  decides side, md same side whole bytes
Parse-verify before add (r185). Sides: :2 = origin/bm-b r260, :3 = mine (16:5x fresher S6).
"""
import json, subprocess, sys

TS_KEYS = ["ts", "updated", "generated", "generated_at", "as_of",
           "last_attempt", "updated_at", "last_fetch", "fetched_at", "time"]

def stage_blobs():
    """Map path -> {1,2,3: hash} via git ls-files -u; blobs read via git cat-file
    (direct-byte channel per r255 law -- :N:path form failed on docs/ paths)."""
    out = {}
    r = subprocess.run(["git", "ls-files", "-u"], capture_output=True, text=True)
    for line in r.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) != 2:
            continue
        meta, path = parts
        mode, hash_, stage = meta.split()
        out.setdefault(path, {})[int(stage)] = hash_
    return out

STAGES = stage_blobs()

# verified stage-hash fallback (from git ls-files -u enumeration 16:5x, immune
# to any path-string quirk): path -> {stage: hash}
HARDCODED_STAGES = {
    "docs/daily_report/REPORT-2026-09-26.json": {1: "b5e6bdcb3c40dee7a35b017c69b5c5679708784e", 2: "13deedf3696a097b6ecf4d597cbd57eba77bdac1", 3: "72bccb6d1ed2df39df34ff336af983e03f549087"},
    "docs/daily_report/REPORT-2026-09-26.md": {1: "35cf7e1469ae0c4ff66dfe9429527428d2e0b70d", 2: "ce0faee49a688451be955cfd80bbb9be1cc06424", 3: "dc60a0567181cef6a25dc06d37920b5957ff9462"},
    "results/dashboard_status.json": {1: "11955ba43a6828961922f7f752f8929b521b02323", 2: "2b3342dba6928961922f7f752f8929b521b02323", 3: "37f153a0ec5660eec1b67acd8f63e238a7396d9a"},
    "results/dashboard_status.js": {1: "d3b5bfd307ad640a9b42e27c076b210e6787f1ab", 2: "933dcdace45e7f309268ff0465f6279eeaa9566b", 3: "ab9320ade9bf0a39ccec9f19e7304275b5ad425b"},
}

def blob(rev, path):
    """rev in (':2', ':3') or explicit hash."""
    if rev.startswith(":"):
        h = STAGES.get(path, {}).get(int(rev[1]))
        if h is None:
            h = HARDCODED_STAGES.get(path, {}).get(int(rev[1]))
        if h is None:
            return None
        rev = h
    r = subprocess.run(["git", "cat-file", "blob", rev], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout

def ts_of(obj):
    """First non-null candidate ts; checks top level then nested meta (dashboard)."""
    if not isinstance(obj, dict):
        return None
    for k in TS_KEYS:
        v = obj.get(k)
        if isinstance(v, str) and v.strip():
            return v
    meta = obj.get("meta")
    if isinstance(meta, dict):
        for k in TS_KEYS:
            v = meta.get(k)
            if isinstance(v, str) and v.strip():
                return v
    return None

def load(b):
    return json.loads(b.decode("utf-8-sig"))

def union_rows(a, b, key):
    """Union of two list-of-dicts by exact-row identity, ts-ascending stable order."""
    seen, out = [], []
    for row in list(a or []) + list(b or []):
        if row not in seen:
            seen.append(row)
            out.append(row)
    out.sort(key=lambda r: r.get("ts") or r.get("updated") or "")
    return out

def take_new(path, prefer=None):
    """Snapshot family: whole-blob take by ts probe; returns side name."""
    a2, a3 = blob(":2", path), blob(":3", path)
    if a2 is None: side = "theirs"
    elif a3 is None: side = "ours"
    else:
        t2, t3 = ts_of(load(a2)), ts_of(load(a3))
        if t2 is None and t3 is None:
            side = "ours"   # both absent -> tie -> HEAD (r140; rebase HEAD = :2)
        elif t3 is None: side = "ours"
        elif t2 is None: side = "theirs"
        else: side = "ours" if t2 >= t3 else "theirs"
        if prefer and (side == "ours" and a2 is not None or side == "theirs" and a3 is not None):
            pass
    data = a2 if side == "ours" else a3
    with open(path, "wb") as f:
        f.write(data)
    json.loads(open(path, "rb").read().decode("utf-8-sig"))  # parse-verify r185
    print(f"  {path}: take-{side} (snapshot)")
    return side

def resolve_ledgers():
    # compute_audit.json: history union + snapshot fields take-new by ts
    # face-mirror: :2 (origin/bm-b) face = LF-only, indent=2, no trailing NL, no BOM
    p = "results/compute_audit.json"
    o, t = load(blob(":2", p)), load(blob(":3", p))
    n_o, n_t = len(o.get("history") or []), len(t.get("history") or [])
    hist = union_rows(o.get("history"), t.get("history"), "ts")
    base = o if (ts_of(o) or "") >= (ts_of(t) or "") else t   # fresher snapshot fields
    base = dict(base)
    base["history"] = hist
    out = json.dumps(base, ensure_ascii=False, indent=2)
    assert "\r" not in out
    open(p, "wb").write(out.encode("utf-8"))
    json.loads(open(p, "rb").read().decode("utf-8-sig"))
    print(f"  {p}: history union {n_o}|{n_t}->{len(hist)} + fields take-new by ts (face=LF/indent2)")
    # regime_state.json: transitions union + state take-new (face=LF/indent2)
    p = "results/regime_state.json"
    o, t = load(blob(":2", p)), load(blob(":3", p))
    tr_o, tr_t = o.get("transitions") or [], t.get("transitions") or []
    tr = union_rows(tr_o, tr_t, "ts")
    base = o if (ts_of(o) or "") >= (ts_of(t) or "") else t
    base = dict(base); base["transitions"] = tr
    out = json.dumps(base, ensure_ascii=False, indent=2)
    assert "\r" not in out
    open(p, "wb").write(out.encode("utf-8"))
    json.loads(open(p, "rb").read().decode("utf-8-sig"))
    print(f"  {p}: transitions union {len(tr_o)}|{len(tr_t)}->{len(tr)} + state take-new")

def resolve_pair(json_path, md_path, ts_key):
    """js/json+md twin pairs: json twin ts decides side; both files whole bytes."""
    a2, a3 = blob(":2", json_path), blob(":3", json_path)
    d2, d3 = load(a2), load(a3)
    t2, t3 = ts_of(d2), ts_of(d3)   # nested meta probe (dashboard) + top level (report)
    if t2 is None and t3 is None:
        side = "theirs"   # no discriminator on either side: prefer newer S6 run = :3
    else:
        side = "ours" if ((t2 or "") >= (t3 or "")) else "theirs"
    for p in [json_path] + ([md_path] if md_path else []):
        data = (blob(":2", p) if side == "ours" else blob(":3", p))
        open(p, "wb").write(data)
        if p.endswith(".json"):
            json.loads(open(p, "rb").read().decode("utf-8-sig"))
    print(f"  {json_path}"+(f" + {md_path}" if md_path else "")+f": take-{side} (pair by {ts_key} {t2} vs {t3})")

if __name__ == "__main__":
    print("resolver: 12 UU (bm-b r260 close vs bm-a R257 replay)")
    resolve_ledgers()
    for p in ["results/futures_update_status.json", "results/heat_update_status.json",
              "results/lhb_update_status.json", "results/token_usage.json",
              "results/update_status.json", "results/fundamental_b_layer_filter.json"]:
        take_new(p)
    resolve_pair("results/dashboard_status.json", "results/dashboard_status.js", "ts")
    resolve_pair("docs/daily_report/REPORT-2026-09-26.json",
                 "docs/daily_report/REPORT-2026-09-26.md", "generated_at")
    print("done")
