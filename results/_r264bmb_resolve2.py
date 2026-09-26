# r264 bm-b wave-2 resolver (replay onto bm-a 44315b64 r262 smoke-fix closeout).
# All S6 snapshots ts-probed: take-THEIRS (18:00-01 > my 17:54-55).
# compute_audit history union; regime_state ledger-check + take-theirs;
# daily_scorecard ts-less deterministic face take-theirs; CODELY line-union.
import json
import subprocess


def stage(s, path):
    return subprocess.run(["git", "show", f":{s}:{path}"], capture_output=True).stdout


def faces(b):
    return dict(bom=b.startswith(b"\xef\xbb\xbf"), crlf=b"\r\n" in b, tail=b.endswith(b"\n"))


RESOLVED = []

# take-theirs whole bytes (ts-probed newer)
for p in [
    "docs/daily_report/REPORT-2026-09-26.json",
    "docs/daily_report/REPORT-2026-09-26.md",
    "results/update_status.json",
    "results/token_usage.json",
    "results/fundamental_b_layer_filter.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/futures_update_status.json",
    "results/dashboard_status.json",
    "results/dashboard_status.js",
    "results/daily_scorecard.json",
]:
    with open(p, "wb") as f:
        f.write(stage(2, p))
    print("take-theirs:", p)
    RESOLVED.append(p)

# compute_audit: history union by ts + state fields take-theirs
p = "results/compute_audit.json"
a, b = json.loads(stage(2, p).decode("utf-8-sig")), json.loads(stage(3, p).decode("utf-8-sig"))
ha, hb = a.get("history", []), b.get("history", [])
tsa = {h.get("ts") for h in ha}
merged = ha + [h for h in hb if h.get("ts") not in tsa]
merged.sort(key=lambda h: h.get("ts", ""))
print(f"audit history: |{len(ha)}| + |{len(hb)}| -> |{len(merged)}| union")
a["history"] = merged
base = faces(stage(2, p))
out = json.dumps(a, ensure_ascii=False, indent=1).replace("\n", "\r\n" if base["crlf"] else "\n")
if base["tail"]:
    out += "\r\n" if base["crlf"] else "\n"
with open(p, "wb") as f:
    f.write(out.encode("utf-8"))
RESOLVED.append(p)

# regime_state: union divergent list keys, else take-theirs
p = "results/regime_state.json"
a, b = json.loads(stage(2, p).decode("utf-8-sig")), json.loads(stage(3, p).decode("utf-8-sig"))
union_needed = False
for k in a:
    if isinstance(a[k], list) and a[k] != b.get(k):
        seen = {json.dumps(x, sort_keys=True) for x in a[k]}
        a[k] = a[k] + [x for x in b[k] if json.dumps(x, sort_keys=True) not in seen]
        union_needed = True
if not union_needed:
    with open(p, "wb") as f:
        f.write(stage(2, p))
    print("regime_state: take-theirs (no divergent ledger)")
else:
    base = faces(stage(2, p))
    out = json.dumps(a, ensure_ascii=False, indent=1).replace("\n", "\r\n" if base["crlf"] else "\n")
    if base["tail"]:
        out += "\r\n" if base["crlf"] else "\n"
    with open(p, "wb") as f:
        f.write(out.encode("utf-8"))
    print("regime_state: ledger union")
RESOLVED.append(p)

# CODELY.md line-union
p = "CODELY.md"
ta = stage(2, p).decode("utf-8-sig")
tb = stage(3, p).decode("utf-8-sig")
seen = set(ta.split("\n"))
newl = [l for l in tb.split("\n") if l not in seen and l.strip()]
merged = ta
if newl:
    if not merged.endswith("\n"):
        merged += "\n"
    merged += "\n".join(newl) + "\n"
print(f"CODELY: theirs + {len(newl)} mine-only lines")
with open(p, "wb") as f:
    f.write(merged.encode("utf-8"))
RESOLVED.append(p)

print("RESOLVED:", len(RESOLVED))
for p in RESOLVED:
    if p.endswith(".json"):
        json.loads(open(p, "rb").read().decode("utf-8-sig"))
print("parse-verify: ALL PASS")
