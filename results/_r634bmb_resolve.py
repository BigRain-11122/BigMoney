"""r634 bm-b rebase conflict resolver (bigmoney-conflict-resolve skill canon).

31 UU files vs origin 5-commit window (bm-a r641 x3 + bm-c r428 + satengine tick).
Recipes per classifier + SKILL.md:
- rolling-ledger/append-log (compute_audit history, regime_state lists,
  x2_watch_log.jsonl lines): union both blobs zero row loss.
- everything else = whole-doc derive/regen snapshot faces (daily report, live
  usage, scorecards, paper accounts, statuses, attrition scan evidence):
  take-new by generation ts, WHOLE-SIDE BYTES (no re-serialization).
- same-second tie -> HEAD side (origin, r140 law).
Stage map during rebase: :2 = origin side, :3 = my commit side.
Receipt printed to results/_r634bmb_resolve_receipt.json.
"""
import json
import re
import subprocess
import sys

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
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
        ["git", "show", f":{stage}:{path}"], cwd=ROOT, capture_output=True
    )
    if p.returncode != 0:
        raise RuntimeError(f"missing stage {stage} for {path}")
    return p.stdout


def canon(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False)


def extract_ts_json(d, depth=0, best=None):
    """Shallowest TS_KEY hit wins; fallback max ISO string anywhere."""
    if best is None:
        best = {}
    if isinstance(d, dict):
        for k, v in d.items():
            if isinstance(v, str) and k in TS_KEYS and ISO.search(v):
                if "depth" not in best or depth < best["depth"]:
                    best = {"depth": depth, "ts": v, "key": k}
                if depth == best["depth"] and k not in best.get("keys", []):
                    pass
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


receipt = {"union": [], "snapshot": [], "notes": []}

# ---------------- union faces ----------------
# 1) compute_audit.json: history union + latest take-new
p = "results/compute_audit.json"
a, b = json.loads(blob(2, p)), json.loads(blob(3, p))
seen, hist = set(), []
for row in a["history"] + b["history"]:
    c = canon(row)
    if c not in seen:
        seen.add(c)
        hist.append(row)
newer = b if json_gen_ts(blob(3, p))[0] > json_gen_ts(blob(2, p))[0] else a
merged = {"latest": newer["latest"], "history": hist}
fmt = detect_fmt(blob(2, p))
write_fmt(merged, fmt, p)
assert len(hist) == len({canon(r) for r in a["history"]} | {canon(r) for r in b["history"]}), "audit union loss"
receipt["union"].append(
    {
        "path": p,
        "recipe": "history union + latest take-new",
        "A_rows": len(a["history"]),
        "B_rows": len(b["history"]),
        "union_rows": len(hist),
        "latest_side": "mine" if newer is b else "origin",
    }
)

# 2) regime_state.json: scalar take-new + lists union
p = "results/regime_state.json"
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
write_fmt(base, fmt, p)
receipt["union"].append(
    {
        "path": p,
        "recipe": "scalar take-new + triggers/transitions/history union",
        "ts_A": ts_a,
        "ts_B": ts_b,
        "scalar_side": "mine" if base is b else "origin",
    }
)

# 3) x2_watch_log.jsonl: line-level union, ts-sorted merge
p = "results/x2_watch_log.jsonl"
la = blob(2, p).decode("utf-8").splitlines()
lb = blob(3, p).decode("utf-8").splitlines()
sa, sb = set(la), set(lb)
merged_lines = [ln for ln in la if ln in sa] + [ln for ln in lb if ln not in sa]
merged_lines.sort(key=lambda ln: ISO.search(ln).group(0) if ISO.search(ln) else "")
assert len(merged_lines) == len(sa | sb), "x2 union loss"
nl = "\r\n" if b"\r\n" in blob(2, p) else "\n"
open(p, "wb").write((nl.join(merged_lines) + nl).encode("utf-8"))
receipt["union"].append(
    {
        "path": p,
        "recipe": "line-level union ts-sorted",
        "A": len(la),
        "B": len(lb),
        "union": len(merged_lines),
        "A_only": len(sa - sb),
        "B_only": len(sb - sa),
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
    "results/daily_scorecard.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-09-30.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/token_usage.json",
    "results/update_status.json",
]

for p in SNAPSHOTS:
    ra, rb = blob(2, p), blob(3, p)
    if ra == rb:
        open(p, "wb").write(ra)
        receipt["snapshot"].append({"path": p, "side": "identical", "ts_A": None, "ts_B": None})
        continue
    if p.endswith(".json") or p.endswith(".js") is False and p.endswith(".md") is False:
        pass
    if p.endswith(".md"):
        ts_a, ev_a = md_gen_ts(ra)
        ts_b, ev_b = md_gen_ts(rb)
    elif p.endswith(".js"):
        # js-wrapper: keep producer bytes; ts from meta.generated_at
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
    if p.endswith((".json",)):
        json.loads(data)  # parse-verify before write-back (r185)
    open(p, "wb").write(data)
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
    open(r"results/_r634bmb_resolve_receipt.json", "w", encoding="utf-8"),
    ensure_ascii=False,
    indent=1,
)
n_mine = sum(1 for e in receipt["snapshot"] if e["side"] == "mine")
n_org = sum(1 for e in receipt["snapshot"] if e["side"] == "origin")
n_id = sum(1 for e in receipt["snapshot"] if e["side"] == "identical")
print(
    f"RESOLVED union=3 snapshot={len(SNAPSHOTS)} "
    f"(mine={n_mine} origin={n_org} identical={n_id})"
)
for e in receipt["union"]:
    print("U:", e["path"], {k: v for k, v in e.items() if k != "path"})
for e in receipt["snapshot"]:
    print("S:", e["path"], e["side"], e.get("ts_A"), "vs", e.get("ts_B"))
