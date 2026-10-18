# ST-007 首次合成冒烟回执（first-synthesis smoke · GPT-SoVITS）

> 站点=CONTENT-LOOP v0.1 ST-007（r1016 轮升格 r1017 首动作·声库车道 P1 ≤10-22）；
> 环境=ST-005 GPT-SoVITS 全六相位 done @gpt_sovits_env done 6/6 @2026-10-19T04:11:25（CPU 车道·VOICE-PIPELINE-SKELETON-v1 §6）；
> 时点=2026-10-19T05:58:13。云端零调用（429 经济）。

## 冒烟结论：零样本推理链 PASS

- **参考音 → 音色克隆 → 目标文本合成 → wav 产物 → 确定性校验** 全链走通。
- 产物=`C:\Fluxgroup\FluxGroup\media\drama-tools\voice_smoke\st007\out\output.wav`（时长 4.42s·采样率 32000Hz·RMS 0.0105·282924 bytes）。
- 推理耗时 26.2s（CPU fp32·v1 预训练对：s1bert25hz-2kh-longer-epoch=68e-step=50232.ckpt + s2G488k.pth）。

## 参考音来源（寻源披露）

- 选用=**本仓自产 r998 结构试音素材**（`ep002_line04`·角色「长」·3.42s·文本『我在上班。你到底想干嘛？』）。
- 与声银行短线（ST-006 manifest ref_clip_sourcing_shortlist）的关系：本路线=短线中
  「self-recorded / 自产素材」档的落地版——盘上已有真实普通话对白素材（r998 试音产物·
  零许可风险·逐行文本可从 MANIFEST-r998.json 机读·试音零硬旗件），优先于外部语料
  （AISHELL-3 许可面未审·留作正式声银行站的后续选项）。
- 参考音挑选判据：AUDITION-r999 硬/软/节拍旗零命中 + 单说话人 + 3-10s 窗 + 文本无长破折号。

## 冒烟边界（如实）

- 本站=**链路验证**，非音色定稿：冒烟参考音不是正典角色声银行条目，
  `content/drama/voice_bank/manifest.json` 各角色 ref_clips 仍为空（正式寻源站待开）。
- 输出未经人耳听感门（听感抽检=后续 QC 站的活）；本站校验面=确定性三查
  （存在性/时长-字率带/静音 RMS 门）。
- 音色一致检（入行门）未跑——冒烟产物不写声银行、不入 CEO 面。
- 环境补丁披露（推理首跑暴露 env 冒烟面只验 import 未验 load 的潜伏缺口，本站幂等修复）：
  ① env deps 相位剥离 jieba_fast（sdist 需 MSVC·无该工具链）→ site-packages 别名 shim
  （jieba_fast→纯 Python jieba·分词慢 2-4 倍·CPU 车道可接受）；
  ② torchaudio 2.11 移除传统音频后端、load() 硬依赖 torchcodec+FFmpeg shared DLL（本机无 DLL 面，
  torchcodec 轮子装了链不上）→ 推理相关 5 文件 9 调用位 marker 守卫包裹 `_bmb_ta_load`
  （先走原生、异常回退 soundfile·py_compile 全绿）——smoke 与 api_v2 批产双车道一次修族；
  ③ match_librosa 重采样路径依赖 resampy（repo requirements 未含）→ pip 幂等补装；
  状态面 env_shim/audio_loader_patch/env_pip 字段留证，修复配方版本化于本 runner 资产件可复跑。
- 产物件位于 gitignored media 区（CEO 交付律）；本回执+状态面=入 git 证据。

## 下一步（CONTENT-LOOP 后续站位）

- 正典声银行条目站：每角色 1-3 条参考音（优先继续挖 r998 自产素材对齐角色·缺口再走外部语料）
  + 音色一致检入行；GPT-SoVITS 微调面（每角色 LoRA/ckpt）评估。
- 批产站：逐镜 TTS 批产 runner（resume-safe·失败行隔离）+ QC 门三查接线。
