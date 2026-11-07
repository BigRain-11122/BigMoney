# E504 — who composes a dated face name, and from which symbol

**Round** r1533 bm-b · **Evidence cutoff** 2026-11-07 · **Face** `results/state_tilt/NAMECOMPOSE-2026-11-07.json`
(latest `results/state_tilt/namecompose_latest.json`) · **Script** `scripts/e504_name_compose.py`

## The question

E485 (r1529) found two vintages whose payload states the day before the name and concluded the
basename is *composed by a round script from a date variable*, so the literal never appears in a
write statement. That is a statement about the writer census, not about the date. This study reads
the composing expression itself for every dated member of E485's population and publishes, per
naming site, which date symbol fills the date slot and whether that symbol is a **clock read** (the
run day) or the **payload's own cutoff** (the data day).

## Method

Population = E485's 571 member rows (97 families); 567 carry exactly one literal date in the
basename (the 4 range names are skipped and published as skipped). Sources = 3,738 `.py` files
under the repository minus `legacy/`, `Money02/`, `results/`, `data/`, `.codely-cli/` and this
study's own files; 3,619 parse (119 are disclosed as syntax-skipped).

A **naming site** is a string-building expression — f-string, `+` concatenation, `%` formatting or
`.format()` — whose constant skeleton reproduces the member's basename with the date inside exactly
one dynamic gap. Matching is a full-name regex, so a stem borrowed from another family cannot pass
the prefilter alone. When the leading constant is empty the family prefix is itself a variable, and
its literal values are resolved in the same module (`tag = "TREND" if ... else "WEIGHTING"`).

Origin resolution walks the date expression inside one module: `datetime.now()`/`date.today()`
family → clock; a subscript/attribute whose key names a date field, or a `.get('evidence_cutoff')`
→ payload; `args.x` → CLI; a date literal → module constant; a function argument → parameter; a
symbol never bound here → unresolved; disagreeing bindings → mixed.

## Readings (2026-11-07)

| | value |
|---|---|
| members with a single date | 567 (370 ISO / 197 compact) |
| naming sites | 123 |
| (site, member) pairs | 885 |
| members named by ≥1 site | 506 |
| **only by the payload cutoff** | **338** |
| **only by the run clock** | **2** |
| by more than one origin | 112 |
| no composing site in this repo | 61 |
| site origins | payload 85 · clock 2 · parameter 2 · mixed 8 · unresolved 26 |

The 402 comparable files reproduce E485 exactly: **124 compact / 278 ISO**. Among the compact 124:
69 payload-only, **2 clock-only**, 30 no site, 12 multi-origin. Among the ISO 278: 205 payload-only,
0 clock-only, 24 no site, 27 multi-origin. So the compact spelling is not what carries the clock —
one family is.

## The two E485 one-day cases, answered

* `results/e24_ladder_weighting/WEIGHTING-20261021.json` — site **S0036**
  `scripts/e24_ladder_weighting.py:590` composes `'%s-%s.json' % (tag, stamp)` with
  `stamp = datetime.now().strftime("%Y%m%d")`. **The name is the run day**, the payload's
  `evidence_cutoff` is the data day: the one-day lag is the distance between the clock and the last
  complete bar, not a mistake.
* `results/_w280bmc_20261021_probe_receipt.json` — no composing site exists in this repository (the
  one-off script that wrote it is gone). Published as no-site, not guessed.

## Self-caught measurement bugs

1. **One word, two populations.** The resolver class `mixed_assignments_…` and the site-level label
   for "this site names members through more than one origin" were the same string, so five sites
   looked self-contradictory to the gate. Split into `ORIGIN_VOCAB` (rows) and `SITE_ORIGIN_VOCAB`
   (sites). Name-is-semantics, again.
2. **A scanner that demands a leading literal loses exactly the sites that matter.** 56 candidate
   sites had an empty leading constant because the family prefix is a variable; among them was
   S0036, the clock site E485's whole finding is about. Resolving the prefix's static values
   recovered it.
3. **Only walking `ast.Assign` reports bound symbols as never-assigned.** Adding `for` targets,
   comprehension targets, tuple unpacking, `with … as` and walrus took the unresolved pairs from
   313 to 169 — a fact about the walk, not about the code.
4. **A stem prefilter matches prose.** Before requiring the composed skeleton to end in a file
   suffix, 56 "unresolved naming sites" were round-report prose rows; the real count is 0.

## Verification

`run` rc0 · `check` problems=[] · `verify` re-derives the same face (problems=[], 33 s) ·
`selftest` 23/23 · smoke leg `1/1` green with `--doctor` going red and restoring the face
byte-identically (sha 311105084107 in/out) · S6 leg `name_compose` rc0.

**Not claimed:** the full smoke suite was not run this window; the rest of the S6 chain was not
re-run; no cloud, no GPU, nothing deleted.