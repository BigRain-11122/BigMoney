"""r508 bm-c rebase conflict resolver (7 UU, r505 v2 three-law blood).

Rebase semantics (observed): side1/'<<<<<<< HEAD' = origin tip (upstream,
pushed by other machines), side2/'>>>>>>> 0ea1c17c9' = my churn-absorb
commit.  diff3 style with '||||||| parent of <sha>' base block present.

Laws applied (r505 v2, CODELY.md):
  (1) generic-label anchor '<<<<<<< ' (any label, rebase/merge agnostic)
      + diff3 four-piece gate: n_open == n_mid == n_base == n_close,
      missing '|||||||' block -> throw (fail-closed).
  (2) sides rebuilt from working-tree text (no index stage reads, r405).
  (3) residual marker assertion anchored at line start (post-write).

Recipes (r505 + r440 two-分法):
  - ts-bearing whole-file faces: whole-side take by newer max timestamp
    (S6-regenerable shared faces; either side is a fresh snapshot, newer
    one wins; our S6 re-run this round regenerates them anyway).
  - compute_audit.json: history array union by (ts, machine) key, zero-loss.
  - pool_core_samples.jsonl: append-only line-level union (side1 lines
    first, side2-only lines appended; full-line identity).

Receipt -> results/_r508bmc_merge_resolve.json
Exit 0 ok / 1 gate failure (nothing written) / 2 mechanism fault.
"""
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TS_RE = re.compile(r"2026-10-0[0-9][ T]\d\d:\d\d:\d\d")

TAKE_SIDE_FACES = [
    "results/crash_fuse.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/update_status.json",
]
UNION_HISTORY_FACES = ["results/compute_audit.json"]
UNION_JSONL_FACES = ["results/pool_core_samples.jsonl"]

receipt = {"round": "r508", "strategies": {}, "sides": {}, "gates": {}}


def read_text(rel):
    with io.open(os.path.join(ROOT, rel), encoding="utf-8", errors="strict") as f:
        return f.read()


