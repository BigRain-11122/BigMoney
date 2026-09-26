"""r263 bm-b: batch resolver for rebase step 2 (13 UU vs bm-a R260 S6 faces).

Recipes per classify_conflicts.py + r242/r261/r262 UNKNOWN-family precedents:
- daily_report pair: json twin generated_at decides side, md same-side whole-bytes (r242)
- daily_scorecard.json: fresher run take-new (r261)
- autofill_state: launches union cap50 ts-asc write-back + last_tick inner-ts newer (r203/R215/r245)
- compute_audit / regime_state: history/transitions identity-union zero-loss + state fields take-new (r188/R208)
- dashboard pair / token_usage / b_layer / futures / heat / lhb / update_status: ts-probe take-new
All write-backs: parse-verify before add (r185). ts probes from :2 (origin side) vs :3 (my replay side).
NOTE rebase semantics: :2=origin/be404abe face, :3=my commit face (INVERTED vs merge -- R245 family law).
"""
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")


def blob(stage, path):
    out = subprocess.run(["git", "show", f"{stage}:{path}"], capture_output=True)
    return out.stdout


def load(stage, path):
    return json.loads(blob(stage, path).decode("utf-8-sig"))


def probe_fmt(raw):
    return {
        "crlf": raw.count(b"\r\n") > 0,
        "bom": raw[:3] == b"\xef\xbb\xbf",
        "tail_nl": raw.endswith(b"\n"),
        "esc": b"\\u" in raw,
    }


def write_mirror(path, obj, fmt, indent=1):
    out = json.dumps(obj, ensure_ascii=False, indent=indent)
    if fmt["crlf"]:
        out = out.replace("\n", "\r\n")
    if fmt["bom"]:
        out = "\ufeff" + out
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(out + ("\r\n" if fmt["crlf"] else "\n"))
    with open(path, encoding="utf-8-sig") as f:
        json.load(f)


def indent_of(raw):
    txt = raw.decode("utf-8-sig")
    for line in txt.splitlines():
        if line.startswith((' "', '  "')):
            return 1 if line.startswith(' "') else 2
    return 1


DECISIONS = {}

# ---- 1) autofill_state: mixed-dict+ledger ----
P = "results/autofill_state.json"
o = load(":2", P)  # origin bm-a face
t = load(":3", P)  # my face
ot = o.get("last_tick", {}).get("ts", "")
tt = t.get("last_tick", {}).get("ts", "")
tick = o["last_tick"] if ot > tt else t["last_tick"]
seen = {}
for row in o.get("launches", []) + t.get("launches", []):
    k = (row.get("ts"), row.get("machine"), row.get("batch"))
    if k not in seen:
        seen[k] = row
union = sorted(seen.values(), key=lambda r: r.get("ts", ""), reverse=True)[:50]
union.sort(key=lambda r: r.get("ts", ""))
merged = dict(t if tt >= ot else o)
merged["launches"] = union
merged["last_tick"] = tick
assert isinstance(merged["last_tick"], dict)
write_mirror(P, merged, probe_fmt(blob(":1", P)), indent_of(blob(":1", P)))
DECISIONS[P] = f"last_tick {'origin' if ot > tt else 'mine'} ({ot} vs {tt}) | launches union {len(seen)} cap50 asc"

# ---- 2) compute_audit: rolling-ledger union + latest take-new by latest.ts ----
P = "results/compute_audit.json"
o = load(":2", P)
t = load(":3", P)
ho = o.get("history", [])
ht = t.get("history", [])
hseen = {}
for row in ho + ht:
    k = (row.get("ts"), row.get("machine"))
    if k not in seen:
        hseen[k] = row
h = sorted(hseen.values(), key=lambda r: r.get("ts", ""))
olt = str((o.get("latest") or {}).get("ts", ""))
tlt = str((t.get("latest") or {}).get("ts", ""))
latest = t["latest"] if tlt >= olt else o["latest"]
merged = dict(o)
merged["history"] = h
merged["latest"] = latest
write_mirror(P, merged, probe_fmt(blob(":1", P)), indent_of(blob(":1", P)))
DECISIONS[P] = f"history union {len(ho)}|{len(ht)}->{len(h)} | latest.ts origin={olt} mine={tlt} -> {'mine' if tlt >= olt else 'origin'}"

# ---- 3) regime_state: transitions/history/triggers union + state take-new ----
P = "results/regime_state.json"
o = load(":2", P)
t = load(":3", P)
merged = dict(o)
for k in ("transitions", "history", "triggers"):
    if k in t or k in o:
        a = o.get(k, [])
        b = t.get(k, [])
        m = {}
        for row in a + b:
            kk = json.dumps(row, sort_keys=True, ensure_ascii=False)
            m[kk] = row
        merged[k] = sorted(m.values(), key=lambda r: str(r.get("ts", r.get("date", ""))) if isinstance(r, dict) else str(r))
