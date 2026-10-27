# 本地关键帧基线探测（KF-LOCAL-BASELINE · bm-b · 2026-10-20）

> 触发=CEO 令 2026-10-20「节约云端 token，优先本地算力」+ 漫剧 REBUILD-PLAN-v2 的 D3 站原定云端 seedream。
> 目的=**用证据决定 D3 该不该走云端**，不靠习惯。
> 成本=本地 GPU 约 1 分钟出三帧；云端 0 次。判读=1 次多模态调用。

## 一、配置与实测

| 项 | 值 |
|---|---|
| 引擎 | ComfyUI 0.36.0 + `sd_xl_base_1.0.safetensors`（本机唯一 SDXL 底模） |
| 尺寸 / 采样 | 832×1216 竖屏 · 28 步 · cfg 6.5 · dpmpp_2m + karras |
| 耗时 | 25.2s（首帧含加载）/ 14.0s / 14.0s |
| 显存 | 释放 Ollama 后 985 MiB 占用起跑，未 OOM |
| 产物 | `C:\Fluxgroup\FluxGroup\media\drama-tools\kf_probe_local\kf_{101,102,103}.png` + `sheet.png` |

## 二、判读结论（多模态盲评·逐项）

1. **质感：未达标。** 皮肤是 SDXL 典型蜡质高光，发际线像"画"出来的；缩略图能骗眼，全尺寸近看是 CG 人偶感，塑料感明确。**不到动漫程度，但离"仿真人"差一档。**
2. **解剖：面部没崩，手崩。** 中帧双手交握糊成一团（AI 典型糊手）；左帧右手疑似指节异常（不确定，不下定论）。
3. **场景：最偏离的一项。** 生成结果更像"老银行柜台/邮政/中药铺"：木柜台、铁窗、**粉笔黑板**。90 年代证券营业部的核心视觉（翻牌行情大屏）没有出现；右帧近景暴露**伪汉字**——中文观众零容忍。
4. **一致性：不合格。** 三帧是两个到三个不同的人（脸型/发型/肤色/主光全变），只能算"同类型角色"，不能当同角色连续叙事。
5. **可拍性不足。** 背景全部重度虚化，拿不到空间信息，做不了正反打与走位。

## 三、路由判据（据此定线）

**结论：`SDXL base 单靠提示词`不足以承担漫剧关键帧，不应直接拿它省掉云端。** 但失败原因**不是"本地不行"**，而是缺少三件东西：

| 缺口 | 补法（均为一次性本地投入，之后零云端边际成本） |
|---|---|
| 写实质感 | 换 photoreal SDXL 底模（如 RealVisXL / Juggernaut 系，约 6.5GB 一次性下载） |
| 角色一致性 | 每角色 LoRA（kohya 管线本机已跑通）+ 参考图条件（IP-Adapter / InstantID） |
| 场景考据 | 场景 prompt 库（翻牌大屏/营业部座椅群/晨光水汽）+ **汉字一律不交给底模生成**（做贴片或后期合成） |

## 四、执行序建议（省 token 优先）

1. **一次性下载 photoreal 底模**（≈6.5GB，本地磁盘，无按次计费）→ 用同一 prompt 复跑对照。
2. 起 1 个角色 LoRA（需 IP 定选 + 角色三视图；属导演席决策面）。
3. 垫图条件（IP-Adapter/InstantID）确认装机。
4. **复测仍不达"仿真人 CG 人偶 + 场景考据"及格线** → 该镜才升云端 seedream，附本文件作对照证据（>500 积分走确认闸）。
5. 在此之前，本地能力可用于：**animatic 占位帧 / 构图试验 / 光位试验**（不参与终稿质检门）。

## 五、诚实边界

- 本探测只验了 base SDXL + 纯提示词，未验 photoreal 底模与 LoRA/垫图组合——**不能据此判定"本地永远做不了"**。
- 判读来自 1 次多模态调用（成本考虑），非多席盲评；正式质检仍走导演席。
- 三帧已保留，可作后续对照基线（同 seed 同 prompt 复跑即可比）。

## 六、第二轮：本机存量资产盘点（2026-10-20 02:0x）

盘 ComfyUI models 发现本机**已经备好更强的一整套**，无需下载：

| 资产 | 规格 | 状态 |
|---|---|---|
| `qwen_image_2.1_turbo_int8_convrot` + `qwen_3_4b_fp8_mixed`(TE) + `qwen_image_2.1_vae_bf16` + `qwen_image_2.1_turbo_lora` | DiT int8 6.9G / TE 5.4G / VAE 644M / LoRA 871M | **VAE 装载失败**（见下） |
| `z_image_turbo_int8_convrot` + `z_image_ae` + distill LoRA | 5.9G / 320M / 151M | 未试 |
| `minimax_h3_fl2va_pruned_int4` + H3 VAE/LoRA/TE | DiT 16G·TE 15G | 8G 档不可行（超显存） |
| `RealESRGAN_x4plus` | 64M | 可用（放大/补细节） |

### 第二轮实测（Qwen-Image 2.1 Turbo int8）

- ComfyUI 0.36 **支持** `qwen_image` CLIP 类型与 `EmptySD3LatentImage`，UNET/TE 加载无碍；
- **但 VAELoader 失败**：`Error(s) in loading state_dict for WanVAE: size mismatch for encoder.conv1.weight: copying a param with shape [96, 4, 1, 3, 3]` → VAE 与当前 ComfyUI 版本的 WanVAE 实现不配对（版本/VAE 变体问题）；
- 结论：**该四件套需要配套配方或较新的 ComfyUI**。原始票 **POOL-0021（Qwen-Image-2.1-Turbo KF 提速试烧）派给 bm-c**，其配方可直接复用；本机不重复排障。

### 底模下载可行性（如实）

| 通道 | 实测 | 判定 |
|---|---|---|
| hf-mirror 直连 | 20MB / 169s ≈ **0.12MB/s**（6.5GB 需 ~15h） | 今晚不可行 |
| Clash 代理直连 huggingface.co | 请求失败 | 不可用 |
| ModelScope `AI-ModelScope/RealVisXL_V4.0` | 404 | 无此仓 |

→ photoreal 底模获取记 **open item**（可断点续传待带宽改善，或走 bm-c/bm-a 已有机位转存）。

## 七、路由建议（双轨并行·云端不关）

> 2026-10-20 勘正：CEO 明确「云端和本地都要有」。本节的"本地优先"指**分工次序**，不是禁用云端。

1. **终稿级关键帧仍可走云端 seedream**（质量上限·并行产线）；本文件提供本地基线作为对照与"本地能做到什么"的证据。云端按次记账，>500 积分走确认闸。
2. **本地承担量与迭代**：构图试验、光位试验、animatic 占位、同 seed 参数对照——无限次跑，把方向试对后再决定终稿由哪条线出。
3. 存量资产优先修通（向 bm-c 取 POOL-0021 的 Qwen-Image 2.1 四件套配方；同四件本机已在盘）：配通后本机可承担相当比例 KF，云端只在本地达不到的镜次使用——**提高本地占比、把云端花在刀刃上，不是替代云端**。
4. photoreal SDXL 底模断点续传 = open item（不阻塞，带宽允许时补）。
5. 角色一致性：LoRA（本机 kohya 管线已通）+ 参考图条件，IP 定选后启动；两条线共用该资产。