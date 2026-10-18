# 正典声银行条目 v0.1（canon voice-bank entries · ST-008）

> 站点=CONTENT-LOOP v0.1 ST-008（r1017 指针件 2·声库车道 P1 ≤10-22）；
> 承接=ST-006 manifest v0.1（条目 schema+入行门规格）+ ST-007 链路验证 PASS；
> 正身=content/drama/voice_bank/manifest.json（本件=回执面）。时点=2026-10-19T06:20:58。
> 车道=cpu；云端零调用（429 经济）。选片+分析耗时 0.2s。

## 入行结论：5/7 角色参考音入行（音色一致检 v0.1）

- 入行判据=选片律（AUDITION-r999 硬/软/节拍旗零命中+单说话人+ok+1.5-10s 窗+3.5s 甜点距排序）
  + 音色一致检 v0.1 确定性代理门（跨片 F0 相对差 ≤15%·RMS 极差 ≤8dB·谱心相对差 ≤20%）。
- 素材=**本仓自产 r998 结构试音件**（零许可风险·逐行文本机读·真实普通话对白）——
  manifest 寻源短线「self-recorded/自产素材」档的落地；外部语料（AISHELL-3）许可面仍留待后续站。

| 角色 | r998 对齐 | 入行片数 | F0 中位 (Hz) | 门 |
|---|---|---|---|---|
| CH | 长->protagonist | 3 | 106.0 | pass |
| XIONG | 熊->villain | 3 | 165.8 | pass |
| RED | 红利->reporter female | 2 | 239.7 | pass |
| MANCANG | 满仓->comic happy6 | 0 | 多片见正身 | no-material |
| XIONGWEI | 熊伟->villain-son | 2 | 162.8 | pass |
| FATHER | 父->father | 1 | 151.0 | pass-single-clip-vacuous |
| BOY | - | 0 | 多片见正身 | no-material |

## 逐角色入行明细（clip 级证据在 manifest 正身）

- **CH**（3 片·pass）：ep003_line19、ep002_line04、ep001_line10。
- **XIONG**（3 片·pass）：ep003_line06、ep002_line18、ep002_line15。
- **RED**（2 片·pass）：ep003_line04、ep003_line03。
- **XIONGWEI**（2 片·pass）：ep002_line12、ep003_line07。
- **FATHER**（1 片·pass-single-clip-vacuous）：ep001_line02。
- **MANCANG**：EP001-003 的 7 条满仓行全部带 AUDITION 硬旗 CLIPPED（无干净片）——**诚实缺口不入行**，寻源=后续站（自录/CEO 提供/带许可审的外部语料）。
- **BOY**：EP001-003 无儿童声行素材——**诚实缺口不入行**，寻源=后续站（自录/CEO 提供/带许可审的外部语料）。

## 诚实边界

- **共享底嗓债**：XIONG/XIONGWEI/FATHER 三角色在 r998 全部由 voice_07 底噪渲染（F0 构造性
  近同·熊家父子=族内共享系合理）；MANCANG 与旁白共享 voice_05 底。差异化=后续参数/微调站
  （full-episode casting 前必须解）。
- 单片角色（FATHER）过检=「单片空真」档：行内有 1 条干净素材、无跨片可检面——补片=后续批素材扩产。
- 音色一致检 v0.1=确定性代理（F0/RMS/谱心），非说话人嵌入级音色同一性检——嵌入级门=后续站。
- 入行参考音未经人耳听感门（听感抽检=QC 站的活）；r998 试音旗标 25 行 CLIPPED 件已按律排除。

## 下一步（CONTENT-LOOP 后续站位）

- BOY 参考音寻源站（儿童声·许可面先审）+ 单片角色补片（新批台词/去削波再产）。
- 角色差异化站：voice_07/voice_05 共享底嗓的参数分档或 GPT-SoVITS 微调面评估。
- 批产站：逐镜 TTS 批产 runner（resume-safe·失败行隔离）+ QC 门三查接线（入行参考音为本站产物）。