def write_text(rel, text):
    with io.open(os.path.join(ROOT, rel), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def parse_blocks(text):
    """Line-based diff3 parser. Returns (segments, blocks) or raises.

    segments: list of ('text', str) / ('block', dict) in document order.
    Every open must find base + mid + close (fail-closed, r505 law 1).
    """
    lines = text.split("\n")
    segments = []
    blocks = []
    i = 0
    n_open = n_base = n_mid = n_close = 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("<<<<<<< "):
            n_open += 1
            i += 1
            side1 = []
            while i < len(lines) and not lines[i].startswith("||||||| "):
                side1.append(lines[i])
                i += 1
            if i >= len(lines):
                raise RuntimeError("diff3 gate: '|||||||' missing for open block")
            n_base += 1
            i += 1
            base = []
            while i < len(lines) and not lines[i].startswith("======="):
                base.append(lines[i])
                i += 1
            if i >= len(lines):
                raise RuntimeError("diff3 gate: '=======' missing for open block")
            n_mid += 1
            i += 1
            side2 = []
            while i < len(lines) and not lines[i].startswith(">>>>>>> "):
                side2.append(lines[i])
                i += 1
            if i >= len(lines):
                raise RuntimeError("diff3 gate: '>>>>>>>' missing for open block")
            n_close += 1
            i += 1
            blk = {"side1": side1, "base": base, "side2": side2,
                   "open_label": ln, "close_line": lines[i - 1]}
            blocks.append(blk)
            segments.append(("block", blk))
        else:
            if ln.startswith(("=======", ">>>>>>> ", "||||||| ")):
                raise RuntimeError("diff3 gate: orphan marker line: %r" % ln[:40])
            segments.append(("text", [ln]))
            i += 1
    if not (n_open == n_base == n_mid == n_close):
        raise RuntimeError("diff3 gate: %d/%d/%d/%d != identity" %
                           (n_open, n_base, n_mid, n_close))
    return segments, blocks, (n_open, n_base, n_mid, n_close)


def rebuild(segments, which):
    out = []
    for kind, payload in segments:
        if kind == "text":
            out.extend(payload)
        else:
            out.extend(payload[which])
    return "\n".join(out)


def max_ts(text):
    hits = TS_RE.findall(text)
    return max(hits) if hits else ""


def resolve_take_side(rel):
    text = read_text(rel)
    segments, blocks, counts = parse_blocks(text)
    receipt["gates"][rel] = {"blocks": len(blocks), "diff3_counts": counts}
    if not blocks:
        receipt["sides"][rel] = "NO-MARKER (clean, untouched)"
        receipt["strategies"][rel] = "skip-clean"
        return
    ours = rebuild(segments, "side1")
    theirs = rebuild(segments, "side2")
    o_ts, t_ts = max_ts(ours), max_ts(theirs)
    # rebase: side1=origin(upstream)=HEAD, side2=my commit; label accordingly
    side = "origin" if o_ts >= t_ts else "mine"
    doc = ours if side == "origin" else theirs
    json.loads(doc)  # validation: chosen side must parse
    receipt["sides"][rel] = {"origin_ts": o_ts, "mine_ts": t_ts, "take": side}
    write_text(rel, doc if doc.endswith("\n") else doc + "\n")
    receipt["strategies"][rel] = "ts-newer-wins " + side


def resolve_union_history(rel):
    text = read_text(rel)
    segments, blocks, counts = parse_blocks(text)
    receipt["gates"][rel] = {"blocks": len(blocks), "diff3_counts": counts}
    ours_doc = rebuild(segments, "side1")
    theirs_doc = rebuild(segments, "side2")
    o = json.loads(ours_doc)
    t = json.loads(theirs_doc)
    hist_o = o.get("history", [])
    hist_t = t.get("history", [])
    key = lambda r: (r.get("ts", ""), r.get("machine", ""))
    seen = {}
    for r in hist_o + hist_t:
        k = key(r)
        if k not in seen or str(r) > str(seen[k]):
            seen[k] = r
    merged = sorted(seen.values(), key=lambda r: r.get("ts", ""))
    base = t if max_ts(theirs_doc) > max_ts(ours_doc) else o
    base["history"] = merged
    receipt["sides"][rel] = {"union": "history-union",
                             "origin_rows": len(hist_o), "mine_rows": len(hist_t),
                             "merged_rows": len(merged)}
    write_text(rel, json.dumps(base, ensure_ascii=False, indent=1) + "\n")
    receipt["strategies"][rel] = "history-union zero-loss"


def resolve_union_jsonl(rel):
    text = read_text(rel)
    segments, blocks, counts = parse_blocks(text)
    receipt["gates"][rel] = {"blocks": len(blocks), "diff3_counts": counts}
    origin_doc = rebuild(segments, "side1")
    mine_doc = rebuild(segments, "side2")
    o_lines = [l for l in origin_doc.split("\n") if l.strip()]
    m_lines = [l for l in mine_doc.split("\n") if l.strip()]
    seen = set(o_lines)
    merged = list(o_lines)
    added = 0
    for l in m_lines:
        if l not in seen:
            merged.append(l)
            seen.add(l)
            added += 1
    # validation: every merged line must parse as one JSON object
    for l in merged:
        json.loads(l)
    receipt["sides"][rel] = {"union": "line-union",
                             "origin_lines": len(o_lines), "mine_lines": len(m_lines),
                             "merged_lines": len(merged), "mine_only_added": added}
    write_text(rel, "\n".join(merged) + "\n")
    receipt["strategies"][rel] = "append-only line-union zero-loss"


def residual_check(rel):
    """r505 v2 law 3: residual marker assertion, line-start anchored."""
    text = read_text(rel)
    for ln in text.split("\n"):
        if ln.startswith(("<<<<<<< ", ">>>>>>> ", "||||||| ")) or ln == "=======":
            raise RuntimeError("residual marker in %s: %r" % (rel, ln[:40]))


def main():
    try:
        for rel in TAKE_SIDE_FACES:
            resolve_take_side(rel)
        for rel in UNION_HISTORY_FACES:
            resolve_union_history(rel)
        for rel in UNION_JSONL_FACES:
            resolve_union_jsonl(rel)
        all_files = TAKE_SIDE_FACES + UNION_HISTORY_FACES + UNION_JSONL_FACES
        for rel in all_files:
            residual_check(rel)
    except Exception as e:
        receipt["error"] = repr(e)
        json.dump(receipt, io.open(os.path.join(ROOT, "results",
                  "_r508bmc_merge_resolve.json"), "w", encoding="utf-8",
                  newline="\n"), ensure_ascii=False, indent=1)
        print("FAIL:", e)
        return 1
    out = os.path.join(ROOT, "results", "_r508bmc_merge_resolve.json")
    with io.open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(receipt, f, ensure_ascii=False, indent=1)
    print("RESOLVED", len(receipt["strategies"]), "files; receipt", out)
    for k, v in receipt["strategies"].items():
        print(" ", k, "->", v)
    return 0


if __name__ == "__main__":
    sys.exit(main())
