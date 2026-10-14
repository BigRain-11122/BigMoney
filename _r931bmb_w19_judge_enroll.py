# -*- coding: utf-8 -*-
# _r931bmb_w19_judge_enroll.py -- r931 bm-b: enroll TRIAL-LABOR-W19-JUDGE (single
# shard 0of1) into results/runnable_pool.json (shared) + results/runnable_pool.bm-b.json
# (lane). W18-JUDGE pool-entry pattern verbatim; runner-derived id/key mirror
# (trial_labor_w19.py L1921-1922 literal); raw-text surgical insert after W19-SCREEN-SHARD-7.
# Laws: r509/r500 raw-text surgical + byte-probe-first, r859 parse-gate-before-write,
# r694 needle uniqueness, r399 double-file, r485 ser() EOL, r429 machine-local
# checkpoint lane pin (W19-SCREEN enrollment precedent).
# Gate matrix in-script: runner_exists / prereg_frozen / data_deps_present /
# dup-id / inbox_guard(fetch=True).
import json
import os
import re
import sys
import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
SHARED = os.path.join(ROOT, "results", "runnable_pool.json")
LANE = os.path.join(ROOT, "results", "runnable_pool.bm-b.json")
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
EOL = "\r\n"
NEW_IDS = ["TRIAL-LABOR-W19-JUDGE"]
ANCHOR_ID = "TRIAL-LABOR-W19-SCREEN-SHARD-7"

receipt = {"round": "r931 bm-b", "action": "W19 judge pool enrollment",
           "ts": NOW, "gates": {}, "files": {}, "ids": NEW_IDS}


def fail(msg):
    receipt["error"] = msg
    print("ABORT: %s" % msg)
    with open(os.path.join(ROOT, "results", "_r931bmb_w19_judge_enroll.json"),
              "w", encoding="utf-8") as f:
        json.dump(receipt, f, ensure_ascii=False, indent=1)
    sys.exit(2)


def run_gates():
    g = receipt["gates"]
    g["runner_exists"] = os.path.exists(
        os.path.join(ROOT, "scripts", "trial_labor_w19.py"))
    pp = os.path.join(ROOT, "research", "TRIAL_LABOR_W19_PREREG.md")
    head = ""
    okf = os.path.exists(pp)
    if okf:
        with open(pp, encoding="utf-8", errors="replace") as f:
            head = "".join(f.readline() for _ in range(12))
    m = re.search(u"【状态[:：]([^】]*)】", head)
    g["prereg_frozen"] = bool(okf and m and "FROZEN" in m.group(1).upper())
    deps = ["results/trial_labor_w19/judge_state.json",
            "Money02/data/cache/t18_deep_panel/ohlcv"]
    g["data_deps_present"] = all(
        os.path.exists(os.path.join(ROOT, d)) for d in deps)
    # D-leg cache claim-time local presence (r316)
    import pathlib
    g["d_leg_parquets"] = len(list(pathlib.Path(
        os.path.join(ROOT, deps[1])).glob("*.parquet")))
    try:
        sys.path.insert(0, os.path.join(ROOT, "Tools"))
        import inbox_guard
        frozen = False
        det_l = []
        for probe in ("TRIAL-LABOR-W19-JUDGE", "TRIAL-LABOR-W19"):
            fr, det = inbox_guard.conflict(ROOT, "bm-b", probe, fetch=True)
            frozen = frozen or bool(fr)
            det_l.append("%s -> %s" % (probe, det))
        g["inbox_guard"] = "FREEZE" if frozen else "CLEAR"
        g["inbox_guard_detail"] = "; ".join(det_l)
    except Exception as ex:  # degrade parity with autofill submit
        g["inbox_guard"] = "guard-fault-degrade"
        g["inbox_guard_detail"] = str(ex)[:200]
    hard = (g["runner_exists"] and g["prereg_frozen"]
            and g["data_deps_present"] and g["d_leg_parquets"] > 0)
    if not hard:
        fail("hard gate red: %s" % json.dumps(g))
    if g["inbox_guard"] == "FREEZE":
        fail("rival declaration freeze: %s" % g["inbox_guard_detail"])
    return g


