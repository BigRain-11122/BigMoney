# R-20261008-mv-ai-premium-craft-01 — AI 生成高级质感 MV 镜头工艺深研（第六波·CEO 令 P-2026-10-08-05 十七追加令）
> 溯源：ledger P-2026-10-08-05（CEO 原话「好好研究如何用AI生成高级质感的MV镜头…油腻感，掉帧感，镜头感等都非常差劲…在本地系统能力范围内解决」）·消费方=BigStream mv0001 产线 v3.1（S0 关键词定稿/S2 段落表/S3 生成参数/S4 关键帧）·判据预注册=四问（三病根治+本地管线 spec v1）
> 域边界：本件=AI 生成技术质感（提示词体系/插帧/超分/模型选型参数）；镜头语法/剪辑图/FFmpeg 调色链=第四波在飞件；时代语言=第五波禁碰。内部锚已先读禁重复：R-20260930-video-models-01（LTX 主选+提示词词序律+RIFE MIT 免依赖位）、R-20261008-aistream-pipeline-02（模型谱系）、R-20261008-2dlive-alternatives-00/03（HunyuanVideo-1.5 Territory 判废留痕+「只留可用帧」三步闸）、R-20261008-mv-elevate-method-01（B站修复保味律）、mv-directors-01（minterpolate 慢插帧语法）。
> 验证声明：外部调用 20/20 封顶。A 级=api.github.com 六仓直读（2026-10-08 星数/许可/末推全量）+仓内已验件；B 级=Hailuo 反提示词方法论页/unifab 插帧指南（厂商页直读·方法论面采信）；C 级=CSDN 运镜长文（跨 5 工具实测·直读前 7000 字符）/fluxvine 电影感教程（直读全量）/videoai·lovart·minimaxh3·openvideomaker·头条·搜狐（DDG 摘要级）。失败面如实录：MCP GitHub 搜索 ×2 解析故障（与 aistream-02 同症·转 api.github.com 补齐）；api.github 首轮 3 仓 JSON 尾段截断（补读齐）；toutiao 深读正文 0 字节（反爬·降摘要级）；抖音/B站/知乎正文 JS·登录墙（标题+摘要级取用）；公众号直采未及（预算尽·CN 社区面由 CSDN/知乎/头条摘要覆盖）。三态=确认/推测/待证；数字全带出处。

## 一、油腻感：根因四柱与根治三件【根因与根治=确认（B/C 多源+仓内互证）】
- 根因四柱：①过饱和+激进 HDR=廉价智能手机味≠35mm 胶片（B·Hailuo 反提示词页直读）②过度平滑塑料皮肤+"symmetrical perfection"假人感=AI 伪影首要标记（同 B；知乎 C 摘要同向「画面过度完美」）③平光呆板阴影/荧光灯感（同 B）④美学模板化：堆「cinematic/epic/stunning+film grain」=「orange and teal soup」橙青糊汤（C·videoai.me DDG 摘要）、「电影感」是 AI 听过一百万次的形容词已学会忽略，有效的是镜头运动/景别/光线方向等具体视觉语言（C·lovart DDG 摘要）。仓内互证：B站 4K 修复「保味律」——AI 过度拉平滑磨掉颗粒=粉丝「回拒」（elevate-method-01·B/C 双源）。
- 根治三件：①**结构律**（C·CSDN 直读）：六模块句式〔镜头运动+速度幅度+主体动作+场景环境+光线氛围+画质风格〕·运镜词放句首吃注意力权重·前三模块不省。②**负面词模块化**（B·Hailuo 直读）：人物模块 "plastic skin, wax figure, mannequin, over-smoothed texture, airbrushed, symmetrical perfection"；光影模块 "fluorescent lighting, flat shadows, over-exposed highlights, HDR, oversaturated colors"；完整性模块 "morphing textures, jittery motion"；**比例律=负面词占全文 20-30% token**（过短无压制力·超 40% 饿死创造性致纹理糊）；模糊词禁用（"ugly/bad"→换技术词 "oversharpened, digital noise"）。**红线注记：蒸馏档 guidance=1.0 时负词失效（in-house diffusers 文档·A）→负词体系只对 CFG>1 档生效**。③**后置质感层**（C·fluxvine 直读·与保味律双源）：grain 用专用胶片颗粒 overlay 非简单噪声·粒径匹配介质（35mm 细粒）·Overlay/Soft Light 混合·透明度 20-40%·「感受到而非看到」·超分与编码压缩会磨掉颗粒→**grain 必须在管线最后补**（压缩后再轻 grain pass 回补）。

