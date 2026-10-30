# r1376 — the cache sweep r1374/r1375 kept deferring, run to a count

**Round:** 1376 · bm-c · 2026-10-31
**Card:** E291 — yielded: bm-a r1176 landed E290 on origin while this push was in flight, so the card is renumbered here (labels only; the finding is unchanged) · **Tool:** `Tools/live_value_cache_audit.py` (selftest 14/14)
**Face:** `results/live_value_cache_audit.json`

## The sentence both previous rounds ended on

r1374 wrote the rule down (`stress_inputs_digest`) and applied it to one cache.
r1375 found the same defect living in a second file and fixed that too. Both closed with
the same admission — *"the same question has not been asked of every face on this host
that caches a live value across ticks; the sweep was rule-led inside the etf_book family,
not exhaustive across the repo."*

An admission repeated twice is a to-do that nobody owns. This round replaced it with a
number.

## What the scan asks

Not "does this file mention a cache" — 194 functions do, and 112 of those turned out to be
a local dict called `cache` that never reads anything back. The question is narrower and
mechanical: **a function that (1) writes JSON, (2) loads a previous value and compares it,
and (3) whose cache-ish name is compared against literal keys.** Only that function can
serve a stale number.

Three classifications, and the middle one is the one that matters:

| verdict | meaning |
|---|---|
| `digest_in_key` | the key it compares carries a digest/fingerprint — the r1375 form |
| `module_has_digest_key_does_not` | the module hashes something; **this** key does not. r1375's defect lived exactly here: a digest existed, one cache used it |
| `no_digest_anywhere` | nothing in the module hashes anything |

Plus a fourth axis that the first version of this scan lacked: what happens **when the
comparison fails**. A gate that `raise`s on mismatch cannot serve a stale number — it
stops. A face that `return`s the cached payload is the one the whole family is about.
Reporting both under one count is how an audit becomes noise.

## Reading (698 files: `scripts/` + `Tools/`)

```
16 cache decisions | 13 serve on a key with no digest | 2 refuse on mismatch
```

- `digest_in_key` **1** — `etf_book_beta_menu.selftest`, keyed on `inputs_sha256`
  (r1375's fix, now visible as the only fully-digested comparison in the tree).
- `module_has_digest_key_does_not` **7**
- `no_digest_anywhere` **8**
- `unreadable` **0** — see the BOM pit below; six files were unreadable in the first pass.
- `serves_without_digest` **13** — the reading list.
- Skipped by rule, disclosed rather than hidden: 1,464 `_`-prefixed one-shot scratch
  tools (they write faces as a by-product of a closeout, they are not a value served
  twice), and 83 cache-ish names that never compare anything.

## Two judgement calls that changed the answer

1. **Matching prose counts nothing.** The first run matched the word `cache` inside
   docstrings and comments: 194 "cache writers", 112 "without a digest". Names only —
   a variable called `cached` is a face, a sentence saying "cache" is prose. 194 → 21.
2. **`import hashlib` never creates a `Name` node.** So a module that hashes something
   else read as `no_digest_anywhere`, which is a wrong sentence about a wrong file. The
   import table is now read too, and the half-covered case is a separate verdict — with
   its own leg (L12) because it is exactly r1375's defect shape.

## Pit found on the way (E1)

Six real, working files (`scripts/etf_book_beta_menu.py`, `scripts/t11_negday_ic.py`,
`Tools/tree_shrink_guard.py`, …) were reported as **unreadable**, i.e. silently outside
the sweep. Cause: they start with a UTF-8 BOM (`\ufeff`), and `ast.parse` rejects it as an
invalid non-printable character at line 1. Fixed by reading `utf-8-sig`. The lesson is the
same one r1375 learned from `os.path.relpath` across drives: **a scanner that cannot read
a file must not report it as clean** — here the state was at least named `unreadable`
rather than dropped, which is the only reason it was findable.

## What this does not do

The 13 rows are a **reading list, not a verdict list**. A static read cannot see a key
built in a loop, a key stored in a dataclass, or a digest that reaches the cache some
other way; and a face in the list may be provably safe on inspection. The claim this
round makes is only the countable one: the repo has 16 places that decide whether to
reuse a live value, and 13 of them decide it without a digest in the key — where the
previous answer was "we looked at the etf_book family".