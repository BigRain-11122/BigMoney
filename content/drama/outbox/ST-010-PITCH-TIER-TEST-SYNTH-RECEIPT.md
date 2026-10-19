# ST-010 分档试合成回执（pitch-tier test-synthesis · voice_07 家族）

> 站点=CONTENT-LOOP v0.1 ST-010（r1020 指针件 1 首动作·r1019 债·声库车道 P1 ≤10-22）；
> 承接=ST-009 分档方案；正身=results/drama_env/pitch_tier_test_synth.json；本件=回执面。
> 时点=2026-10-19T11:00:03。车道=cpu；云端零调用；文本受控设计=三角色同句『成交量不会说谎，人心才会。』。

## 核心发现（本站主产出）

**零样本同句合成会把三角色 F0 全部拉平**（文本驱动韵律盖过参考音音高）：

| 角色 | 参考音 F0 | 合成原样 F0 | 拉平方向 |
|---|---|---|---|
| XIONG | 165.8 Hz | 173.5 Hz | 上漂 |
| XIONGWEI | 162.8 Hz | 172.0 Hz | 上漂 |
| FATHER | 151.0 Hz | 177.8 Hz | 上漂 |

合成原样对 F0 相对差=0.9%/2.4%/3.3%——**共享底嗓债在合成面上比参考音面更深**（同嗓带），且 ST-009 按参考音 F0 冻结的分档（{"XIONG": 0, "XIONGWEI": 3, "FATHER": -1}）在合成面上投影不足（门判=FAIL）。

## 二段法：合成面重分档 + 校验-调整环（ST-009 tier_search 同律复用）

stage2 在合成原样 F0 上重跑确定性分档搜索（方向约束 XIONG≤0/XIONGWEI≥0/FATHER≤0·最小总移位）；
因名义半音≠实测半音（DSP 后 F0 中位偏离几何投影），搜索结果过**校验-调整环**：
实测复测→未达标对按方向律+搜索域扩 1 半音→复测（≤3 迭代·确定性·全程留痕）。

| 角色 | 合成原样 F0 | 搜索移位 | 调整环终档 | 投影 F0 | 实测分档后 F0 | RMS 复配（dBFS） |
|---|---|---|---|---|---|---|
| XIONG | 173.5 Hz | +0 st | +0 st | 173.5 Hz | 173.5 Hz | -26.4 → -26.4 |
| XIONGWEI | 172.0 Hz | +3 st | +3 st | 204.5 Hz | 205.1 Hz | -27.9 → -27.9 |
| FATHER | 177.8 Hz | -4 st | -5 st | 141.1 Hz | 139.4 Hz | -29.2 → -29.2 |

校验-调整环轨迹：
- 迭代 0：offsets={"XIONG": 0, "XIONGWEI": 3, "FATHER": -4} → 实测对 15.4%/15.0%/28.1% → 未达标→续调
- 迭代 1：offsets={"XIONG": 0, "XIONGWEI": 3, "FATHER": -5} → 实测对 15.4%/19.7%/32.0% → 全对达标

## 分离矩阵（同嗓带判据：F0 相对差 ≤15% = 同嗓带）

| 角色对 | 合成原样（债面） | stage1 冻结分档 | stage2 重分档 | 判读 |
|---|---|---|---|---|
| XIONG–XIONGWEI | 0.9% | 15.4% | 15.4% | 达标（出同嗓带） |
| XIONG–FATHER | 2.4% | 6.6% | 19.7% | 达标（出同嗓带） |
| XIONGWEI–FATHER | 3.3% | 21.0% | 32.0% | 达标（出同嗓带） |

**门判=PASS**：stage2 重分档后组内所有对 F0 相对差 ≥15% 判据 全对达标（总移位 8 st·最大 |移位| 5 st）。

## 诚实边界

- KEY FINDING: zero-shot same-text synthesis homogenizes F0 register toward text prosody (raw synth XIONG/XIONGWEI/FATHER all ~172-178Hz despite ref F0 165.8/162.8/151.0) -- ref-clip-derived tier offsets do NOT transfer to synthesized outputs; tier must be derived per synthesis chain (this station = stage-2 re-tier), and the batch station must re-verify separation per line (per-line F0 drift)
- nominal semitone != measured semitone on real speech (DSP-shifted F0 median deviates from the geometric projection: FATHER -4st nominal -> ~-3.5st measured) -- separation gates must verify on MEASURED outputs (the station verify-adjust loop), not on projections; this loop is the batch-station method prototype
- librosa pitch_shift = phase-vocoder + resample: formants move with F0 (not strictly formant-preserving; corrects the ST-009 wording); the +/-3 st safe zone applies to DSP distortion risk
- F0/centroid proxy only (autocorr metric family); embedding-level timbre identity = future station
- single-line sample per character (1 sentence); multi-line robustness = batch-production station
- ear-check (human listening spot-check) NOT run at this station -- queued for the QC gate; this station = deterministic acoustic gate
- XIONG offset +0 st = raw baseline passthrough (RMS re-match identity)
- FATHER single admitted clip 2.31s padded to 3.05s with tail silence to clear the engine 3-10s ref gate (no clean alternative material per ST-008; re-supply station pending)
- re-tier max |offset| = 5 st exceeds the +/-3 st DSP safe zone (min-total solution under direction constraints; ear-check weight rises; root fix remains distinct-source re-supply -- ST-011/ST-009 sec.3)

## 产物面（gitignored media 区·CEO 交付律）

- XIONG：合成原样=`C:\Fluxgroup\FluxGroup\media\drama-tools\voice_smoke\st010\XIONG\out\output.wav`；冻结面分档=`C:\Fluxgroup\FluxGroup\media\drama-tools\voice_smoke\st010\XIONG\tier_frozen.wav`；交付分档=`C:\Fluxgroup\FluxGroup\media\drama-tools\voice_smoke\st010\XIONG\tier.wav`
- XIONGWEI：合成原样=`C:\Fluxgroup\FluxGroup\media\drama-tools\voice_smoke\st010\XIONGWEI\out\output.wav`；冻结面分档=`C:\Fluxgroup\FluxGroup\media\drama-tools\voice_smoke\st010\XIONGWEI\tier_frozen.wav`；交付分档=`C:\Fluxgroup\FluxGroup\media\drama-tools\voice_smoke\st010\XIONGWEI\tier.wav`
- FATHER：合成原样=`C:\Fluxgroup\FluxGroup\media\drama-tools\voice_smoke\st010\FATHER\out\output.wav`；冻结面分档=`C:\Fluxgroup\FluxGroup\media\drama-tools\voice_smoke\st010\FATHER\tier_frozen.wav`；交付分档=`C:\Fluxgroup\FluxGroup\media\drama-tools\voice_smoke\st010\FATHER\tier.wav`

## 下一步（CONTENT-LOOP 后续站位）

- 批产站接线：分档必须在合成面上逐行验证（每行 F0 漂移不同=固定移位不保分离·逐行复测+自适应）。
- ST-011 BOY/MANCANG 寻源站（童声/市井底嗓·许可面先审；天然异底=根解路线）。
- 人耳抽检面（QC 门三查之一）+ 嵌入级音色同一性检=后续站。

