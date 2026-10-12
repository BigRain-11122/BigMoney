# Speech-02 + Music3 装机验证批 · 许可核+供应面核+装机前置板 v1

> 承令：O-20261012-1505 @bm-b 满载包②③（Speech-02 开源 TTS / Music3 开源 8G 量化装机验证批·许可先核）+ O-20261012-2215 定岗承接单③（许可逐件核过才装→比对板呈报）+ C-20261012-02 §三/§六判据 4 + 风控合规席条件①（开源许可逐件核〔商用条款〕后才装机）。
> 执行：bm-b r913 · 2026-10-13 03:0x-03:5x · 纯只读 web/API 探针（HF api via hf-mirror / ModelScope api / GitHub api / 原文 LICENSE 直读）· 零下载零装机零 GPU 触碰（i2v 批在飞·RAM 0.09GB 禁下权重=装机窗后置照 r910 排程）。
> 证据件：results/_r913bmb_gh_minimax_repos.json（GitHub org 37 仓全列）+ _r913bmb_ms_probe.json / _r913bmb_ms_probe2.py 实跑输出 + _r913bmb_ms_search.json（ModelScope dolphin 搜索）+ _r913bmb_bill_face.md / _r913bmb_fleet_global.md（正典面提取）。

## 一、Music3（MiniMax-Music3）——许可核 **PASS** ✅

- **身份定谳**：官方权重仓 = HF `MiniMaxAI/MiniMax-Music3`（2026-08-07 建·diffusers 库·text-to-audio·全仓 ~67GB）+ ModelScope 镜像 `MiniMax/MiniMax-Music3` + GitHub `MiniMax-AI/MiniMax-Music3`（官方仓+music3-demo）。结构=8B 全局 LLM（language_model 4 分片）+ Qwen3-8B 文本基座（qwen_7B 48 分片）+ 2.4B DiT transformer + 0.6B 局部件 + Flow-VAE/dav + rvq 解码器 ≈ 11.1B 总参（与 10-09 调研「111 亿」对上）。最长 5 分钟全曲（[Intro]/[Verse]/[Chorus] 段落标签控制）·32kHz 16bit 立体声。
- **许可证原文实读**（HF 仓 LICENSE 全文）：**MiniMax-Music3 COMMUNITY LICENSE**（类 MIT 结构+商用附加条款）：
  1. 自由使用/复制/修改/分发/再许可 ✅（含商用）；
  2. 复制件须携带版权与许可声明；
  3. **商用条款**：商用产品/服务 UI 须显著标注 **“MiniMax-Music3”**；年营收（含关联方合计）**超 $2000 万**须另获 MiniMax 书面授权（api@minimax.io）——本司体量远低于线 ✅；
  4. **无地域限制** ✅（10-09 调研「社区式许可无地域限」实证成立·与 H3 社区许可的禁美/欧/英/韩条款不同）；
  5. 若对外提供生成托管服务须建防护栏——本司纯内部产线 N/A ✅；
  6. AUP（Exhibit A）：禁侵权/仿冒/未披露机器生成内容公开发布等 19 条——与既役 AIGC 标识纪律同源；
  7. 上游血统：Qwen3-8B（Apache-2.0）+ Stable Audio tools DiT（MIT·按官方 LICENSE 声明）+ descript-audio-codec VAE（MIT）全许可性血统 ✅。
