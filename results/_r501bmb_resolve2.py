"""r501 bm-b rebase resolver WAVE-2: r500 closeout commit vs origin daemon ticks.
Same canon as _r501bmb_resolve.py (v1) plus:
- CODELY.md: memory-union (line-level union, dedup identical lines, keep order)
- extra plain snapshots (attrition scan/fundamental/futures/lhb/prospect
  summaries/t35_open_fill/update_status)
Probe law: parse JSON before deep_ts walk (v1 live-fire: bytes probe -> '' ->
silent tie). Stage semantics: :2:=ours=new base (origin), :3:=theirs=replayed.
"""
import json
import subprocess
import sys

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
sys.path.insert(0, ROOT + r"\results")
from importlib import import_module
_v1 = import_module("_r501bmb_resolve")

blob = _v1.blob
probe_face = _v1.probe_face
write_mirror = _v1.write_mirror
deep_ts = _v1.deep_ts
pick = _v1.pick
union_list = _v1.union_list


def main():
    # twin groups (probe .json member once, same side for whole group)
    groups = [
        ("docs/daily_report/REPORT-2026-10-01", [".json", ".md"]),
        ("docs/live_usage/LIVE-2026-10-01", [".json", ".md"]),
        ("docs/live_usage/LIVE-latest", [".json", ".md"]),
    ]
    for stem, exts in groups:
        stage, ev = pick(blob(2, stem + ".json"), blob(3, stem + ".json"),
                        stem)
        for ext in exts:
            p = stem + ext
            raw = blob(stage, p)
            if ext == ".json":
                obj = json.loads(raw.decode("utf-8"))
                write_mirror(f"{ROOT}\\{p}", obj, probe_face(raw))
            else:
                with open(f"{ROOT}\\{p}", "wb") as f:
                    f.write(raw)
        print(f"group {stem}: {ev}")

    # dashboard js mirrors json winner
    pj = "results/dashboard_status.json"
    stage, ev = pick(blob(2, pj), blob(3, pj), pj)
    raw = blob(stage, pj)
    write_mirror(f"{ROOT}\\{pj}", json.loads(raw.decode("utf-8")),
                 probe_face(raw))
    with open(f"{ROOT}\\results\\dashboard_status.js", "wb") as f:
        f.write(blob(stage, "results/dashboard_status.js"))
    print(f"dashboard(.json+.js): {ev}")

    # plain take-new snapshots
    snaps = [
        "results/scorecard_v1.json", "results/strategy_scorecard.json",
        "results/token_usage.json", "results/update_status.json",
        "results/_attrition_guard_scan.json",
        "results/fundamental_b_layer_filter.json",
        "results/futures_update_status.json",
        "results/lhb_update_status.json",
        "results/prospect_paper/_summary.json",
        "results/prospect_promotion/_summary.json",
        "results/t35_open_fill_verify.json",
    ]
    for p in snaps:
        stage, ev = pick(blob(2, p), blob(3, p), p)
        raw = blob(stage, p)
        obj = json.loads(raw.decode("utf-8"))
        write_mirror(f"{ROOT}\\{p}", obj, probe_face(raw))
        print(f"snapshot {p}: {ev}")

    # rolling-ledgers: union + take-new snapshot fields
    for p, keys in [("results/compute_audit.json",
                     ("history", ["ts", "generated_at", "id"])),
                    ("results/regime_state.json",
                     ("history", ["ts", "date", "as_of", "id"]))]:
        o = json.loads(blob(2, p).decode("utf-8"))
        t = json.loads(blob(3, p).decode("utf-8"))
        ts_o, ts_t = deep_ts(o), deep_ts(t)
        base = o if (ts_t <= ts_o) else t
        m = {**o, **base}
        for key, dks in [keys, ("transitions", ["ts", "date", "as_of", "id"])]:
            if key in o or key in t:
                m[key] = union_list(o.get(key, []), t.get(key, []), dks)
                print(f"  {p}.{key}: union {len(o.get(key, []))}+"
                      f"{len(t.get(key, []))} -> {len(m[key])}")
        write_mirror(f"{ROOT}\\{p}", m, probe_face(blob(2, p)))
        print(f"ledger {p}: base ts ours={ts_o!r} theirs={ts_t!r}")

    # CODELY.md: memory-union (line-level union, dedup identical)
    p = "CODELY.md"
    o = blob(2, p).decode("utf-8")
    t = blob(3, p).decode("utf-8")
    ol = o.split("\n")
    tl = t.split("\n")
    # common prefix/suffix trim -> union the differing tails, keep both orders
    pref = 0
    while pref < min(len(ol), len(tl)) and ol[pref] == tl[pref]:
        pref += 1
    suf = 0
    while (suf < min(len(ol), len(tl)) - pref
           and ol[len(ol) - 1 - suf] == tl[len(tl) - 1 - suf]):
        suf += 1
    mine = tl[pref:len(tl) - suf]      # replayed side's new lines
    theirs = ol[pref:len(ol) - suf]    # base side's new lines
    seen = {ln for ln in theirs}
    merged_new = theirs + [ln for ln in mine if ln not in seen]
    out = "\n".join(ol[:pref] + merged_new + ol[len(ol) - suf:])
    with open(f"{ROOT}\\{p}", "wb") as f:
        f.write(out.encode("utf-8"))
    print(f"CODELY.md union: base-new={len(theirs)} replay-new={len(mine)} "
          f"kept={len(merged_new)} (dedup {len(mine) - sum(1 for ln in mine if ln in seen)})")

    # post-write parse verify (r185)
    for p in [g + e for g, ex in groups for e in ex if e == ".json"] + \
             [pj, "results/dashboard_status.json"] + snaps + \
             ["results/compute_audit.json", "results/regime_state.json"]:
        json.load(open(f"{ROOT}\\{p}", encoding="utf-8"))
    print("resolve WAVE-2 OK: all json faces re-parsed clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
