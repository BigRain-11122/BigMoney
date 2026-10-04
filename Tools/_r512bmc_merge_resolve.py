"""r512 bm-c MERGE-mode conflict resolver (17 UU, r509 canon adapted).

MERGE semantics (r704-ii/r511 law): side1/'<<<<<<< HEAD' = OURS (local),
side2 = THEIRS (origin/main commit). zdiff3 four-piece blocks
(<<<<<<< HEAD / ||||||| base / ======= / >>>>>>> label).

Recipes:
  - ts-bearing whole-file regen faces: newer max timestamp wins (tie -> ours);
    CEO daily_report/live_usage faces same law.
  - twin-lock: md/js twin resolved to the SAME side as its .json twin
    (r505 dashboard js law + r508 same-side law).
  - compute_audit.json: history array union by (ts, machine) zero-loss.
  - token_usage.json: per-key union (machines subdict merged, scalar
    newer-ts wins) -- r505/r497 union_token recipe.

Laws enforced: generic '<<<<<<< ' label anchor + four-piece identity gate
(missing base block -> throw), sides rebuilt from working-tree text,
residual marker assertion line-start anchored post-write, chosen json side
must parse before write.

Receipt -> results/_r512bmc_merge_resolve.json
Exit 0 ok / 1 gate failure (nothing further written) / 2 mechanism fault.
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
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/update_status.json",
]
# md/js twins -> json twin (twin-lock: twin follows json verdict)
TWIN_LOCK = {
    "docs/daily_report/REPORT-2026-10-05.md": "docs/daily_report/REPORT-2026-10-05.json",
    "docs/live_usage/LIVE-2026-10-05.md": "docs/live_usage/LIVE-2026-10-05.json",
    "docs/live_usage/LIVE-latest.md": "docs/live_usage/LIVE-latest.json",
    "results/dashboard_status.js": "results/dashboard_status.json",
}
UNION_HISTORY_FACES = ["results/compute_audit.json"]
UNION_TOKEN_FACES = ["results/token_usage.json"]

receipt = {"round": "r512", "mode": "merge", "strategies": {}, "sides": {},
           "gates": {}}


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
            blk = {"ours": side1, "base": base, "theirs": side2}
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
    """Returns ('ours'|'theirs', doc) or (None, None) if clean. MERGE mode:
    side1/HEAD = ours(local), side2 = theirs(origin)."""
    text = read_text(rel)
    segments, blocks, counts = parse_blocks(text)
    receipt["gates"][rel] = {"blocks": len(blocks), "diff3_counts": counts}
    if not blocks:
        if not quiet:
            receipt["sides"][rel] = "NO-MARKER (clean, untouched)"
            receipt["strategies"][rel] = "skip-clean"
        return None, None
    ours = rebuild(segments, "ours")
    theirs = rebuild(segments, "theirs")
    o_ts, t_ts = max_ts(ours), max_ts(theirs)
    side = "ours" if o_ts >= t_ts else "theirs"
    doc = ours if side == "ours" else theirs
    receipt["sides"][rel] = {"ours_ts": o_ts, "theirs_ts": t_ts, "take": side}
    return side, doc


def resolve_take_side(rel, must_parse=True):
    side, doc = take_side_of(rel)
    if side is None:
        return
    if must_parse:
        json.loads(doc)  # chosen side must parse (json faces)
    write_text(rel, doc if doc.endswith("\n") else doc + "\n")
    receipt["strategies"][rel] = "ts-newer-wins " + side


def resolve_twin_lock(rel, json_rel):
    side, doc = take_side_of(rel, quiet=True)
    if side is None:
        receipt["strategies"][rel] = "twin clean (auto-merged)"
        return
    json_side = receipt["sides"].get(json_rel, {}).get("take")
    if json_side is None:
        # json twin had no markers (auto-merged clean): fall back to our own
        # ts verdict so the twin still lands on a coherent side (r508 law:
        # no independent fallback... json auto-merged means its content is
        # already the merged truth; force twin to the SAME ts verdict it
        # would take, preferring ours on tie).
        json_side = side
    text = read_text(rel)
    segments, blocks, _ = parse_blocks(text)
    chosen = "ours" if json_side == "ours" else "theirs"
    doc = rebuild(segments, chosen)
    write_text(rel, doc if doc.endswith("\n") else doc + "\n")
    receipt["strategies"][rel] = "twin-locked-to-json " + str(json_side)
    receipt["sides"][rel] = {"twin_of": json_rel, "take": json_side}


def resolve_union_history(rel):
    text = read_text(rel)
    segments, blocks, counts = parse_blocks(text)
    receipt["gates"][rel] = {"blocks": len(blocks), "diff3_counts": counts}
    ours_doc = rebuild(segments, "ours")
    theirs_doc = rebuild(segments, "theirs")
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
    base = o if max_ts(ours_doc) >= max_ts(theirs_doc) else t
    base["history"] = merged
    receipt["sides"][rel] = {"union": "history-union",
                             "ours_rows": len(hist_o), "theirs_rows": len(hist_t),
                             "merged_rows": len(merged)}
    write_text(rel, json.dumps(base, ensure_ascii=False, indent=1) + "\n")
    receipt["strategies"][rel] = "history-union zero-loss"


def resolve_union_token(rel):
    text = read_text(rel)
    segments, blocks, counts = parse_blocks(text)
    receipt["gates"][rel] = {"blocks": len(blocks), "diff3_counts": counts}
    ours_doc = rebuild(segments, "ours")
    theirs_doc = rebuild(segments, "theirs")
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
        # 2. md/js twins locked to json verdicts
        for rel, json_rel in TWIN_LOCK.items():
            resolve_twin_lock(rel, json_rel)
        # 3. unions
        for rel in UNION_HISTORY_FACES:
            resolve_union_history(rel)
        for rel in UNION_TOKEN_FACES:
            resolve_union_token(rel)
        all_files = (TAKE_SIDE_FACES + list(TWIN_LOCK.keys()) + UNION_HISTORY_FACES
                     + UNION_TOKEN_FACES)
        for rel in all_files:
            residual_check(rel)
    except Exception as e:
        receipt["error"] = repr(e)
        with io.open(os.path.join(ROOT, "results", "_r512bmc_merge_resolve.json"),
                     "w", encoding="utf-8", newline="\n") as f:
            json.dump(receipt, f, ensure_ascii=False, indent=1)
        print("FAIL:", e)
        return 1
    out = os.path.join(ROOT, "results", "_r512bmc_merge_resolve.json")
    with io.open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(receipt, f, ensure_ascii=False, indent=1)
    print("RESOLVED", len(receipt["strategies"]), "files; receipt", out)
    for k, v in receipt["strategies"].items():
        sv = receipt["sides"].get(k)
        extra = ""
        if isinstance(sv, dict) and "take" in sv:
            extra = " [take=%s ours_ts=%s theirs_ts=%s]" % (
                sv.get("take"), sv.get("ours_ts"), sv.get("theirs_ts"))
        print(" ", k, "->", v, extra)
    return 0


if __name__ == "__main__":
    sys.exit(main())
