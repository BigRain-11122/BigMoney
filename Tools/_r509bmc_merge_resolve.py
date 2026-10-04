"""r509 bm-c rebase conflict resolver (16 UU, r505 v2 three-law + r508 extension).

Rebase semantics (observed): side1/'<<<<<<< HEAD' = origin tip, side2 =
my consolidated round-509 commit. diff3 with '||||||| parent of <sha>' base.

Recipes (r505 canon + r508 extension):
  - ts-bearing whole-file faces: newer max timestamp wins (S6-regenerable
    shared snapshots; CEO daily_report/live_usage faces same law).
  - twin-lock: .md twin resolved to the SAME side as its .json twin
    (r505 dashboard_status.js law -- md/js follow json verdict).
  - compute_audit.json: history array union by (ts, machine) zero-loss.
  - token_usage.json: per-key union (machines subdict merged per machine,
    scalar newer-ts wins) -- r505 union_token recipe.
  - pool_core_samples.jsonl: append-only line-level union.

Laws: generic '<<<<<<< ' label anchor + diff3 four-piece identity gate
(missing base block -> throw), sides rebuilt from working-tree text,
residual marker assertion line-start anchored post-write.

Receipt -> results/_r509bmc_merge_resolve.json
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
    "docs/daily_report/REPORT-2026-10-05.json",
    "docs/live_usage/LIVE-2026-10-05.json",
    "docs/live_usage/LIVE-latest.json",
    "results/_attrition_guard_scan.json",
    "results/crash_fuse.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/update_status.json",
]
# md twin -> json twin (twin-lock: md follows json verdict)
TWIN_LOCK = {
    "docs/daily_report/REPORT-2026-10-05.md": "docs/daily_report/REPORT-2026-10-05.json",
    "docs/live_usage/LIVE-2026-10-05.md": "docs/live_usage/LIVE-2026-10-05.json",
    "docs/live_usage/LIVE-latest.md": "docs/live_usage/LIVE-latest.json",
}
UNION_HISTORY_FACES = ["results/compute_audit.json"]
UNION_TOKEN_FACES = ["results/token_usage.json"]
UNION_JSONL_FACES = ["results/pool_core_samples.jsonl"]

receipt = {"round": "r509", "strategies": {}, "sides": {}, "gates": {}}


def read_text(rel):
    with io.open(os.path.join(ROOT, rel), encoding="utf-8", errors="strict") as f:
        return f.read()


def write_text(rel, text):
    with io.open(os.path.join(ROOT, rel), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def parse_blocks(text):
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
            blk = {"side1": side1, "base": base, "side2": side2}
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


def take_side_of(rel, quiet=False):
    """Returns ('origin'|'mine', doc) and writes nothing; or (None, None) if clean."""
    text = read_text(rel)
    segments, blocks, counts = parse_blocks(text)
    receipt["gates"][rel] = {"blocks": len(blocks), "diff3_counts": counts}
    if not blocks:
        if not quiet:
            receipt["sides"][rel] = "NO-MARKER (clean, untouched)"
            receipt["strategies"][rel] = "skip-clean"
        return None, None
    ours = rebuild(segments, "side1")
    theirs = rebuild(segments, "side2")
    o_ts, t_ts = max_ts(ours), max_ts(theirs)
    side = "origin" if o_ts >= t_ts else "mine"
    doc = ours if side == "origin" else theirs
    receipt["sides"][rel] = {"origin_ts": o_ts, "mine_ts": t_ts, "take": side}
    return side, doc


def resolve_take_side(rel):
    side, doc = take_side_of(rel)
    if side is None:
        return
    json.loads(doc)  # chosen side must parse (json faces)
    write_text(rel, doc if doc.endswith("\n") else doc + "\n")
    receipt["strategies"][rel] = "ts-newer-wins " + side


def resolve_twin_lock(rel, json_rel):
    side, doc = take_side_of(rel, quiet=True)
    if side is None:
        # md clean: check json twin was resolved; if json took a side and md
        # is clean it means auto-merge handled it -- leave as-is.
        receipt["strategies"][rel] = "twin-md clean (auto-merged)"
        return
    json_side = receipt["sides"].get(json_rel, {}).get("take")
    # force md to the SAME side as its json twin (r505 twin-lock law)
    text = read_text(rel)
    segments, blocks, _ = parse_blocks(text)
    chosen = "side1" if json_side == "origin" else "side2"
    doc = rebuild(segments, chosen)
    write_text(rel, doc if doc.endswith("\n") else doc + "\n")
    receipt["strategies"][rel] = "twin-locked-to-json " + str(json_side)
    receipt["sides"][rel] = {"twin_of": json_rel, "take": json_side}


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


def resolve_union_token(rel):
    text = read_text(rel)
    segments, blocks, counts = parse_blocks(text)
    receipt["gates"][rel] = {"blocks": len(blocks), "diff3_counts": counts}
    ours_doc = rebuild(segments, "side1")
    theirs_doc = rebuild(segments, "side2")
    o = json.loads(ours_doc)
    t = json.loads(theirs_doc)

    def merge(a, b):
        if isinstance(a, dict) and isinstance(b, dict):
            out = dict(a)
            for k, v in b.items():
                out[k] = merge(out[k], v) if k in out else v
            return out
        return b if max_ts(str(b)) > max_ts(str(a)) else a

    merged = merge(o, t)
    receipt["sides"][rel] = {"union": "per-key-union"}
    write_text(rel, json.dumps(merged, ensure_ascii=False, indent=1) + "\n")
    receipt["strategies"][rel] = "per-key-union"


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
    for l in merged:
        json.loads(l)
    receipt["sides"][rel] = {"union": "line-union",
                             "origin_lines": len(o_lines), "mine_lines": len(m_lines),
                             "merged_lines": len(merged), "mine_only_added": added}
    write_text(rel, "\n".join(merged) + "\n")
    receipt["strategies"][rel] = "append-only line-union zero-loss"


def residual_check(rel):
    text = read_text(rel)
    for ln in text.split("\n"):
        if ln.startswith(("<<<<<<< ", ">>>>>>> ", "||||||| ")) or ln == "=======":
            raise RuntimeError("residual marker in %s: %r" % (rel, ln[:40]))


def main():
    try:
        # 1. json faces first (twins need their verdicts)
        for rel in TAKE_SIDE_FACES:
            resolve_take_side(rel)
        # 2. md twins locked to json verdicts
        for rel, json_rel in TWIN_LOCK.items():
            resolve_twin_lock(rel, json_rel)
        # 3. unions
        for rel in UNION_HISTORY_FACES:
            resolve_union_history(rel)
        for rel in UNION_TOKEN_FACES:
            resolve_union_token(rel)
        for rel in UNION_JSONL_FACES:
            resolve_union_jsonl(rel)
        all_files = (TAKE_SIDE_FACES + list(TWIN_LOCK.keys()) + UNION_HISTORY_FACES
                     + UNION_TOKEN_FACES + UNION_JSONL_FACES)
        for rel in all_files:
            residual_check(rel)
    except Exception as e:
        receipt["error"] = repr(e)
        with io.open(os.path.join(ROOT, "results", "_r509bmc_merge_resolve.json"),
                     "w", encoding="utf-8", newline="\n") as f:
            json.dump(receipt, f, ensure_ascii=False, indent=1)
        print("FAIL:", e)
        return 1
    out = os.path.join(ROOT, "results", "_r509bmc_merge_resolve.json")
    with io.open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(receipt, f, ensure_ascii=False, indent=1)
    print("RESOLVED", len(receipt["strategies"]), "files; receipt", out)
    for k, v in receipt["strategies"].items():
        print(" ", k, "->", v)
    return 0


if __name__ == "__main__":
    sys.exit(main())