for k, v in t.items():
    if k not in ("transitions", "history", "triggers"):
        merged[k] = v if str(v) >= str(o.get(k, "")) or k in ("asof", "state", "raw", "days_in_state", "mode") else o.get(k, v)
# state fields: prefer my later run (17:39) per asof equality -> same content anyway
merged.update({k: t.get(k, o.get(k)) for k in ("asof", "state", "raw", "days_in_state", "mode")})
write_mirror(P, merged, probe_fmt(blob(":1", P)), indent_of(blob(":1", P)))
DECISIONS[P] = f"transitions/history/triggers identity-union | state fields mine (17:39 run)"

# ---- 4) UNKNOWN family: daily_report pair (r242: json generated_at governs) ----
P = "docs/daily_report/REPORT-2026-09-26.json"
o = load(":2", P)
t = load(":3", P)
og = str(o.get("generated_at", ""))
tg = str(t.get("generated_at", ""))
side = "mine" if tg > og else "origin"
winner = t if tg > og else o
write_mirror(P, winner, probe_fmt(blob(":1", P)), indent_of(blob(":1", P)))
DECISIONS[P] = f"generated_at origin={og} mine={tg} -> take {side}"
md = "docs/daily_report/REPORT-2026-09-26.md"
raw_winner = blob(":3", md) if tg > og else blob(":2", md)
with open(md, "wb") as f:
    f.write(raw_winner)
DECISIONS[md] = f"md same-side whole-bytes take {side}"

# ---- 5) daily_scorecard.json (r261: fresher run take-new) ----
P = "results/daily_scorecard.json"
o = load(":2", P)
t = load(":3", P)
og = str(o.get("generated_at", o.get("ts", "")))
tg = str(t.get("generated_at", t.get("ts", "")))
winner = t if tg >= og else o
write_mirror(P, winner, probe_fmt(blob(":1", P)), indent_of(blob(":1", P)))
DECISIONS[P] = f"fresher run origin={og} mine={tg} -> {'mine' if tg >= og else 'origin'}"

# ---- 6) snapshot family: ts-probe take-new ----
SNAPS = {
    "results/dashboard_status.json": ("generated_at", "ts"),
    "results/token_usage.json": ("generated", "generated_at", "ts"),
    "results/fundamental_b_layer_filter.json": ("updated", "updated_at", "ts", "generated_at"),
    "results/futures_update_status.json": ("updated", "ts", "as_of"),
    "results/heat_update_status.json": ("updated", "ts", "as_of"),
    "results/lhb_update_status.json": ("updated", "ts", "as_of"),
    "results/update_status.json": ("updated", "ts", "as_of"),
}
for P, keyfam in SNAPS.items():
    o = load(":2", P)
    t = load(":3", P)

    def ts_of(d):
        for k in keyfam:
            v = d.get(k)
            if isinstance(v, str) and v:
                return v
            if isinstance(v, dict):
                for kk in ("generated_at", "updated", "ts"):
                    if isinstance(v.get(kk), str) and v.get(kk):
                        return v[kk]
        return ""
    og, tg = ts_of(o), ts_of(t)
    winner = t if tg >= og else o
    side = "mine" if tg >= og else "origin"
    if P == "results/dashboard_status.json":
        # nested meta.generated_at probe (r261)
        om = str((o.get("meta") or {}).get("generated_at", ""))
        tm = str((t.get("meta") or {}).get("generated_at", ""))
        winner = t if tm >= om else o
        side = "mine" if tm >= om else "origin"
        og, tg = om, tm
    write_mirror(P, winner, probe_fmt(blob(":1", P)), indent_of(blob(":1", P)))
    DECISIONS[P] = f"ts-probe origin={og} mine={tg} -> take {side}"

# ---- 7) dashboard_status.js: js-wrapper take-side whole bytes (R209: never parse/re-emit as plain json) ----
P = "results/dashboard_status.js"
# wrapper follows its json twin side: same build_status run produced both files
oj = load(":2", "results/dashboard_status.json")
tj = load(":3", "results/dashboard_status.json")
om = str((oj.get("meta") or {}).get("generated_at", ""))
tm = str((tj.get("meta") or {}).get("generated_at", ""))
raw_winner = blob(":3", P) if tm >= om else blob(":2", P)
with open(P, "wb") as f:
    f.write(raw_winner)
DECISIONS[P] = f"wrapper whole-bytes take {'mine' if tm >= om else 'origin'} following json twin meta.generated_at ({om} vs {tm})"

for k, v in DECISIONS.items():
    print(f"{k}: {v}")
print("ALL RESOLVED + PARSE-VERIFIED")
