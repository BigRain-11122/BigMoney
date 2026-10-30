# DIGEST — r1379 (bm-c, 2026-10-31): the gate moved into a helper and the census lost the face (card E295)

**Inherited, not assumed.** This window opened on an uncommitted estate covering three rounds
(r1376 tool + face, r1377 alloc checkpoint, r1378 value classes) plus a fourth (r1379) that had been
started and abandoned mid-way: `Tools/live_value_cache_audit.py selftest` stood at **35 legs, 1 red**
(`L35 a gate that lives in a helper is still a gate on the face that uses it`). Per r1366 an inherited
tree is a subject, not a summary: every leg was re-run here before anything was committed.

**The red leg was pointing at a real hole, and at a leg that passed for the wrong reason.** r1378 fixed
`member_reinforce_p1.finalize` by moving its disk read *and* its provenance gate into `_chain_base()`.
Two consequences, both invisible to the audit as it stood:

1. The census enters a function through a cache-ish NAME plus a literal-key read. `finalize` no longer
   contains any comparison — it contains a call. So the fixture written for `L35` was **ignored** by the
   scanner (0 rows, `ignored=1`), and the leg could never pass.
2. The live row was **worse than a miss**: it was published as
   `reads_a_stored_value: false, evidence_class: no_stored_value_read` — a false sentence about a face
   whose ledger head comes straight off disk — and `L34`'s `live_served(...) is False` passed because
   the value had *vanished from the table*, not because a gate stood in front of it. A leg that
   passes for the wrong reason is the defect it was written to catch, one level up.

**What changed (`Tools/live_value_cache_audit.py`, selftest 35 → 37, all PASS).**

- `helper_facts(name)` returns `(identity keys, loads off disk)`; a caller is admitted by delegation
  **only when the helper it calls actually checks identity keys** (`delegated` requires `disk and ks`).
  Admitting every caller of every disk-loading helper is how r1376's 40 report readers came back in.
- `_call_targets()` reads the names bound by the call — and had to learn tuple unpacking
  (`prev_total, chain_base_src = _chain_base(...)`): reading only `ast.Name` targets made the gated
  helper look like a call that returns nothing.
- `_json_payload_names()` + a shared `_taint()`: a producer serves a number by **writing it into its
  product**, not only by returning it. `finalize` bakes the inherited head into
  `trials_chain_base.prev_total` and `json.dump`s it; a return-only taint rule said "serves nothing".
- `persisted` is now true when a gated helper is merely **called** (unbound, e.g. `_selfconsistent(x)`
  used as an assertion). The face did read a stored value; it just did not hand it on.
- a function is not its own helper (`nm != fn.name`): `e39_panel_census.selftest` was reporting itself
  as a delegated gate.

**Effect on the published face** (`results/live_value_cache_audit.json`, republished):

| | r1378 | r1379 |
|---|---|---|
| cache decisions | 16 | **31** |
| identity-checked | 0 | **19** |
| serving a stored value with no digest anywhere | 2 | **1** (`alloc_backtest.run_cell_faces` — digest handed in as an argument, F9-d already forces the recompute) |
| non-faces filed | 14 | 21 (11 fixtures, 8 read-not-served, 2 memos) |

Six faces now leave the headline **for the right reason** — `member_reinforce_p1.finalize`,
`wild_route_lab.run_shard/finalize`, `alphagen_rg_census.cmd_run`, `cn_mkneutral_p1.cmd_run`,
`p1e_neighbor_corr.run` — each with the helper name and the identity keys it checks published beside
it. Nothing was downgraded: the two rows that were memos stayed memos, the five `no_digest_anywhere`
rows all read disk without serving.

**One more thing the estate would have shipped.** `Tools/s6_chain_bmc.py` in the working tree had
**deleted two legs bm-a added in r1175** (`etf_book_flip_contamination`, `etf_book_shock_day`) — a
rebuild from an older base, the r609 family. Restored to `origin/main` verbatim before commit; the
pre-push ownership claw is the only guard that would have caught it after the fact.

**Card E295.** A scan keyed on where a value is *used* stops seeing it the moment the producer moves
the read into a helper — and the first symptom is not a missing row but a row that says the opposite
of the truth. Ask a census of "who reads disk" not "what is named cache": the delegation edge, the
tuple-unpacking binding, and the json payload all have to be in it, or the fix that made the code
safer will quietly make the audit more confident.

Pos: `Tools/live_value_cache_audit.py` (`helper_facts` / `_call_targets` / `_json_payload_names` /
`_taint`, L36/L37) + `results/live_value_cache_audit.json` + `scripts/member_reinforce_p1.py`
(`_chain_base`) + digest `DIGEST-20261031-r1379-delegation-blind-spot.md`.