## 二、掉帧感：诊断三分律+插帧件口碑+帧率策略【确认（B 主源+A 级数据·机制项标推测）】
- **诊断三分律**（B·unifab 直读）：掉帧感三兄弟先分诊再下药——choppy=帧数量不够（单帧锐利但运动步进·"a pan judders; fast action strobes"）→插帧；flicker=帧间不一致（纹理沸腾/亮度脉动·逐帧暂停看各自都好）→**deflicker pass 而非插帧**；blur=帧内软→超分增强。核心判词：**「掉帧感是帧数量问题，不是帧质量问题」**（"quantity of frames problem, not a quality of frames problem"）；诊断法=逐帧步进检查。
- **本地插帧件口碑**【A·api.github.com 2026-10-08】：hzwer/Practical-RIFE=1,028★·MIT·2026-08-27 仍在推（活跃）RIFE 主线源码；nihui/rife-ncnn-vulkan=1,108★·MIT·独立 exe 免重依赖（2024-01 后稳态）=批处理轻量位；n00mkrad/Flowframes=2,058★·GPL-3.0·2026-05 活跃=Windows GUI（RIFE CUDA/NCNN·24/30→60/120fps·flowframes.app 官宣 Windows 10/11 免费）；**google-research/FILM=3,154★·Apache-2.0·archived=true（2024-08 末推）=判弃**。
- **帧率策略**：①本地三模型原生 24fps（LTX 121f@24fps=5s·Wan 720p@24·in-house A）→成片 24fps 直用不补帧（2001 胶片感正对口）。②**插帧拉满 60/120fps=「soap-opera effect」过顺反成新型 AI 味**（B·unifab）——慢动作段才插到 48/60 再 setpts 慢放（unifab B+in-house 邝盛 minterpolate 慢插帧语法·双源确认）。③8-16fps 源（CogVideoX 类）才启用 RIFE 补 24（in-house 待证位触发条件）。④管线序=插帧在前·超分最后（"resolution is added last"·B 单源→A/B 对打留待证池）。⑤AI 帧帧锐利无快门模糊→24fps 高速运动会频闪=掉帧感一源（机制推测）；甩镜是自带动态模糊的唯一例外（C·CSDN）；180° 快门模糊补层=第四波 FFmpeg 域。⑥快速/遮挡运动插帧易 ghosting/warping（B·unifab）→运镜幅度收小（运动幅度参数 5-7/10·超 8=边缘扭曲·CSDN C 直读）。
- **模型质感配置**（先读件深化·不重复谱系）：LTX-0.9.8-13B-distilled=蒸馏 4-10 步**取上带 8-10 保时序连贯**+guidance 1.0+121f/5s 段（in-house A）；HunyuanVideo-1.5=8.3B 蒸馏 480P I2V 8-12 步（可 4）+FP8+cache 推速+4090 单卡 75s+6GB 社区地板（in-house A）**但 Territory 法务红线判废留痕在案（2dlive-00 防线二 LICENSE 直验）→PRODUCTION.md S3「恢复后主径」须法务复核通过才可转正**；Wan2.2-5B GGUF Q4（Apache）=bm-c 16GB 重验台（in-house·质感档 steps/cfg 待证）。

## 三、镜头感：运镜语法核心律+首帧锚图分工+段间连续【确认（C 多源互证+A 级内锚）】
- **运镜语法核心律**（C·CSDN 跨 5 工具实测直读+多 C 源互证）：①AI 不懂摄影物理只认文本-像素统计关联→**近义词组合拳**（一动作多线索："camera moves forward into the scene"+"the scene gets closer and closer"）。②**镜头运动与主体运动分两句写**（最深的坑：动词融合=混合怪运动——"Camera dolly in, a man running..."而非"dolly in and man running"；in-house LTX 卡例相机句独立·双源）。③速度副词紧随镜头词（"Camera slowly pushes in toward…"＞句尾放速度）。④起幅落幅显式（"from wide shot to close-up"减中途变形跳跃）。⑤dolly in=物理推·透视真实·呼吸感；zoom in=变焦推·背景压缩·冲击力——**电影感优先 dolly**。⑥摇镜翻车率高→"camera pan"不裸用 "pan"+"camera stays in place"（in-house LTX "camera remains stationary"·双源）。⑦环绕角度越小越可控（"slight orbit"≫360°·大环绕人脸畸变率直线上升；大幅环绕/跟拍/升降会「暴露未见场景结构」迫使模型脑补=minimaxh3 C 摘要同向）。⑧手持呼吸感="轻微、受控的微幅晃动"（禁只写"很有动感"·openvideomaker C 摘要）。⑨甩镜="fast whip pan"自带转场+动态模糊。⑩情绪化落幅："缓缓推近人物含泪的眼眸"＞"推镜头"（头条 90 词实测 C 摘要：「不是AI不懂镜头，是我们没给它说人话」）。⑪同一提示词跨模型差异大→同镜多跑选优+**seed 锁定·迭代只改对应字段**。
- **首帧锚图分工**【确认·A/B 双源】：图=构图+身份硬条件（in-house LTX image= 条件 A）；「I2V 以高质量静帧打底显著降低负词工作量·构图已锚」（B·Hailuo）；提示词只管运动+氛围（in-house 词序律）。
- **段间运动连续性**：①转场感拉镜=起点终点两个画面都写出+“revealing/turning into”连接（CSDN C 直读）。②跨片段漂移=LTX 官方自认「规模化实用的实际障碍」→四件套（参考图条件+IC-LoRA+LoRA+多片段工作流·in-house 2dlive-03 A 摘要）。③段间动势衔接=PRODUCTION.md S2 既有闸维持。

