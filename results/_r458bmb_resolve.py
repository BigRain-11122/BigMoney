"""_r458bmb_resolve.py -- bm-b r458 rebase collision resolver (step 1/3: r457 replay batch).

Origin delta landed after r457's failed push (stage :2: = current origin/main):
  - bm-c r265 (SLOT-10 freeze steps 1-5 + CODELY r265 entry + state-bm-c bridge)
  - bm-a r467 (W13 GENERATE+SCREEN receipts + CODELY re-arch 7.8KB: r467 entries
    + pointer consolidation drops 8 lines per r444 dedupe law + W13 pool faces)
My replayed side (:3:) = r457 (fix-red fundamental + S6 faces + CODELY reorg).

Recipes per bigmoney-conflict-resolve SKILL.md (classifier 16 + 1 UNKNOWN):
- snapshot twins (REPORT / LIVE groups): deep-ts probe, ONE side wins all (r98/r99/r100).
- plain snapshots incl. classifier-UNKNOWN _attrition_guard_scan.json (manual
  adjudication: scan-evidence snapshot, take-new by ts; r454/r457 precedent).
- fundamental_status.json MANUAL adjudication: take-MINE (truth-wins -- mine =
  post-fix rc0 full face @10:55:14 with fresh 11635-row snapshot; origin @11:05:07
  = bm-a r467 pre-fix-code rc2 error face {ok,updated,error} describing stale
  code that this very rebase removes; post-push repo code = fixed => truthful
  current face = mine; r457 addendum precedent "fresher TRUTHFUL state wins").
- rolling-ledger (compute_audit history/ts + regime_state history/asof): union
  zero-loss + state take-new (r188/R208).
- marks jsonl: append-log line-level union, parse-verify, sort by ts (r188/r217).
- CODELY.md: NEITHER side pure append (mine = r457 reorg; origin = r467 in-place
  re-arch) -> edit-union: my face + origin 4 added lines (r265 entry + r467
  entry + 2 r467 merge pointers) - origin 8 dropped pointer lines; then hot-cold
  trim to <=10KB hard line (archives oldest pointer lines verbatim into
  research/memory-archive/202609.md new section; zero-loss).
Parse-verify every JSON; zero-loss assertions per family.
"""
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def blob(spec):
    return subprocess.run(["git", "show", spec], capture_output=True).stdout.decode("utf-8", errors="replace")


WALL = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")
report = []


def deep_ts(obj):
    best = ""
    def scan(o):
        nonlocal best
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, (str, int, float)):
                    nk = str(k).lower().replace("_", "").replace("-", "")
                    if any(p in nk for p in ("ts", "generated", "updated", "asof",
                                             "attempt", "scanned", "written")):
                        s = str(v)
                        if WALL.match(s) and s > best:
                            best = s
                else:
                    scan(v)
        elif isinstance(o, list):
            for it in o:
                scan(it)
    scan(obj)
    return best


def take_group(paths):
    ts_by_side = {"c": "", "m": ""}
    for p in paths:
        try:
            ts_by_side["c"] = max(ts_by_side["c"], deep_ts(json.loads(blob(":2:" + p))))
        except Exception:
            pass
        try:
            ts_by_side["m"] = max(ts_by_side["m"], deep_ts(json.loads(blob(":3:" + p))))
        except Exception:
            pass
    winner = "m" if ts_by_side["m"] >= ts_by_side["c"] else "c"
    for p in paths:
        data = blob((":3:" if winner == "m" else ":2:") + p)
        if p.endswith(".json"):
            json.loads(data)
        with open(p, "w", encoding="utf-8", newline="") as f:
            f.write(data)
        report.append((p, f"take-{winner} group (c={ts_by_side['c'] or '-'} m={ts_by_side['m'] or '-'})"))
    return winner


