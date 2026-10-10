# -*- coding: utf-8 -*-
# r856 bm-c rebase resolver: 14 UU shared regen faces (bm-b r865 same-window S6 co-run)
# bloodline: _r852bmc_rebase_resolver.py (ts-audited newer-wins per face, md twins follow json,
#            compute_audit history ts-key UNION per r773 law).
# rebase mode: :2: = ours (r856 absorb-2 dd35875a4), :3: = theirs (bm-b r865 bba56e39a).
import subprocess, json, re, io

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
GIT = r"C:\Program Files\Git\cmd\git.exe"

UU_ALL = [
    "docs/daily_report/REPORT-2026-10-11.json", "docs/daily_report/REPORT-2026-10-11.md",
    "docs/live_usage/LIVE-2026-10-11.json", "docs/live_usage/LIVE-2026-10-11.md",
    "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",            # UNION face (r773)
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
]
TWIN_OF = {  # follower -> authority
    "docs/daily_report/REPORT-2026-10-11.md": "docs/daily_report/REPORT-2026-10-11.json",
    "docs/live_usage/LIVE-2026-10-11.md": "docs/live_usage/LIVE-2026-10-11.json",
    "docs/live_usage/LIVE-latest.md": "docs/live_usage/LIVE-latest.json",
}

TS_RE = re.compile(r"(\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2}(?::\d{2})?)")

def norm_ts(s):
    if s is None:
        return None
    s = str(s)
    m = TS_RE.search(s)
    if not m:
        return None
    date, hm = m.group(1), m.group(2)
    if len(hm) == 5:
        hm += ":00"
    return date + "T" + hm

def stage_bytes(stage, path):
    r = subprocess.run([GIT, "-C", REPO, "show", ":%d:%s" % (stage, path)], capture_output=True)
    if r.returncode != 0 or not r.stdout:
        return None
    return r.stdout

def ts_of(raw):
    if raw is None:
        return None
    try:
        d = json.loads(raw.decode("utf-8", "replace"))
    except Exception:
        m = TS_RE.search(raw[:4096].decode("utf-8", "replace"))
        return norm_ts(m.group(0)) if m else None
    def dig(o):
        if isinstance(o, dict):
            for k in ("ts", "generated_at", "generated", "updated_at", "updated", "asof", "cutoff"):
                if k in o and isinstance(o[k], (str, int, float)):
                    n = norm_ts(str(o[k]))
                    if n:
                        return n
            for v in o.values():
                r = dig(v)
                if r:
                    return r
        elif isinstance(o, list):
            for v in o:
                r = dig(v)
                if r:
                    return r
        return None
    return dig(d)

def write_bytes(path, data):
    full = REPO + "\\" + path.replace("/", "\\")
    with io.open(full, "wb") as f:
        f.write(data)

def git_add(path):
    subprocess.run([GIT, "-C", REPO, "add", path], check=True)

report = []

def resolve_side(path, side, why):
    raw = stage_bytes(side, path)
    assert raw is not None and len(raw) > 0, "empty side %d for %s" % (side, path)
    assert b"<<<<<<<" not in raw and b">>>>>>>" not in raw, ("marker in staged side blob", path, side)
    write_bytes(path, raw)
    # marker-guard leg (r808 law): verify disk face clean BEFORE add
    full = REPO + "\\" + path.replace("/", "\\")
    body = io.open(full, "r", encoding="utf-8", errors="replace").read()
    assert "<<<<<<<" not in body and ">>>>>>>" not in body, ("marker on disk after resolve", path)
    git_add(path)
    report.append((path, why))

# ---- phase 1: json faces ts-newer-wins (skip union + twins) ----
json_side = {}
for p in UU_ALL:
    if p == "results/compute_audit.json" or p in TWIN_OF or not p.endswith(".json"):
        continue
    o, t = ts_of(stage_bytes(2, p)), ts_of(stage_bytes(3, p))
    if o is None and t is None:
        side, why = 2, "no-ts-both->ours"
    elif t is None:
        side, why = 2, "theirs-no-ts->ours"
    elif o is None:
        side, why = 3, "ours-no-ts->theirs"
    else:
        side = 2 if o >= t else 3
        why = "ts ours=%s theirs=%s -> %s" % (o, t, "ours" if side == 2 else "theirs")
    json_side[p] = side
    resolve_side(p, side, why)

# ---- phase 2: twin followers take authority's side (r708/r939) ----
for p, auth in TWIN_OF.items():
    side = json_side.get(auth, 2)
    resolve_side(p, side, "twin-follows %s -> %s" % (auth, "ours" if side == 2 else "theirs"))

# ---- phase 3: compute_audit.json = history ts-key union (r773) ----
o_raw, t_raw = stage_bytes(2, "results/compute_audit.json"), stage_bytes(3, "results/compute_audit.json")
o_d, t_d = json.loads(o_raw.decode("utf-8")), json.loads(t_raw.decode("utf-8"))
o_hist, t_hist = o_d.get("history", []), t_d.get("history", [])
union = {}
for e in t_hist:
    union[e.get("ts")] = e
for e in o_hist:  # ours wins same-ts collision (newer replay)
    union[e.get("ts")] = e
merged = sorted(union.values(), key=lambda e: str(e.get("ts")))
merged = merged[-201:]  # match writer cap shape
base = o_d if (ts_of(o_raw) or "") >= (ts_of(t_raw) or "") else t_d
base["history"] = merged
write_bytes("results/compute_audit.json", json.dumps(base, ensure_ascii=False, indent=1).encode("utf-8") + b"\n")
git_add("results/compute_audit.json")
report.append(("results/compute_audit.json",
               "UNION ts-key ours=%d theirs=%d -> union=%d (cap 201) latest-base=%s" %
               (len(o_hist), len(t_hist), len(merged), "ours" if base is o_d else "theirs")))

for p, why in report:
    print("%s: %s" % (p, why))
print("RESOLVED %d files (14 UU expected)" % len(report))
assert len(report) == 14, "expected 14 resolved faces, got %d" % len(report)
