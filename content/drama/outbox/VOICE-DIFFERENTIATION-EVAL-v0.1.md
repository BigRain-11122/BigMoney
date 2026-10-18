# 角色音色差异化评估 v0.1（VOICE-DIFFERENTIATION-EVAL · ST-009）

> 站点=CONTENT-LOOP ST-009；承接=ST-008 入行回执「共享底嗓债」披露面；
> 数据正身=content/drama/voice_bank/manifest.json（入行片级 F0/RMS/谱心证据）；
> 本件=评估回执。时点=2026-10-19T07:44:42+08:00。车道=cpu；零云端；纯确定性测量零判据触碰。

## 一、共享底嗓债实测（音色一致检 v0.1 同族口径）

判据：跨角色 F0 相对差 ≤15% 且谱心相对差 ≤20% = 同嗓带（same-voice-band）。

| 角色A | 角色B | 底嗓 | F0相对差 | 谱心相对差 | 判读 |
|---|---|---|---|---|---|
| CH | FATHER | 异族 | 32.4% | 2.0% | 可分 |
| CH | RED | 异族 | 58.4% | 19.8% | 可分 |
| CH | XIONG | 异族 | 40.3% | 12.4% | 可分 |
| CH | XIONGWEI | 异族 | 40.4% | 6.6% | 可分 |
| FATHER | RED | 异族 | 38.4% | 21.3% | 可分 |
| FATHER | XIONG | 同族 | 11.6% | 10.6% | 同嗓带 |
| FATHER | XIONGWEI | 同族 | 11.9% | 4.7% | 同嗓带 |
| RED | XIONG | 异族 | 30.3% | 29.7% | 可分 |
| RED | XIONGWEI | 异族 | 30.1% | 25.0% | 可分 |
| XIONG | XIONGWEI | 同族 | 0.3% | 6.2% | 同嗓带 |

同嗓带对数=3。voice_07 三人组（XIONG 170.9Hz / XIONGWEI 171.4Hz / FATHER 151.0Hz）：XIONG-XIONGWEI 相对差仅 0.3%——声学上同一把嗓子，债成立且可测。

## 二、音高分档方案（确定性搜索·最小总移位）

搜索约束：XIONG（50s 威严老板）≤0 半音；XIONGWEI（20s 儿子）≥0；FATHER（50s 疲惫慈父）≤0；
目标=组内所有对 F0 相对差 ≥15%（出同嗓带）；优化=最小化总移位（DSP 失真最小）。

| 角色 | 现测 F0 中位 | 分档移位 | 投影 F0 |
|---|---|---|---|
| XIONG | 170.9 Hz | +0 st | 170.9 Hz |
| XIONGWEI | 171.4 Hz | +3 st | 203.8 Hz |
| FATHER | 151.0 Hz | -1 st | 142.5 Hz |

投影后组内对：
- FATHER–XIONG：F0 相对差 16.6%（≥15% 达标）
- FATHER–XIONGWEI：F0 相对差 30.1%（≥15% 达标）
- XIONG–XIONGWEI：F0 相对差 16.2%（≥15% 达标）

执行载体=合成后 DSP 变调（librosa pitch_shift 族·保共振峰），±3st 内为安全区；
保共振峰移位只动 F0——分档的分离轴=F0（谱心留在原带，见诚实边界）。

## 三、方法可行性表

| 路径 | 可行性 | 判读 |
|---|---|---|
| 合成后 DSP 变调分档 | 本窗可落 | voice_07 家族首选：零新素材、确定性、±3st 安全区；下一站=分档试合成实测 |
| GPT-SoVITS 逐角色微调 | 对同底嗓无效（诚实负发现） | 微调加深底嗓同一性——同族分离靠它=方向错误；微调只服务「新源说话人」 |
| 换源寻根（新底嗓素材） | 根解 | BOY（童声）/MANCANG（市井喜感）寻源站天然带新底嗓；寻源选片须避开 voice_04/05/07/12 现役底 |
| 组内既有参考片挑片 | 已实测不足 | 组内片本来同底同近 F0——挑片无法制造分离（本表第一行的实测依据） |

MANCANG 定位提示：其底嗓债是与旁白共享 voice_05——但入行素材全 CLIPPED 未入行，
差异化随寻源站自然解决（寻源即选新底嗓），无需 DSP 分档。BOY 同理（童声源天然异底）。

## 四、诚实边界

- F0/RMS/centroid proxy only; embedding-level timbre identity = future station
- FATHER median from a single clip (fragile; re-supply station pending)
- formant-preserving DSP moves F0 only; centroid band stays (F0 band is the separating axis)
- fine-tune on same-base (voice_07) material cannot separate the family -- root fix is distinct source voices
- RMS loudness re-match required after DSP shift at the synthesis station

## 五、后续站位（建议）

- ST-010 分档试合成站：XIONG/XIONGWEI/FATHER 各 1 句过 GPT-SoVITS + 分档移位，复测 F0 分离达标与人耳抽检面。
- ST-011 BOY/MANCANG 寻源站（许可面先审）：BOY 童声（许可红线先审）+ MANCANG 去削波再产/新源。
- 嵌入级音色同一性检=后续站（本评估=F0/谱心代理面）。

