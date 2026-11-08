# DIGEST 2026-11-08 r1566 bm-b — E538: where the parcel that kept moving actually lands

**Question carried in from E535.** Of the six sites E534 published as handed onward, five never reach a
second reader and exactly one is still moving: `_resolve_module_chain` returns `_resolve_chain_text(...)`
at `scripts/e398_latest_family.py:410`, and E535 published all three of that callee's consumers as
"hands the value on again". "Hands it on again" is a sentence about the consumer, not about the value.

**Measurement (static, no execution, no rewrite).** Each consumer is classified from its own body:

| site | consumer | what its body does | disposition |
|---|---|---|---|
| 440 | `_resolve_chain_text` | `return _resolve_module_chain(...)` | knot |
| 445 | `_attr_static_dir` | `return _resolve_module_chain(...)` | knot |
| 646 | `classify` | `found = _resolve_module_chain(...)`; `if found:`; `dict(evidence, family_dir=found, ...)` returned | exit into a named field |

The two "still moving" consumers are a **call-graph knot**, not a chain:
`_resolve_module_chain → _resolve_chain_text → _resolve_module_chain`. No value leaves the resolver
family through either of them. The one real exit names `family_dir` in the evidence payload that the
same module writes with `json.dump` at line 1078.

**Price (joined off the census face as it is written, not asserted in-batch).** 237 published read
sites; **4 of them** carry a `family_dir` this arm produced (`share 0.0169`):

* `Money02/live_pull.py:12` — `D.LIVE_DIR -> data/live`
* `Money02/live_view.py:16` — `D.LIVE_DIR -> data/live`
* `Money02/preflight_data.py:58` — `D.LIVE_DIR -> data/live`
* `Money02/preflight_data.py:59` — `D.LIVE_DIR -> data/live`

All four are classed `family_stated_at_the_site`. The label says the site states the family; the value
came from an imported constant resolved three functions away. So 4 of the 206 "stated at the site" rows
are not stated at the site — that residue is E539.

**Reusable lessons.**

1. "The consumer forwards it again" is a graph question, not a chain question. A resolver family calling
   itself looks exactly like a hand-off; check whether the hop returns to the same entry (2 of 3 here),
   or the loop count gets published as a hop count.
2. Price a field by joining the face that is already on disk. The 4/237 only exists because the census
   face was written by another study at its own cutoff; asserting it in-batch would be self-certifying.
3. **A published face's file name is an ownership.** This study's first `run` wrote into E530's
   `thirdhop_latest.json` and overwrote it (recovered with `git checkout`; E530's leg went red until
   then). `write_face` now reads the `study` key of whatever is on disk and refuses a foreign owner.
4. **A leg name is an ownership too.** `third_hop` was already E530's; a duplicate name makes `--only`
   silently run both legs and report one red with an empty tail — which is what happened, and is why the
   collar was waiting for.
5. A gate needs both halves: an exit row must name a field, and a knot row must not. Without those two
   legs a doctored face could re-label a knot as an exit and pass.

**Evidence.** `scripts/e538_third_hop.py` run rc0 / check problems=0 / verify problems=0 (rebuild byte
identical) / selftest clean (6 arms + 4 doctored faces refused); face
`results/state_tilt/PARCELLANDING-2026-11-08.json` + `parcellanding_latest.json`; S6 leg
`parcel_landing` rc0 0.06s; smoke leg `# E538` 1/1 and `scripts/run_e538_smoke_leg.py --doctor` 1/1 red
by design; card E538 appended to `knowledge/METHODOLOGY_ASSETS.md` (numstat 18/0).

**Not claimed.** The full smoke suite was not launched and the rest of the S6 chain (collectors,
market_regime, scorecards, papers) was not re-run this window.