# BigStream 提示词撰写规范 v1.3（定稿）

> **CEO 三连令**：O-20261009-1815「自媒体公司好好去研究一下提示词的撰写，你现在写的很有问题，AI识别肯定做不出来好的结果」· O-20261009-1830「多写专业词汇，要具体到某个颜色某个运镜等等，好好去调研开源社区的分享案例什么的，形成机制，不要用模糊的人类自然语言！」+「大量使用成熟的相关skill，并派出专家指导和审查」
> **CEO 令 v1.3（2026-10-15）**：「好好去调研，提示词的各种技巧和规则，你现在写的提示词，还是容易误导AI。好好看官方文档。摸清规则，每次提示词都要过1遍提示词专家审才能开始生产。」——**专家审闸已立法（PROMPT-EXPERT-GATE-v1·本目录）**，本规范=闸的规则正身。
> 适用：mv0001《爱在西元前》全管线（Krea 2 Turbo t2i / Qwen-Image-Edit-2511 / MiniMax-H3 本地 / Seedance 云端）+ 41 曲全产线
> 状态：v1.2（2026-10-12）：运镜章升格五槽语法（正典=mv0001-handover/canon/CAMERA-DIRECTION-v1.md）→ **v1.3（2026-10-15）：新增 §十 V3 四型病灶律（官方归因版）+ 专家审闸挂接**——官方规则调研全档=cph4/research/R-20261015-prompt-rules-official.md（四路波·A 级源）

---

## 卷首·总律

**可检测性原则（本规范一切条款的母法）**：
> **一个词如果不能被摄影机、麦克风、测光表或秒表检测到，就改写它。**

- 可执行词：光源方位/色温值/光比、相机焦段/光圈/f 值行为、运镜类型+幅度+速度、胶片型号/滤镜/颗粒、调色方向+具体色名、秒级时间轴。
- 不可执行词（全禁）：电影感/大片感/史诗感/唯美/震撼/氛围感/高级感/意境/好看/8K/杰作/超写实——情绪标签让模型回归训练先验，产出=「模型那天的心情」（cineprompt.io 实证：'cinematic lighting' 可能给一盏背景灯，也可能给一整套 Storaro 布光）。
- **零否定律（Qwen 系管线）**：负面=ConditioningZeroOut 死通道，一切 NOT/no/without 全部注入正面条件。官方改写器规则 8 原文：「改写之后的prompt中不应该出现任何否定词。」
- **约束词分家律**：Seedance 官方约束句（「保持无字幕，不要生成Logo水印」）与 Qwen-Edit 官方后缀（「，超清，4K，电影级构图」）是各自官方口径的**例外授权位**——仅限该位使用，画面内容描述区仍零否定。

---

## 一、病灶诊断（官方背书定谳）

| # | 病灶 | 证据 |
|---|---|---|
| 1 | **否定词大墙**：NOT Korean idol / no K-pop / no makeup / NO_TEXT 墙 → 把 K-pop/makeup/watermark 概念注入每张图的正面条件 =「太韩化」顽疾总根源 | 官方改写器规则 8（QwenLM/Qwen-Image prompt_utils.py）；社区实证（r/comfyui/Civitai/知乎三源） |
| 2 | 跨图无效指令：`The same young man in every image`（t2i 无跨图机制） | 机制事实 |
| 3 | 编辑指令与画面描述混写（fastface 一句塞 11 层） | 官方口径：一句直接具体改动 |
| 4 | 结构松散/景别缺失/权重稀释（60–120 词堆砌无主线） | 官方公式未按序 |
| 5 | **年代错位词**（图面「干净现代感」来源）：Vision3 5219/5207=2007/09 型号、teal 阴影/变宽耀斑/2383=2010s 审美、85mm f/1.8 奶油焦外=现代 | 摄影指导专家审查 |
| 6 | **视频面根因**：H3 质量依赖 Context-IR 预处理（官方原话 critical）——该模块未开源，本地直跑没有 → 必须自己写官方结构化长文自担预处理 | MiniMax-H3 README |

---

## 二、词表与禁词机制（lint 三名单）

**机制件**：`scratch/mv-carve-bma/prompt_lexicon.py`（产线唯一 prompt 来源，禁手写散文）。

