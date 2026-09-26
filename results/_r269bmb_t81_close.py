"""r269 bm-b: close T-81 (applicability-domain judgment chain) -- status
claimed -> done with result_ref + progress_r269, after post_review acceptance
face landed (4 rows T-81-* all derived YES 19:25:45 this round).

Byte-face mirror (probed from HEAD blob via git cat-file this round,
results/_r269bmb_probe.py): no BOM, LF-only, no trailing newline,
ensure_ascii=False, indent=1. Key layout mirrors T-79 done-face convention:
result_ref inserted after claimed_at, final progress entry appended last.
"""
import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "fleet", "tasks", "T-2026-09-26-81-P1.json")

PROGRESS = ("R269 bm-b CLOSURE: slice chain s1-s4 complete (r254 profile cards / "
            "r255 L3 activation evidence / r257 sample science / r265 landing "
            "hooks), acceptance face encoded this round -- 4 post_review rows "
            "registered (results/_r269bmb_t81_postreview.py; checks anchored to "
            "pre-frozen preregs + deterministic product fields per r256 reanchor "
            "law) and ALL derived YES on same-round reviewer run (YES=28 NO=0 "
            "WAIT=5; results/post_review.jsonl ts 19:25:45). Hook armed "
            "(n_landings 0), landing != activation, new landings route to fresh "
            "prereg judgments. No reopen face. Ticket flipped done by claim owner "
            "bm-b r269.")

RESULT_REF = ("research/PROFILE_CARDS_P1.md + results/strategy_scorecard.json "
              "profile_cards/landing_hooks faces + research/L3_ACTIVATION_EVIDENCE.md "
              "+ research/SAMPLE_SCIENCE_P1.md + research/LANDING_HOOKS_P1.md "
              "(chain r254/r255/r257/r265; post_review T-81-* x4 YES r269)")


def main():
    with io.open(PATH, encoding="utf-8") as fh:
        d = json.load(fh)
    assert d["status"] == "claimed", "unexpected status: " + str(d["status"])
    assert "result_ref" not in d, "result_ref already present"
    assert "progress_r269" not in d, "progress_r269 already present"
    d["status"] = "done"
    # rebuild preserving key order; result_ref after claimed_at (T-79 face)
    out = {}
    for k, v in d.items():
        out[k] = v
        if k == "claimed_at":
            out["result_ref"] = RESULT_REF
    out["progress_r269"] = PROGRESS
    # byte-face mirror: no BOM, LF, ensure_ascii=False, indent=1, no trailing \n
    with io.open(PATH, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print("T-81 flipped done; keys:", list(out.keys()))


if __name__ == "__main__":
    main()
