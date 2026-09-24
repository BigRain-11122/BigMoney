# 机队扩容验收包 v1.0（T-26）— BG-B/BG-C 接入 BigMoney 回测池

> 授权链：CEO 直令 O-20260924-1655（「机队其他的cpu，马上用起来，规则一样」）→ GM 开票 T-2026-09-24-26 → 集团转办 HQ-FEEDBACK F-20260924-12。
> 本件=BigMoney 侧验收准备（身份模板+共享件四机验证+首单派工分片表）；BG-B/BG-C 侧接入动作（clone→bootstrap→register）由其本机执行。
> 认领：r110 bm-b（F-04，commit 294efb2）。

## 1. 新节点接入 SOP（以本仓实况为准）

1. `git clone git@github.com:BigRain-11122/BigMoney.git`（Money02/、logs/、.codely-cli/、fleet/machine.json 为各机局部，clone 不含、禁手拷——fleet\README.md）
2. **一键自举（实际在仓路径）**：`python bootstrap.py`（依赖自装·清华镜像回退→20 项自检→总控数据生成）
3. 身份：`copy fleet\_machine.dual-role.template fleet\machine.json` → 编辑 `machine_id`（BigMoney 侧续编 **bm-d / bm-e**）→ 主归属=Biggame 保主（借算律 fleet-allocations §三）
4. 心跳落位：首心跳写 `fleet\machines\<本机id>.json`（last_seen/epoch/clock_read 单瞬同源三件+total_ram_gb+cpu_util_pct，P-33）
5. 循环+看门狗注册（路径自适应、幂等 -Force 无害）：
   - `powershell -NoProfile -ExecutionPolicy Bypass -File Tools\register_loop_task.ps1`
   - `powershell -NoProfile -ExecutionPolicy Bypass -File Tools\register_watchdog_task.ps1`
6. 首单派工：见 §4 分片表——clone 完成即有活干，不空转。

> ⚠️ **缺件披露（诚实门）**：O-1655 §二与 HQ-F-12 引用的 `Tools\bootstrap-machine.ps1 -Roles bigmoney` **不在仓**（`git log --all` 零历史+本机盘缺件，2026-09-24 19:3x 实测）——疑似 T-08 式半提交（owner=O-1538 交付面 bm-a/GM 侧未 commit）。已发 MSG 请 owner 提交原件（守约式：不重建不代写，owner 原件为准）；owner 落件后本节步骤 2 改用一条命令形态。在此之前新节点一律用上述实际路径（bootstrap.py+两 register 脚本），验收门 A4 以实际路径判。

## 2. 共享件四机就绪验证表（A1-A6）

| 门 | 组件 | 在仓实况（r110 验证） | 新节点验收判据 |
|----|------|----------------------|----------------|
| A1 | 水位探针 `scripts\py_watermark.py` | ✓ 在仓·S6 常设链已接线·selftest 子命令离线自检 | `python scripts\py_watermark.py selftest` rc=0 |
| A2 | 看门狗 C7 `Tools\watchdog.ps1`（+`register_watchdog_task.ps1`） | ✓ 在仓·路径自适应·三机共享先例（bm-a R81 注入验收 10/10 真杀） | schtasks 查询 Bigmoney-LoopWatchdog 在册 |
| A3 | 迭代循环 `Tools\iteration_loop.ps1`（+`register_loop_task.ps1`） | ✓ 在仓·路径自适应 | schtasks 查询 Bigmoney-IterationLoop 在册 |
| A4 | 一键自举 | ⚠️ `bootstrap-machine.ps1` 缺件（§1 披露）；实际路径=`python bootstrap.py` | `python -m smoke_test` 23/23 PASS |
| A5 | 身份模板 | ✓ `fleet\_machine.json.template`（单角色）+ 本票新增 `fleet\_machine.dual-role.template`（双角色） | fleet\machine.json 含 main_owner 字段 |
| A6 | 数据面 | core48 日线 CSV 在仓（smoke 直读）；bars 1.09GB 与 Money02 深轴缓存**不入库**（`fleet\TRANSFER.md` A-变体·BigMoney-data 私库） | 首单选 §4 J-1 腿 L=纯仓内数据即跑；涉深轴腿 D=先走 TRANSFER.md |

