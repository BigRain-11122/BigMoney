# -*- coding: utf-8 -*-
# _r930bmb_w19_screen_enroll.py -- r930 bm-b: enroll TRIAL-LABOR-W19-SCREEN-SHARD-0..7
# into results/runnable_pool.json (shared) + results/runnable_pool.bm-b.json (lane).
# W18-SCREEN pool-entry pattern verbatim (lane pin rationale documented), runner-derived
# id/key mirror (trial_labor_w19.py L1255-1256 literal), raw-text surgical insert.
# Laws: r509/r500 raw-text surgical + byte-probe-first, r859 parse-gate-before-write,
# r694 needle uniqueness + batch-prefix shard keys, r399 double-file, r485 ser() EOL.
# Gate matrix replicated in-script (submit leg shape-mismatch disclosed: house precedent
# workers_plan string form vs submit --workers int; W17/W18 both hand-enrolled):
# runner_exists / prereg_frozen / data_deps_present / dup-id / inbox_guard(fetch=True).
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
NEW_IDS = ["TRIAL-LABOR-W19-SCREEN-SHARD-%d" % i for i in range(8)]
WAVE_SHARDS = 8
CELLS_TOTAL = 546  # 346 paired + 200 nulls (frozen prereg sec.3 / sec.9)

receipt = {"round": "r930 bm-b", "action": "W19 screen shard pool enrollment",
           "ts": NOW, "gates": {}, "files": {}, "ids": NEW_IDS}