def take_new(p, note=""):
    ts_c = deep_ts(json.loads(blob(":2:" + p)))
    ts_m = deep_ts(json.loads(blob(":3:" + p)))
    winner = "m" if ts_m >= ts_c else "c"
    data = blob((":3:" if winner == "m" else ":2:") + p)
    json.loads(data)
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(data)
    report.append((p, f"take-{winner} (c={ts_c} m={ts_m}){note}"))


def take_mine_manual(p, note):
    data = blob(":3:" + p)
    json.loads(data)
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(data)
    report.append((p, f"take-m MANUAL {note}"))


def union_ledger(p, ledger_key, ident):
    dc = json.loads(blob(":2:" + p))
    dm = json.loads(blob(":3:" + p))
    hc, hm = dc[ledger_key], dm[ledger_key]
    seen, merged = set(), []
    for row in hc + hm:
        key = row[ident]
        if key not in seen:
            seen.add(key)
            merged.append(row)
    merged.sort(key=lambda r: str(r[ident]))
    ts_c, ts_m = deep_ts(dc), deep_ts(dm)
    src = dm if ts_m >= ts_c else dc
    out = dict(src)
    out[ledger_key] = merged
    json.loads(json.dumps(out))
    with open(p, "w", encoding="utf-8", newline="") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    report.append((p, f"union {len(hc)}+{len(hm)}->{len(merged)} on {ledger_key}/{ident}, state take-{'m' if ts_m >= ts_c else 'c'}"))


def union_marks(p):
    lc = [ln for ln in blob(":2:" + p).splitlines() if ln.strip()]
    lm = [ln for ln in blob(":3:" + p).splitlines() if ln.strip()]
    seen, merged = set(), []
    for ln in lc + lm:
        if ln not in seen:
            seen.add(ln)
            merged.append(ln)
    def tskey(ln):
        try:
            return str(json.loads(ln).get("ts", ""))
        except Exception:
            return ""
    merged.sort(key=tskey)
    for ln in merged:
        json.loads(ln)
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(merged) + "\n")
    report.append((p, f"append-log union {len(lc)}+{len(lm)}->{len(merged)} lines, sorted by ts"))


