# DIGEST 2026-11-10 r1652 bm-b — E633: the read forms the classifier does not name

**Card** E633 (seeded r1651 by this lane) · **Face** `results/state_tilt/READFORMGAP.json`
(+ `readformgap_latest.json`) · **Script** `scripts/e633_read_forms.py` (selftest 29/29) ·
**Legs** smoke `E633 …` (1/1, doctor 1/1 red, face restored byte-identically) ·
S6 `python Tools/s6_chain_bmb.py 1652 --only read_forms` → rc=0 0.05s problems=[] ·
**products** `results/runnable_pool.json` E633 done / E634 seeded

## The question

E632 (r1651) counted read **nodes** on the 13 lines E631 had counted, using the classifier E623
built: a string subscript or a `.get("key")` call. E632 published the limit itself — a same-key read
in a form the classifier does not name is invisible at node level exactly as it was at line level.
E633 prices that hole on the population E632 had already fixed.

## Method

Re-parse each module holding a counted read line, resolve the function spanning the dead line,
resolve the **receiver** of the counted read (leftmost name of its base), follow one hop of local
aliasing (`v = d`), then classify every other access of that receiver that starts on the **same
physical line**: subscript / keyed call / membership test / iteration / bare use / container call,
with the chain depth published on each. Seven classes, keyed on one question — does this access read
*this key* without producing a read node — plus a three-valued `could_force_a_second_read`
(`True` / `False` / `null` for a computed key that reads *some* key, not demonstrably this one).

## Reading

13 counted read lines, **13 resolve to a receiver**, 29 accesses of those receivers on those lines:

| class | count | note |
| --- | --- | --- |
| `recognised_read_of_the_key` | 13 | re-derives E632's published node total exactly |
| `unnamed_entry_read_of_the_key` | **0** | `"k" in d` / `del d["k"]` / `setdefault` / `pop` — none present |
| `read_with_a_computed_key` | 5 | all member lookups: `sleeves[tid]` ×4, `faces[UP_E350]` |
| `read_of_a_different_key` | 1 | `P["n"]` beside the counted `P["days"]` |
| `read_below_the_receiver` | 9 | the chain has already left the receiver object |
| `container_enumeration` | 1 | the bare `ports` truthiness test in `ports["x1"] if ports else None` |
| `write_of_the_key` | 0 | — |

10 of 13 lines carry at least one other access of their receiver; 0 aliases were found, so the
"variable subscript" form the card names is not exercised at all on this population.

**Verdict** `no_counted_read_line_names_this_key_outside_the_classifier_so_the_node_count_E632_
published_stands`.

## What this is worth

The duplicate denominator E631 left standing has now been attacked at four levels — value (E625),
handover (E626), second name (E627), receiver origin (E628), caller write (E630), read multiplicity
(E631), node multiplicity (E632) — and this is the last place it could have moved: an entry read with
no node to count. It is empty. The five computed-key reads are published in their own class instead
of being folded into a same-key count, because `sleeves[tid]` reads *a* key of `sleeves` and the
census cannot show which; that they name member records rather than the counted factor key is stated
as a reading of the sites, not as a measurement.

## Limits (published on the face)

1. the receiver is a **name**, so `a[b]["k"]` and `a["k"]` share one — depth is published per access
   so the reader can separate them (E206/E207 family);
2. the walk is **line-scoped** by construction: an access that starts on a neighbouring line belongs
   to that line's count — seeded as E634;
3. aliasing is one hop, inside the function body only: a parameter, an attribute, or a comprehension
   alias is not followed;
4. a computed key is `null`, never `False`: it reads some key, and deciding whether it is this one
   would be a guess;
5. `.items()/.keys()/.values()` iterate the container and are classed container-level — they read
   entries but produce no single-key read node, so counting them as same-key reads would manufacture
   the very gap this study was asked to measure.

## Two instrument notes

**(a) a stored subscript is not a read, a deleted one is.** The first draft classified every
subscript on the receiver with the counted key as `recognised` — which silently made `del d["k"]` a
positive read node. The store/delete contexts are now their own classes (a delete raises `KeyError`,
so it reads presence; a store reads nothing) and a fixture leg pins each.

**(b) a line with no recognised read needs its receiver picked by role, not by traversal order.**
`ast` walk order is not document order, so taking the first non-target name on `d = m[k2]` picked the
argument `k2`. The receiver is now the name that actually appears as the base of an access on that
line, falling back to the first non-target name only when no access exists.