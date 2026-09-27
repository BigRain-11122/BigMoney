# -*- coding: utf-8 -*-
"""r97 bm-c rebase-resolve: 26-UU same-window S6-family storm (bm-a r344 vs bm-c r97).
Laws applied:
- r342 wave-2: same-family re-derivation faces -> take-new byte-verbatim by deep-ts (M side uniformly newer 18:48:3x-18:51:1x vs A 18:48:0x-18:50:2x).
- r84/r96: autofill_state last_tick same-second tie (both 18:50:01) -> HEAD (bm-a) side, launches asserted identical.
- r342: compute_audit rolling-ledger union by (ts,machine) key, zero-loss, ts-asc sort, latest=newest row.
- r333/r334: x2_watch_log append-log line union (both sides' distinct-ts watch lines kept).
Sides: HEAD = origin/main (bm-a r344 tip aee0fa02), MINE = 32b4edae.
Stage with -c core.autocrlf=false to preserve blob byte-face (r343 law). Resolve BEFORE :X0:02 tick (r91 law)."""
import subprocess, json, sys

MINE = "32b4edae"

def blob(ref, path):
    r = subprocess.run(["git", "show", "%s:%s" % (ref, path)], capture_output=True)
    assert r.returncode == 0, (ref, path, r.stderr[:200])
    return r.stdout

def stage(path, data):
    with open(path, "wb") as f:
        f.write(data)
    subprocess.run(["git", "-c", "core.autocrlf=false", "add", path], check=True)

# ---------- 1) take-new byte-verbatim (M side freshest, deep-ts probed) ----------
TAKE_M = [
    "docs/daily_report/REPORT-2026-09-27.json", "docs/daily_report/REPORT-2026-09-27.md",
    "results/daily_scorecard.json", "results/dashboard_status.js", "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json", "results/futures_update_status.json",
    "results/heat_update_status.json", "results/lhb_update_status.json",
    "results/paper/COMPOSITE-CE-01_paper.json", "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json", "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json", "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-09-24.json", "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json", "results/prospect_promotion/_summary.json",
    "results/regime_state.json", "results/scorecard_v1.json", "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json", "results/token_usage.json", "results/update_status.json",
]
for p in TAKE_M:
    stage(p, blob(MINE, p))
print("take-new byte-verbatim: %d faces (M side)" % len(TAKE_M))

# ---------- 2) autofill_state.json: same-second tie -> HEAD(bm-a) verbatim ----------
P = "results/autofill_state.json"
a, m = blob("HEAD", P), blob(MINE, P)
ja, jm = json.loads(a.decode("utf-8")), json.loads(m.decode("utf-8"))
assert ja["launches"] == jm["launches"], "launches diverged -> union law required, abort"
assert ja["last_tick"]["ts"] == jm["last_tick"]["ts"] == "2026-09-27 18:50:01", "tie premise broken"
assert ja["last_tick"]["machine"] == "bm-a" and jm["last_tick"]["machine"] == "bm-c"
stage(P, a)
print("autofill_state: same-second tie -> HEAD(bm-a) verbatim (launches 48==48 asserted)")

# ---------- 3) compute_audit.json: rolling-ledger union (ts,machine) key ----------
P = "results/compute_audit.json"
rawA, rawM = blob("HEAD", P), blob(MINE, P)
ja, jm = json.loads(rawA.decode("utf-8")), json.loads(rawM.decode("utf-8"))
assert sorted(ja.keys()) == sorted(jm.keys()) == ["history", "latest"], ja.keys()
assert ja["latest"] == ja["history"][-1] and jm["latest"] == jm["history"][-1], "latest!=history[-1] structure"
ka = {(r["ts"], r.get("machine")): r for r in ja["history"]}
km = {(r["ts"], r.get("machine")): r for r in jm["history"]}
assert len(ka) == 201 and len(km) == 201, (len(ka), len(km))
shared = set(ka) & set(km)
a_only = set(ka) - set(km)
m_only = set(km) - set(ka)
assert len(shared) == 200 and len(a_only) == 1 and len(m_only) == 1, (len(shared), a_only, m_only)
for k in shared:
    assert ka[k] == km[k], "shared row content drift: %s" % (k,)
merged_rows = list({**ka, **km}.values())
merged_rows.sort(key=lambda r: r["ts"])
assert len(merged_rows) == 202
merged = {k: (merged_rows if k == "history" else merged_rows[-1]) for k in ja}  # preserve side-A key order (latest first)
assert merged["latest"]["ts"] == "2026-09-27 18:48:39", merged["latest"]["ts"]  # audit rows carry ts only, no machine field
# face round-trip detect on side A (LF face, indent 2, NO trailing newline), then reuse for merged dump
face = None
for ind in (2, 1, 4, None):
    for esc in (False, True):
        cand = json.dumps(ja, ensure_ascii=esc, indent=ind).encode("utf-8")
        if cand == rawA:
            face = (ind, esc, "lf-notrail"); break
        if cand + b"\n" == rawA:
            face = (ind, esc, "lf-trail"); break
        if cand.replace(b"\n", b"\r\n") == rawA:
            face = (ind, esc, "crlf-notrail"); break
        if (cand + b"\n").replace(b"\n", b"\r\n") == rawA:
            face = (ind, esc, "crlf-trail"); break
    if face: break
assert face, "compute_audit face round-trip detect failed"
out = json.dumps(merged, ensure_ascii=face[1], indent=face[0]).encode("utf-8")
if face[2].endswith("trail"): out += b"\n"
if face[2].startswith("crlf"): out = out.replace(b"\n", b"\r\n")
stage(P, out)
print("compute_audit union: 201|201 -> 202 rows (A-only 18:48:02 bma + M-only 18:48:39 bmc), latest=bmc 18:48:39, face=%s" % (face,))

# ---------- 4) x2_watch_log.jsonl: append-log line union ----------
P = "results/x2_watch_log.jsonl"
rawA, rawM = blob("HEAD", P), blob(MINE, P)
eol = "\r\n" if b"\r\n" in rawA else "\n"
assert (b"\r\n" in rawM) == (eol == "\r\n"), "eol face diverges"
linesA = rawA.decode("utf-8").split(eol)
linesM = rawM.decode("utf-8").split(eol)
if linesA and linesA[-1] == "": linesA = linesA[:-1]
if linesM and linesM[-1] == "": linesM = linesM[:-1]
sa, sm = set(linesA), set(linesM)
assert len(linesA) == 894 and len(linesM) == 894
assert len(sa - sm) == 6 and len(sm - sa) == 6, (len(sa - sm), len(sm - sa))
union = list(dict.fromkeys(linesA + linesM))  # dedupe, first-occurrence order
union.sort(key=lambda ln: json.loads(ln)["ts"])  # stable chronological
assert len(union) == 900
tail = union[-1]
assert json.loads(tail)["ts"] == "2026-09-27 18:50:39", tail[:80]
out = eol.join(union) + (eol if rawA.endswith(eol.encode()) else "")
stage(P, out.encode("utf-8"))
print("x2log union: 894|894 -> 900 lines (A 6 @18:49:39-40 + M 6 @18:50:37-39 kept, ts-sorted)")

# ---------- final census ----------
r = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
uu = [l for l in r.stdout.splitlines() if l.startswith("UU")]
assert not uu, "still UU: %s" % uu
print("ALL RESOLVED: 26 UU -> 23 take-M + 1 tie-HEAD + 2 union | zero UU remaining")
