# CSA 冒烟 verdict — v1.1 工单 1（StoryDiffusion 跨镜一致性 · SD1.5 适配）（2026-10-17）

> 执行=bm-b「全面开工」窗；工件=`media/drama-eps/csa-smoke/`（13 件·id×4/csa×4/base×4/对比板·gitignored 媒体区）；日志链=`E:\Fluxgroup\.codely-cli\csa_smoke_f{3..6}.log`；判定法=对比板多模态盲评（同角色跨镜一致性 CSA vs 基线·≥9/10 为批内锁线）。

## 结论（先看这行）

**技术链路 GO：CSA 行同人一致性 7/10 vs 基线 2/10——明确大幅增益、零结构崩坏（无多人/断肢/崩脸）**；但 9/10 批内锁绝对线未达，归因=锚组自身噪声+单格漂移+背影镜不可验（判读员给出可抬升路径）。建议：CSA 进 v1.1 作批内锁辅助面，**须配锚清洗纪律**；是否清锚后二轮冒烟复测 9/10 线，留 CEO/工单裁量。

## 冒烟配置

- 模型=anything-v3.0-pruned-fp16（SD1.5 线）；512×768·24 步 DDIM·CFG 7.0；clip_skip=2 手写编码（diffusers 0.33.1 SD 管线无 clip_skip，neg 同 list 类型律）；产线锚 GENERAL/STYLE_C/NEG 取自 drama_ep_burn.py。
- 臂 1（CSA）：id 银行 4 场景（write=True，白衫领带年轻男×4 场景）→ 4 真实场景（write=False 注入）；臂 2（基线）：同 4 场景同种子、diffusers 原生处理器。
- 掩码机=StoryDiffusion 维护版（app.py/notebook XL 两级）：mask1024=(H//32)(W//32)=384tok、mask4096=(H//16)(W//16)=1536tok，sa32=sa64=0.5（notebook 原值）。

## 六飞飞行史与根因链（复用必读）

1. **SD1.5 up_blocks 四块解剖**（CPU 探针 csa_probe_anatomy.py 实证）：`up_block_types=[UpBlock2D, CrossAttnUpBlock2D ×3]`——up_blocks.0 无注意力；自注意力层在 **1/2/3**，通道 1280/640/320 = 384/1536/6144 token @512×768。维护版两级掩码只覆盖 384+1536 → **正法=只剔 up_blocks.3**（latent/1 层·SDXL 无此级）。flights 3/4 同号复炸（24576 vs 6144 SDPA 广播崩）根因=误剔 .2 留 .3：6144tok 层落 else 分支拿到 1536 基掩码。
2. 基线臂 `set_default_attn_processor()` 拒 gu.AttnProcessor2_0（StoryDiffusion 类同名非同源）→ 显式重设 diffusers 原生 AttnProcessor2_0（flight 5 死点·flight 6 修毕）。
3. 子代理通道模型 293s 超时 0 工具调用死 → **.cmd 裸路径后台进程正法**（run_in_background 直跑）。
4. 六飞终局：EXIT=0·13 件全落盘（flight 6）。

## 盲评明细（对比板 3×4：行 1=id 锚组·行 2=CSA·行 3=基线）

- CSA 行 7/10：2-1 与 2-3 几乎同脸；失分=2-2 单格漂移（发色变浅/灰西装替白衬衫/肤色青灰）+2-4 背影镜不可验+2-1 年龄感略上浮。
- 基线行 2/10：四格=发福中年/白发少年/平涂风蓝发青年/背影——体型/年龄/画风全维坍塌，不构成同一角色。
- 锚组自身噪声：id 1-2 青绿色头发（锚内不一致），疑似被 CSA 行 2-1 继承=「锚清洗纪律」的直接证据。
- 判读员抬升路径：①清洗锚组（剔除青绿发格）再测；②黑发/白衬衫硬约束 token 压 2-2 类漂移；③背影/小人物镜加面部参考或 ID 损失（一致性感知永远缺一角的镜型）。
- 劣化检查：CSA 行无主体多人融合/断肢/多指级结构崩坏；2-1 背景乘客半融化属可容忍级。

## v1.1 落点建议

1. 工单 2（参照批 SDEdit 注入）/工单 5（burn.py 挂 CSA 分支）技术面放行——csa_smoke.py 全修复版为移植母版（含臂毕即存盘守护）。
2. 锚清洗纪律入批产：id 银行帧先过锚一致检（发型/发色/着装三元组零漂移）再入银行；ANCHOR 三元组写硬约束。
3. 二轮冒烟（清锚复测）为可选项：若 CEO 要 9/10 绝对线证据再烧；相对增益（7 vs 2）已足支撑「批内锁辅助面」定位。
4. 遗留观察项：背影/远景镜的锁面盲区（判读员③）——工单 3 角色数据集收割时留意（每角色 20-30 张中配正面占比）。

—— bm-b 执行窗 · 2026-10-17
