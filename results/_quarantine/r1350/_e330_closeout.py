"""r1350 closeout: round report row + state-bm-b.json faces (bm-b only)."""
import io
import json
import os

TS = "2026-11-01T05:10:00+08:00"
FACE = "results/state_tilt/UNPINNEDCHOICE-2026-11-01.json"

row = (
    "| %s | r1350 | bm-b | **watermark: RED pool-batch-runnable-idle-low-cpu at open (1 ready card = "
    "E330, py 0.1-0.2%%); the round burned the ready head E330 in-round** | E330 unpinned choice: "
    "across 2,284 sources / 646k code lines the tree makes exactly **1** two-reference decision -- "
    "e242's `_face_file` pointer-first chain with a pinned 2026-10-29 fallback -- and **0** of them "
    "are pinned by an assertion; a two-line swap returns 2026-10-29 instead of 2026-10-30 today for 2 "
    "of its 4 call-site stems (owncross, sharediff) with every leg still green, and for "
    "per_member_gamma the pinned branch names a cut that is not on disk at all. Zero argparse defaults "
    "name a face (39 `add_argument` lines) and zero functions carry a mutable default; 34 `or` lines "
    "with a face on one side only are published as rejected rather than dropped. **CURRENT:** E330 "
    "done. **LATEST PHYSICAL:** %s. **NEXT MILESTONE:** E331 pointer-only readers (ready, due next "
    "round, <=48h). **PRODUCT:** a decision nothing asserts is a decision a two-line edit can reverse "
    "with every light still green |\n" % (TS, FACE)
)

with io.open(os.path.join("logs", "iteration-loop", "round_reports.md"), "a",
             encoding="utf-8", newline="\n") as fh:
    fh.write(row)

S = os.path.join("state-bm-b.json")
st = json.load(io.open(S, encoding="utf-8"))
st["round"] = 1350
st["round_no"] = 1350
st["round_no_label"] = "r1350"
st["round_no_ts"] = TS
st["study"] = "E330_unpinned_choice"
st["task"] = ("r1350 E330: the tree makes one two-reference decision (e242's _face_file) and no "
              "assertion pins it; swapping its order returns a cut one vintage older today")
st["task_short"] = "r1350 E330 unpinned choice"
st["verdict"] = "an_unpinned_decision_would_return_a_different_cut_if_the_order_were_swapped_today"
st["selftest"] = "e330_unpinned_choice 30/30"
st["smoke"] = "leg E330 executed standalone: PASS (full suite not re-run this window)"
st["s1"] = ("full suite not re-run this window; the new S6 leg ran verify problems=[] (~40s) and the "
            "new smoke leg was exec'd out of smoke_test.py standalone: PASS")
st["s6"] = ("orphan py_faces=7 orphans=0 residents=0 | dualrun ZERO-DRIFT 821 entries streak 51 | "
            "attrition CLEAN 4 ledgers (3 historical shrinks healed) | unpinned_choice verify rc=0 "
            "~40s | sat engine rc=0 idle; compute_audit / py_watermark / lane collectors not re-run "
            "this window (stated plainly)")
st["s7"] = "loop pin=2 no-op; watchdog and claws unchanged this window (checked previous round)"
st["sat_engine"] = "rc=0 idle"
st["watermark_red"] = ("RED pool-batch-runnable-idle-low-cpu at open (1 ready card = E330, py "
                       "0.1-0.2%); burned the ready head E330 in-round and seeded E331")
st["watermark_note"] = st["s6"]
st["verdict_line"] = ("watermark red at open (pool-batch-runnable-idle-low-cpu, 1 ready = E330) -> "
                      "authored, verified and published E330 in-round; board re-seeded with E331")
st["ts"] = TS
st["updated"] = TS
st["updated_at"] = TS
st["work"] = "r1350 E330 unpinned choice + delivery"
st["r1350"] = {
    "dept": "research+engineering",
    "study": "E330_unpinned_choice",
    "face": FACE,
    "verdict": st["verdict"],
    "finding": (
        "2,284 sources / 646k code lines carry exactly one construct that picks between two "
        "references to one family: e242's _face_file (pointer first, pinned 2026-10-29 second). It "
        "is unpinned -- no assertion in its own selftest region or in the chain/smoke files names "
        "_face_file. Per stem: owncross and sharediff hold a 2026-10-30 pointer, so a swapped order "
        "returns 2026-10-29 today; AGGATT's pointer and fallback agree; per_member_gamma's pinned "
        "branch names a cut that is not on disk and returns None. Zero argparse defaults name a face "
        "(39 add_argument lines seen), zero functions carry a mutable default, and 34 `or` lines "
        "offering a face on one side only are rejected and published rather than dropped."),
    "pit": (
        "(1) a scanner reads its own test input: e329's handles_in_line('for cand in (...)') line was "
        "counted as a second fallback chain -- the operator must be found on a string-masked copy of "
        "the line, not on the raw line where handles live inside quotes. (2) an `or` beside a face is "
        "not a choice between two vintages: 34 of 35 such lines have the face on one side only "
        "(os.path.join(outdir or OUTDIR, 'x_latest.json')), and the rejected count has to be "
        "published because a silent cut prints the same zero as a clean corpus. (3) a chain is one "
        "decision but many stems: the first draft set outcome_today from AGGATT and swap_changes_today "
        "from owncross (r1234 name-law), fixed by publishing per_stem and deriving the row reading "
        "from the first disagreeing stem. (4) three of my own selftest expectations were wrong before "
        "the code was (a 'both defaults are stale' count, a call-site stem, a fixture without a "
        "pointer) -- r1281 shape: assert the mechanism, then the number."),
    "not_run": ("full 330+ leg smoke suite not re-run (~35 min); the new smoke leg was exec'd out of "
                "smoke_test.py standalone: PASS. GPU untouched (parked C-20261014-01); cloud "
                "untouched; nothing deleted, no quarantine action; bm-a/bm-c lane collectors "
                "honoured their guards."),
    "product": [
        "scripts/e330_unpinned_choice.py (run / verify problems=[] / selftest 30/30)",
        "results/state_tilt/UNPINNEDCHOICE-2026-11-01.json + unpinnedchoice_latest.json",
        "Tools/s6_chain_bmb.py leg unpinned_choice (~40s, corpus scan)",
        "smoke_test.py leg (executed standalone: PASS)",
        "knowledge/METHODOLOGY_ASSETS.md card E330",
        "research/digests/DIGEST-20261101-r1350-e330-unpinned-choice.md",
        "results/runnable_pool.json E330 done with result_ref; E331 seeded ready",
    ],
    "pool": ("E330 done with result_ref; E331-POINTER-ONLY-READERS seeded ready (821 entries: 820 "
             "done / 1 ready)"),
    "s1": st["s1"], "s6": st["s6"], "s7": st["s7"], "ts": TS,
}

with io.open(S, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(st, fh, indent=1, ensure_ascii=False, sort_keys=True)
    fh.write("\n")

print("round report row appended; state round_no =", st["round_no"])
print("state parses:", bool(json.load(io.open(S, encoding="utf-8"))))