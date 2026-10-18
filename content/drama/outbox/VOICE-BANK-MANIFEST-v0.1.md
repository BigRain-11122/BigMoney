# 声银行清单 v0.1（voice-bank manifest · ST-006）

> 站点=CONTENT-LOOP v0.1 ST-006；承=ST-003 评估件「后续批次：环境安装+首批声银行条目」；
> 正身=content/drama/voice_bank/manifest.json（本件=回执面）。生成时点=2026-10-19T03:52:01。

## 7 正典角色声音条目（voice_manifest 描述档）

| id | 性别 | 年龄感 | 质感 | 状态 |
|---|---|---|---|---|
| CH | male | early-20s | calm, restrained, quietly intense young man | awaiting-ref-clips |
| XIONG | male | 50s | deep, unhurried, authoritative magnate | awaiting-ref-clips |
| RED | female | early-20s | bright, crisp, professional office voice | awaiting-ref-clips |
| MANCANG | male | mid-20s | loud, cheerful, plump-market-vendor warmth | awaiting-ref-clips |
| XIONGWEI | male | mid-20s | cold, sharp, clipped, minimal words | awaiting-ref-clips |
| FATHER | male | 50s | weary, kind, low and worn | awaiting-ref-clips |
| BOY | male | child ~12 | thin, frightened, high-pitched | awaiting-ref-clips |

## 入行门（锚清洗纪律的声音面移植）

- 每角色 1-3 条参考音入行前过「音色一致检」；跨集音色漂移=判负打回（行内零漂移）。
- 与视觉面 ANCHOR 三元组硬约束（ST-004）同构：入行前过检，行内零漂移。

## 参考音寻源短线（离线事实·未复核许可面）

- **AISHELL-3 (SLR93)**：multi-speaker Mandarin, ~8k speakers; license = research-use caveats -- commercial drama use needs license review (honest gap)
- **aidatatang_200zh (SLR29)**：Mandarin, license review needed
- **self-recorded / CEO-provided clips**：zero license risk, physical-domain action; highest tone-fit ceiling
- **zero-shot bootstrap from a stock base voice + cross-check**：possible after env ready; consistency gate still applies

## 诚实缺口

- no ref clips yet (clip acquisition = next station, gated on ST-005 env)
- corpus licenses not yet reviewed for commercial use
- engine params pinned at the first synthesis station, not here