1. **NEG 名单**（Qwen 系零否定）：not/no/without/avoid/never/non- + 缩写（don't/can't/won't/isn't/doesn't）——词边界正则+撇号归一捕捉（子串法误伤 piano/casino、漏网 nothing/can't 的坑已修）。
2. **VAGUE 名单**（模糊词全禁）：beautiful/stunning/aesthetic/masterpiece/8k/dreamy/ethereal/whimsical/cozy/glass skin/porcelain skin/airbrushed/vibrant/epic/photorealistic 等 40+ 词；`cinematic` 灰名单=仅首句 1 次合法。
3. **CONCEPT 名单**（概念注入词，写进条件=注入该概念）：korean/K-pop/idol/salon/makeup/watermark/typography/logo——**反韩化的正确姿势=全词消失，不是否定它**。
4. **FIX_MAP 否定改写器**：`no makeup→bare face, natural matte skin` 等 25 条对照表代码化，lint 命中自动替换复检。
5. **长度闸**：40–200 词（官方上限 200）；**ID 块逐字复用律**：同一人所有镜头引用同一 ID 常量，禁止改写（文本身份漂移）。
6. **f 值行为写法**：不写「浅景深」，写 `f/1.4, only the eyes in focus, ears already soft`。

**正面等价改写表（节选）**：

| 禁 | 正 |
|---|---|
| NOT a Korean idol, no K-pop styling | plain 2001 Taiwanese campus wardrobe, loose unbranded cotton |
| no makeup, no glossy grooming | bare face, matte natural skin with visible pores, unstyled hair |
| no see-through fringe, no curtain bangs | heavy straight solid fringe lying flat over the eyebrows |
| no beautification, no smoothing | keep natural skin with visible pores and 35mm film grain |
| NO_TEXT 墙 | 删除（出字=噪声，重 roll） |

---

## 三、Krea 2 Turbo（t2i）——官方结构公式 + 专业词表组装

**官方公式**（prompt_utils.py）：身份（ethnicity/gender/age）→服装发型→面部/皮肤→姿态动作→周围环境光照→**镜头与风格收尾**。单段连贯散文，英文 <200 词，禁 Markdown 列表/标签堆砌。Krea 2 官方：natural language、长细节出最佳、文字渲染加引号。

**组装器槽位**（build_shot，词表键入）：
- 景别/机位：`head-and-shoulders framing, at eye level`
- ID（逐字复用常量）：`a 20-year-old Taiwanese student with heavy-lidded monolid eyes, a thick lower lip, softly rounded cheeks and a thick black fringe lying flat over his eyebrows`
- 服装（WARDROBE_M）：`loose white short-sleeve school-uniform shirt with dark collar trim...`
- 光（LIGHT·色温+灯型+行为）：`a tungsten practical lamp at 3200K lights the face from frame left, a warm amber pool with deep falloff into shadow`
- **收尾（镜头+调色+胶片）**：`Shot on 35mm lens at f/2.8, 2001 telecine grade with warm skin tones, milky lifted blacks and blooming practical highlights, shot on 35mm Kodak Vision 500T 5279 with visible grain and halation on practical lights`

**2001 年代正确参数（摄影指导定谳）**：胶片=Kodak Vision 500T **5279**（夜）/ 250D **5246**（日）（Vision3 5219/5207 是 2007/09 型号·判「干净现代」）；球面 1.85/4:3 框（变宽 2.39=2010s 判删）；特写 35–50mm f/2.8–4 深焦靠柔光镜软化（85mm f/1.8 奶油焦外=现代判删）；调色=telecine 暖肤色+奶黑+practical 高光晕（teal 阴影/2383 LUT=2010s 判删）；蓝调时刻 8000K+钠灯 2200K 撞色；年代签名光色词=**sodium 钠灯/fluor 荧光管/halo 穿烟逆光光晕/godray 神庙光柱/telecine 调色/plyset 手绘景片**。

---

## 四、Qwen-Image-Edit-2511（编辑管线）——官方三规则

