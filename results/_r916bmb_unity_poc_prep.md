# unity-mcp POC · bm-b 执行档案（O-20261011-2333-bm-c 回执底稿 · due 2026-10-13 12:00）

状态：PREP COMPLETE（可交付腿全落）· LIVE-ACTION GATED（i2v lane 后执行窗·令内优先级条款原文）
执笔：bm-b r916 · 2026-10-13 09:5x · 静默工作律（令 §6）

## 1 版本面（实读）
- MCP server：`C:\Users\Administrator\.local\bin\mcp-for-unity.exe`（安装 2026-09-28 18:57；Python 单文件；CLI 面：`--transport {stdio,http}` `--http-url/-host/-port` `--default-instance`；无 --version 旗标→usage 面取证；本会话工具组=同 server 之 stdio 实例 ×3 活体）
- 编辑器：Tuanjie `2022.3.62t13`（`C:\Program Files\Tuanjie 2022.3.62t13`）+ Tuanjie Hub（`AppData\Local\Programs\Tuanjie Cowork\hub\tuanjie.exe`）
- 编辑器侧桥包：`com.coplaydev.unity-mcp` 本机 15 个 Tuanjie 工程全零命中（manifest 扫描：MiniGame 12 工程 + TileBenchProj + Graybox 2 工程，2026-10-13 09:3x 实测）——**POC 实弹前置链=装包+开编辑器，尚未发生**

## 2 环境探针链（三窗实录）
| 窗 | 探针 | 结果 |
|---|---|---|
| r901 10-11 22:5x | find_gameobjects（unity-mcp 工具面） | "No Unity Editor instances found"（编辑器未开=执行硬前件，O-2333 回执窗诚实受理） |
| r915 10-13 09:16 | 同上 | 同结果；09:14:52 检出「Tuanjie 进程」当时判为 editor-open window |
| r916 10-13 09:39 | 同上 + 进程级核验 | 同结果；**定谳：09:14:52/09:27:26 进程=Tuanjie Hub 登录窗（hub\tuanjie.exe + Tuanjie.Licensing.Client），非编辑器工程窗**——CEO 正在执行 Tuanjie Hub 重登（10-10 起两大物理件之首件），编辑器工程窗=CEO 物理依赖 |

## 3 坑录（本窗新增，candidate）
1. **Hub/editor 进程面混淆**：`Get-Process`名匹配 `tuanjie` 命中 Hub（`Tuanjie Cowork\hub\tuanjie.exe`）与编辑器同族——判「编辑器工程已开」必须验 CommandLine（Hub=hub\tuanjie.exe；编辑器=Tuanjie 2022.3.62t13\Editor\Tuanjie.exe -projectpath ...）。r915 「editor-open window live」判读据此修正。
2. **server 侧 "No Unity Editor instances found" 双因不分**：编辑器未开 vs 编辑器开了但桥包未装，server 面同一句话——必须进程级+manifest 双核验定谳（本档 §1/§2 即此）。
3. **RAM 门**：i2v 批烧录中开编辑器=OOM 级联险（本晨 09:30 实证：machine-state resume 直启 Ollama 4.2GB VRAM→ComfyUI r915d CUDA OOM 阵亡→09:47 交互会话复活）——令内「勿占 GPU/主线 CPU」条款与之互证，POC 执行窗=批后。

## 4 升产线判读（一页·框架面，live-action 后定稿）
- 判据面：POC 令要求「实弹动作+截图留证」后判「是否升产线工具」。
- 框架判读（当前证据）：工具链三件齐备度 2/3——server ✓（Codely 内建 unity-mcp 工具组，本会话即活体）、编辑器 ✓（2022.3.62t13 在机）、桥包 ✗（零工程装有）。若批后装包+开窗一次过→升产线倾向正面（City3D/剧本 v5 场景审计/组件查找/截图自动化即用）；装包失败/编辑器窗不开→判负回执（判负=收获，令原文）。
- 执行触发器（已上板）：i2v 53/53 + RAM≥4GB 双门→N2U3 flip 同窗顺延装包+开最小工程（TileBenchProj）→实弹（find_gameobjects/资产审计）→截图→fleet/inbox 终版回执。

## 5 12:00 回执预案
- 批 ETA ~12:00-12:30（26/53 @09:50，~4.5min/clip）。12:00 边界轮回执=本档+批末窗执行态（若窗已开=实弹+截图；未开=诚实分段：prep 三腿全交+live-action 触发器在位+ETA 同日下午）。
