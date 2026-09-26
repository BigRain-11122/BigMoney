"""r298 bm-b rebase batch resolver #3: 27-file UU batch (bm-a r294 vs bm-b r298,
same-window S6 chains on both machines). Classifier: 12 canonical classes +
16 UNKNOWN hand-qualified here as deterministic re-derivation artifacts with
runtime-metadata drift (strip-meta equality gate -> take-new side; any real
semantic diff -> STOP for manual). Recipes: memory-union CODELY (R208/r212),
rolling-ledger compute_audit (r188/R208) + regime_state, append-log x2_watch
(r188), js-wrapper dashboard_status.js take-side bytes (R209), snapshots
take-new (R208/R216), daily_report regen-face same-day idempotent law
(oldest generation superseded, kept in git history).
"""
import io
import json
import re
import subprocess

RUNTIME_META = {"ts", "generated", "generated_at", "generated_ts", "updated_at",
                "updated", "elapsed_sec", "elapsed", "duration_sec", "runtime_sec",
                "as_of", "now", "wall_clock", "run_at", "run_ts", "last_run",
                "report_ts", "build_ts", "built_at", "refreshed_at", "checked_at",
                "epoch", "elapsed_sec_total"}


def blob(stage, path):
    return subprocess.run(["git", "show", f":{stage}:{path}"],
                           capture_output=True, check=True).stdout


def cano(x):
    return json.dumps(x, ensure_ascii=False, sort_keys=True)


def strip_meta(x):
    if isinstance(x, dict):
        return {k: strip_meta(v) for k, v in x.items()
                if k not in RUNTIME_META}
    if isinstance(x, list):
        return [strip_meta(v) for v in x]
    return x


def max_ts(x, acc):
    if isinstance(x, dict):
        for k, v in x.items():
            if k in RUNTIME_META and isinstance(v, (str, int, float)):
                acc.append(str(v))
            max_ts(v, acc)
    elif isinstance(x, list):
        for v in x:
            max_ts(v, acc)


def side_newer(a, b):
    aa, bb = [], []
    max_ts(a, aa)
    max_ts(b, bb)
    return (max(aa) if aa else "") >= (max(bb) if bb else "")


resolved, notes = [], []

# ---- 1) CODELY.md: memory-union (both machines' entries kept verbatim) -------
raw = io.open("CODELY.md", encoding="utf-8").read()
m = re.search(r"<<<<<<< HEAD\n(.*?)\n=======\n(.*?)\n>>>>>>> [^\n]*\n", raw, re.S)
assert m, "CODELY conflict block not found"
theirs, mine = m.group(1).strip("\n"), m.group(2).strip("\n")
union_block = mine + "\n" + theirs          # chronological: r298 04:5x then bm-a 05:0x
out = raw[:m.start()] + union_block + "\n" + raw[m.end():]
_bad = [l for l in out.splitlines()
        if l.startswith(("<<<<<<<", "=======", ">>>>>>>"))]
assert not _bad, ("marker line left", _bad[:2])   # mid-line marker strings in kenglu text are legit
with io.open("CODELY.md", "w", encoding="utf-8", newline="") as f:
    f.write(out)
assert len(out.encode("utf-8")) <= 10 * 1024, len(out.encode("utf-8"))
resolved.append("CODELY.md(memory-union 2+0)")
notes.append("CODELY union bytes=%d<=10KB" % len(out.encode("utf-8")))

# ---- 2) compute_audit.json: rolling-ledger union + latest take-new ----------
P = "results/compute_audit.json"
o = json.loads(blob(2, P).decode("utf-8-sig"))
t = json.loads(blob(3, P).decode("utf-8-sig"))
so = {cano(r) for r in o["history"]}
st = {cano(r) for r in t["history"]}
rows = sorted(list(t["history"]) + [r for r in o["history"] if cano(r) not in st],
              key=lambda r: r.get("ts", ""))
assert len(rows) == len(so | st), (len(rows), len(so | st))
latest = o["latest"] if side_newer(o["latest"], t["latest"]) else t["latest"]
with io.open(P, "wb") as f:
    f.write(json.dumps({"latest": latest, "history": rows},
                       ensure_ascii=False, indent=1).encode("utf-8"))
json.load(io.open(P, encoding="utf-8-sig"))
resolved.append("compute_audit(union %d rows latest=%s)" % (len(rows), latest.get("ts")))

