"""_r457bmb_resolve.py -- bm-b r457 rebase collision resolver.

Origin delta landed between my S0 pull and push (rebase stage :2: = origin):
  - bm-c r264 (SLOT-10 + CODELY union reorg 9597->9244B: dropped 2 redundant
    Feedback cold-pointer lines per r449 dedupe law, appended r264 hot entry,
    appended r264 archive section)
  - bm-a r467 pre (W13 carry: grammar ledger + candidates + marks ticks)
My side (:3:): fix-red + S6 faces + CODELY reorg (r454/r455 -> pointer,
r457 entry appended) + r457 archive section.

Recipes per bigmoney-conflict-resolve SKILL.md:
- snapshot twins (REPORT / LIVE groups): deep-ts probe, ONE side wins all.
- plain snapshots incl. classifier-UNKNOWN _attrition_guard_scan.json
  (manual adjudication: scan-evidence snapshot, take-new by ts; facts
  probed: mine 10:57:31 > origin 10:41:22) -- R208/r100/R350 hardened probe.
- rolling-ledger (compute_audit/regime_state): history union zero-loss +
  state take-new (r188/R208).
- marks jsonl: append-log line-level union, parse-verify, sort by ts.
- research/memory-archive/202609.md (classifier UNKNOWN -> manual):
  both sides appended one section each; edit-union = origin content +
  my r457 section appended (r264 landed 10:39, mine written 10:52).
- CODELY.md: NEITHER side is a pure append (mine = in-place reorg, origin =
  in-place dedupe drops) -> edit-union: my side verbatim, apply origin's
  removed-lines (the 2 Feedback pointers), insert origin's added line
  (r264 bm-c entry) before my r457 tail entry (chronological landing order).
Parse-verify every JSON; zero-loss assertions per file family.
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
                    if any(p in nk for p in ("ts", "generated", "updated",
                                            "asof", "attempt", "scanned", "written")):
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


def take_new(p):
    ts_c = deep_ts(json.loads(blob(":2:" + p)))
    ts_m = deep_ts(json.loads(blob(":3:" + p)))
    winner = "m" if ts_m >= ts_c else "c"
    data = blob((":3:" if winner == "m" else ":2:") + p)
    json.loads(data)
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(data)
    report.append((p, f"take-{winner} (c={ts_c} m={ts_m})"))


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
        json.loads(ln)  # parse-verify every line
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(merged) + "\n")
    report.append((p, f"append-log union {len(lc)}+{len(lm)}->{len(merged)} lines, sorted by ts"))


def resolve_archive():
    p = "research/memory-archive/202609.md"
    oc = blob(":2:" + p).splitlines(keepends=True)
    om = blob(":3:" + p).splitlines(keepends=True)
    # longest common line-prefix
    n = 0
    while n < len(oc) and n < len(om) and oc[n] == om[n]:
        n += 1
    their_suffix = "".join(oc[n:])
    my_suffix = "".join(om[n:])
    assert their_suffix.lstrip("\n").startswith("## 热冷整编 2026-09-30 r264 bm-c"), \
        f"origin suffix unexpected: {their_suffix[:80]!r}"
    assert my_suffix.lstrip("\n").startswith("## 热冷整编 2026-09-30 r457 bm-b"), \
        f"my suffix unexpected: {my_suffix[:80]!r}"
    base_common = "".join(oc[:n])
    assert their_suffix.strip() in blob(":2:" + p) and my_suffix.strip() in blob(":3:" + p)
    out = base_common.rstrip("\n") + "\n\n" + their_suffix.lstrip("\n").rstrip("\n") + "\n\n" + my_suffix.lstrip("\n")
    if not out.endswith("\n"):
        out += "\n"
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(out)
    report.append((p, f"edit-union: common {n} lines + origin r264 section + my r457 section ({len(out.encode('utf-8'))}B)"))


def resolve_codely():
    p = "CODELY.md"
    base_lines = blob(":1:" + p).splitlines()
    oc_lines = blob(":2:" + p).splitlines()
    my_lines = blob(":3:" + p).splitlines()
    # origin delta vs base (multiset line diff)
    tmp_base = list(base_lines)
    added = []
    for ln in oc_lines:
        if ln in tmp_base:
            tmp_base.remove(ln)
        else:
            added.append(ln)
    removed = tmp_base  # base lines origin dropped
    assert len(added) == 2, f"origin added-lines unexpected ({len(added)}): {[a[:50] for a in added]}"
    assert added[0].startswith("- [2026-09-30 r264 bm-c]"), f"added[0]: {added[0][:60]!r}"
    assert added[1].startswith("- 冷层指针（r264"), f"added[1]: {added[1][:60]!r}"
    assert len(removed) == 3, f"origin removed-lines unexpected ({len(removed)}): {[r[:50] for r in removed]}"
    rem_263 = [ln for ln in removed if ln.startswith("- [2026-09-30 r263 bm-c]")]
    rem_465 = [ln for ln in removed if ln.startswith("- [2026-09-30 r465 bm-a]")]
    rem_454 = [ln for ln in removed if ln.startswith("- [2026-09-30 r454 bm-b]")]
    assert len(rem_263) == 1 and len(rem_465) == 1 and len(rem_454) == 1, \
        f"removed set not r263+r465+r454: {[r[:50] for r in removed]}"
    # apply origin edits to MY face
    out_lines = [ln for ln in my_lines if ln not in removed]
    # insert origin's r264 pair at origin's position: after the r261-合并 pointer
    anchor = next(i for i, ln in enumerate(out_lines)
                  if ln.startswith("- 冷层指针（r261 合并"))
    out_lines[anchor + 1:anchor + 1] = added  # entry then pointer (origin file order)
    out = "\n".join(out_lines) + "\n"
    assert "<<<<<<<" not in out and ">>>>>>>" not in out
    for ln in added:
        assert ln in out
    for ln in removed:
        assert ln not in out
    assert "- [2026-09-30 r457 bm-b]" in out  # my tail entry intact
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(out)
    size = len(out.encode("utf-8"))
    assert size < 10240, f"merged CODELY {size}B over 10KB line"
    report.append((p, f"edit-union: my reorg kept + origin adds r264 entry+pointer @Feedback + drops r263/r465 (archived by bm-c r264) ({size}B)"))


# -- twins (groups take ONE side) --
take_group(["docs/daily_report/REPORT-2026-09-30.json", "docs/daily_report/REPORT-2026-09-30.md"])
take_group(["docs/live_usage/LIVE-2026-09-30.json", "docs/live_usage/LIVE-2026-09-30.md",
            "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md"])

# -- plain snapshots (attrition scan = manual adjudication take-new by ts, r454 precedent) --
for p in ["results/_attrition_guard_scan.json", "results/fundamental_b_layer_filter.json",
          "results/fundamental_status.json", "results/futures_update_status.json",
          "results/lhb_update_status.json", "results/token_usage.json",
          "results/update_status.json"]:
    take_new(p)

# -- rolling ledgers --
union_ledger("results/compute_audit.json", "history", "ts")
union_ledger("results/regime_state.json", "history", "asof")

# -- append-log --
union_marks("results/paper/marks/marks-20260930.jsonl")

# -- UNKNOWN manual faces --
resolve_archive()
resolve_codely()

print("=== _r457bmb_resolve.py ===")
for p, note in report:
    print(f"{p} | {note}")
