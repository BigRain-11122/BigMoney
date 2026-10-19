# ST-012 声银行入行证据包（W012 · MANCANG v1）

> 站点=CONTENT-LOOP W012（bm-b 本地自驱池·cpu-only·2026-10-20 本轮实跑）；
> 承接=ST-012 微调回执（`content/drama/outbox/ST-012-VOICE-FINETUNE-RECEIPT.md`）§六「入行=ST-009 复检 + manifest admission」；
> 判据单源=`content/drama/runner_assets/voice_bank_entries.py`（F0 相对 ≤15% · RMS 极差 ≤8.0 dB · 谱心相对 ≤20%）——本站零重实现、零新判线；
> 只读测量：零网络、零 GPU、零音频写入；**不写 voice_bank/manifest.json**（入行执行属声银行站）。

## 一、判决

**ADMISSION-EVIDENCE-READY**

| 门 | 判据 | 实测 | 判决 |
|---|---|---|---|
| G1 跨片音色一致（ST-008 语义） | F0 ≤15%·RMS ≤8.0 dB·谱心 ≤20% | f0_dev 0.0067 · rms_spread 0.34 dB · centroid_dev 0.0317 | **pass** |
| G2 相对底嗓不塌（微调未回落通用基） | 同上阈值对底嗓 | F0 3.03% · 谱心 9.56% · RMS +7.71 dB | **pass** |
| G3 语料下限 | 行数 ≥10 且总时长 ≥45s | 13 行 / 48.6s | **pass-minimum** |
| 辅证 held-out F0 跨度 | 同一音色三次合成应聚拢 | 1.00% | 参考 |

## 二、逐片实测（底嗓=自举 ep003_l02）

| 样本 | F0 中位 (Hz) | 谱心 (Hz) | RMS (dBFS) | 相对底嗓（F0 / 谱心 / RMS） |
|---|---|---|---|---|
| 底嗓参考 | 310.6 | 1678.0 | -20.78 | — |
| holdout_01_ft.wav | 320.0 | 1616.6 | -28.43 | 3.03% / 3.66% / -7.65 dB |
| holdout_02_ft.wav | 316.8 | 1517.6 | -28.15 | 2.00% / 9.56% / -7.37 dB |
| holdout_03_ft.wav | 320.0 | 1567.8 | -28.49 | 3.03% / 6.57% / -7.71 dB |

## 三、入行清单（供声银行站执行，非本站写）

- 角色：MANCANG（满仓）·底嗓=`voice_09.wav`（ST-012 试验选择，非正典定谳）
- 微调权重：`C:\Fluxgroup\FluxGroup\media\drama-tools\GPT_weights_v2Pro\mancang-v1-e15.ckpt`
- s2 权重：`C:\Fluxgroup\FluxGroup\media\drama-tools\voice_train\st012\exp\mancang-v1\logs_s2_v2Pro\G_233333333333.pth`
- A/B 素材：`C:\Fluxgroup\FluxGroup\media\drama-tools\voice_train\st012\ab`（holdout_01..03_ft.wav）
- 语料：`C:\Fluxgroup\FluxGroup\media\drama-tools\voice_train\st012\corpus\train.list`（13 行 / 48.6s，合成 corpus）

## 四、诚实边界

- training corpus is synthetic (IndexTTS bootstrap), not human-recorded
- no human listening gate in this station (deterministic proxies only)
- proxy-level consistency, NOT embedding-level speaker identity
- voice_bank/manifest.json untouched: admission execution is a separate station
- corpus sits just above the 45s floor (48.6s): enough to validate the chain, not to ship tone
- finetuned output is 7.7 dB below the bootstrap base -- downstream mixing must normalise gain (level gate is NOT covered by this pack)

## 五、下一站

ST-009 timbre-consistency recheck (with the finetuned voice) -> voice_bank manifest admission

> 机器孪生=`results/drama_env/st012_admission_evidence.json`（同刻同源，字节确定性可再生）。