# ---- 3) regime_state.json: rolling-ledger (list keys union, scalars new) -----
P = "results/regime_state.json"
o = json.loads(blob(2, P).decode("utf-8-sig"))
t = json.loads(blob(3, P).decode("utf-8-sig"))
newer_is_2 = side_newer(o, t)
merged = {}
for k in set(o) | set(t):
    ov, tv = o.get(k), t.get(k)
    if isinstance(ov, list) and isinstance(tv, list) and ov and isinstance(ov[0], dict):
        seen = {cano(x) for x in ov}
        merged[k] = sorted(list(ov) + [x for x in tv if cano(x) not in seen],
                           key=lambda r: str(r.get("ts", r.get("date", ""))))
    else:
        merged[k] = ov if newer_is_2 else tv
with io.open(P, "wb") as f:
    f.write(json.dumps(merged, ensure_ascii=False, indent=1).encode("utf-8"))
json.load(io.open(P, encoding="utf-8-sig"))
resolved.append("regime_state(ledger-union side=%s)" % ("2" if newer_is_2 else "3"))

# ---- 4) x2_watch_log.jsonl: append-log line union, ts sort -------------------
P = "results/x2_watch_log.jsonl"
o = [l for l in blob(2, P).decode("utf-8-sig").splitlines() if l.strip()]
t = [l for l in blob(3, P).decode("utf-8-sig").splitlines() if l.strip()]
seen = {l for l in o}
un = sorted(list(o) + [l for l in t if l not in seen],
            key=lambda l: str(json.loads(l).get("ts", "")))
assert len(un) == len({l for l in o} | {l for l in t})
with io.open(P, "wb") as f:
    f.write(("\n".join(un) + "\n").encode("utf-8"))
resolved.append("x2_watch_log(union %d lines)" % len(un))

# ---- 5) snapshot / regen-face files: strip-meta equality -> take-new --------
REGEN_FACE = {"docs/daily_report/REPORT-2026-09-27.json",
              "docs/daily_report/REPORT-2026-09-27.md"}   # same-day idempotent regen law
SNAPSHOTS = ["results/dashboard_status.json", "results/dashboard_status.js",
             "results/fundamental_b_layer_filter.json", "results/futures_update_status.json",
             "results/heat_update_status.json", "results/lhb_update_status.json",
             "results/token_usage.json", "results/update_status.json",
             "results/daily_scorecard.json", "results/scorecard_v1.json",
             "results/strategy_scorecard.json", "results/t35_open_fill_verify.json",
             "results/prospect_paper/_summary.json", "results/prospect_promotion/_summary.json",
             "results/paper_export/export-2026-09-24.json", "results/paper_export/latest.json",
             "results/paper/COMPOSITE-CE-01_paper.json", "results/paper/COMPOSITE-CE-02_paper.json",
             "results/paper/DROUGHT-CE-01_paper.json", "results/paper/ENGULF-CE-01_paper.json",
             "results/paper/NEEDLE-DE-01_paper.json", "results/paper/VOLATILITY-CE-01_paper.json"]
manual = []
for p in REGEN_FACE | set(SNAPSHOTS):
    b2, b3 = blob(2, p), blob(3, p)
    if p.endswith(".json"):
        j2, j3 = json.loads(b2.decode("utf-8-sig")), json.loads(b3.decode("utf-8-sig"))
        equal = cano(strip_meta(j2)) == cano(strip_meta(j3))
        newer2 = side_newer(j2, j3)
    else:
        equal = p in REGEN_FACE          # md/js: byte-face artifacts, regen law covers
        newer2 = True                    # upstream r294 ran later (05:0x vs 04:56)
    if p in REGEN_FACE:
        take2 = True                    # same-day regen face: newest generation wins
    elif equal:
        take2 = newer2
    else:
        manual.append(p)
        continue
    data = b2 if take2 else b3
    with io.open(p, "wb") as f:
        f.write(data)
    if p.endswith(".json"):
        json.load(io.open(p, encoding="utf-8-sig"))
    tag = "regen-face" if p in REGEN_FACE else ("strip-equal take-new side%s" % ("2" if take2 else "3"))
    resolved.append("%s(%s)" % (p, tag))

print("resolved:", len(resolved))
for r in resolved:
    print("  OK", r)
print("MANUAL-STOP needed for:", manual if manual else "none")
for n in notes:
    print("note:", n)
assert not manual, ("REAL SEMANTIC DIFF — manual required", manual)

# ---- 6) final marker sweep over all conflict files --------------------------
U = subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"],
                   capture_output=True, text=True).stdout.split()
for p in U:
    body = io.open(p, "rb").read().decode("utf-8", errors="replace")
    bad = [l for l in body.splitlines()
           if l.startswith(("<<<<<<<", "=======", ">>>>>>>"))]
    assert not bad, ("marker line left", p, bad[:2])
print("marker sweep clean; remaining UU files:", U)