1. **一句直接具体的改动+保持项**（官方正例：`Replace the man's hat with a dark brown beret; keep smile, short hair, and gray jacket unchanged`）——描述**结果状态**，不重述整幅画面、不写编辑过程。
2. **多参照图必须点名** picture 1/2/3（最优 1–3 张）；构图跟随 image1（底潜空间源）。
3. **风格描述放句尾**；妆容/表情修改必须 natural and subtle, never exaggerated（官方红线）。
4. 官方后缀位（例外授权）：结尾加 `，超清，4K，电影级构图`（官方稳定器——lint 对 edit 模式放行）。
5. 官方强烈建议 LLM 改写前置（不 rewrite 结果不稳定）——无本地 LLM，以三段式规则组装逼近：
   `Change only [部位] to [参照 picture N].` + `Picture N shows the same person from another angle for identity reference.` + `Keep identical face shape and head angle, identical eyes and gaze, identical nose, mouth and jawline, identical skin with natural film grain and pores.`
6. denoise 判例沿用：锁脸 0.55–0.6 / 发型档 0.62–0.7。

---

## 五、MiniMax-H3（本地视频）——Context-IR 自担 + 官方三字段

**根因（官方原话）**："H3-Context-IR is critical to the quality of the final output"——未开源，本地直跑必须自己写官方结构化长文。

**I2VA 官方结构**（build_h3_i2va 组装）：
```
For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.
integrated_multimodal_description: [首帧锚定→action onset→continuous development→result or reaction]
overall_soundscape: [环境声总结]
non_diegetic_music: N/A (song laid in post)   ← MV 后期贴歌防音轨打架
```
- **运镜五槽公式（v1.2 升格·替换旧三维公式·正典=mv0001-handover/canon/CAMERA-DIRECTION-v1.md）**：MOVE 动作+目的地 / CURVE 速度曲线（缓入缓出·**平速语 `at slow speed` 族全禁**）/ MOTIVE 动机（相机回答画内事件）/ TEXTURE 2001 操作质感（脚架 locked-off·地轨 floor dolly·手持 breath-sway）/ ALIVE 画内活体——例：`The camera eases toward his profile on a slow floor dolly as his heavy-lidded eyes lift from the half-cut row, gathering only as far as his gaze travels, and settling on the lifted look.`；每镜限一动作；orbit 只许 ≤20° 小弧（完美整圈=AI 签名）；互补律=主体复杂则镜头稳；lint video 模式 **[FLAT] 平速门**执法。
- 切镜带时间戳：`[Shot 2] At 00:03.500, the camera cuts to...`（切镜须引入新信息；仅变距离/角度优先用运镜）
- 官方范本=8 秒拉面静态镜头：固定机位+蒸汽持续升腾+中段焦点转移——**静态特写+微呼吸=官方最稳区**（我方 8.5 分判例吻合）。
- H3 词汇（fal 官方托管方）：subtle handheld shake / rack focus / fine grain, soft highlight halation, restrained color。
- 社区强化版结构（Alex Patrascu 实测）：SCENE CONTEXT→TIMELINE 秒级分拍→LOCATION MAP 构图定位→CAMERA（距离/高度/总位移上限）→PHYSICS→LIGHTING→AUDIO→POSITIVE LOCKS→真实设备收尾。

---

## 六、Seedance（云端 generate_video）——中文八要素 + 防崩尾句

**官方公式**：精准主体+动作细节+场景环境+光影色调+镜头运镜+视觉风格+画质+约束条件（60–100 词）。

- **单镜单运镜红线**（官方：「同时要求推拉摇移会增加画面的不稳定性」）——一动作+缓入缓出曲线短语+动机+质感短语照带（v1.2 运镜五槽的 Seedance 装法·正典=canon/CAMERA-DIRECTION-v1 §四）。
- **低缓连续小动作优先**（官方：「规避狂奔、大跳、剧烈翻滚」）；动作量化（缓慢抬手/快速转头）；情绪外化（悲伤=低头+肩膀微颤+攥紧衣角）。
- **禁精确秒数时间戳**（官方：强限时长导致异常——与 H3 相反，跨模型不套用）。
- 主体绑定：`张三@图片1` 标签法，2–3 个稳定静态特征。
- **防崩尾句（官方原文）**：`全局约束：人物面部稳定不变形，动作自然流畅，无卡顿无闪烁；保持无字幕，不要生成Logo水印。`（竖屏出字率高）
- ID 防漂移：人脸用大头照特写+全身照分图；双胞胎→「禁止生成同款分身」。
- 官方灯光杠杆：「Adding a single line about lighting is more effective than adding ten adjectives.」

