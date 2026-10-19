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
| ST-005 | done | cpu-code | st005_gpt_sovits_env_ignite | none | voice-library env bootstrap: GPT-SoVITS phased install driver (venv+torch-cpu+de | claimed@bm-b@2026-10-19T03:41:40 |
| ST-006 | done | cpu-code | st006_voice_bank_manifest | none | voice-bank manifest v0.1: 7 canon character voice entries (schema+descriptors+re | claimed@bm-b@2026-10-19T03:52:01 |
| ST-007 | done | cpu | st007_first_synthesis_smoke | ST-005 | first-synthesis smoke: GPT-SoVITS v1 zero-shot chain validation (in-house r998 a | claimed@bm-b@2026-10-19T05:58:21 |
| ST-008 | done | cpu | st008_voice_bank_entries | ST-007 | canon voice-bank entries v0.1: role-aligned ref clips 1-3/char from r998 in-hous | claimed@bm-b@2026-10-19T06:18:16 |
| ST-009 | done | cpu | st009_voice_differentiation_eval | ST-008 | character voice differentiation eval v0.1: voice_07/voice_05 shared-base debt me | claimed@bm-b@2026-10-19T07:45:35 |
| ST-010 | done | cpu | st010_pitch_tier_test_synth | ST-009 | pitch-tier test-synthesis station: XIONG/XIONGWEI/FATHER 1 line each through GPT | claimed@bm-b@2026-10-19T10:56:10 |
| ST-011 | done | cpu | st011_boy_mancang_sourcing | none | BOY/MANCANG sourcing station: child-voice license review FIRST (BOY) + MANCANG d | claimed@bm-b@2026-10-19T11:52:25+08:00 |
| ST-012 | open | gpu-night | v0.2-pending | none | character-voice LoRA training lane: GPT-SoVITS base finetune (GitHub wheels scan | - |
| ST-013 | done | cpu | st013_dubbing_sheet_prep | none | dubbing sheet preprocessing EP001-003 (一路长虹): per-line character/emotion/est-dur | claimed@bm-b@2026-10-19T14:11:15 |

Loop state: rounds=54 last=2026-10-19T13:52:01
