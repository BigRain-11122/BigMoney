"""r635 bm-b reland resolver (bigmoney-conflict-resolve skill canon).

Second resolution pass: cherry-pick of 95c5aa76a (pick-1', round 634 content
resolved on base b090bbaea) onto origin tip ac66d9127 in ISOLATED worktree
(r630-3 daemon-treadmill law). 14 UU faces = exact predicted intersection.

Recipes per r634 classifier (vetted, results/_r634bmb_classify.json):
- results/compute_audit.json   rolling-ledger: history union + latest take-new (r188/R208)
- results/regime_state.json     rolling-ledger: scalar take-new + lists union (R208)
- 12 snapshot faces              take-new by generation ts whole-side bytes
  (token_usage wholesale-take-new = vetted: meter re-derives whole doc each round)

Stage map during cherry-pick: :2 = ours = ac66d9127 (origin), :3 = theirs =
95c5aa76a (mine). Tie -> HEAD side (:2, r140 law). Receipt -> iso
results/_r635bmb_resolve_receipt.json (lands in the reland commit).

Usage: python results/_r635bmb_resolve2.py <iso-root>
"""
import json
import re
import subprocess
import sys

ISO_ROOT = sys.argv[1]
ISO = re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}")
TS_KEYS = (
    "generated",
    "generated_at",
    "generated_from_state_updated",
    "updated",
    "updated_at",
    "ts",
    "scan_ts",
    "written_at",
    "last_run",
)


def blob(stage, path):
    p = subprocess.run(
        ["git", "show", f":{stage}:{path}"], cwd=ISO_ROOT, capture_output=True
    )
    if p.returncode != 0:
        raise RuntimeError(f"missing stage {stage} for {path}")
    return p.stdout


def stage_exists(stage, path):
    p = subprocess.run(
        ["git", "show", f":{stage}:{path}"], cwd=ISO_ROOT, capture_output=True
    )
    return p.returncode == 0


def canon(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False)


def extract_ts_json(d, depth=0, best=None):
    if best is None:
        best = {}
    if isinstance(d, dict):
        for k, v in d.items():
            if isinstance(v, str) and k in TS_KEYS and ISO.search(v):
                if "depth" not in best or depth < best["depth"]:
                    best = {"depth": depth, "ts": v, "key": k}
            else:
                extract_ts_json(v, depth + 1, best)
    elif isinstance(d, list):
        for v in d[:200]:
            extract_ts_json(v, depth + 1, best)
    return best


def json_gen_ts(raw):
    d = json.loads(raw)
    hit = extract_ts_json(d)
    if hit:
        return hit["ts"], f"key={hit['key']}@d{hit['depth']}"
    isos = ISO.findall(raw.decode("utf-8", errors="replace"))
    if isos:
        return max(isos), "max-iso-fallback"
    return None, "none"


def md_gen_ts(raw):
    head = raw.decode("utf-8", errors="replace")[:400]
    m = ISO.search(head)
    return (m.group(0), "md-header") if m else (None, "none")


def detect_fmt(raw):
    txt = raw.decode("utf-8", errors="replace")
    m = re.match(r"\{\n(\s+)\"", txt)
    indent = len(m.group(1)) if m else 1
    return {
        "indent": indent,
        "crlf": b"\r\n" in raw,
        "ensure_ascii": not any(ord(c) > 127 for c in txt),
        "trailing_nl": raw.endswith(b"\n"),
    }


def write_fmt(obj, fmt, path):
    s = json.dumps(
        obj,
        ensure_ascii=(True if fmt["ensure_ascii"] else False),
        indent=fmt["indent"],
    )
    if fmt["trailing_nl"]:
        s += "\n"
    data = s.encode("utf-8")
    if fmt["crlf"]:
        data = data.replace(b"\n", b"\r\n")
    open(path, "wb").write(data)


def ipath(p):
    return ISO_ROOT + "\\" + p.replace("/", "\\")


receipt = {"union": [], "snapshot": [], "skipped": [], "notes": []}

# ---------------- union faces ----------------
# 1) compute_audit.json: history union + latest take-new (r188/R208)
p = "results/compute_audit.json"
if not (stage_exists(2, p) and stage_exists(3, p)):
    receipt["skipped"].append({"path": p, "why": "no stages = auto-merged or unchanged"})
else:
    a, b = json.loads(blob(2, p)), json.loads(blob(3, p))
    seen, hist = set(), []
    for row in a["history"] + b["history"]:
        c = canon(row)
        if c not in seen:
            seen.add(c)
            hist.append(row)
    ts_a, _ = json_gen_ts(blob(2, p))
    ts_b, _ = json_gen_ts(blob(3, p))
    if ts_b is None:
        newer = a
    elif ts_a is None:
        newer = b
    else:
        newer = b if ts_b > ts_a else a
    merged = {"latest": newer["latest"], "history": hist}
    fmt = detect_fmt(blob(2, p))
    write_fmt(merged, fmt, ipath(p))
    assert len(hist) == len({canon(r) for r in a["history"]} | {canon(r) for r in b["history"]}), "audit union loss"
    receipt["union"].append(
        {
            "path": p,
            "recipe": "history union + latest take-new",
            "A_rows": len(a["history"]),
            "B_rows": len(b["history"]),
            "union_rows": len(hist),
            "latest_side": "mine" if newer is b else "origin",
            "ts_A": ts_a,
            "ts_B": ts_b,
        }
    )

