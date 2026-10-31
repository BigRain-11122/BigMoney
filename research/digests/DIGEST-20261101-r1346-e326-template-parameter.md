# DIGEST 2026-11-01 (r1346 bm-b) -- E326: who quotes a template face without its parameter

**Question (pool card E326, seeded by r1345).** E325 closed the FACE layer: no face in the 51-face
population is an orphan once every way of naming a file is allowed. But 30 of those faces are
reached only through a format template (`"BANDDEFLATE-%s.json" % CUTOFF`) or a composed path, and a
template has a **free parameter**. A face written at cutoff X answers a different question than the
same template at cutoff Y. So: do the consumers of those faces carry the parameter -- and which
published numbers are tied to a face whose parameter is not republished beside the number?

**Answer (population = E325's own template/composed faces, 2280 in-repo sources, static only).**
Of the 30 faces, 20 carry a parameter (an ISO date, a compact stamp, or the class suffix an
underscore family varies) and 10 are composed paths, which spell their name in full and therefore
have no parameter to carry. Every consumer outside the writers -- 14 of 34 references -- either
spells the face's own name (5) or fills the template from a name it defines (9). **No consumer
resolves a parameterised family without naming the parameter, and no published number is tied to
a face that does not republish its parameter.**

| reading | count |
|---|---|
| faces in population | 30 |
| parameterised / static | 20 / 10 |
| named by a source other than their writer | 8 |
| parameterised faces that republish the parameter beside their numbers | 18 |
| parameterised faces that do not | 2 (`_fund_divlowvol_p2_freeze_probe_local.json`, `e40_cashleg_drag/CASHLeg-20261027.json`) -- both named only by their own writers |
| consumers outside the writers: literal pin / own constant / read back / unpinned | 5 / 9 / 0 / 0 |

Verdict (recomputed by the gate from the frozen constants):
`every_consumer_of_a_parameterised_face_supplies_the_parameter_in_its_own_source`.

**Three rules that had to be measured rather than assumed.**

1. **Naming a dated face IS pinning its parameter.** `load("BANDDEFLATE-2026-10-29.json")` writes
   the date into the consumer's own source, so it answers that date's question by construction.
   The risky shape is the opposite one -- a glob or a pointer that resolves whichever face is on
   disk -- so the classifier's weakest class is reserved for it. A first draft treated the family
   prefix `REPRO-` as a reference and "found" 13 unpinned consumers inside gate labels such as
   `G-REPRO-v1`; a bare prefix only counts when followed by a format marker or a glob.
2. **A consumer is judged by its weakest naming line.** A file that pins the date in one place and
   globs the family in another is an unpinned consumer. Applying that rule moved exactly one
   consumer from "literal pin" to "supplies its own constant" and created no finding.
3. **A composed path has no parameter at all**, so it cannot be a silent-parameter finding. The
   10 static faces are published as `kind: none` rather than being folded in as "0 risk".

**What this negative does NOT cover -- published, because it is the next card's population.**
The scan follows only direct references to a face family. **11 of the 20 parameterised faces are
reachable through 143 `*latest*.json` pointers** in their own directories: a reader that opens the
pointer never sees a date in a file name at all. Those pointer consumers are counted here but their
sources are not traversed, and the face says so in `limits`.

**Wiring.** The census rides the S6 chain (`template_parameter_consumers`, verify re-derives every
consumer class from the tree, ~2s) and the smoke suite carries a leg that refuses a stored verdict
or per-face class table that does not re-derive, and refuses a "carried parameter" reported as a
silent number. selftest 16/16, including the fixtures that separate the four classes, the pointer
limit's disclosure, and the self-exclusion of this scanner from its own corpus.