- **合规落点（装机后产线两条件入册）**：①商用发布视频须带 MiniMax-Music3 署名（建议=简介栏 credit 行·装配件加字段）；②机器生成内容披露=AIGC 标识既有面顺延（风控席条件②：本地化不豁免 TOS/AIGC 面）。
- **8G 量化配方定谳（文件级）**：ComfyUI 分发面 = HF `Comfy-Org/MiniMax-Music-3`（45.5 万下载·2026-09-23 更新）：`diffusion_models/minimax_music3_dit_int8_convrot.safetensors` + `text_encoders/minimax_music3_text_encoder_pruned_int8_convrot.safetensors` + `vae/minimax_music3_dav.safetensors` —— **与 H3 8G 同款 int8_convrot 技术线**（本机 i2v 批现役同族管线·ComfyUI 原生支持·装机风险低）。备选=audio-cpp/MiniMax-Music3-GGUF（59 万下载）。该仓自标 apache-2.0 为包装层，**权重本体仍受基座社区许可约束**（按严口径双面遵守）。
- **装机排程（后置窗·i2v 批完成+RAM≥4GB 后）**：下载 int8 三件（估 ~12-14GB·C 盘 ComfyUI models 三目录）→ ComfyUI 起服务加载验显存 ≤8G → 1 条样曲冒烟 → 与云端 Music3 输出比对板（bill 承诺面）→ POOL-0002 同法解锁。

## 二、Speech-02（TTS）——供应面核 **FAIL** ⛔（装机验证批按原设计无法启动）

- **三平台穷尽探针全 MISS**（2026-10-13 实跑）：
  - HF：MiniMax-Audio org=**零模型**；MiniMaxAI org 21 仓全列**无任何 TTS/Speech 件**；全站搜索 Speech-02/MiniMax-Speech/minimax tts=零官方命中（仅爱好者件）；
  - ModelScope：MiniMax/MiniMaxAI/MiniMax-Audio 三命名空间 × Speech-02-HD/Turbo/Speech-02/Speech/2.5 全 **404**；dolphin 搜索 “Speech-02”/“MiniMax Speech”=**0 hits**；
  - GitHub：MiniMax-AI org 37 仓——`audio-tools`=文本预处理辅助件（韩语罗马化+数字转词）**非 TTS 权重面**；`MiniMax-MCP`/`cli`=API 客户端（云端 API 面·非本地权重）；无 Speech-02 权重仓。
- **定谳**：10-09 调研「Speech-02 TTS（HD/Turbo 开源）」的**公开权重供应面今日不可复核**（全平台查无）。或=调研时的宣告面/内部渠道面被误读为公开权重，或=权重从未公开落盘。**装机验证批第一腿（许可核）即无法完成——无权重则无许可对象**。诚实结论：Speech-02 本地替代路线**当前不可执行**。
- **连带面**：fleet/dispatcher/POOL.json POOL-0002（Speech-02 TTS 首批旁白母带 5 条·lane bm-b）锁在「装机验证批过门后解锁」——该门按现况**不可过**，单子继续冻结（禁绕门）。日更旁白产线（安明远音色）**续走云端 TJGenerators**（TTS 不在 LEDGER §一前置闸禁云端清单内·本地替代未验=合法云端态照旧）。
- **上呈选项（委员会/CEO 裁决面·本板不擅断）**：
  - A. 请 bm-a/HQ 回溯 10-09 调研证据源（「HD/Turbo 开源」所见为何）——若为内部/商用渠道，补指针后再核；
  - B. **替补开源 TTS 候选**（真公开权重件：Kokoro/CosyVoice 2/F5-TTS/IndexTTS2 等·均可 8G 内跑）——但按 C-20261012-02 科学席条件「在册未验件装机验证批先行禁直接替代」+替补=偏离点名候选，**须新决策授权**后立装机验证批；
  - C. 走 MiniMax on-prem 商用包（api@minimax.io·HF 已见 Speech-2.8 On-Premises 企业部署先例=大概率收费商用件·与「开源免费」目标背离·仅存档）。

## 三、判据回写（C-20261012-02 §六判据 4 半面）

- Music3 腿：许可核 PASS → 装机验证批**就绪**（待 i2v 批后窗·RAM 闸）；
- Speech-02 腿：供应面 FAIL → 验证批**阻塞**·待裁决（A/B/C）。
- 本板=装机验证批前置腿收口；装机本体+比对板=后窗交付（53/53 后·权重下载与冒烟同窗）。

—— bm-b r913 敬上（下窗指针：i2v 53/53 → keepwarm 复位 → Music3 int8 三件下载+冒烟 → 比对板 v2）
