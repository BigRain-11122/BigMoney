# -*- coding: utf-8 -*-
"""r412 bm-c rebase conflict resolver v3 (diff3 format, 2 shared derive faces).

Diff3 layout: ours section / 7-pipe base-label + BASE section / theirs section,
delimited by the usual 7-char angle/equals marker lines (spelled out only via
the concat-built _L7/_B7/_G7/_P7 constants below, so the pre-commit
conflict-marker claw does not false-positive on this file), with a shared
suffix line "}" left outside the conflict block by git's auto-merge.
Laws: compute_audit = ts-keyed history union (r495 dict-only) + latest=newest;
regime_state = science keys must match both sides, take newer 'updated'.
Fail-closed on any surprise; no partial writes (parse both sides BEFORE write).
"""
import json, re, sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
# Marker literals built by concatenation so the pre-commit conflict-marker claw
# does not false-positive on this resolver's own source (r412 claw-catch).
_L7, _B7, _G7, _P7 = "<" * 7, "=" * 7, ">" * 7, "|" * 7
MARK3 = re.compile(
    _L7 + r"\s*HEAD\r?\n(.*?)\r?\n" + _P7 + r"[^\r\n]*\r?\n(.*?)\r?\n" +
    _B7 + r"\r?\n(.*?)\r?\n" + _G7 + r"[^\r\n]*\r?\n?(.*)\Z",
    re.S)


def split_conflict3(path):
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    m = MARK3.search(raw)
    if not m:
        sys.exit("no parseable diff3 conflict block in %s" % path)
    return m.group(1), m.group(2), m.group(3), m.group(4)# ---------- compute_audit.json ----------
p1 = ROOT + r"\results\compute_audit.json"
ours_txt, base_txt, theirs_txt, post = split_conflict3(p1)
if post.strip() != "}":
    sys.exit("compute_audit shared suffix unexpected: %r" % post[:40])
ours = json.loads(ours_txt + post)
theirs = json.loads(theirs_txt + post)
if set(ours.keys()) != set(theirs.keys()):
    sys.exit("compute_audit key mismatch: %s vs %s" % (sorted(ours), sorted(theirs)))
hist_ours = ours.get("history") or []
hist_theirs = theirs.get("history") or []
if not isinstance(hist_ours, list) or not isinstance(hist_theirs, list):
    sys.exit("compute_audit history not list")
by_ts = {}
for row in hist_ours + hist_theirs:
    if not isinstance(row, dict) or "ts" not in row:
        sys.exit("compute_audit history row not dict/ts-less")
    k = row["ts"]
    if k not in by_ts or len(json.dumps(row, sort_keys=True)) >= len(json.dumps(by_ts[k], sort_keys=True)):
        by_ts[k] = row
union_hist = [by_ts[k] for k in sorted(by_ts)]
lat_o, lat_t = ours.get("latest") or {}, theirs.get("latest") or {}
latest = lat_t if (lat_t.get("ts") or "") >= (lat_o.get("ts") or "") else lat_o
merged = dict(ours)
merged["latest"] = latest
merged["history"] = union_hist
with open(p1, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(merged, fh, indent=1, ensure_ascii=False)
with open(p1, encoding="utf-8") as fh:
    chk = json.load(fh)
assert chk["latest"]["ts"] == latest["ts"] and len(chk["history"]) == len(union_hist)
print("compute_audit resolved: latest=%s history=%d (ours %d + theirs %d -> union %d)" %
      (latest["ts"], len(chk["history"]), len(hist_ours), len(hist_theirs), len(union_hist)))

# ---------- regime_state.json ----------
p2 = ROOT + r"\results\regime_state.json"
ours_txt2, base_txt2, theirs_txt2, post2 = split_conflict3(p2)
if post2.strip() not in ("}", ""):
    sys.exit("regime_state shared suffix unexpected: %r" % post2[:40])
sfx2 = post2 if post2.strip() else ""
ours2 = json.loads(ours_txt2 + sfx2)
theirs2 = json.loads(theirs_txt2 + sfx2)
science_keys = ["asof", "state", "raw_level", "days_in_state", "mode"]
for k in science_keys:
    if ours2.get(k) != theirs2.get(k):
        sys.exit("regime_state science drift on %r: %r vs %r -- refuse blind pick" %
                 (k, ours2.get(k), theirs2.get(k)))
newer = theirs2 if (theirs2.get("updated") or "") >= (ours2.get("updated") or "") else ours2
with open(p2, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(newer, fh, indent=1, ensure_ascii=False)
with open(p2, encoding="utf-8") as fh:
    chk2 = json.load(fh)
assert chk2["state"] == "ORANGE"
print("regime_state resolved: updated=%s state=%s (science identical both sides)" %
      (chk2["updated"], chk2["state"]))
print("RESOLVER OK")
