# CONTENT-LOOP QUEUE -- drama line (bm-b host, v0.1)

> Carrier: Bigmoney-ContentLoop S4U task (20-min). Machine ledger = queue.json (single-writer);
> this file is a regenerated face -- never hand-edit. Protocol: claim-by-file, station states
> open/claimed/done/blocked; five-piece gates stay in-loop (no downgrade); director step-gate
> per station; CEO = terminal review only; account writes = physical-domain pause face.
> Law refs: CONTENT-OS-LOOP-BLUEPRINT-v1 sec.3; O-20261018-2144-bm-c sec.2.1; DIRECTOR-STEP-GATE-v1.

## Gates

| gate | state | note |
|---|---|---|
| ceo-direction-gate-v1-pilot3x20 | closed | PILOT-001 3x20s rough samples delivered 10-16; CEO direction-gate receipt NOT yet on ledger. v1->v2 upgrade trigger (PRODUCTION-SYSTEM sec.8.3) requires this ga |

## Stations

| id | state | lane | runner | require | title | claim |
|---|---|---|---|---|---|---|
| ST-001 | done | cpu | st001_rootcause_gather | none | J-D0-1 taildrop SLA violation root-cause self-cert (LEDGER pending backfill row) | claimed@bm-b@2026-10-18T23:50:27 |
| ST-002 | open | cpu+gpu-light | v0.2-pending | manual-gate:ceo-direction-gate-v1-pilot3x20 | v1.1 voice grade: IndexTTS-2 environment install (modelscope morning window) + 2 | - |
| ST-003 | done | cpu | st003_voice_library_first_batch | none | voice-library lane first batch: GPT-SoVITS (63k stars) / OpenVoice (37k stars) c | claimed@bm-b@2026-10-19T02:37:11 |
| ST-004 | done | cpu-code | st004_csa_anchor_precheck | none | CSA anchor-cleaning discipline into production: id-bank anchor consistency pre-c | claimed@bm-b@2026-10-19T02:37:31 |

Loop state: rounds=12 last=2026-10-19T02:37:25