# 2) regime_state.json: scalar take-new + triggers/transitions/history union (R208)
p = "results/regime_state.json"
if not (stage_exists(2, p) and stage_exists(3, p)):
    receipt["skipped"].append({"path": p, "why": "no stages = auto-merged or unchanged"})
else:
    a, b = json.loads(blob(2, p)), json.loads(blob(3, p))
    ts_a, ts_b = a["updated"], b["updated"]
    base, other = (b, a) if ts_b > ts_a else (a, b)
    for key in ("triggers", "transitions", "history"):
        seen = {canon(r) for r in base[key]}
        for row in other[key]:
            if canon(row) not in seen:
                base[key] = base[key] + [row]
                seen.add(canon(row))
    fmt = detect_fmt(blob(2, p))
    write_fmt(base, fmt, ipath(p))
    receipt["union"].append(
        {
            "path": p,
            "recipe": "scalar take-new + triggers/transitions/history union",
            "ts_A": ts_a,
            "ts_B": ts_b,
            "scalar_side": "mine" if base is b else "origin",
        }
    )

# ---------------- snapshot faces (whole-side bytes take-new) ----------------
SNAPSHOTS = [
    "docs/daily_report/REPORT-2026-10-03.json",
    "docs/daily_report/REPORT-2026-10-03.md",
    "docs/live_usage/LIVE-2026-10-03.json",
    "docs/live_usage/LIVE-2026-10-03.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/token_usage.json",
    "results/update_status.json",
]

for p in SNAPSHOTS:
    if not stage_exists(2, p):
        receipt["skipped"].append({"path": p, "why": "no stage2 = not conflicted"})
        continue
    ra, rb = blob(2, p), blob(3, p)
    if ra == rb:
        open(ipath(p), "wb").write(ra)
        receipt["snapshot"].append({"path": p, "side": "identical"})
        continue
    if p.endswith(".md"):
        ts_a, ev_a = md_gen_ts(ra)
        ts_b, ev_b = md_gen_ts(rb)
    elif p.endswith(".js"):
        # js-wrapper: producer format = window.DASH_DATA = {...}; ts from meta.generated_at
        m_a = re.search(r'"generated_at": "([^"]+)"', ra.decode("utf-8", errors="replace"))
        m_b = re.search(r'"generated_at": "([^"]+)"', rb.decode("utf-8", errors="replace"))
        ts_a, ts_b = (m_a.group(1) if m_a else None), (m_b.group(1) if m_b else None)
        ev_a = ev_b = "js-meta.generated_at"
    else:
        ts_a, ev_a = json_gen_ts(ra)
        ts_b, ev_b = json_gen_ts(rb)
    if ts_a is None and ts_b is None:
        side, why = "origin", "no-ts-tie->HEAD(r140)"
    elif ts_b is None or (ts_a is not None and ts_a >= ts_b):
        side, why = "origin", "A newer or tie->HEAD(r140)"
    else:
        side, why = "mine", "B newer"
    data = rb if side == "mine" else ra
    for mk in (b"<<<<<<<", b">>>>>>>"):
        assert mk not in data, f"marker in chosen side {p}"
    if p.endswith(".json"):
        json.loads(data)  # parse-verify before write-back (r185)
    open(ipath(p), "wb").write(data)
    receipt["snapshot"].append(
        {
            "path": p,
            "side": side,
            "ts_A": ts_a,
            "ts_B": ts_b,
            "evidence": f"A:{ev_a} B:{ev_b} -> {why}",
        }
    )

json.dump(
    receipt,
    open(ipath("results/_r635bmb_resolve_receipt3.json"), "w", encoding="utf-8"),
    ensure_ascii=False,
    indent=1,
)
n_mine = sum(1 for e in receipt["snapshot"] if e["side"] == "mine")
n_org = sum(1 for e in receipt["snapshot"] if e["side"] == "origin")
n_id = sum(1 for e in receipt["snapshot"] if e["side"] == "identical")
print(
    f"RESOLVED union=2 snapshot={len(SNAPSHOTS)} skipped={len(receipt['skipped'])} "
    f"(mine={n_mine} origin={n_org} identical={n_id})"
)
for e in receipt["union"]:
    print("U:", e["path"], {k: v for k, v in e.items() if k != "path"})
for e in receipt["snapshot"]:
    print("S:", e["path"], e.get("side"), e.get("ts_A"), "vs", e.get("ts_B"))
