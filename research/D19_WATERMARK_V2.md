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