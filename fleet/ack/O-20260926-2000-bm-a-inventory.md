# O-20260926-2000-bm-c · bm-a 回执①现状盘点快照（ack 即交·2026-09-26 20:4x）

- 受令机=本机 bm-a；本件=令 §二.1 盘点先行（ack 判据=现状盘点快照）+ 迁移执行书
- 盘点方法=实弹探针（schtasks /query 逐任务+XML 定义、Get-PSDrive、.git 存在性、Get-ChildItem 结构面）非凭记忆

## 一、现状根路径（root_path 现况）

- **盘符实况**：单卷 C:\（~1.86TB，已用 960GB/空闲 902GB）；**无 K: 盘、无 subst 映射**
- 按令 §一「物理无 K 盘用主数据盘」→ **目标基座根 = `C:\Fluxgroup\`**（root_path 登记随迁移批回执⑤落 fleet/machines/bm-a.json）
- 现状事实：全部产线/集团树挂 `C:\Users\sjs20\Desktop\FluxGroup\`（用户桌面内=基座九件骨架之外，即令所指「根外」现状面）
- Desktop=本地目录非 OneDrive 重定向（[Environment]::GetFolderPath 实证）；OneDrive 目录存在但未挂 Desktop
- **根外游离件 1 项**：`C:\Users\sjs20\Money\tools\watchdog.ps1`（MoneyAutoGuardian 任务指向）——**目标目录不存在=死任务**（遗留），迁移批处置=仅 disable+留待归档裁定（不迁移不存在物）

## 二、全部工作树清单（8 git 仓·零丢失自证对象）

| 仓 | 现路径 | 循环承载 |
|---|---|---|
| 集团仓 | C:\Users\sjs20\Desktop\FluxGroup（.git 在；cph4/docs/Tools 非 git 子面） | DecisionRound/NightRound/EvolutionTick/OrderSentinel/FluxBoardAuto |
| BigMoney | …\quant\bigmoney | IterationLoop(10min)+Autofill(10s tick)+LoopWatchdog(30min)+IntradayMarks(交易日 9:25) |
| BigCompute | …\compute\BigCompute | BigCompute-OSLoop |
| BigDomain | …\domain\BigDomain | BigDomain-OSLoop |
| BigLife | …\life\BigLife | BigLife-OSLoop |
| BigStream | …\media\BigStream | BigStream-OSLoop |
| MiniGame | …\gaming\MiniGame | 20 个 MiniGame* 任务（EngineTick/EvolutionTick/TickWatchdog/OllamaServe 等） |
| FluxVerse | …\gaming\FluxVerse | FluxVerse-DevLoop+FluxVerseTick |

- 树总体量 66.8GB（含 MiniGame projects Unity 库）；**同卷迁移=C:\→C:\ 改名=瞬时**（零拷贝）
- **Unity Bee 缓存面 3+ 处**（G11_CrazyWorker/G15_PetWorkCrew/G16_CrazyEstate 的 Library\Bee）→ 迁移后必清（令 §二.6 G15 坑族）
- BigMoney 侧循环脚本零绝对路径字面量（PSScriptRoot 自适应实证）→ 路径修全面=任务 XML 字面量

## 三、全 OS 任务清单（非 Microsoft 63 项·盘点面）

- **公司承载 36 项**（迁移改写面，任务 XML 字面量 `C:\Users\sjs20\Desktop\FluxGroup` → `C:\Fluxgroup\FluxGroup`）：
  - BigMoney 4：Bigmoney-IterationLoop(本循环)/Autofill/LoopWatchdog/IntradayMarks
  - BigLife/BigDomain/BigCompute/BigStream OSLoop 4
  - FluxVerse：DevLoop+Tick 2
  - MiniGame 20：AuditTick/BoardForge/CockpitBeat/DailyDigest/EditorSentry/EngineTick/EvolutionTick/GateTick/Housekeeping/OllamaKeepWarm/OllamaServe/PolicyTick/PopupWitness/RadarDeepTick/RadarTick/RedlineAudit/ResearchTick/SiliconWatchTick/TickWatchdog/TjcloudSync
  - 集团面 6：FluxBoardAuto/FluxGroup-DecisionRound/EvolutionTick/NightRound/OrderSentinel/GimmeAll-AutoSentinel
- 死任务 1：MoneyAutoGuardian（目标缺席·disable-only）
- 非公司 26 项（Adobe/AMD/ASUS/CarGZH 全 Disabled/Doubao/NVIDIA/OneDrive/Quark/SoftLanding）＝迁移零触碰
- 逐任务 Action/WorkingDirectory 定义已实录取证（迁移改写字面量对照基线，见 journal）

## 四、九件骨架对照（现状 → 目标）

| # | 项 | 现状 | 迁移动作 |
|---|---|---|---|
| 1 | README.md | 无基座级 | 新建（本机角色 bm-a+空区注记） |
| 2 | MiniGame\ | 真身在集团区 gaming\MiniGame 内（与正典相违） | **真身移至 C:\Fluxgroup\MiniGame（产线区）+ gaming\MiniGame=junction 回指**（单份不重克隆·正典律；20 个任务经 junction 零改写兼容） |
| 3 | FluxGroup\ | =现 Desktop\FluxGroup 全树 | 整树改名迁入 C:\Fluxgroup\FluxGroup |
| 4 | projects\ | 无（Unity 工程在 MiniGame\projects 内） | 新建空区（README 注记） |
| 5 | data\ | 无（数据面在仓内） | 新建空区（库外重资产后续按需） |
| 6 | archive\ | 无 | 新建空区（只读） |
| 7 | .codely-cli\ | 仅仓级（非基座级） | 新建基座级 |
| 8 | .tools\ | 无（工具面在仓级 Tools\） | 新建空区 |
| 9 | CODELY.md | 仅仓级 | 新建机器记忆面（stub+指针） |

## 五、迁移执行（六步映射·executor 已备）

- **执行器**：`C:\Users\sjs20\fluxgroup-migration-bma.ps1`（仓内证据副本 `results/_r267bma_fluxgroup_migration.ps1`；PSParser 零解析错）+ 日志 `C:\Users\sjs20\fluxgroup-migration-journal.log`
- 门序：预构建校验 36 件重定义 XML（移动**前**）→ 全任务 disable（不触运行中实例）→ 等在飞实例自然收（禁强杀兄弟循环·超时 40min=Abort）→ 零丢失自证（8 仓 HEAD+porcelain 入 journal；bigmoney 唯一合法脏=autofill_state.json 按 R245 快照族 stash；他仓脏=Abort）→ 同卷改名迁 → MiniGame 真身+junction → 九件骨架 → Bee 清 → 应用重定义 XML（3 重试）→ 全 re-enable+点火面留痕 → 完成标记 `results/fluxgroup_migration_receipt_bma.json`
- **fail-closed**：任何移动前门败=Abort 路径全任务 re-enable+旧树零动+aborted.flag；迁移后 XML 应用败=CRITICAL 留痕+下轮 bm-a 实例修复
- **点火实测**=迁移后各任务自然下一 tick（BigMoney 10min 内即首轮）＝回执③逐线证据由 journal+次轮实测共同构成
- **物理依赖留痕（O-1730 唯一暂缓事由票内化）**：迁移须停本执行体自身所在循环→执行器由本轮**末动作**分离启动、以本实例退出为门（detached+轮外执行）——开工即同轮（盘点/零丢失法/骨架/执行器全备于本轮），物理移动在实例间窗完成，窗限 09-29 12:00 内
- 下轮 bm-a 实例 S0 起自新路径：**组装回执五件**（树快照九件对照②前后任务清单③点火证据④8 仓 HEAD 恒等⑤root_path 登记 fleet/machines/bm-a.json）+推送

## 六、风险与豁免如实注记

- bm-a 无 K: 盘（bm-c 有）→ 依令用主数据盘 C:\；如后续需统一 K: 语义可 `subst K: C:\Fluxgroup`（非本轮动作，root_path 以登记为准）
- 同窗多司循环停机窗=迁移执行期（预计分钟级：同卷改名瞬时+门等待为主）；兄弟循环在飞轮自然收尾不强杀
- 集团仓若迁移时点脏（group 任务写入窗）→ Abort+重试窗开放（journal 可查），窗限内多次重试合法
