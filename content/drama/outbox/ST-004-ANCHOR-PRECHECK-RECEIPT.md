# ST-004 锚清洗纪律入产线回执（CSA v1.1 item 2 · anchor pre-check）

> 站点=CONTENT-LOOP v0.1 ST-004；法源=cph4/fleet/drama-dept-v1/epburn-handover/
> CSA-SMOKE-VERDICT-20261017.md v1.1 条款 2（工单 2/5 技术面 GO 承接）；时点=2026-10-19T02:37:31。

## 交付三件

1. **anchor_precheck.py 工具**（部署=`C:\Fluxgroup\MiniGame\Tools\comfy\anchor_precheck.py`；版本化源=bigmoney
   `content/drama/runner_assets/anchor_precheck.py`）：ANCHOR 三元组校验（发型/发色/着装）+
   id 银行入行门（manifest 零漂移）+ 同角色跨帧行清单零漂移检 + 视觉席位工单面
   （emit_frame_check——像素级帧检=多模态席位的活，工具只做确定性面）。
2. **drama_ep_burn.py 锚清洗补丁**（`C:\Fluxgroup\MiniGame\Tools\comfy\drama_ep_burn.py`·本批落补丁）：
   - 5 个正典锚补齐发色/发型钉（绿发漂移根因位）：RED（black hair ponytail）/MANCANG（short
     black hair）/XIONGWEI（neat black hair）/FATHER（unkempt black hair·长锚 rain-soaked black
     hair）/BOY（short black hair）；CH（black hair）与 XIONG（silver temples）原已达标零改。
   - 启动硬闸 anchor_gate()：烧制前校验 7 正典角色 IDS_C 三元组，缺项=ANCHOR_TRIPLE_FAIL
     exit 2 拒烧（fail-fast·不再带病入产）。
   - CLIP 77-token 预算注记：紧锚头均 +2 词（expand_c 景尾吸收机制既有·CSA 判决条款 2 的
     定谳取舍：锚漂移之害>景尾截短之损）。
3. **自检+探针双绿**：anchor_precheck --selftest（离线断言 9 条含反例）=issing-manifest": true, "cross-frame-drift-detected": true}}；
   补丁后正典紧锚 in-process 探针=validate_canon 7/7 PASS。

## 诚实边界

- 帧级（像素）一致性检不在本件射程（=多模态席位工单面）；本件=文本/清单级确定性面。
- 补丁只钉锚文本与启动闸，未动 expand/expand_c 注入算法、种子、STEPS/CFG（零行为面改动
  除锚文本本身）。
- MiniGame/Tools/comfy=非 git 工具区（盘面为正身）；版本化源与回执走 bigmoney 仓。
