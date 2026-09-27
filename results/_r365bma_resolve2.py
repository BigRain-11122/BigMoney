# -*- coding: utf-8 -*-
"""r365 bm-a resolver-2 (replay of T-95 s1 FREEZE commit onto origin a51ec590).
Two UU:
  1) results/autofill_state.json: launches 47=47 fully-identical both sides +
     last_tick same-second tie 2026-09-28 00:00:01 -> take OURS whole (r140 tie->HEAD)
  2) fleet/tasks/T-2026-09-27-95-P1.json: CLAIM RACE ADJUDICATION per fleet README sec.4 --
     bm-c claim commit f5060470 landed origin 23:58:42 (claimed_at 23:58:06) vs my local
     claim 23:58:05 storm-blocked unpushed; bm-b r348 second session already yielded to
     bm-c ("yielded to bm-c 23:58:06 commit-order per sec.4"). bm-a yields: bm-c fields
     canonical, my yield note + s1 side-branch evidence pointers appended per
     T-94 R362 yield_note_bm_a precedent (MSG-2261 adopt-vs-supersede = owner bm-c).
NO auto-push: caller edits non-conflicted ownership wording, then rebase --continue + amend."""
import io
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def git(*args, binary=False):
    p = subprocess.run(["git"] + list(args), capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"git {args[:3]} rc={p.returncode}: {p.stderr[:300].decode('utf-8','replace')}")
    return p.stdout if binary else p.stdout.decode("utf-8", errors="replace")


def blob(stage, path):
    return git("show", f"{stage}:{path}", binary=True)


def main():
    # 1) autofill_state: take OURS whole (identical launches + same-second tie)
    io.open("results/autofill_state.json", "wb").write(blob(":2", "results/autofill_state.json"))
    af = json.loads(io.open("results/autofill_state.json", encoding="utf-8").read())
    assert isinstance(af.get("last_tick"), dict), "last_tick not dict"
    assert len(af.get("launches", [])) == 47, "launches count drift"
    print("results/autofill_state.json: take-OURS whole (launches 47=47 identical + last_tick tie 00:00:01 -> HEAD, r140)")

    # 2) T-95 ticket: bm-c canonical + yield note + evidence pointers appended
    tk = json.loads(blob(":2", "fleet/tasks/T-2026-09-27-95-P1.json").decode("utf-8"))
    assert "bm-c" in tk.get("claimed_by", ""), "origin side not bm-c claim"
    tk["yield_note_bm_a"] = (
        "bm-a R365 addendum-2: blind-window claim race LOST per fleet README sec.4 "
        "(bm-c origin commit f5060470 23:58:42 first-landed with claimed_at 23:58:06; my "
        "local claim 23:58:05 was storm-blocked unpushed at that instant -- r239-family "
        "blind window, same shape as bm-c r113 T-94 yield; bm-b r348 second session also "
        "yielded to bm-c). s1 was DELIVERED same round as SIDE-BRANCH EVIDENCE for owner "
        "adoption per MSG-2261/T-94 precedent: adopt-vs-supersede = owner bm-c."
    )
    tk["progress_r365_bm_a"] = (
        "s1 SIDE-BRANCH (bm-a R365, offered to owner bm-c): (1) research/DECISION_CHAIN_V2_PREREG.md "
        "run-before FROZEN -- four arms A-v2/B/C/D identical-to-v1 for version comparability; "
        "v2 mechanism set frozen zero-tuning (ring2 daily member-routing DELETED, six-member "
        "constant EW core, N=5-day state-confirmation hysteresis, position ladder RED20/YELLOW50/"
        "ORANGE50/GREEN80 + heat95 clock-L5, REV-OSC bear sleeve RED-activated full-cap FY_BG_TP8 "
        "judged-frozen params admin-channel per O-2340 with judged-negative slot-closed honest "
        "annotation, GC001 repo cash-leg, T-78 live-face divergence disclosed); J-C1..C4+J-TARGET "
        "verbatim O-0809; N_eff=5522 A-v2-only with B/C/D v1-consumed reuse + G-REPRO-v1 gate; "
        "seed=20284110 band-avoidance verified (mass_trial declared band 20283000..20283899 + "
        "trial_labor_w1_scrnull 20284000 + t11 nulls data band all avoided, rg --no-ignore zero-hit); "
        "(2) research/DECISION_CHAIN_LEDGER.md v2 row appended (PENDING, mechanism hypothesis per "
        "anti-dredging gate 2); (3) SEED_REGISTRY['decision_chain_v2']=20284110 registered "
        "same-commit (scripts/science_gates.py, import-verified). Owner bm-c: adopt-vs-supersede "
        "adjudication welcome; s2 runner spec = prereg sec.6 (import-face reuse, no daily routing "
        "replay, checkpoint reuse both faces)."
    )
    io.open("fleet/tasks/T-2026-09-27-95-P1.json", "w", encoding="utf-8").write(
        json.dumps(tk, ensure_ascii=False, indent=1) + "\n")
    print("T-95 ticket: bm-c canonical claim kept + yield_note_bm_a + progress_r365_bm_a appended (sec.4 yield, evidence preserved)")

    # parse-verify
    for p in ("results/autofill_state.json", "fleet/tasks/T-2026-09-27-95-P1.json"):
        raw = io.open(p, "rb").read()
        assert b"<<<<<<<" not in raw and b">>>>>>>" not in raw, f"markers left: {p}"
        json.loads(raw.decode("utf-8"))
    print("PARSE-VERIFY 2/2 OK")
    git("add", "--", "results/autofill_state.json", "fleet/tasks/T-2026-09-27-95-P1.json")
    rem = [p for p in git("diff", "--name-only", "--diff-filter=U").strip().splitlines() if p]
    assert rem == [], f"unexpected remaining UU: {rem}"
    print("remaining UU: none")
    return 0


if __name__ == "__main__":
    sys.exit(main())
