# -*- coding: utf-8 -*-
"""r1177 closeout: round report row, state face, heartbeat fields."""
import io
import json
import os
import time
from datetime import datetime

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW = "2026-10-27T12:06:00+08:00"

REPORT = (
    "| %s | r1177 | dept:engineering | **CURRENT**: smoke red leg = fleet GPU face "
    "self-consistent -- key vram_used_gb (used family, GB unit) sat outside every "
    "spelling table so it kept a random round's number while all MiB siblings were "
    "rewritten | **REAL ARTIFACT**: Tools/gpu_face.py (selftest 24 -> 28 legs, "
    "restate()/gpu_mem_family() pattern rule + live face healed: apply restated "
    "vram_used_gb/vram_free_gb from one probe, gpu_replaced 25 keys) | "
    "**NEXT MILESTONE**: E97 readset routing or E105 level single-name column, "
    "<=48h | **MECHANISM**: ownership is no longer an enumeration -- family+unit "
    "are derived from the key tokens and apply() restates every numeric GPU-memory "
    "spelling the face actually carries; what still ages is a formatted value the "
    "numeric pass cannot touch, and that is what audit now reports | "
    "**EVIDENCE**: smoke 85/85 PASS (was 84/85), gpu_face selftest 28/28, "
    "audit findings=[] on the live face | **S6**: D-19 probe ZERO-DELTA "
    "(dec c514b69c / ord c067b3b2, triple-mode reproducible), attrition CLEAN "
    "4 ledgers / 2 healed, orphan face=0 (9 py faces), sat engine any alive, "
    "watermark py_low_board_clear with 2 ready pool units | "
    "**BOARD**: pool ready 2 (E97/E105); orders 114 files / ack 115 / unacked 0; "
    "inbox empty | **NOT DONE THIS WINDOW**: the heavy S6 pandas chain was not "
    "re-run (previous round ran 50 legs rc0 at 11:50, six minutes before this "
    "one opened) -- honest note, not a green claim | "
    "**local not on origin commits=0 (pre-commit)** |\n"
) % NOW

ROW = ("\n- [2026-10-27 r1177 bm-b] Widening a spelling table by enumeration fails "
       "the same way every time (E110-style pit, third recurrence in this file): "
       "gpu_face's FREE/USED tables had been extended twice by hand (prefix rule "
       "r1299, RAM list + free GB pair r1169) and the live face still carried "
       "`vram_used_gb` -- a used-family GB spelling nobody tabulated -- at a random "
       "round's value while all 25 MiB siblings were rewritten from one probe. "
       "Durable fix = derive family and unit from the key tokens "
       "(gpu_mem_family) and have apply() restate every numeric GPU-memory spelling "
       "the face already carries (restate), so a new spelling cannot age just by "
       "being new. Ownership is then 'apply() will refresh it', and the audit's "
       "remaining unowned class is a FORMATTED value the numeric pass cannot touch "
       "(a '4.6 GB' string outside the pair table) -- that one is reported, not "
       "silently shadowed. Two obsolete legs had to be inverted with the law "
       "(a stale stray is restated, not reported) and two were added for the live "
       "defect (vram_used_gb restated from the same probe + audits clean). "
       "Pointer: Tools/gpu_face.py selftest 24 -> 28 legs; smoke 85/85.\n")


