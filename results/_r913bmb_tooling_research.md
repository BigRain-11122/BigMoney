# 短视频生产管线·开源件调研（TOOLING-RESEARCH · 2026-10-10）

- 判据：开源「短视频自动生成/爆款管线」哪些部件值得接入自有管线（选题→设计案→评审→TJGenerators→assemble_meme.py→发布）；硬约束：Windows+PS5.1 计划任务、无 docker；TTS/音效/BGM/图生视频/装配已自有——只补缺不重复
- 方法：纯 web 调研（零内部文件、零 clone）；GitHub REST 仓档+README 直读=A 源，技术媒体=B/C 源；stars/许可/末次提交均出自仓档（2026-10-10 读）；未验细节标 🟡
- 链路覆盖记法：选题/文案/TTS/素材/字幕/合成/发布（✓有 △部分 ✗无）

## 项目评估（9 项）

### 1. MoneyPrinterTurbo · harry0703 · ⭐129.4k · MIT · Python · 末推 2026-10-10（当日仍在提交）
链路：文案✓(10+LLM及统一网关) TTS✓(Edge免费/Azure/MiniMax等) 素材✓(Pexels/Pixabay/本地+文生视频) 字幕✓ 合成✓(moviepy+ffmpeg) 发布✓(TikTok/IG/YT Shorts 自动上传) 选题△(关键词入)｜Win✓ 官方一键启动包(start.bat·Py3.11·GPU非必需) 无 docker 可跑
拆借：跨平台发布器、文案 prompt 库、素材源 API 封装｜冗余：TTS/素材/合成与自有件高度重叠→整链不引入、只拆件｜判负注记：原版 MoneyPrinter（harry0703 与 FujiwaraChok）两仓 404=已并入本仓｜源 https://github.com/harry0703/MoneyPrinterTurbo
### 2. pyJianYingDraft · GuanYixuan · ⭐4.5k · Apache-2.0 · Python · 末推 2026-09-26
链路：字幕✓(.srt 导入批量排版) 合成△(生成剪映草稿+驱动剪映客户端批量导出成片) 余✗｜Win✓ pip 装(Py3.8/3.11)；批量导出走 uiautomation、仅 Windows 可跑、官方建议夜间闲时执行——与 PS5.1 计划任务机队天作之合
拆借：整库直用——时间线 JSON→剪映草稿（花字/气泡/贴纸/转场/关键帧/滤镜/模板模式替换素材与文本），与 capcut-edit skill 互补（彼=改已有工程，此=从零生成+批量出片）｜硬约束：剪映6+ 加密 draft_content.json、7+ 隐藏控件→客户端须锁 5.x–6.x；同作者 pyCapCut(CapCut 版) 开发中🟡｜源 https://github.com/GuanYixuan/pyJianYingDraft
### 3. auto-editor · WyattBlue · ⭐5.5k · Unlicense · Nim(pip 分发) · 末推 2026-10-10
链路：合成前粗剪单点（静音/静止帧检测自动剪除、导出 Premiere/Resolve/FCP 时间线）余✗｜Win✓ pip 单 CLI 即装即用、无 docker（官网 B 源）
拆借：装配前自动去废帧/去静音前处理，直接挂 assemble_meme.py 上游｜冗余：无（我们缺自动粗剪件）｜源 https://github.com/WyattBlue/auto-editor
### 4. FunClip · modelscope · ⭐6.4k · MIT · Python · 末推 2026-10-08（v2.1.0 于 2026-07 首次版本化发布·B 源）
链路：字幕✓(FunASR Paraformer 转录·字级时间戳) 切片✓(按文本段/说话人 CAM++/LLM 选段) 合成✗ TTS✗｜Win✓ 本地部署（Windows 部署指南·C 源；模型较重）
拆借：Paraformer 字级时间戳+LLM 选段→「长视频自动切片器」，长素材→切片喂管线｜线索修正：非 B 站出品，系阿里通义 FunASR 系（OpenBMB 旧路径 404→现仓 modelscope/FunClip）｜源 https://github.com/modelscope/FunClip
### 5. NarratoAI · linyqh · ⭐11.4k · MIT · Python · 末推 2026-09-17
链路：解说类：文案✓(LLM) TTS✓ 素材✓(本地素材库/Pexels 语义匹配🟡) 字幕✓(whisper🟡) 合成✓(moviepy·topics A) 发布✗｜Win：Python 可跑（部署细节🟡）
拆借：解说词↔镜头语义对齐逻辑、字幕对齐｜价值=「解说视频」新类目工艺参考｜冗余：TTS/合成重叠｜源 https://github.com/linyqh/NarratoAI
### 6. ShortGPT · RayVentura · ⭐8.0k · MIT · Python · 末推 2025-02-10（停滞≈20 个月）
链路：文案✓ 素材✓(网络检索下载🟡) 字幕✓ 合成✓(Asset/时间线抽象引擎) TTS△🟡 发布✗（功能集为仓档自述+社区转述·B/C）｜Win：pip 可装🟡
拆借：仅参考其 Asset/时间线抽象（对 assemble_mime 的 JSON 结构演进有启发）｜冗余：全链重叠｜源 https://github.com/RayVentura/ShortGPT
### 7. OpenCreator（原 KrillinAI）· krillinai · ⭐12.7k · Apache-2.0 · TypeScript(桌面 App) · 末推 2026-10-10
链路：翻译✓(100+语言·B/C 源) 配音✓(TTS/语音克隆) 字幕✓ 合成△(多平台画幅适配：抖音/小红书/B站/视频号/TikTok/YT) 发布△🟡｜Win✓ 跨平台桌面 App，但重、不宜无人值守挂计划任务
拆借：出海多语配音+平台适配清单思路｜冗余：TTS/字幕与自有件重叠、TS 栈集成成本高→暂不接｜源 https://github.com/krillinai/OpenCreator
### 8. TikTokDownloader · JoeanAmier · ⭐16.6k · 许可🟡 · JavaScript · trending 中文区本月+916（2026-10 读）
链路：管线外挂件——抖音作品/数据采集→选题对标喂料 余✗｜Win✓ 多形态分发🟡
拆借：对标账号数据源（选题端输入）｜风险：平台 ToS 灰区，引入前过合规评审｜源 https://github.com/JoeanAmier/TikTokDownloader