## 3. 双角色身份模板

`fleet\_machine.dual-role.template`（本票新增，bm-a/BG-A 同盒先例的抽象）：
```json
{
  "machine_id": "bm-d",
  "role": "compute-node",
  "main_owner": "biggame",
  "borrow_compute": {"pool": "bigmoney-backtest", "priority": "BelowNormal", "law": "fleet-allocations s3"},
  "joined": "2026-09-XX"
}
```
主归属保主=Biggame 主活恒优先，空闲 CPU 借入 BigMoney 回测池；身份文件本地私有不入库（X104 教训，fleet\README.md §身份）。

## 4. 首单派工分片表（first-job assignment pack）

| 单 | 内容 | Runner/接口 | 数据面 | 判据/门 |
|----|------|-------------|--------|---------|
| **J-1** | **T-22 PROSPECT 虚拟时点 beat-rate 分片**（22 PROSPECT 员×base/x2 双面；t24 晋升腿 3 的实证源，消费方代码已点名「T-26 first-job pack」） | `python scripts\p5c_virtual_timepoint.py run --leg L --shard <i> --shards <N>`（原生分片参数；PROSPECT 池动态读） | 腿 L=本地 core48 日线 CSV（零 Money02 争用，clone 即跑） | P-5/P-5B 冻结口径（beat_rate_6m≥0.70 base 面门控·x2 披露）；**起跑前普查漂移门必设**（r105 坑律㊀：活面板不复现冻结计数即中止）；spawn 前由 T-22/T-24 owner 核 prereg 指定段——**禁新节点自定判据** |
| J-2 | 通用 BelowNormal 回测池入池（未来网格批/XSTOCK 类 post 链分片） | 各批自带 `--shard/--shards` 或 checkpoint 分片 | 按批 | 与三机完全相同：批起跑=schtasks/Start-Process BelowNormal·checkpoint 杀安全·err log 尾部必读（r107 律） |
| 禁区 | T-22 finalize（跨机 cells 合并）=**GM 并点专属**，新节点不碰；PROSPECT 成员文件/results\paper\ 零写（晋升执行归注册管线） | — | — | — |

J-1 分片建议：22 员按成员区间切（bm-d=前 11 员、bm-e=后 11 员）或按 --shard 均分；产出=results\t22\cells_*.jsonl（含 member 键，t24_prospect_promotion.py 读取面）。

## 5. 规则恒同条款（与 bm-a/bm-b/bm-c 完全一致）

- 满载低优先级池：回测批一律 BelowNormal（O-1136 工程正典）；Biggame 主活随时抢占（借算律）。
- 水位红牌闭环：watchdog C7 每 30min tick（红牌=尾 3 样本 py<70%+可跑批→僵尸三查杀+升级件 results\watermark_red.json）；**杀只清卡死进程、续跑归批既有自愈、C7 不代发**。
- 禁造任务凑数（O-1612 诚实律）；无活=水位 verdict=board_clear 合法 idle。
- 大文件传输一律走 fleet\TRANSFER.md 机制，禁塞 git。
- 写域纪律：每机只写自己心跳文件；票面 JSON 一律 python utf-8 无 BOM（r106 坑律）。

## 6. 新节点验收门（接入完成判据·全过=acceptance PASS）

1. `python -m smoke_test` 23/23 PASS
2. `python scripts\py_watermark.py selftest` rc=0（A1）
3. schtasks 查询 Bigmoney-IterationLoop + Bigmoney-LoopWatchdog 双任务在册（A2/A3；**以 schtasks /query 为准**，R49 坑律）
4. fleet\machine.json 含 machine_id/main_owner（A5）
5. 首心跳落 fleet\machines\<id>.json 且 last_seen/epoch/clock_read 单瞬同源（P-33）
6. S6 维护链一轮实跑无掩盖级异常（exit 契约原样上报）
7. 首单 J-1 分片起跑或诚实入队（禁空转）

## 7. 状态与维护

- r110 bm-b：本件 v1.0 交付（T-26 deliverable）。bootstrap-machine.ps1 owner-commit 请求 MSG 已发；owner 落件后 §1/§A4 更新一条命令形态。
- 后续维护：首单判据变更归 T-22/T-24 owner 预注册面；本件只维护接入机制事实（低频编辑）。
