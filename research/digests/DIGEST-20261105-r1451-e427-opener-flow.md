# DIGEST 2026-11-05 r1451 bm-b -- E427: location is not dataflow

**Question.** E426 found 2,818 templates "inside a function that opens a file" and stopped at the
location. Does that opener actually read the name the template built?

**Answer.** For 83.5% of the bound ones, yes: of 2,208 bound in-opener templates, 1,844 are read by
an opener in their own function (1,825 directly, 730 of them the opener argument itself; 19 through
one rebinding), 364 are bound and unread, and 466 more carry no binding at all.

**Numbers.** 2,674 specific in-opener templates over 3,452 modules; E426 published 2,818
*unfiltered* in-opener templates, today's unfiltered recount is 2,825 (+7, corpus growth), so the
two differ by the specificity filter and not by drift. Share read 0.8351.

**Three rules.** (a) Unbound is a shape, not a class -- folding 466 into "unread" inflates that bill
by 128%. (b) A binding climb that stops at the first call finds nothing: a template nested in
`os.path.join(...)` is bound by the assignment holding the join. (c) The direct-argument case must be
decided before the ascent, because the ascent consumes node identity.

**Bounds.** One rebinding hop only; identifier matching, not scope resolution; an opener is counted
by call name, so a helper that opens inside itself is invisible.

**Product.** `scripts/e427_opener_flow.py` (reuses E426 by import), face
`results/state_tilt/OPENERFLOW-2026-11-05.json` + latest, smoke leg (1/1, doctor 1/1 red), S6 leg
`opener_flow` (rc=0).
