"""R314 bm-b pool done-flip: T-89 PROSPECT-REGIME-SEGMENTS + T-90 DECISION-CHAIN-E2E-X2.

r302 law: flip FIRST -- runners never edit the pool, so a completed shard
stays "ready" and the next autofill tick re-burns it (no-op relaunches) and,
worse, the O-0947 crash-fuse confirm window (FUSE_CONFIRM_MIN=25min,
runner dead + shard not landed) turns every fast-completing shard into a
FALSE confirmed crash at age>25min -> shared-fuse refusal of the entry.
Live instance: dce2-legacy-lb done 09:33:54 (1884/1884 cells, 66.5s),
false-crash window opens 09:57:47.

Evidence gate (refuse on ANY mismatch, zero blind flips):
  runner's own done marker on this machine (lane-local face):
    X2   results/decision_chain/done_x2_{axis}_{shard}.json
    PROS results/pros_segs/done_{axis}_{shard}.json
  marker.shard/axis/face exact-match entry runner_args;
  marker.cells_written == marker.cells_total;
  marker.cells_total == N_MEMBERS * eligible-range positions
    (positions = max(0, min(pos_to, census) - min(pos_from, census)));
  marker.n_eligible == frozen prereg census (X2: legacy 1255 / deep 1506
    per DECISION_CHAIN_E2E_P1 s9; PROS: legacy 1256 / deep 1506 per
    PROS_REGIME_SEGMENTS_P1 s2-iii amendment);
  N_MEMBERS derived from the frozen runners' own faces (t34.ATTACK+CHOP,
    prospect_regime_segments.N_MEMBERS), zero re-derivation.
Probe-subset markers (e.g. done_x2_legacy_lA.json 36 cells) fail the
expected-cells gate -> refused. Idempotent: done entries skipped.
Re-run each round while the two batches grind (r315+ next-pointer).
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

POOL = os.path.join(ROOT, "results", "runnable_pool.json")

BATCHES = {
    "scripts/decision_chain_e2e.py": {
        "entry_prefix": "DECISION-CHAIN-E2E-X2-",
        "marker_dir": os.path.join(ROOT, "results", "decision_chain"),
        "marker_fmt": "done_x2_{axis}_{shard}.json",
        "face": "x2",
        "census": {"legacy": 1255, "deep": 1506},
        "ticket": "T-2026-09-27-90",
    },
    "scripts/prospect_regime_segments.py": {
        "entry_prefix": "PROSPECT-REGIME-SEGMENTS-",
        "marker_dir": os.path.join(ROOT, "results", "pros_segs"),
        "marker_fmt": "done_{axis}_{shard}.json",
        "face": "base",
        "census": {"legacy": 1256, "deep": 1506},
        "ticket": "T-2026-09-26-89",
    },
}


def n_members(runner):
    if "decision_chain_e2e" in runner:
        import t34_early_signal as t34
        return len(t34.ATTACK) + len(t34.CHOP)
    import prospect_regime_segments as prs
    return prs.N_MEMBERS


def parse_args(runner_args):
    a = {}
    i = 0
    while i < len(runner_args) - 1:
        k = runner_args[i]
        if k.startswith("--"):
            a[k[2:]] = runner_args[i + 1]
            i += 2
        else:
            i += 1
    return a


def main():
    raw = open(POOL, "rb").read()
    pool = json.loads(raw.decode("utf-8-sig"))
    flips, pending, refused = [], [], []
    for e in pool.get("entries", []):
        cfg = BATCHES.get(e.get("runner"))
        if not cfg or not str(e.get("id", "")).startswith(cfg["entry_prefix"]):
            continue
        if e.get("status") != "ready":
            continue                      # done/retired -> idempotent skip
        a = parse_args(e.get("runner_args", []))
        axis, shard = a.get("axis"), a.get("shard")
        pos_from, pos_to = int(a["pos-from"]), int(a["pos-to"])
        census = cfg["census"].get(axis)
        nm = n_members(e["runner"])
        exp = nm * max(0, min(pos_to, census) - min(pos_from, census))
        mp = os.path.join(cfg["marker_dir"],
                          cfg["marker_fmt"].format(axis=axis, shard=shard))
        if not os.path.isfile(mp):
            pending.append(f"{e['id']}: marker absent (not yet run here)")
            continue
        m = json.load(open(mp, encoding="utf-8-sig"))
        why = None
        if m.get("shard") != shard or m.get("axis") != axis:
            why = f"marker shard/axis mismatch {m.get('shard')}/{m.get('axis')}"
        elif m.get("face") != cfg["face"]:
            why = f"face {m.get('face')} != {cfg['face']}"
        elif m.get("n_eligible") != census:
            why = f"n_eligible {m.get('n_eligible')} != frozen census {census}"
        elif m.get("cells_written") != m.get("cells_total"):
            why = f"partial {m.get('cells_written')}/{m.get('cells_total')}"
        elif m.get("cells_total") != exp:
            why = f"cells_total {m.get('cells_total')} != expected {exp}" \
                  f" ({nm} members x {exp // nm} pos) -- probe-subset refused"
        if why:
            refused.append(f"{e['id']}: {why}")
            continue
        ref = os.path.relpath(mp, ROOT).replace("\\", "/")
        e["status"] = "done"
        e["result_ref"] = ref
        e["note_done"] = (f"r314 bm-b flip: full-completion marker "
                          f"{m['cells_written']}/{m['cells_total']} cells "
                          f"(finished {m.get('finished_at')}), {cfg['ticket']} "
                          f"verdict face = batch harvest pending remaining "
                          f"shards; flip law r302")
        for sh in e.get("shards", []):
            sh["status"] = "done"
            sh["result_ref"] = ref
        flips.append(f"{e['id']}: flipped done "
                     f"({m['cells_written']}/{m['cells_total']} cells)")

    if flips:
        nl = "\r\n" if b"\r\n" in raw[:2000] else "\n"
        indent = 1 if raw[:200].find(b'\n "') >= 0 else 2
        text = json.dumps(pool, ensure_ascii=False, indent=indent)
        with open(POOL, "w", encoding="utf-8", newline="") as fh:
            fh.write(text + nl)
        chk = json.load(open(POOL, encoding="utf-8-sig"))
        n_done = sum(1 for e in chk["entries"]
                     if str(e.get("id", "")).startswith(
                         ("DECISION-CHAIN-E2E-X2-", "PROSPECT-REGIME-SEGMENTS-"))
                     and e.get("status") == "done")
        assert n_done >= len(flips), "flip write-back lost entries"

    print(f"r314 pool flip: {len(flips)} flipped, {len(pending)} pending, "
          f"{len(refused)} refused")
    for line in flips + pending + refused:
        print("  " + line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
