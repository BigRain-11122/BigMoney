# 固定声管线骨架 v1（fixed-voice pipeline skeleton · ST-003）

> 承接=VOICE-LIBRARY-EVAL-20261019.md（主选 GPT-SoVITS/备选 OpenVoice）；
> 法源=O-20261018-2144-bm-c §2.1 + DIRECTOR-STEP-GATE-v1（逐站门）+人物一致性律（声音面）。

## 站位（v0 蓝图）

1. **台词面**：episodes/EP*.json 对白行 → 按角色归并（drama-001-stockera 面板）。
2. **声银行（voice bank）**：每正典角色条目 schema = `{id, ref_clips[1-3], engine, params,
   voice_manifest{性别/年龄感/质感}, added_ts}`；入行门=同角色多参考音「音色一致检」
   （锚清洗纪律的声音面移植）+独立 lane 目录（不入 CEO 试验账本面）。
3. **TTS 批产**：逐镜音频件·确定性参数档·resume-safe·失败行隔离重试（断点续拉范式）。
4. **QC 门（三查·声音面）**：音频存在性/时长-字率带（台词长度匹配）/听感抽检（盲评位；
   不过门=打回不进装配）。
5. **装配面**：音频入集装配器（画面+对白音轨）；与 MV 音轨律不冲突——漫剧台词=剧情音·
   非 MV 歌轨面（O-20261009-1901 律域=BigStream MV 线）。
6. **车道纪律**：cpu 先行（GPT-SoVITS CPU 推理慢→夜间批产）；GPU 面=ST-002 门后评估；云端禁用。
7. **一致性法律继承**：跨集音色漂移=判负打回（受众面第一优先）。

## 与视觉面锚清洗纪律的对齐（ST-004 同窗落地）

- 视觉面=ANCHOR 三元组硬约束（发型/发色/着装）+id 银行入行前一致检（anchor_precheck.py）；
  声音面同构=voice_manifest 三描述+参考音入行前一致检——两面上位同一纪律：**入行前过检，
  行内零漂移**。
