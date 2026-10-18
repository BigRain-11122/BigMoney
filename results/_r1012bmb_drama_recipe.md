# EPBurn 工具链移交包（drama-001-stockera 60 集 EP 量产线）·RECIPE-EPBURN-v1

- 交付：2026-10-17 bm-b r989（溯源=E1 五回执件4 承诺的 EPBurn toolchain git delivery）
- 正身源：`MiniGame/Tools/comfy/`（bm-b 本地·后续改动以源目录为尊再重推）
- 消费面：bm-a / bm-c 的《一路长虹》EP 量产线（60 集·drama-001-stockera）
- 前序：PILOT-001 已于 10-16 交付（3×20s 粗样）·本包=EP 正片线

## 一、件清单（4 件+本 RECIPE）

| 件 | 角色 | 用法 |
|---|---|---|
| `drama_ep_runner.ps1` | 自愈循环 runner v2.3（8min tick） | 计划任务承载；每 tick 探活 ComfyUI→续烧→自停 |
| `drama_ep_burn.py` | 烧制器 | `python drama_ep_burn.py <起集> <止集> [--check]`（含两端·确定性种子·resume-safe） |
| `drama_ep_assemble.py` | 装配器 | `python drama_ep_assemble.py <起集> <止集>`（纯 CPU·ffmpeg） |
| `gen_placeholders.py` | burn 硬依赖模块（ComfyUI 提交通道·`sys.path` 同目录 import） | 与 burn 摆放同盘目录 |

## 二、硬依赖

1. ComfyUI 便携版 + SD1.5 权重（烧制档=512×768·24 步·CFG 7.0·CLIP 77-token 预算压缩栈·卡镜不烧=装配面）
2. ffmpeg（bm-b=`C:\Fluxgroup\MiniGame\Tools\ffmpeg\bin\ffmpeg.exe`）
3. 系统字体 simhei/msyh/simsun 任一（硬字幕·渲染后必抽帧验字）
4. EP 规格：`cph4/fleet/drama-001-stockera/episodes/EP*.json`（60 集一集一 JSON）
5. 出图位：`media/drama-eps/eps-kf/`（按集名自动落盘·>10KB 既有件自动跳过）

## 三、路径移植表（消费机必改——脚本内嵌 bm-b 绝对路径）

脚本头部以下绝对路径按本机基地改写：`$py`（python_embeded）/ `$dir`（Tools\comfy）/ `$epsDir` / `$log` / `OUT` / `KF` / `FF` / burn 内 `sys.path.insert(gen_placeholders)`。三机基地：bm-b=`C:\Fluxgroup`、bm-a=`C:\Users\sjs20\Desktop\FluxGroup`、bm-c=`K:\Fluxgroup`。

## 四、runner v2.3 行为契约（自愈面·三代判例内嵌）

- tick=8min；无 EP json → `NO_JSONS_YET` 空转退出；60 集+0 缺图 → `ALL_60_DONE_SELFSTOP` → `schtasks /Change /TN <任务名> /DISABLE` 自停
  - **10-16 判例：计划任务上下文自停曾 7 拍不触发——烧毕仍须人工核验 `--check` 报 `EPBURN_REMAIN 0` 后手动 `/DISABLE` 兜底，勿单赖自停**
- ComfyUI 探活 `http://127.0.0.1:8198/system_stats`；死 → 重启 `main.py --port 8198`，45s 暖机探针，2 次尝试（v2.2=启动即死同 tick 重生；v2.3=烧制中途死→剩余预算 ≥150s 时限时重生+二次烧）
- 烧制 330s 硬看门狗（挂死烧不再冻结 tick 链·10-16 10:46 判例）；`--check` 出 `EPBURN_REMAIN N`
- IgnoreNew 任务策略=有界超时安全（容忍 tick 超时不双开）
- 日志位：`media/drama-eps/runner.log` + `Tools/comfy/drama-ep-burn.log`

## 五、装配律（drama_ep_assemble.py）

- zoompan 运镜 + 折行硬字幕（17 全宽贪心填满 + 孤尾/行首标点双守卫·EP022_22/EP053_22 判例内嵌）+ 字卡 + 闪回柔焦
- **音轨禁令合规=纯画面出片**（配音/音效=v1.1 IndexTTS 升级面·O-20260909-1955）
- 字体探测序 simhei→msyh→simsun；simsunb tofu 判例=渲染后必抽帧验字

## 六、产出位与回执

- 每集 mp4 → `media/drama-eps/EP<NNN>.mp4`
- 批量烧毕判据=`--check` 报 `EPBURN_REMAIN 0`；回执入 `cph4/fleet/drama-dept-v1/LEDGER.md`
