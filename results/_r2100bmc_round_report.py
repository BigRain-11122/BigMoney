import io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(ROOT, "round_reports-bm-c.md")

line = (
    "2026-11-25T21:1x+08:00 | r2100 | bm-c | **CONTENTION 轮**（证据 `results/_repo_write_contention.bm-c.json`："
    "verdict=CONTENTION rc3，3 宿主存活〔85312@20:01 / 98008@20:02 两个 interactive + 本窗 100140@20:55〕，"
    "开工前 155 张共享面已被别宿主写过、重叠窗内不可归因 0 张；工作树脏 1,949 件）→ 按 r1907 只落新增文件面，"
    "禁改共享面、禁重跑 S6 链、不跑全量冒烟；state/心跳两面均为多宿主共写态面（心跳 20:50 由对端写过），本轮不碰。"
    "watermark verdict=**绿**（`results/watermark_red.json` red=false · lane=healthy · 21:05:04 采样）。"
    "**PRODUCT**：桌面上第一次有人把「按今早的指令，这本书一年挣多少」算成一行钱——"
    "引擎自己只印 carry（125,799 元），L1 的 43,818 元与现金利息 4,135 元从来没进过同一行。"
    "新面 `scripts/policy_return_lattice.py` 枚举 16 个整手组合（IC/IM 各 0–3 手），把每一格按引擎自己的上限"
    "（保证金 ≤35% NAV、名义 ≤2.5× NAV）判合法，再按策略文档的 8%–12% 判带："
    "实跑判决 **INSTRUCTION_ABOVE_TARGET_BAND**——指令落点 IC1/IM1 期望 **173,752 元 = 17.38% 本金**，"
    "比 12% 上限高 **+5.38pp**；阶梯上唯一落在带内的合法格是**只买 IM 一手 = 9.05%**（保证金 13.0%、名义 1.09×），"
    "IC 一手单独 13.49% 已出带。第二件：**目标带其实是本金的一句话**——按住今天这两手不动，"
    "本金 **1,787,038 元**时正好 12%、**4,313,217 元**时正好 8%（标 `counterfactual_lots_held`，"
    "到那些本金时引擎权重规则会要更多手，所以是线不是计划）。第三件：引擎把期货腿的波动截在 3.5% 预算内，"
    "于是几乎每格都印 6.0%，把两手（未截尾 10.5%）和一手（6.8%）抹成同一个风险读数——面里两列并列印，"
    "截尾是政策不是测量。｜证据：`--selftest` **15/15**；负控 `python results\\_r2100bmc_lattice_negative.py` **13/13**"
    "（手改数→CHECK FAILED 且不含 STALE／输入字节动→STALE／缺面→STALE 且点名路径／挪动目标带→旧判词失效／"
    "丢一格→红／合计等于分项／格数=(MAX+1)²／判词落在引擎自己那一格／页面存在且含判词节）；`check` **CHECK_OK rc0**（16 格）。"
    "面 `results/policy_return_lattice.json`、页面 `research/POLICY_RETURN_LADDER.md`、QA `qa/policy-return-ladder-r2100.md`。"
    "｜未做（如实）：①未接进 `Tools/s6_chain_bmc.py` 与 `smoke_test.py`（两者均为对端未提交脏面），本面暂为 check-only 独立腿；"
    "②未重生 11-23 那三张 carry 面（r2099 已列为下一轮工单，CONTENTION 禁写共享面，且双宿主同跑=双烧）；"
    "③全量冒烟未跑（570+ 腿，竞争窗）；④state-bm-c.json / 心跳未写（多宿主共写态面，留给在跑宿主）。"
    "｜S0.5 双扫：fleet/orders **117 件** vs 心跳 orders_ack **331 条**（去 .md 归一）→ **未回执 0**；"
    "集团 `origin/main:docs/decisions.md` 原生字节 **250,586B** sha256 **79e3083b85c130b8…** == 自持水位 → 零新决策零动作"
    "（`git cat-file blob` 直落字节，不经 PS 字符串往返）。｜S7：orphan_face_probe（py_faces=6 / **orphans=0** / resident_servers=2）；"
    "attrition 账本本窗未跑（无账本改动）；IterationLoop / Watchdog 未触碰（脏树轮不做自愈）。"
    "｜**本地未达 origin commit 数**：见下方送达行。"
    "｜**CEO 三行**：当前活＝把三条腿的期望收益算成一行钱，并拿它去对 8%–12% 的目标带"
    "｜最近实物=`K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\research\\POLICY_RETURN_LADDER.md`"
    "（2026-11-25T21:1x·指令 17.38% vs 带 8–12%·唯一带内合法格=IM 一手 9.05%）"
    "｜下个里程碑＝把「按权重配手」与「按期望配手」二选一定成纪律并接进链与冒烟腿（≤48h）"
    "| 记账：轮报告 1 处 + 页面 1 件（脚本渲染）+ QA 1 件 = 3\n"
)

with io.open(path, "a", encoding="utf-8", newline="\n") as f:
    f.write("\n" + line)
print("appended", len(line), "chars")