def main():
    p = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
    with io.open(p, "a", encoding="utf-8", newline="") as fh:
        fh.write(REPORT)

    sp = os.path.join(ROOT, "state-bm-b.json")
    with io.open(sp, encoding="utf-8-sig") as fh:
        st = json.load(fh)
    epoch = int(time.time())
    st.update({
        "round": 1177, "round_no": 1177, "round_no_label": "r1177",
        "ts": NOW, "updated": NOW, "updated_at": NOW,
        "last_seen": NOW, "last_round_at": NOW, "last_round_ts": NOW,
        "last_run": NOW,
        "clock_read": NOW,
        "heartbeat_epoch_utc": epoch,
        "task": "r1177 smoke red: GPU face vram_used_gb unowned",
        "current": "r1177: gpu_face ownership is a pattern rule, not a table",
        "current_task": "next = E97 readset routing table or E105 level single-name column",
        "verdict": ("productive: smoke red closed by a mechanism fix -- the GPU face "
                    "restates any numeric spelling it carries, so a new alias cannot "
                    "age; live face healed (25 keys replaced, vram_used_gb/vram_free_gb "
                    "restated from one probe)"),
        "did": ("closed the smoke red 'fleet: GPU face self-consistent': vram_used_gb "
                "(used family, GB unit) was outside FREE_KEYS/USED_KEYS/GB_KEYS, so "
                "apply() left it at a random round's value. Added gpu_mem_family() "
                "(token-derived family+unit) and restate() (apply restates every "
                "numeric GPU-memory spelling the face carries, string values left to "
                "the pair leg); audit's unowned class narrowed to values the probe "
                "cannot restate. Two legs regrounded (a numeric stray is restated, not "
                "reported) and two added (vram_used_gb restated + audits clean). "
                "selftest 24 -> 28, smoke 84/85 -> 85/85, live face healed by "
                "Tools/gpu_face.py apply (25 keys replaced)."),
        "did_round": 1176,
        "last_action": "closed the GPU face red with a pattern rule; live heartbeat restated",
        "last_action_at": NOW,
        "last_artifact": "Tools/gpu_face.py",
        "latest_artifact": "Tools/gpu_face.py",
        "next": ("r1178: E97 readset routing table (which screened read each charged "
                 "mode actually needs) or E105 level single-name column; both ready"),
        "next_milestone": ("every published level carries its largest single-name read, "
                           "and every charged readset has a routing row (<=48h)"),
        "next_pointer": "r1177 E97 readset routing or E105 level single-name column",
        "orphan_face": 0, "orphan_faces": 0,
        "orphan_face_note": "r1177: no orphan python faces at closeout (9 py faces probed)",
        "sat_engine": {"checked_at": NOW, "status": "alive"},
        "sync": {
            "status": "PENDING",
            "pushed_sha": "",
            "behind_origin_main": 0,
            "local_not_on_origin_main": 0,
            "ts": NOW,
            "note": "r1177 closeout commit",
        },
        "r1177_face": {
            "smoke": "85/85 PASS (red closed: 84/85 at round open)",
            "selftest": "gpu_face 28/28 (was 24, two regrounded + two added)",
            "product": "Tools/gpu_face.py restate()/gpu_mem_family()",
            "live_apply": "25 keys replaced, vram_used_gb + vram_free_gb restated",
            "s6": "D-19 zero delta, attrition CLEAN, orphan 0, watermark py_low_board_clear",
            "not_run": "heavy S6 pandas chain (previous round ran 50 legs rc0 at 11:50)",
            "pool": "ready 2 (E97 / E105)",
            "orders": "114 files / ack 115 / unacked 0",
        },
        "r1177_pit": ("r1177: a spelling table is a permanent liability -- it was widened "
                      "by hand twice (r1299 prefix rule, r1169 RAM list + free GB pair) "
                      "and the live face still carried vram_used_gb at a random round's "
                      "number. Ownership must be 'apply() will refresh it', derived from "
                      "the key tokens, not 'somebody tabulated it'. Sibling: when a law "
                      "changes, the legs that encoded the OLD law must be inverted in the "
                      "same edit -- two selftest legs here asserted 'a stray is reported' "
                      "and both went red the moment restate() landed, which is the correct "
                      "signal and not a regression."),
    })
    with io.open(sp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(st, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")

    cp = os.path.join(ROOT, "CODELY.md")
    with io.open(cp, "a", encoding="utf-8", newline="") as fh:
        fh.write(ROW)

    import sys
    sys.path.insert(0, ROOT)
    from Tools import heartbeat_write
    v, rc = heartbeat_write.write(ROOT, {
        "last_seen": NOW, "clock_read": NOW, "ts": NOW,
        "heartbeat_epoch_utc": epoch,
        "current": "r1177: gpu_face ownership is a pattern rule, not a table",
        "task": "r1177 smoke red closed (GPU face vram_used_gb)",
        "round": 1177, "round_no": 1177,
        "idle_rounds": 0, "agenda_starved": False,
        "cpu_cores": 16,
        "verdict": "idle-free: productive round (smoke 85/85, selftest 28/28)",
        "did": "gpu_face restate() pattern rule; live GPU face healed",
        "next_milestone": "E97 readset routing / E105 single-name column (<=48h)",
    })
    print(json.dumps({"state_bytes": os.path.getsize(sp),
                      "codey_bytes": os.path.getsize(cp),
                      "heartbeat_rc": rc, "gpu": v.get("applied")}, ensure_ascii=False))


if __name__ == "__main__":
    main()