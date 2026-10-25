# D-19 watermark v2 — source-anchored four-tuple (D-20261025-08)

**Status**: implemented and aligned on bm-c in r1265 (deadline 2026-10-26 06:00 met).
**Tools**: `scripts/d19_watermark.py` (`--selftest` 30/30), canonical probe `results/_r686bmb_d19_check.py`.
**State evidence**: `state-bm-c.json` → `last_decisions_watermark_v2`, `last_orders_watermark_v2`; receipt `results/d19_watermark.bm-c.json`.

## Why the content hash alone was not enough

The legacy keys (`last_decisions_sha` / `last_orders_sha`) store a digest of the blob
bytes. A digest proves *what* you read, never *where* you read it — so a watermark can be
unreproducible at origin and still look perfectly well-formed. That is the ghost-sha family
(bm-b r1142/r1145: a stored DEC sha that no origin commit ever produced; every retry pushed
a phantom advance target).

v2 stores the source trio beside the fingerprint:

```
v2:<owner/name>@<commit40>/<blob_bytes>#<sha256>
v2:BigRain-11122/FluxGroup@ff22fb0cd0e88ca8737af7a39a9f3b6a6d1d9f7f/222683#f94a284c...
```

Comparison order: `repo` → `commit_sha` → `blob_bytes` → `sha256`.

| status | meaning | action |
|---|---|---|
| `same` | all four equal | no-op |
| `source_ahead` | same repo, same content, origin tip moved | advance source trio (content identical) |
| `delta` | bytes or digest differ | consume in this round, then `--advance` |
| `stale` | repo differs / quad unparseable | **refuse**; never advance on an unreproducible key |
| `migrating` | no stored quad yet | fall back to the content digest, never to the commit-first triple |

## A live defect this round exposed

The pre-existing triple (`<sha16>@<commit7>/<bytes>`, D-20261024-03) compares **commit before
digest** (`research/pit-protocol-d19.md` lineage). Every unrelated group commit therefore
makes both files report `changed: true` even when the bytes are byte-identical. Observed live
in this window: `decisions_sha == wm_decisions` exactly, yet `decisions_changed: true` purely
because origin moved from the stored commit to `ff22fb0`.

v2 makes the delta verdict **content-first**:

- `same` / `source_ahead` → `changed: false` (the blob bytes are identical)
- `delta` → `changed: true`
- `migrating` → legacy content digest test (the stored key already holds a full digest)
- `stale` → keeps the conservative legacy verdict, so an unverifiable watermark can never be
  read as "nothing new"

The legacy verdicts are preserved in the probe output under `legacy_changed` for audit; the
triple function itself is untouched (its own selftest leg still passes).

## Acceptance leg (the one the decision names)

> 验收 = 各司水位件含四元组且取件命令复现同一 blob

Two pieces ship for this:

1. `verify_stored()` in the probe re-fetches the **stored** commit and re-hashes the blob at
   that commit: `reproducible` / `not_reproducible` / `commit_absent` / `unverifiable`.
   Live check on bm-c after the write:
   `reproducible: blob at ff22fb0:docs/decisions.md matches the stored quad` (same for orders).
2. The update receipt carries `refetch`, a copy-paste command that rebuilds the same blob:
   `git -C <group-tree> show ff22fb0cd0e88ca8737af7a39a9f3b6a6d1d9f7f:docs/decisions.md`

A `not_reproducible` verdict refuses `update --advance` (exit 3). Rebuilding from a verified
fresh read is the explicit, receipt-logged `--repair-stale` path — the ghost is never silently
laundered into a fresh key.

## Pitfalls (both caught in this window)

- **The receipt file is shared by subcommands.** `update` then `verify` on the same path leaves
  the *verify* output in `results/d19_watermark.<machine>.json`, silently discarding the
  update's `v2_status` / `refetch` evidence. Re-run `update` (idempotent no-op) if you need the
  update receipt last, or pass an explicit `--receipt`.
- **Quad grammar lives in the probe, not in the tool.** `d19_watermark.py` loads the probe
  module for parsing so the read face and write face can never disagree on the format; a
  duplicated parser would drift the moment one side gains a field.

## The round line (r1266) -- the verdict has to leave the receipt

The v2 work above made the reproducibility check a *gate* on the write path, but nothing
forced the verdict onto the round report: a phantom watermark could sit in a receipt no one
reads and the round would still close clean. r1266 closes that with one command:

    python scripts/d19_watermark.py line

It prints exactly one ASCII line and writes `results/d19_round_line.<machine>.json`:

    S0.5 D-19 dec=same/repro@ff22fb0/222683 ord=same/repro@ff22fb0/371896 delta=none phantom=none src=BigRain-11122/FluxGroup

Reading it left to right: per face, the delta verdict (`same` / `DELTA`) and the stored-quad
reproducibility token, both anchored at `commit7/bytes`; then which faces carry a delta, which
are phantom (the token is `PHANTOM`, never a clean word), and the repo the read came from.

- Tokens: `repro` / `PHANTOM` / `absent` (migrating) / `no-commit` (commit not in this clone) /
  `unprovable` (no tree, or path absent at that commit) / `unknown` (probe said something new).
- Exit: `0` line printed (a `DELTA` is data, not an error) / `2` probe fault / `3` phantom --
  repair stays an explicit `update --repair-stale` with a verified fresh read.
- The probe's own JSON summary is printed **only on the fault path**: the line supersedes it, and
  the r1045 relay law exists so a failing child is not silent, not so a healthy one is re-printed.
- `format_line` is a pure function of the probe evidence (no clock, no IO), so the round line is
  byte-reproducible; selftest legs L28-L30 pin "every face present", "delta and phantom never
  collapse into each other", and "missing evidence degrades to unknown, never to a clean token".