---

## 七、A/B 归因实验设计（提示词工程专家审查版）

- **A 组**：旧否定墙原样（基线）
- **B′组**：A 逐字仅删否定墙+NO_TEXT——单变量干净验证病灶 1
- **C 组**：官方结构公式改写版（128 词样板）——验证新机制全貌
- 同场景同种子 ×4（冒烟级）；定谳级=8–12 种子×多场景+盲评配对。
- 判据：韩化残留/文字出现率/三律自审（高级/去烂俗/去AI感）。

---

## 八、机制件与产线改造

**已落盘**：`prompt_lexicon.py` v1.3——七类专业词表（年代修正版）+ 三名单 lint + FIX_MAP 否定改写器 + 六组装器（build_shot 官方顺序 / build_edit 三段式 / build_h3_i2va 三字段 / build_seedance 八要素 / build_camera 运镜五槽 / autofix）+ 运镜四新块（CAM_CURVE/CAM_MOTIVE/CAM_DEST/CAM_TEXTURE）+ lint video 模式 [FLAT] 平速门。

**产线脚本改造清单（定版门后执行）**：krea2_campus / designs2/3 / qwen2511_edit / hairera / female_era / fastface 六脚本 prompt 全部改 import 词表组装器；NO_TEXT 常量全产线删除；所有编辑批换三段式。

**skill 复用**：create-game-assets（视觉系统命名法/家族生产复用参照/QA 拼板）已入役；机制件+规范=双产出。

---

## 九、V3 四型病灶律（2026-10-15 CEO 令立法·官方归因版·专家审闸 C/G/D 面正身）

> 调研正身=R-20261015-prompt-rules-official §二（官方原文短引+URL 全档）；本节=产线执法版。

1. **色相渗漏律（C1）**——材质色×调色段双真值源冲突必须显式消解：
   - 病例：主体「towering black basalt stele」+句尾「amber monochrome palette」→出暖棕砂岩（SIL1 实锚·4.0 分判负）。
   - 官方归因：BFL「put first whatever matters most」「正向替代放句首不放 trailing clause」+「色板必须锚定具体对象」（官方示范 `palette of deep purple and black shadows`——色板作用于阴影区不作用于主体）+ Krea「Group subjects with their own attributes」——**句尾全局浮动词=晚到+未绑定=两头落空**（⚠️ 官方无冲突取舍明文·经验律）。
   - 执法：调色词一律写成「光色不改物色」——`torch light gilds the surface amber while the stone itself stays near-black`；禁全画面级 palette 裸词；专家审逐对消解材质色×调色冲突。
2. **媒介锚前置律（G1）**——媒介必须显式声明且前置：
   - 病灶：胶片风格词在库下出赛璐璐平涂（SIL4 实锚·1.0 分判负）。
   - 官方归因：Krea expansion 第 9 条「Preserve User Medium: When the user explicitly requests a medium (e.g. 'photo of', 'photograph of'…), honor it. Do not pivot to a different medium」；BFL 官方模板=媒介第一句定调。
   - 执法：每包收尾段显式 `live-action 35mm film frame`（真人实拍锚）·动画歧义词（illustration/styled 泛词）零容忍；「胶片型号词」≠媒介锚（型号是质感·媒介要声明）。
3. **形制锚律（C4）**——器物必须写到部件级可见特征：
   - 病灶：「iron torches burn low in wall sconces」→出 tiki 玻璃罐火把（SIL1 实锚）。
   - 官方归因：BFL「Describe visible details that distinguish your subject」——名称级描述让模型回训练先验补最常见形制。
   - 执法：器物=构造名词+材质+状态三件（`forged-iron cylindrical sconce bowl, soot-blackened metal, wall-mounted bracket` 级）；品类名后必挂三件，缺一=FIX。
