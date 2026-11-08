# DIGEST-20261108-r1585 — E559: is there anyone on the other end of the chain's channel?

**Round** r1585 (bm-b) · **card** E559 · **parent** E558 (r1584) · **face**
`results/state_tilt/CHAINRCCONSUMER-2026-11-08.json` + `chainrcconsumer_latest.json`

## The question

E558 closed with: the three chain runners record each leg's rc, compare it to zero, print the
NONZERO lines, and then exit 0 — a refusing gate leg is a line in a file, not a failure any
process carries. That sentence has an untested assumption: **someone on the other end collects.**
A collector can sit on two channels, and they fail differently:

* the runner's **process exit code** (a scheduled task, a watchdog, a parent process);
* the **receipt** the runner writes (`results/_r<N>bm[abc]_s6_chain.json`).

## What was measured

Population = live repo code (`scripts/ Tools/ monitor/ firm/ live/ tests/ knowledge/` plus
repo-root files; py/ps1/cmd/bat/vbs). `results/`, `data/`, `logs/` are history, not code.

| arm | reading |
|---|---|
| spawn sites of a chain runner | **2**, both `subprocess.Popen(..., DETACHED_PROCESS\|CREATE_NO_WINDOW)` that print the pid and return — **0 can fail the caller** (they never wait, so the rc is unobservable) |
| receipt readers | **0 outside the writer** (3 writers = the three runners; a writer re-opening its own receipt is a writer, never a reader) |
| import sites | **18**, all read the **leg table** (`smoke_test.py` 15, `scripts/etf_book_registry.py`, `scripts/lane_host_declaration.py`, `smoke_test.py --import`) — structure, not result |
| repo sources declaring a chain action | **0** |
| live scheduled-task census (bm-b, disclosed not gated) | **296 actions, 0 run a chain runner**; 15 bigmoney actions, none of them the chain |

Verdict `nothing_on_any_machine_reads_the_exit_code_or_the_receipt`.

Read it as two closures: E558 showed the failure never reaches a process exit; E559 shows the
receipt it does reach is **written for a reader that does not exist**. The S6 chain is not
scheduled at all — it runs only when a round session types the command, and the two detached
helpers exist to keep the console silent, which is also what makes the rc unobservable.

## Four reusable rules (measured, not assumed)

1. **"Someone records it" is not "someone collects it."** All three runners do the right thing
   on the production side. The consumption side is two detached spawns, zero receipt readers and
   zero scheduled tasks. Any "does this signal get picked up" question has to be measured on the
   consumer side; it cannot be inferred from a well-built producer.
2. **A local helper with a spawn-like name invents a spawn site.** The first cut classified
   `run("CHAIN", [sys.executable, "Tools/s6_chain_bmb.py"], ...)` in `_tmp_r1251_chainseq.py` as
   a waiting spawn — but that `run` is a helper defined in the same file; the process is started
   inside it, and the *caller* merely passes an argv. Fix: resolve the module's imports and only
   accept a bare name that actually came from `subprocess`/`os`; otherwise require the qualifier.
   A control arm now pins this.
3. **A BOM makes "unreadable" look like "absent."** Seven files came out as
   `spawn_shape_this_scan_cannot_fold` on the first build — every one of them was UTF-8 with a
   BOM, so `ast.parse` threw. Reading with `utf-8-sig` first took the count to zero. Same family
   as an empty `literal_eval` or an unfoldable `os.path.join`: publish unreadable as a count,
   never fold it into "there is nothing there".
4. **A census is inside its own corpus.** Adding `Tools/_r1585bmb_task_census.py` (which names
   `s6_chain_bm`) moved `corpus_files` 3892 → 3893 and made `check` report
   `summary does not re-derive`. That is not drift; it is a self-including denominator. Rebuild
   after wiring, and publish `corpus_files` apart from `files naming a runner` so the reader can
   see which is which.

## Bounds (published with the face)

Static AST only; a runtime-built argv is `unfoldable`, not `absent`. The 300+ historical
per-round chain copies under `results/` each re-read their own receipt — history, not consumers,
excluded and said so. The wrapper classes (fails / checks-but-cannot-fail / `$LASTEXITCODE`
after a `.ps1` call / never checks) have no live member today, so the face states that their
positive cases come from fixtures only. The live task census is a one-off receipt
(`results/_r1585bmb_task_census.json`): a live census does not reproduce at build time, so it
is disclosed beside the gate, not gated.

## Wiring

`scripts/e559_chain_rc_consumer.py` (build / check / verify / selftest 24/24) — S6 leg
`chain_rc_consumer` (4.4 s rc=0) — smoke leg `# E559` — standalone leg
`scripts/run_e559_smoke_leg.py` — card `knowledge/METHODOLOGY_ASSETS.md` E559.

Next pool card: **E560** — does the receipt carry enough to triage without the console (does a
non-zero rc short-circuit the loop, is an unrun leg representable, and does a row carry the
first failing leg's name/rc/output)?