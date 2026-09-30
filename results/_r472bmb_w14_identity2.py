"""_r472bmb_w14_identity2.py -- second identity pass: function-name
suffixes _w13 -> _w14 (definition + call sites, count-verified)."""
import sys

DRAFT = "results/_r472bmb_w14_runner_draft.py"
text = open(DRAFT, encoding="utf-8").read()
log = []


def rep(old, new, expect_min=1):
    global text
    n = text.count(old)
    if n < expect_min:
        print(f"IDENTITY2-FAIL: {n} < {expect_min} of {old!r}")
        sys.exit(1)
    text = text.replace(old, new)
    log.append((old, n))


for fn in ("build_grammar_w13", "draw_candidate_sobol_w13",
           "_load_exclusion_rows_w13", "_excluded_w13",
           "_effective_signal_mask_w13", "run_candidate_curve_w13",
           "_null_axis_draw_w13", "_screen_cell_w13",
           "_cell_list_w13", "_dual_nulls_w13",
           "_overlay_stop_disclosure_w13", "_judge_cell_w13"):
    rep(fn, fn.replace("_w13", "_w14"))

open(DRAFT, "w", encoding="utf-8", newline="\n").write(text)
print(f"identity2 OK: {len(log)} function-name renames")
for old, n in log:
    print(f"  [{old}] x{n}")