4. **景深显式律（G4 关联）**——framing 必须显式景深：
   - 病灶：写 35mm 出泛焦（SIL1 实锚）。
   - 官方归因：BFL 官方 Job 表 framing 项**必须含 depth of field**——缺省=模型自由裁量（⚠️ 归因为推断）。
   - 执法：镜头段=焦段+光圈+焦点行为三件齐（`35mm lens, only his silhouette edge in focus, the hall beyond falling soft`）——与 v1 §二.6 f 值行为写法同源，升格为硬检。
5. **起帧主导律（D1·i2v）**——动作必须是首帧状态的自然延伸：
   - 病灶：首帧闭嘴写字+提示词要张口唱→模型拒执行（SING3b 实锚·2.5 分判负两连）。
   - 执法：与首帧对抗的动作一律禁写——要改先改帧（重制 KF）或改动作设计（动作拆到换帧后）；专家审逐镜问「首帧里有什么、提示词要它变成什么」（J2 四答）。
6. **正向替代句位律（B5）**——BFL 官方四步递进入法：
   - 对想要的东西更具体→尽早描述（句首不放句尾）→给替代加细节占空间→给上下文自洽（`a deserted beach at dawn, before the first swimmers arrive` 式）。
   - 我方 FIX_MAP 25 条对照表升格为四步法驱动（lint 命中后按四步改写·不是简单同义替换）。

**专家审闸挂接**：上述六律已入 PROMPT-EXPERT-GATE-v1 检查单（C1/G1/C4/D1/B5 对应条号）——每包过闸才烧（CEO 令铁律·零豁免）。

---

## 十、证据链（五路归笼+2026-10-15 官方规则波）

1. **Qwen 官方**：github.com/QwenLM/Qwen-Image（README + prompt_utils.py 改写器规则 8/结构公式 + prompt_utils_2512.py）· HF Qwen/Qwen-Image 模型卡（negative_prompt 官方态度）
2. **Krea 2 官方**：github.com/krea-ai/krea-2 docs/prompting.md + expansion.txt · krea.ai blog 探索式流程
3. **MiniMax-H3 官方**：github.com/MiniMax-AI/MiniMax-H3（README + skills/h3-prompt-writing base-en.txt）· fal.ai/learn/devs/minimax-h3-prompting-guide · 社区实测 github.com/ecomimagelab/awesome-minimax-h3-prompts
4. **Seedance 官方**：volcengine.com/docs/82379/2222480（经镜像全文提取）· docs.seedance.tv 2.5 指南（镜像核对）
5. **通用方法论**：Google Veo 3.1 prompting guide（cloud.google.com blog + deepmind.google）· OpenAI Sora 2 Cookbook（developers.openai.com/cookbook）
6. **社区分界实证**：cineprompt.io/field-notes/cinematic-is-useless · liminalshort.org/blog/jailbreak-ai · kling-prompt-engineering（github.com/Yuyyxz）· awesome-qwen-image-2-1-prompts · stillslab.com 扩散滤镜解码 · videolens.cc 调色 14 种 · melies.co 运镜句法
7. **专家审查**（2026-10-09 本司派出）：摄影指导（年代修正+2001 签名词+运镜 8 补）· 提示词工程（官方顺序+lint 三名单+FIX_MAP+归因设计）
8. **ComfyUI 官方模板活样例**（本机提取）：api_krea2_t2i / video_minimax_h3_* / api_seedance2_0_* / image_qwen_image_edit_2509_relight
9. **2026-10-15 官方规则波**（CEO 令「好好看官方文档」·R-20261015-prompt-rules-official）：BFL docs.bfl.ml 三页（building/technical/editing）+ Qwen 两代改写器原文 + Krea expansion.txt 原文 + Seedream 官方指南（ark.volcengine.com）+ Anthropic/OpenAI/Gemini 官方提示词指南 + Seedance/MiniMax/Veo/Sora 官方——四路波文件=cph4/research/waves/2026-10-15-prompt-rules/

---

*执笔 bm-a · 2026-10-09 · CEO 三令 O-20261009-1815/1830 全收口 · A/B/B′/C 实验结果随附呈报 · v1.3（2026-10-15）：§九 V3 四型病灶律+专家审闸挂接·CEO 令 O-20261015 立法*
