# FIDELITY-SPEC-v1 — 生成保真规格（提示词+参数·「出图和视频差强人意·务必还原本意」根治件）

> 溯源：CEO 令 2026-10-12 15:4x「分镜都写的很好，但出图和视频差强人意，好好研究提示词和参数设定，务必还原本意」（O-20261012-1540）。
> 证据基：①外源=A 级官方面（krea-ai/krea-2 官方 prompting 文档系·社区验证工作流 20 节点含 8+1 两段采样/289 风格库/12 字段 pose 系）+ComfyUI-Krea2T-Enhancer 官方 README（提示词保真补丁/注意力权重/Image-Only LoRA 加载）+本司 17 回炉三族病灶（构图漂移/运动层漂移/档位污染）+今日 6 帧拉片（置景电影化/胶片指纹 0）。
> 诊断定谳（我们提示词架构对官方最佳实践的四处背离）：
> ①**主体块太短**——官方铁律「subject 必须是最长块；style/props 段比 subject 长=图很好但什么都不是」——我们的 LIGHT/道具块 40-60 词碾压主体一行=构图漂移直接根因；
> ②**零权重**——意图核心（脸贴近镜头/情绪/构图）与道具描述平权竞争；
> ③**无 refine 步**——单段 8 步出图无 0.3 denoise 精修；
> ④**LoRA 文本互染**——角色 LoRA 经共享 DiT 层改写提示词内部表示=「挂了 LoRA 细节反而不可靠」（官方 README 原文）——韩感+漂移的隐性根子。

## 一、八块模板（kf 组装器 v2 重构·官方正序）

```
[景别/构图块]（一行·DiT 高 sigma 期先解析）
[灯光块]（一行·压缩到 ≤25 词——细节降级到光位词）
[主体块]（**最长块**·人/物+服装+材质+ID 块·情绪脸/表演注全并此块）
[环境块]（一行）
[表情块]（脸镜必填：情绪+视线+眉嘴细节）
[次级动态块]（发丝/烟/尘）
[Pose/动作块]（动作镜必填·三段式）
[风格块]（固定尾段一段=2001 MV film still+5279+telecine·全片逐字复用）
```
- 每块独立一行（防 400 词长句互稀释）；主体块字数 **>风格块**（硬律·lint 检项）。

## 二、权重三到五条（意图核心提权·Krea2PromptWeight 语法）

| 镜型 | 权重配方 |
|---|---|
| FACE 近特 | `(face close to the lens:2.5)(眼/眉情绪短语:2)(主体身份首词:1.3)` |
| 直视锚 | `(looking straight into the camera:3)(face close to the lens:2)` |
| 情境唱锚 | `(lips closed mid-song breath:2)(眼先于手凝视:1.5)` |
| 置景镜 | `(single warm light pool:1.5)(figure carved out of darkness:2)` |
| 道具特写 | `(wedge marks catching the light band by band:2)` |
- 全局 strength=1.0 起·整体过驱降到 0.6-0.8·权重 3-5 条封顶（多则稀释）。

## 三、负权重反转律（替代一切散文否定）

- 语法 `(概念:-1 ~ -5)`——**反转非删除**（推向反义相）。-5=实用地板。
- 反韩锚升级：`(K-pop idol styling:-3)(glossy styled grooming:-2)` 取代散文反韩句。
- 置景纠偏：`(vast archaeological depth:-2)`（治「电影化的真」病）。

## 四、参数表（生成档位·两段采样全档启用）

| 档 | 参数 | 用途 |
|---|---|---|
| 试构图档 | 672×384·8 步·cfg1·4 种子/镜·8-20s/张 | **每镜先行**·人眼过构图才升正档（漂移在 1/10 成本截杀） |
| 正典帧档 | 1344×768·**8 步 + 1 步 refine（denoise 0.30·kl_optimal 调度）** | KF 量产 |
| 定版帧档 | RAW bf16 52 步（turbo 禁） | 拍板帧/封面位精出 |
| i2v 批量档 | INT8 768P·124 帧·4 步 turbo·Spectrum on·**first_frame=过闸 KF 原帧** | 夜窗双机 |
| i2v 定版档 | 云端 Context-IR 768P | 定版镜精修（配额内） |

## 五、节点面改造（今窗已装/随派单落 bm-c）

1. **Krea2T-Enhancer**（提示词保真补丁·采样期文本融合路径）——bm-a 已装（今窗 git clone）；bm-c 随令装。
2. **Character-LoRA—Image-Only 加载器**——jman 换此加载（只写图像 token·不染文本 token=LoRA 保真冲突根治）。
3. **Krea2PromptWeight（KJNodes）**——权重+负权重必经节点（MODEL 与 CONDITIONING 双出全接·漏接=静默无效）。
4. i2v 提示词=五槽保留+**单动律强化**（主运动一词配 2-3 权重·次级动态降权）。

## 六、QC 对照意图检（成片闸前新增检）

每帧/条 QC 时**照分镜注记四要素逐项核**（主体/构图/光/情绪）——产物 vs 意图对照表落帧批 QC 件；「六检过但意图偏」=回炉（回炉律）。

---
*v1·bm-a 导演席·2026-10-12 15:5x·消费方=mv_full_shots.py kf()/i2v() 组装器 v2 重构（本窗起·八块+权重+两段采样）+bm-c 夜窗烧帧执法·复引 PROMPT-SPEC v1.1+CAMERA-DIRECTION-v1+ERA-MV-GRAMMAR*