def fail(msg):
    receipt["error"] = msg
    print("ABORT: %s" % msg)
    with open(os.path.join(ROOT, "results", "_r930bmb_w19_screen_enroll.json"),
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
    deps = ["results/trial_labor_w19/w19_cells.json",
            "results/trial_labor_w19/prep_state.json"]
    g["data_deps_present"] = all(
        os.path.exists(os.path.join(ROOT, d)) for d in deps)
    try:
        sys.path.insert(0, os.path.join(ROOT, "Tools"))
        import inbox_guard
        frozen = False
        det_l = []
        for probe in ("TRIAL-LABOR-W19-SCREEN-SHARD-0", "TRIAL-LABOR-W19-SCREEN"):
            fr, det = inbox_guard.conflict(ROOT, "bm-b", probe, fetch=True)
            frozen = frozen or bool(fr)
            det_l.append("%s -> %s" % (probe, det))
        g["inbox_guard"] = "FREEZE" if frozen else "CLEAR"
        g["inbox_guard_detail"] = "; ".join(det_l)
    except Exception as ex:  # degrade parity with autofill submit
        g["inbox_guard"] = "guard-fault-degrade"
        g["inbox_guard_detail"] = str(ex)[:200]
    hard = g["runner_exists"] and g["prereg_frozen"] and g["data_deps_present"]
    if not hard:
        fail("hard gate red: %s" % json.dumps(g))
    if g["inbox_guard"] == "FREEZE":
        fail("rival declaration freeze: %s" % g["inbox_guard_detail"])
    return g


def make_entry(n):
    return {
        "id": "TRIAL-LABOR-W19-SCREEN-SHARD-%d" % n,
        "ticket_ref": ("T-2026-10-14-186 wave ticket lineage (W8=T-120/W9=T-121/"
                       "W10=T-122/W11=T-123/W12=T-124/W13=T-125/W14=T-128/"
                       "W16=T-172/W17=T-178/W18=T-185); W19 = timing-axis 2-arm "
                       "full-cross PAIRED isolation, freeze commit 6c09b1251 (r927), "
                       "runner landed 9f4994569 (r928), generate done (w19_cells 346 "
                       "cells 08:31) + screen-prep done (prep_state 1253 starts gates "
                       "ALL PASS); enrolled r930 bm-b per r929 next-pointer"),
        "prereg_ref": ("research/TRIAL_LABOR_W19_PREREG.md FROZEN 2026-10-14 sec.3 "
                       "screen (346 paired cells + K=200 nulls = 546 screen trials; "
                       "sec.9 pool sequencing 8-shard W17 precedent; timing-axis "
                       "complete-block PAIRED isolation; control arm = per-cell "
                       "as-burned axis[3] frozen face, treatment = other AXIS_TIMING "
                       "face per cell)"),
        "runner": "scripts/trial_labor_w19.py",
        "runner_args": ["screen", str(n), str(WAVE_SHARDS)],
        "lane_owner": "bm-b",
        "priority": 1,
        "consumer_plan": ("TRIAL-LABOR-W19 chain: 8 screen shards -> screen-finalize "
                          "(survival line + G-face battery + ledger append) -> "
                          "judge-prep -> judge -> judge-finalize (verdicts + reform "
                          "face + w19_paired_deltas.json informative-pairs + TWO "
                          "as-burned-T subgroup readings) -> s4 intake; 48h CEO "
                          "report clock starts at judge landing"),
        "workers_plan": {
            "workers": "worker_cap() pool BelowNormal",
            "priority": "BelowNormal",
            "note": ("W17/W18 screen machinery precedent (run_cells_parallel "
                     "multiproc); stride i%%%d of %d cells (~69/shard); RAM gate "
                     "4GB r354 honest-refuse retry" % (WAVE_SHARDS, CELLS_TOTAL)),
        },
        "data_gates": ("fail-closed rc2 until data_deps present (w19_cells + "
                       "prep_state; both landed r928/r929 bm-b committed); "
                       "determinism cross-door = as-burned arm 173 pairs "
                       "byte-identity vs w17_screen_cells.csv control rows AND "
                       "w18_screen_cells.csv as-burned rows (hard VOID); "
                       "GENERATE-GATE precedent r929: product-already-landed + "
                       "same-grammar rerun refused honest rc2"),
        "data_deps": ["results/trial_labor_w19/w19_cells.json",
                      "results/trial_labor_w19/prep_state.json"],
        "status": "ready",
        "shards": [{
            "key": "w19-screen-%dof%d" % (n, WAVE_SHARDS),
            "status": "ready",
            "checkpoint": ("results/trial_labor_w19/checkpoint/screen_shard_%dof%d"
                           ".jsonl (MACHINE-LOCAL r429 gitignored; lane pinned bm-b "
                           "-- screen-finalize reads local CKPT_DIR; stride i%%%d)"
                           % (n, WAVE_SHARDS, WAVE_SHARDS)),
            "note": ("stride i%%%d of %d cells (346 paired + 200 nulls); lane pinned "
                     "bm-b per r429 machine-local checkpoint law (prereg sec.9 'any "
                     "healthy engine' superseded by checkpoint locality, W17 "
                     "enrollment precedent); RAM gate 4GB r354 honest-refuse retry"
                     % (WAVE_SHARDS, CELLS_TOTAL)),
            "owner": None,
        }],
        "entered_at": NOW,
        "entered_by": "bm-b r930 (W18-pattern enrollment, gates in-script)",
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
    anchor_entry = "TRIAL-LABOR-W19-GENERATE"
    if anchor_entry not in ids:
        fail("anchor entry %s absent in %s" % (anchor_entry, os.path.basename(path)))
    anchor = "  }\r\n ],\r\n"  # last-entry close + entries-array close (law_ref follows)
    cnt = text.count(anchor)
    if cnt != 1:
        fail("needle count %d != 1 in %s -- abort" % (cnt, os.path.basename(path)))
    a_pos = text.find(anchor)
    gen_pos = text.find('"id": "%s"' % anchor_entry)
    if not (0 <= gen_pos < a_pos):
        fail("anchor not in GENERATE entry region (gen_pos=%d a_pos=%d)"
             % (gen_pos, a_pos))
    joined = ("," + EOL).join(blocks)
    repl = "  }," + EOL + joined + EOL + " ]," + EOL
    new_text = text.replace(anchor, repl, 1)
    p2 = json.loads(new_text)  # r859 parse gate BEFORE any write
    n_old = len(pool["entries"])
    n_new = len(p2["entries"])
    if n_new != n_old + 8:
        fail("count gate: %d != %d + 8" % (n_new, n_old))
    got = [e.get("id") for e in p2["entries"]]
    for i in NEW_IDS:
        if i not in got:
            fail("inserted id missing post-parse: %s" % i)
    with open(path, "wb") as f:
        f.write(new_text.encode("utf-8"))
    with open(path, "rb") as f:
        p3 = json.loads(f.read().decode("utf-8"))
    ids3 = [e.get("id") for e in p3["entries"]]
    if len(ids3) != n_old + 8 or any(i not in ids3 for i in NEW_IDS):
        fail("post-write re-read assert failed on %s" % os.path.basename(path))
    receipt["files"][os.path.basename(path)] = {
        "entries_before": n_old, "entries_after": len(ids3),
        "bytes_before": len(b), "bytes_after": os.path.getsize(path),
        "added_lines": new_text.count("\n") - text.count("\n"),
    }
    print("%s: entries %d -> %d (+8) bytes %d -> %d"
          % (os.path.basename(path), n_old, len(ids3), len(b),
             os.path.getsize(path)))


def main():
    run_gates()
    blocks = [ser_entry(make_entry(n)) for n in range(8)]
    insert(SHARED, blocks)
    insert(LANE, blocks)
    receipt["status"] = "ENROLLED 8/8 (shared+lane double-file, parse gates green)"
    with open(os.path.join(ROOT, "results", "_r930bmb_w19_screen_enroll.json"),
              "w", encoding="utf-8") as f:
        json.dump(receipt, f, ensure_ascii=False, indent=1)
    print("ENROLLED: TRIAL-LABOR-W19-SCREEN-SHARD-0..7 shared+lane; gates="
          + json.dumps(receipt["gates"], ensure_ascii=False)[:400])


if __name__ == "__main__":
    main()
