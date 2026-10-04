"""r511 bm-c rebase conflict resolver (r509 canon + r510 twin-dispatch fix +
r707 residual-line tolerance).

Architecture (two-tier):
  Tier-1 CANONICAL: results/ faces in merge_lane_views.ALL_FACES delegate to
  `python scripts/merge_lane_views.py resolve <path>` (stage-blob read,
  per-face merger recipes, parse-verified write). runnable_pool/crash_fuse/
  compute_audit/regime_state/update_status/lhb/futures/token_usage.
  Tier-2 LOCAL: ts-take-side json faces (r509), twin-lock md/js to json
  verdict (r510 fix: BOTH twin members dispatched; md-clean fallback resolves
  by own ts instead of blind side2), tolerant append-only jsonl union
  (r707: terminal residual set must be subset of source residual set).

Laws: generic '<<<<<<< ' label anchor (rebase mode: 'Updated upstream' =
origin side1) + diff3 four-piece identity gate (missing base block -> throw),
sides rebuilt from working-tree text (r505), residual marker assertion
line-start anchored post-write (r506 v2), unexpected UU face = fail-closed
abort (zero silent generic fallback).

Receipt -> results/_r511bmc_rebase_resolve.json
Exit 0 ok / 1 gate failure (nothing further written) / 2 mechanism fault.
"""
import io
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TS_RE = re.compile(r"2026-10-0[0-9][ T]\d\d:\d\d:\d\d")

CANONICAL_FACES = [
    "results/runnable_pool.json",
    "results/crash_fuse.json",
    "results/compute_audit.json",
    "results/regime_state.json",
    "results/update_status.json",
    "results/lhb_update_status.json",
    "results/futures_update_status.json",
    "results/token_usage.json",
]
TAKE_SIDE_FACES = [
    "docs/daily_report/REPORT-2026-10-05.json",
    "docs/live_usage/LIVE-2026-10-05.json",
    "docs/live_usage/LIVE-latest.json",
    "results/_attrition_guard_scan.json",
    "results/dashboard_status.json",
    "results/strategy_scorecard.json",
    "results/scorecard_v1.json",
    "results/fundamental_b_layer_filter.json",
    "results/fund_premium_status.json",
]
# twin md/js -> json twin (r510 fix: both members dispatched; md/js follow
# json verdict; json-clean fallback resolves twin by its OWN newer ts)
TWIN_LOCK = {
    "docs/daily_report/REPORT-2026-10-05.md": "docs/daily_report/REPORT-2026-10-05.json",
    "docs/live_usage/LIVE-2026-10-05.md": "docs/live_usage/LIVE-2026-10-05.json",
    "docs/live_usage/LIVE-latest.md": "docs/live_usage/LIVE-latest.json",
    "results/dashboard_status.js": "results/dashboard_status.json",
}
UNION_JSONL_TOLERANT = [
    "results/pool_core_samples.jsonl",
    "results/pool_red_flags.jsonl",
]

receipt = {"round": "r511", "strategies": {}, "sides": {}, "gates": {},
           "canonical": {}, "unexpected": []}


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
    text = read_text(rel)
    segments, blocks, counts = parse_blocks(text)
    receipt["gates"][rel] = {"blocks": len(blocks), "diff3_counts": counts}
    if not blocks:
        if not quiet:
            receipt["sides"][rel] = "NO-MARKER (clean, untouched)"
            receipt["strategies"][rel] = "skip-clean"
        return None, None
    ours = rebuild(segments, "side1")     # rebase mode: side1 = origin
    theirs = rebuild(segments, "side2")   # side2 = mine (replayed)
    o_ts, t_ts = max_ts(ours), max_ts(theirs)
    side = "origin" if o_ts >= t_ts else "mine"
    doc = ours if side == "origin" else theirs
    receipt["sides"][rel] = {"origin_ts": o_ts, "mine_ts": t_ts, "take": side}
    return side, doc


def resolve_take_side(rel):
    side, doc = take_side_of(rel)
    if side is None:
        return
    json.loads(doc)
    write_text(rel, doc if doc.endswith("\n") else doc + "\n")
    receipt["strategies"][rel] = "ts-newer-wins " + side


def resolve_twin_lock(rel, json_rel):
    side, doc = take_side_of(rel, quiet=True)
    if side is None:
        receipt["strategies"][rel] = "twin clean (auto-merged)"
        return
    json_side = receipt["sides"].get(json_rel, {}).get("take")
    text = read_text(rel)
    segments, blocks, _ = parse_blocks(text)
    if json_side in ("origin", "mine"):
        chosen = "side1" if json_side == "origin" else "side2"
        strat = "twin-locked-to-json " + json_side
    else:
        # r510 fix companion: json twin had no conflict of its own -> resolve
        # twin by its OWN newer ts (never a blind side pick)
        o_ts, t_ts = max_ts(rebuild(segments, "side1")), max_ts(rebuild(segments, "side2"))
        chosen = "side1" if o_ts >= t_ts else "side2"
        strat = "twin-own-ts-newer-wins " + ("origin" if chosen == "side1" else "mine")
    doc = rebuild(segments, chosen)
    write_text(rel, doc if doc.endswith("\n") else doc + "\n")
    receipt["strategies"][rel] = strat
    receipt["sides"][rel] = {"twin_of": json_rel,
                             "take": "origin" if chosen == "side1" else "mine"}