## 采纳建议 Top5（按落地价值·档=直接用/需改造/仅参考）
1. pyJianYingDraft【直接用】：管线时间线→剪映草稿+夜间批量导出，补齐「精装成片」（花字/转场/模板）能力，与 capcut-edit 双件合璧；先锁剪映 5.9/6.x 实测
2. auto-editor【直接用】：装配前自动粗剪（去静音/废帧），pip 即插即用，Unlicense 零义务
3. MoneyPrinterTurbo【需改造】：只拆跨平台发布器（TikTok/IG/YT Shorts 自动上传）+文案 prompt 库+素材 API；整链不引入
4. FunClip【需改造】：改造为长视频→切片器（Paraformer 字级时间戳+LLM 选段），作 assemble_meme 前置
5. TikTokDownloader【需改造】：对标数据采集喂选题端；合规评审先行（ToS 灰区）
落选注记：NarratoAI=解说类目立项再评；ShortGPT=停滞、仅参考架构；OpenCreator=出海立项再评

## 验证声明
- 读数：有效外部读取 20 次（GitHub REST/仓档 A 级 11、README 全文 2、web 搜索 B/C 4、trending 2、404 判负直验 4）；零内部项目文件、零 clone
- 判负与重定位（均 API 404 直验）：harry0703/MoneyPrinter 与 FujiwaraChok/MoneyPrinter→已并入 MoneyPrinterTurbo；OpenBMB/FunClip→modelscope/FunClip（CEO 线索「B站开源」修正为阿里通义系）；Slihao/JianYingDraft 系 0 星分叉→正主 GuanYixuan/pyJianYingDraft；scruel/pyJianYingDraft 记忆线索证伪
- 失败面：GitHub MCP search_repositories 本会话解析故障→全程改走 api.github.com/仓页直读；README 经分叉镜像读取（内容同构上游）｜🟡待证：NarratoAI whisper、ShortGPT TTS、TikTokDownloader 许可、pyCapCut 进度、剪映6+ 草稿解密（官方 README 悬赏中）
- 应用表：落点=装备决策呈报→短视频产线引入决策（Top5 各件可独立立项）
