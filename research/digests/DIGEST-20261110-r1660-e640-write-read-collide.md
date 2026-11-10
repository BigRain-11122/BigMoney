# DIGEST r1660 bm-b -- E640: can a two-depth write sit *next to* the reads E633 counts?

**Question** (E640, seeded by r1659): E639 priced the write population corpus-wide (5,513 sites
carry a store or delete, all at the deepest member) but looked only at sites physically on a
counted read line, where it found 18 members and 18 loads. A duplicate-read test has to know whether
the key a counted line reads can be written *anywhere in that function*, not only on its own line.

**Populations** (both re-derived from the tree, `scripts/e640_writeread_collide.py`):
- whole corpus: 13,080 `.py` walked (4 over the 1 MB cap, 0 unreadable, 304 do not parse),
  415,955 Subscript nodes, 45,395 two-depth (line, column) sites in 4,366 files;
- E633's 13 counted read lines, each resolved to its innermost enclosing function.

**Readings**
- Sites by owner: 27,675 sit inside a function (5,289 functions carry one), **17,720 sit at module
  level** and belong to no function.
- Write face by owner: 2,873 write sites inside functions across 1,196 functions; counting every
  owner gives **5,514** (2,641 of them module level). E639 published 5,513 over its own file set --
  the 2,641 vs 2,642-style gap is that E639 excludes its own scripts while this study does not, so
  the two numbers differ by exactly one file, not by a disagreement about what a write site is.
- The 13 counted read lines land in **6 distinct functions**: 5 carry a two-depth site, **3 carry a
  write**, 1 carries none at all. Those 6 scopes hold 156 sites (member ctx load 332 / store 10 /
  del 0) and 10 write sites; 24 sites name the row's key, **0 write it**.
- Write positions relative to the read line: **7 before / 0 on / 3 after**.

**Verdict**
`the_counted_read_lines'_functions_do_carry_two_depth_write_sites_but_none_of_them_names_the_row's_counted_key_at_either_depth,_so_writes_can_sit_next_to_these_reads_only_of_other_keys`

**Why it matters**: the question the duplicate-read chain has been circling is now answered at the
scope that matters -- a write *does* live in three of the six functions, so "no write beside the
read" is false; what is true is narrower and more useful: none of those writes names the counted
key, and none sits on the read line itself.

**Pitfalls recorded**
1. Owner attribution is the whole study: without it 17,720 module-level sites inflate the in-function
   write count by 2,641 and the E639 reconciliation becomes an unexplained gap. Both totals are
   published on the same face with the difference named.
2. Name matching alone is not enough: two `f` functions in one module make a name-only match bind the
   read line to the outer one and mis-place every site. Match by name first, then take the smallest
   containing span, and publish the span so the gate can re-derive "the site is inside it".
3. Presence is not order: 7 of the 10 writes precede the read line and 3 follow it, none sits on it;
   the before/at/after split is published and asserted to add up to the write total.
4. A fixture whose flagged site already carries a write cannot test a lying write flag -- the first
   `--selftest` draft flipped `any_member_is_write` on a load+del site and the leg passed for the
   wrong reason; it now flips a two-load site.

**Product** = `scripts/e640_writeread_collide.py` (selftest 19/19, run/check/verify `problems=[]`),
`results/state_tilt/WRITEREADCOLLIDE.json` + `writereadcollide_latest.json`,
`scripts/run_e640_smoke_leg.py` (1/1 PASS, `--doctor` 1/1 red, face restored byte-identically),
`smoke_test.py` leg E640, `Tools/s6_chain_bmb.py` leg `write_read_collide`, POOL E640 done / E641
seeded.
