# DIGEST r1659 bm-b · E639 — can the depth fold hide a write instead of a read?

**Question** (E639, seeded by r1658): E638 published the ctx of every member of the six two-depth
sites on E633's counted read lines and all six were loads. That is a fact about six sites, not about
the form: the same fold would hide a store or a delete one level below the receiver.

**Populations** (both re-derived from the tree, `scripts/e639_write_below.py`):
- whole corpus: 13,078 parsed `.py` (4 over the 1 MB cap, 0 unreadable, 304 do not parse),
  415,831 Subscript nodes, 45,391 two-depth (line, column) sites in 4,365 files;
- E633's 13 counted read lines, 6 of which carry such a site.

**Readings**
- 5,513 of the 45,391 corpus sites carry a store or delete at any depth
  (member ctx: load 95,229 / store 5,501 / del 12), and **all 5,513 carry it at the deepest
  member** — 0 writes sit at a non-deepest member, which is grammar: in `a[k1][k2] = v` the Store
  ctx is on the outermost subscript.
- On the counted read lines: 6 sites, 18 members, **all loads**. 0 store/delete the row's counted
  key at any depth, 0 at the deepest member; 6 of the 6 sites do have a member naming the row key.

**Verdict** `V_COUNTED_SITES_ARE_READ_ONLY` — the zero is a property of these 6 sites, not of the
form, and the face carries the corpus write total so the zero names what it counted (E444 family).

**Lessons**
1. Publish the zero with the population's counter-phenomenon, or the zero is unfalsifiable.
2. "Writes always sit at the deepest member" is grammar, and it must be a selftest leg — otherwise
   the two equal counters look redundant and get deleted.
3. This population is not E638's: only this study's own files are excluded, so E638's two scripts
   are inside it (13,078 vs 13,076 files, 415,831 vs 415,722 nodes) while the site totals coincide
   exactly — which says those two files carry no such site. Publish the difference, do not reconcile
   it away (E366 family).

**Evidence**: `scripts/e639_write_below.py` (selftest 17/17, run/verify `problems=[]`, rebuild
byte-identical sha 415431424e2d) · `results/state_tilt/WRITEBELOW.json` + `writebelow_latest.json` ·
`scripts/run_e639_smoke_leg.py` (1/1 PASS, `--doctor` 1/1 red with the face restored byte-identically) ·
`smoke_test.py` leg E639 · `Tools/s6_chain_bmb.py` leg `write_below` (rc=0 0.07s) ·
knowledge card E639.