def resolve_codely():
    p = "CODELY.md"
    base_lines = blob(":1:" + p).splitlines()
    oc_lines = blob(":2:" + p).splitlines()
    my_lines = blob(":3:" + p).splitlines()

    tmp_base = list(base_lines)
    origin_added = []
    for ln in oc_lines:
        if ln in tmp_base:
            tmp_base.remove(ln)
        else:
            origin_added.append(ln)
    origin_dropped = tmp_base

    # sanity: origin adds = r265 entry + r467 entry + 2 r467 merge pointers
    assert len(origin_added) == 4, f"origin added {len(origin_added)}: {[a[:60] for a in origin_added]}"
    r265 = [ln for ln in origin_added if ln.startswith("- [2026-09-30 r265 bm-c]")]
    r467e = [ln for ln in origin_added if ln.startswith("- [2026-09-30 r467 bm-a]")]
    r467p = [ln for ln in origin_added if ln.startswith("- 冷层指针（r467 合并")]
    assert len(r265) == 1 and len(r467e) == 1 and len(r467p) == 2, \
        f"origin adds unexpected: {[a[:60] for a in origin_added]}"
    print("origin_dropped count:", len(origin_dropped))
    for ln in origin_dropped:
        print("  drop:", ln[:80])

    # apply origin drops to MY face, then insert origin adds at chronological positions
    out_lines = [ln for ln in my_lines if ln not in origin_dropped]

    # r265 bm-c entry: origin landed before my r457 tail entry -> insert before it
    idx457 = next(i for i, ln in enumerate(out_lines) if ln.startswith("- [2026-09-30 r457 bm-b]"))
    out_lines[idx457:idx457] = r265
    # r467 bm-a entry + pointers: origin r467 landed after r265 and after my r457 was
    # written locally but BEFORE this replay -> chronological tail position after r457
    # for the hot entry; pointers join the pointer block (after r457 pointer line).
    idx457p = next(i for i, ln in enumerate(out_lines) if ln.startswith("- 冷层指针（r457 合并"))
    out_lines[idx457p + 1:idx457p + 1] = r467p
    out_lines.append(r467e[0])

    out = "\n".join(out_lines) + "\n"
    assert "<<<<<<<" not in out and ">>>>>>>" not in out
    for ln in origin_added:
        assert ln in out, f"missing origin add: {ln[:60]}"
    for ln in origin_dropped:
        assert ln not in out, f"dropped line still present: {ln[:60]}"
    assert "- [2026-09-30 r457 bm-b]" in out

    size = len(out.encode("utf-8"))
    print("post-union CODELY size:", size)
    if size > 10240:
        # hot-cold trim: archive oldest 冷层指针 lines verbatim to 202609.md
        pointer_idx = [i for i, ln in enumerate(out_lines) if ln.startswith("- 冷层指针")]
        # archive the oldest by their merge-ref number (lowest first)
        def refnum(ln):
            m = re.search(r"r(\d+) 合并", ln)
            return int(m.group(1)) if m else 0
        ptr_sorted = sorted(pointer_idx, key=lambda i: refnum(out_lines[i]))
        archived = []
        i_ptr = 0
        while size > 10240 and i_ptr < len(ptr_sorted):
            li = ptr_sorted[i_ptr]
            archived.append(out_lines[li])
            out_lines[li] = None  # mark for removal
            i_ptr += 1
            size = len(("\n".join(l for l in out_lines if l is not None) + "\n").encode("utf-8"))
        out_lines = [l for l in out_lines if l is not None]
        out = "\n".join(out_lines) + "\n"
        assert "<<<<<<<" not in out
        # archive verbatim zero-loss
        ap = "research/memory-archive/202609.md"
        arch = open(ap, encoding="utf-8").read()
        section = ("\n## CODELY 热冷整编 2026-09-30 r458 bm-b rebase-union 窗批\n\n"
                   + "\n".join(archived) + "\n")
        with open(ap, "a", encoding="utf-8", newline="") as f:
            f.write(section)
        report.append((ap, f"archived {len(archived)} CODELY pointer lines verbatim (r458 trim)"))
    size = len(out.encode("utf-8"))
    assert size <= 10240, f"merged CODELY {size}B still over 10KB"
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(out)
    report.append((p, f"edit-union: my r457 reorg + origin r265/r467 adds - origin 8 drops + trim "
                       f"({size}B, archive-verbatim)"))


# -- twins (groups take ONE side) --
take_group(["docs/daily_report/REPORT-2026-09-30.json", "docs/daily_report/REPORT-2026-09-30.md"])
take_group(["docs/live_usage/LIVE-2026-09-30.json", "docs/live_usage/LIVE-2026-09-30.md",
            "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md"])

# -- plain snapshots (attrition scan = manual adjudication take-new by ts, r454/r457 precedent) --
for p in ["results/_attrition_guard_scan.json", "results/fundamental_b_layer_filter.json",
          "results/futures_update_status.json", "results/lhb_update_status.json",
          "results/token_usage.json", "results/update_status.json"]:
    take_new(p)

# -- fundamental_status: MANUAL truth-wins adjudication --
take_mine_manual("results/fundamental_status.json",
                 "(mine=10:55 post-fix rc0 full face; origin=11:05 bm-a pre-fix-code rc2 error face; "
                 "rebase carries my fix => truthful face = mine)")

# -- rolling ledgers --
union_ledger("results/compute_audit.json", "history", "ts")
union_ledger("results/regime_state.json", "history", "asof")

# -- append-log --
union_marks("results/paper/marks/marks-20260930.jsonl")

# -- CODELY edit-union + trim --
resolve_codely()

print("=== _r458bmb_resolve.py (batch 1/3: r457 replay) ===")
for p, note in report:
    print(f"{p} | {note}")