def _jsonl_parses(line):
    try:
        json.loads(line)
        return True
    except Exception:
        return False


def resolve_union_jsonl_tolerant(rel):
    text = read_text(rel)
    segments, blocks, counts = parse_blocks(text)
    receipt["gates"][rel] = {"blocks": len(blocks), "diff3_counts": counts}
    origin_doc = rebuild(segments, "side1")
    mine_doc = rebuild(segments, "side2")
    o_lines = [l for l in origin_doc.split("\n") if l.strip()]
    m_lines = [l for l in mine_doc.split("\n") if l.strip()]
    # r707 residual tolerance: pre-scan BOTH sides for historical residual
    # (non-parseable) lines; they are lawful source content, kept verbatim.
    o_resid = {l for l in o_lines if not _jsonl_parses(l)}
    m_resid = {l for l in m_lines if not _jsonl_parses(l)}
    src_resid = o_resid | m_resid
    seen = set(o_lines)
    merged = list(o_lines)
    added = 0
    for l in m_lines:
        if l not in seen:
            merged.append(l)
            seen.add(l)
            added += 1
    term_resid = {l for l in merged if not _jsonl_parses(l)}
    if not term_resid <= src_resid:
        raise RuntimeError("r707 gate: terminal residual not subset of source residual in %s" % rel)
    receipt["sides"][rel] = {"union": "line-union-tolerant",
                             "origin_lines": len(o_lines), "mine_lines": len(m_lines),
                             "merged_lines": len(merged), "mine_only_added": added,
                             "source_residual_lines": len(src_resid),
                             "terminal_residual_lines": len(term_resid)}
    write_text(rel, "\n".join(merged) + "\n")
    receipt["strategies"][rel] = "append-only line-union tolerant zero-loss"


def resolve_canonical(rel):
    r = subprocess.run([sys.executable, os.path.join(ROOT, "scripts",
                                                      "merge_lane_views.py"),
                        "resolve", rel], capture_output=True, cwd=ROOT,
                       timeout=300)
    out = (r.stdout + b"\n" + r.stderr).decode("utf-8", "replace")
    receipt["canonical"][rel] = {"rc": r.returncode, "tail": out.strip()[-400:]}
    if r.returncode != 0:
        raise RuntimeError("canonical resolve failed for %s: %s" % (rel, out[-300:]))
    receipt["strategies"][rel] = "canonical merge_lane_views resolve"


def residual_check(rel):
    text = read_text(rel)
    for ln in text.split("\n"):
        if ln.startswith(("<<<<<<< ", ">>>>>>> ", "||||||| ")) or ln == "=======":
            raise RuntimeError("residual marker in %s: %r" % (rel, ln[:40]))


def uu_list():
    r = subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"],
                       capture_output=True, cwd=ROOT)
    return [l.strip() for l in r.stdout.decode("utf-8", "replace").split("\n")
            if l.strip()]


def save_receipt():
    out = os.path.join(ROOT, "results", "_r511bmc_rebase_resolve.json")
    with io.open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(receipt, f, ensure_ascii=False, indent=1)
    return out


def main():
    try:
        uus = uu_list()
        receipt["uu_faces"] = uus
        known = set(CANONICAL_FACES) | set(TAKE_SIDE_FACES) | set(TWIN_LOCK) | set(UNION_JSONL_TOLERANT)
        unexpected = [u for u in uus if u.replace("\\", "/") not in known]
        if unexpected:
            receipt["unexpected"] = unexpected
            save_receipt()
            print("FAIL-CLOSED: unexpected UU faces:", unexpected)
            return 1
        rels = [u.replace("\\", "/") for u in uus]
        # 1. canonical tier first (pool/fuse/audit/token mergers)
        for rel in rels:
            if rel in CANONICAL_FACES:
                resolve_canonical(rel)
        # 2. ts-take json faces
        for rel in rels:
            if rel in TAKE_SIDE_FACES:
                resolve_take_side(rel)
        # 3. twin md/js locked to json verdicts (r510 fix: both dispatched)
        for rel, json_rel in TWIN_LOCK.items():
            if rel in rels:
                resolve_twin_lock(rel, json_rel)
        # 4. tolerant jsonl unions
        for rel in rels:
            if rel in UNION_JSONL_TOLERANT:
                resolve_union_jsonl_tolerant(rel)
        all_files = (CANONICAL_FACES + TAKE_SIDE_FACES + list(TWIN_LOCK.keys())
                     + UNION_JSONL_TOLERANT)
        for rel in all_files:
            if rel in rels:
                residual_check(rel)
        out = save_receipt()
        print("RESOLVED", len(receipt["strategies"]), "of", len(rels), "UU faces; receipt", out)
        for k, v in receipt["strategies"].items():
            print(" ", k, "->", v)
        return 0
    except Exception as e:
        receipt["error"] = repr(e)
        save_receipt()
        print("FAIL:", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