## 四、落地件：AI 视频质感管线 spec v1（本地可跑·至超分为止·调色/grain 交接第四波）
| 站 | 件+参数 | 硬件档 |
|---|---|---|
| ①生成 | LTX-0.9.8-13B-distilled 主选（in-house）：蒸馏 8-10 步·guidance 1.0·121f@24fps=5s 段·原生分辨率出·六模块运镜词·I2V 首帧锚图；备选 Wan2.2-5B GGUF Q4（Apache）；HunyuanVideo-1.5=法务卡勿装机 | 12GB 档（bm-a offload·in-house）；16GB 档（bm-c）=Wan 重验台 |
| ②帧闸 | 只留可用帧+RMSE 漂移过滤（in-house）；逐帧步进三病分诊（unifab B） | 全档低载 |
| ③插帧 | rife-ncnn-vulkan CLI（MIT·免依赖）或 Flowframes GUI（GPL-3.0·Windows）；**仅** 8-16fps 源补 24+慢动作段 48/60；禁全片 60/120（soap-opera）；FILM 判弃（archived） | 8GB 档可跑（ncnn 端侧设计位·A 仓定位）；全档 |
| ④deflicker | ffmpeg deflicker（概念 B·参数=第四波 FFmpeg 域）；仅 flicker 帧用 | 全档 CPU |
| ⑤超分 | Real-ESRGAN（BSD-3-Clause·37,018★·video 模式）或 Video2X GUI（22,024★·AGPL-3.0 商用注记·集成 rife/realcugan/realesrgan·2026-03 活跃）；超分最后·轻量优先防过磨（保味律） | 8GB 档走 ncnn 位（realesrgan-ncnn 存在性待证）；16GB 档重批 |
| ⑥交接 | 第四波落点C 调色链（暖橙 grade+halation）→grain 最后补：Overlay/Soft Light 20-40%·35mm 细粒（fluxvine+保味律双源） | 全档 |
- 档位口径注：派工单「bm-a 8GB」与 model-matrix bm-a=4070S 12GB 冲突→按显存档执行（8GB=bm-b/12GB=bm-a/16GB=bm-c）。

## 五、结论应用表（落点四选一）
| 结论 | 落点 | 状态 |
|---|---|---|
| 运镜六模块+分句律+起幅落幅+速度副词紧随→S2 段落表运镜提示词模板 | 分镜表（mv0001 S2） | 待发 |
| 负面词三模块词表+20-30% 比例律+蒸馏档失效注记→S4 关键词定稿 | PRODUCTION.md 正典（S4） | 待发 |
| 帧率三律（24 直用/慢动作 48/禁 120）+管线序（生成→插帧→超分→grain 最后） | PRODUCTION.md 正典（S3/S5） | 待发 |
| 帧率三律（24 直用/慢动作 48/禁 120）+管线序（生成→插帧→超分→grain 最后）+选型判（FILM 禁用/Video2X AGPL 注记/rife-ncnn 主+Flowframes 备）→spec v1 落典·装机试点随正典下发 | PRODUCTION.md 正典（S3/S5） | 待发 |
| HunyuanVideo-1.5 Territory 条款对我方商用适用性（S3 主径法务门·2dlive-00 A 级直验在前） | 待证池（法务复核位） | 待证 |
| Wan2.2-5B 质感档 steps/cfg·插帧↔超分管线序 A/B·realesrgan-ncnn 存在性·HunyuanVideo fps 原生值 | 待证池 | 待证 |

- 更新记录：T0 骨架落盘 → T1 内锚 6 件直读+GitHub 六仓 A 级（11/20）→ T2 DDG 四轮 CN/EN（15/20）→ T3 深读五路 4 成 1 败（20/20 封顶）→ 终稿；P-65 自纠一处：应用表落点由通用四选一改为任务令指定四选一（就地纠留痕）。
- 防线二：已抽验（主会话 10-08）——两承重主张 api.github.com 直读全过：①google-research/frame-interpolation archived=true（末推 2024-08-10·判弃成立）；②xinntao/Real-ESRGAN stargazers_count=37,019·BSD-3-Clause（与调研报 37,018 一致）；RIFE 家族活跃度主张与 Practical-RIFE/Flowframes 末推时间戳采信调研员 A 级直读。
