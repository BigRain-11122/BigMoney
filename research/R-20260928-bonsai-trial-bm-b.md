# R-20260928 bonsai fleet trial — bm-b lane receipt (T-2026-09-28-99)

- CEO order P-2026-09-28-07 · fleet task T-2026-09-28-99 · sole spec = cph4/research/R-20260928-bonsai-fleet-trial.md (HQ repo)
- Machine lane: bm-b (RTX 3070 8GB) = tight-envelope GPU trial, bare-window run
- Evidence (machine-readable, live-run numbers, zero pre-write): `results/_r386bmb_bonsai_trial_result.json` (orchestrator `results/_r386bmb_bonsai_trial.py`, run r388 14:57:09→14:58:00 pid 8516)
- Boundary honored: T-70 negative (coding production lane excluded, cloud-retained face, no switch); probes are advisory-QA lanes only

## 1. deploy — PASS

- Byte anchors 3/3 MATCH: model 5,946,648,928 · llama-bin.zip 257,322,810 · cudart.zip 391,443,627
- Runtime = PrismML-Eng/llama.cpp fork b10743 (build adfffbe41 10743) Win CUDA 12.4, unpacked in-repo `labbench/bonsai/runtime/` (gitignored)
- llama-server `-ngl 99 -fa on -c 4096` : `/health` ok in **5.6s** (port 8079)

## 2. speed — 40.75 tok/s tg128 (tight envelope)

- llama-bench `-p 512 -n 128 -r 3`: **tg128 = 40.75 ± 0.30 tok/s**, pp512 = 914.41 ± 18.71 tok/s (wall 19.1s)
- Fleet comparison face: bm-a 4070S anchor 54.7 tok/s → bm-b 3070 = 74.5% of anchor (envelope-consistent)
- Live chat completions (ctx 4096, enable_thinking false per weak-machine law): 27.2–31.1 tok/s interactive

## 3. coexist — needs-yield-window (honest)

- Trial ran in bare window: Ollama 7b keepwarm NOT resident; keepwarm pause valve pre-paused since **2026-09-19 10:49** (= pre-trial state; post-trial unchanged, no restore action needed to return to prior state)
- Same-card coexistence verdict: 27B PTQ1_0 (5.53 GiB VRAM full offload) + 7b (~5 GB) cannot share the 8GB card → **needs-yield-window** (bare window discipline required; valve mechanism already in force)
- Post-trial GPU restored to baseline 912 MiB used / 7107 MiB free (server self-terminated by orchestrator)

## 4. quality — 3/3 probes PASS (self-graded + verifiable keys)

| probe | lane | result |
|---|---|---|
| P1-numeric-summary | BigMoney deep-QA / research summary | PASS 7/7 keys preserved (ORANGE_COOL, 4, 0, MA200, 10, 0.77, 65%) — 45 tok / 1.5s |
| P2-first-review-lookahead | complex first-review doc (advisory, T-70 boundary) | PASS — caught `shift(-1)` future-data + correct fix — 34 tok / 1.2s |
| P3-t1-cost-arithmetic | risk/cost model arithmetic | PASS — 周二 + 26.082 bp = 13.041×2 exact — 84 tok / 2.7s |

## Conclusion (tri-state): **observe**

All four receipt pieces pass on the tight envelope; coexistence requires the bare-window discipline (needs-yield-window). Lane-level adoption as a standing local light-QA/advisory face is a resource commitment → defer to fleet CEO round (first round 2026-09-30 13:00) with this receipt as evidence; recommend **observe→adopt-candidate for local light-QA lane** given 3/3 quality, 40.75 tok/s, and the already-idle 7b face on this box. Coding production lane stays excluded per T-70.
