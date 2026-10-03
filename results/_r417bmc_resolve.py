# -*- coding: utf-8 -*-
# r417 bm-c conflict resolver (rebase 139a0c939 onto origin tip 3ee7ee1ec, 28 UU files).
# Laws engaged: r498 (AA envelope-divergence -> assert-then-take-side), 3ee7ee1ec bm-a
# precedent (json newer-wins), r570 domain law (append-only jsonl line-union dict-only),
# r578 (dashboard host=bm-a authority -> non-host yields to origin side).
# CODELY.md hand-merged: keep bm-a's 2 new r624 hot entries, drop r614/r415 (migrated by r417).
import json, subprocess, sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

def stage(side, path):
    r = subprocess.run(["git", "-C", ROOT, "show", ":%s:%s" % (side, path)], capture_output=True)
    if r.returncode != 0:
        print("ABORT stage %s:%s rc=%d" % (side, path, r.returncode))
        sys.exit(2)
    return r.stdout

def ts_of(blob):
    try:
        j = json.loads(blob.decode("utf-8-sig"))
    except Exception:
        return None, None
    ts = j.get("ts") or j.get("generated") or j.get("generated_at") or j.get("updated_at")
    return ts, j

# ---------- 1. CODELY.md hand merge ----------
codely_wt = open(ROOT + r"\CODELY.md", "rb").read().decode("utf-8")
nl = "\r\n" if "\r\n" in codely_wt else "\n"
lines = codely_wt.split(nl)
# locate conflict block (diff3 order: <<<<<<< HEAD-side ||||||| base-side ======= theirs-side >>>>>>>)
i_start = next(i for i, ln in enumerate(lines) if ln.startswith("<<<<<<<"))
i_base = next(i for i, ln in enumerate(lines) if i > i_start and ln.startswith("|||||||"))
i_sep = next(i for i, ln in enumerate(lines) if i > i_base and ln.startswith("======="))
i_end = next(i for i, ln in enumerate(lines) if i > i_sep and ln.startswith(">>>>>>>"))
head_side = lines[i_start+1 : i_base]
theirs_side = lines[i_sep+1 : i_end]
if any(ln.strip() for ln in theirs_side):
    print("ABORT theirs side non-empty, unexpected: %s" % theirs_side[:2])
    sys.exit(2)
# keep only the two r624 bm-a entries from HEAD side (drop r614/r415 already migrated by r417)
keep = [ln for ln in head_side if "r624 bm-a" in ln]
dropped = [ln for ln in head_side if "r624 bm-a" not in ln and ln.strip()]
if len(keep) != 2 or len(dropped) != 2:
    print("ABORT codely keep=%d dropped=%d (expect 2/2)" % (len(keep), len(dropped)))
    sys.exit(2)
for d in dropped:
    if not ("r614 bm-b" in d or "r415 bm-c" in d):
        print("ABORT unexpected drop line: %s" % d[:60])
        sys.exit(2)
merged = lines[:i_start] + keep + lines[i_end+1:]
new_text = nl.join(merged)
# residue checks (line-start match only: stock r511 entry contains '=======' as content substring)
for bad in ("<<<<<<<", "=======", ">>>>>>>", "|||||||"):
    if any(ln.startswith(bad) for ln in merged):
        print("ABORT conflict marker residue %s" % bad)
        sys.exit(2)
if any(("r614 bm-b" in ln or "13:0x r415 bm-c" in ln) for ln in merged):
    print("ABORT migrated entry residue in CODELY")
    sys.exit(2)
if sum(1 for ln in merged if "r624 bm-a" in ln) != 2:
    print("ABORT r624 count wrong")
    sys.exit(2)
open(ROOT + r"\CODELY.md", "wb").write(new_text.encode("utf-8"))
print("CODELY merged: keep 2 r624 entries, drop r614/r415 (migrated), bytes=%d" % len(new_text.encode("utf-8")))

# ---------- 2. x2_watch_log.jsonl line-union (r570 domain law, dict-only) ----------
p = "results/x2_watch_log.jsonl"
o = stage("2", p).decode("utf-8").splitlines()
t = stage("3", p).decode("utf-8").splitlines()
seen, union = set(), []
for ln in o + t:
    ln = ln.strip()
    if not ln:
        continue
    try:
        j = json.loads(ln)
    except Exception:
        print("ABORT x2 unparseable line")
        sys.exit(2)
    if not isinstance(j, dict):
        print("ABORT x2 non-dict line (r570 type-gate)")
        sys.exit(2)
    key = json.dumps(j, sort_keys=True, ensure_ascii=False)
    if key not in seen:
        seen.add(key)
        union.append(ln)
open(ROOT + "\\" + p, "w", encoding="utf-8", newline="\n").write("\n".join(union) + "\n")
print("x2_watch_log union: origin=%d mine=%d -> union=%d" % (len(o), len(t), len(union)))

# ---------- 3. dashboard 2 files: host=bm-a authority -> take origin (stage 2, r578 yield law) ----------
for p in ("results/dashboard_status.js", "results/dashboard_status.json"):
    open(ROOT + "\\" + p, "wb").write(stage("2", p))
    print("dashboard yield-to-origin: %s (%dB)" % (p, len(stage("2", p))))

# ---------- 4. remaining json/md idempotent faces: newer-wins by ts ----------
NEWER_WINS = [
    "docs/daily_report/REPORT-2026-10-03.json", "docs/daily_report/REPORT-2026-10-03.md",
    "docs/live_usage/LIVE-2026-10-03.json", "docs/live_usage/LIVE-2026-10-03.md",
    "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json", "results/compute_audit.json",
    "results/daily_scorecard.json", "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json", "results/lhb_update_status.json",
    "results/regime_state.json", "results/scorecard_v1.json",
    "results/strategy_scorecard.json", "results/t35_open_fill_verify.json",
    "results/token_usage.json", "results/update_status.json",
    "results/paper_export/export-2026-09-30.json", "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json", "results/prospect_promotion/_summary.json",
    "results/paper/COMPOSITE-CE-01_paper.json", "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json", "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json", "results/paper/VOLATILITY-CE-01_paper.json",
]
picked = {"origin": 0, "mine": 0}
for p in NEWER_WINS:
    o2, t3 = stage("2", p), stage("3", p)
    ots, oj = ts_of(o2)
    tts, tj = ts_of(t3)
    if ots is None and tts is None:
        # md or non-ts: deterministic re-derive face -> prefer MINE (later S6 run, this round's evidence)
        side, blob = "mine", t3
    elif ots is None:
        side, blob = "mine", t3
    elif tts is None:
        side, blob = "origin", o2
    else:
        side, blob = ("mine", t3) if str(tts) >= str(ots) and tts != ots else ("origin", o2)
        if tts == ots:
            side, blob = "mine", t3  # equal ts: prefer later-run local evidence
    open(ROOT + "\\" + p, "wb").write(blob)
    picked[side if side in picked else ("origin" if side == "origin" else "mine")] += 1
    print("newer-wins %s -> %s (origin_ts=%s mine_ts=%s)" % (p, side, ots, tts))
print("RESOLVED: newer-wins picked origin=%d mine=%d, dashboard yield=2, x2 union=1, codely hand=1" %
      (picked["origin"], picked["mine"]))