def make_entry():
    return {
        "id": "TRIAL-LABOR-W19-JUDGE",
        "ticket_ref": ("T-2026-10-14-186 wave ticket lineage (W8=T-120/W9=T-121/"
                       "W10=T-122/W11=T-123/W12=T-124/W13=T-125/W14=T-128/"
                       "W16=T-172/W17=T-178/W18=T-185); W19 = timing-axis 2-arm "
                       "full-cross PAIRED isolation, freeze commit 6c09b1251 (r927), "
                       "runner landed 9f4994569 (r928); screen-finalize landed r931 "
                       "bm-b (null p95 0.5116 in-band HIT, pred 43/obs 43, 173/173 "
                       "dual-source determinism byte-identity, survivors 70/346); "
                       "judge-prep landed r931 bm-b (56 blocks / 112 judged cells); "
                       "enrolled r931 bm-b per r930 next-pointer"),
        "prereg_ref": ("research/TRIAL_LABOR_W19_PREREG.md FROZEN 2026-10-14 sec.3 "
                       "judge (56 blocks x 2 arms = 112 judged cells; SEED_REGISTRY "
                       "3 keys 20640000/20640500/20641000 freeze-commit same-commit "
                       "R250; evidence_cutoff 2026-09-22 lockbox; timing-axis "
                       "complete-block PAIRED isolation)"),
        "runner": "scripts/trial_labor_w19.py",
        "runner_args": ["judge", "0", "1"],
        "lane_owner": "bm-b",
        "priority": 1,
        "consumer_plan": ("TRIAL-LABOR-W19 chain: judge -> judge-finalize "
                          "(verdicts + reform face + w19_paired_deltas.json "
                          "informative-pairs + TWO as-burned-T subgroup readings) "
                          "-> s4 intake; 48h CEO report clock starts at judge "
                          "landing"),
        "workers_plan": {
            "workers": 8,
            "priority": "BelowNormal",
            "note": ("judge cells dual-leg L+D runs + dual nulls B/P; "
                     "W18-JUDGE single-shard pace ~8min/188 cells precedent "
                     "(r893); 112 cells lighter; worker_cap() RAM guard at "
                     "runtime"),
        },
        "data_gates": ("fail-closed rc2 until judge_state.json present (landed "
                       "r931 bm-b); RAM gate 4GB r354 with AUTOFILL-PARK "
                       "honest-refuse (r797; runner carries park markers + "
                       "flush); D-leg deep panel = t18 cache asserted claim-time "
                       "local presence (r316: registry-time presence != "
                       "claim-time local presence); single-shard W13/W17/W18-"
                       "JUDGE precedent"),
        "data_deps": ["results/trial_labor_w19/judge_state.json",
                      "Money02/data/cache/t18_deep_panel/ohlcv"],
        "status": "ready",
        "shards": [{
            "key": "w19-judge-0of1",
            "status": "ready",
            "checkpoint": ("results/trial_labor_w19/checkpoint/judge_shard_0of1"
                           ".jsonl (MACHINE-LOCAL r429 gitignored; row-level "
                           "done-set resume cross-kill law; judge-finalize "
                           "reads local CKPT_DIR)"),
            "note": ("claim key matches runner _worker_claim w19-judge-0of1 "
                     "(trial_labor_w19.py L1921-1922); lane pinned bm-b per "
                     "r429 machine-local checkpoint law (W19-SCREEN "
                     "enrollment precedent)"),
            "owner": None,
        }],
        "entered_at": NOW,
        "entered_by": "bm-b r931 (W18-JUDGE-pattern enrollment, gates in-script)",
    }


def ser_entry(e):
    raw = json.dumps(e, ensure_ascii=False, indent=1)
    lines = raw.split("\n")
    return EOL.join(("  " + ln) if ln else ln for ln in lines)


def insert(path, blocks):
    with open(path, "rb") as f:
        b = f.read()
    text = b.decode("utf-8")
    crlf = text.count("\r\n")
    lf_only = text.count("\n") - crlf
    if lf_only:
        fail("EOL probe %s: host not CRLF (%d LF-only of %d lines) -- abort"
             % (os.path.basename(path), lf_only, crlf))
    pool = json.loads(text)
    ids = [e.get("id") for e in pool.get("entries", [])]
    dup = [i for i in NEW_IDS if i in ids]
    if dup:
        fail("dup-id gate %s: %s" % (os.path.basename(path), dup))
    if ANCHOR_ID not in ids:
        fail("anchor entry %s absent in %s" % (ANCHOR_ID, os.path.basename(path)))
    anchor = "  }\r\n ],\r\n"  # last-entry close + entries-array close
    cnt = text.count(anchor)
    if cnt != 1:
        fail("needle count %d != 1 in %s -- abort" % (cnt, os.path.basename(path)))
    a_pos = text.find(anchor)
    anchor_pos = text.find('"id": "%s"' % ANCHOR_ID)
    if not (0 <= anchor_pos < a_pos):
        fail("anchor not in %s entry region (pos=%d a_pos=%d)"
             % (ANCHOR_ID, anchor_pos, a_pos))
    joined = ("," + EOL).join(blocks)
    repl = "  }," + EOL + joined + EOL + " ]," + EOL
    new_text = text.replace(anchor, repl, 1)
    p2 = json.loads(new_text)  # r859 parse gate BEFORE any write
    n_old = len(pool["entries"])
    n_new = len(p2["entries"])
    if n_new != n_old + 1:
        fail("count gate: %d != %d + 1" % (n_new, n_old))
    got = [e.get("id") for e in p2["entries"]]
    for i in NEW_IDS:
        if i not in got:
            fail("inserted id missing post-parse: %s" % i)
    with open(path, "wb") as f:
        f.write(new_text.encode("utf-8"))
    with open(path, "rb") as f:
        p3 = json.loads(f.read().decode("utf-8"))
    ids3 = [e.get("id") for e in p3["entries"]]
    if len(ids3) != n_old + 1 or any(i not in ids3 for i in NEW_IDS):
        fail("post-write re-read assert failed on %s" % os.path.basename(path))
    receipt["files"][os.path.basename(path)] = {
        "entries_before": n_old, "entries_after": len(ids3),
        "bytes_before": len(b), "bytes_after": os.path.getsize(path),
        "added_lines": new_text.count("\n") - text.count("\n"),
    }
    print("%s: entries %d -> %d (+1) bytes %d -> %d"
          % (os.path.basename(path), n_old, len(ids3), len(b),
             os.path.getsize(path)))


def main():
    run_gates()
    blocks = [ser_entry(make_entry())]
    insert(SHARED, blocks)
    insert(LANE, blocks)
    receipt["status"] = "ENROLLED 1/1 (shared+lane double-file, parse gates green)"
    with open(os.path.join(ROOT, "results", "_r931bmb_w19_judge_enroll.json"),
              "w", encoding="utf-8") as f:
        json.dump(receipt, f, ensure_ascii=False, indent=1)
    print("ENROLLED: TRIAL-LABOR-W19-JUDGE shared+lane; gates="
          + json.dumps(receipt["gates"], ensure_ascii=False)[:400])


if __name__ == "__main__":
    main()
