"""r665: append-mode canon additions (zero rewrite of existing bytes):
THEME_EVENT_LIBRARY.md §九 / METHODOLOGY_ASSETS.md E29 card / TREASURE_REGISTRY row."""
import io

LIB = "research/shortline/THEME_EVENT_LIBRARY.md"
METHOD = "knowledge/METHODOLOGY_ASSETS.md"
TREASURE = "knowledge/TREASURE_REGISTRY.md"

sec9 = """

## 九、R6 起点探测面网格普查（2026-10-04 bm-a r665·T-2026-10-04-165-P1 续作·E28 滞后确认律的下一刀）

> 背景与问题：v0.3 诚实披露「爆发确认规则=滞后确认器非起点探测器」（CEO 锚 16 例仅 2 例 ±30td 命中）——本节问廉价下一问（O-1901 意义门·census before burn）：**哪类更早的日线面能探测 CEO 锚起点？** 本节=描述性探针非判决批：零注册资格零纸盘资产零判线零账本行；任何判决消费（起点判据入 prereg）须新冻结预注册。

- **规则（冻结·先声明后跑·零看结果调线）**：四候选起点面——nearlimit7（单日涨幅 ≥+7%）/ volstart（量 ≥2.0×前 60 bars 中位且日涨幅 ≥+3%）/ break60（收盘 > 前 60 日收盘最高）/ fast10（10td 收益 ≥+10%）；扫描窗 = 锚−60..+40 bars（锚映射到首个 ≥锚交易日·窗头截断如实披露）；主判据 = |Δtd| ≤ 10、对照 = |Δcal| ≤ 30（v0.3 同面）；基线 B0 = v0.3 爆发规则逐事件记录**引用不重算**（单源）。
- **网格结果（16 事件 × 4 面）**：**fast10 = 最优起点面**——12/16 窗内起火、**7/16 落 ±10td**（中位 Δ=+2td·点火后首个十日快腿）vs B0 2/16@±30cal；volstart 9/16 起火但中位 −21td、|Δ| 中位 22（早而散）；break60 12/16 起火中位 −24td、|Δ| 中位 53（更早更散）；nearlimit7 仅 4/16（A 股 ETF 题材启动少以近涨停单日开场）。
- **锚双面性发现（诚实面·E29 律）**：5 个窗外起火中 4 个为负 Δ（CYB2013 −30 / SOE2015 −38 / TECH5G2019 −56 / DEEPSEEK2025 −55）——**机械起点可比 CEO 共识锚早数周**（锚亦可能是滞后共识面）；GOLD2024 +28 = 慢研磨型。未来起点判据预注册须先裁定「锚真值口径」（锚 = 叙事共识 vs 机械起点）或用非对称容差，**禁拿对称 ±N 直接判**。
- **4 无起火**：BELTROAD2014 / ZHONGTEIGU2023 / AI2023 / PV2021（头截断）——慢烧/代理晚面·单日族看不见，如实披露不补火。
- **消费指向（一刀判决消费仍须新冻结 prereg）**：fast10 = 题材判决批点火轴的候选起点面（v0.3 算法事件集上的持续性别重测、R4 两问重演均须以本面重定锚）；E28 集群主导律同窗适用（fast10 网格消费前同日集群分层）。
- **产物**：results/theme_ring/theme_ignition_face_probe.json+csv + scripts/theme_ignition_face_probe.py（selftest 13/13·确定性零 rng·预算 60s 内·B0 引用单源）。
"""

e29 = """
- **E29 起点探测面网格法+锚双面性律（start-face anchor-grid probe·theme line R6 实证）**（proven·描述性探针）：①**起点面网格法**——事件起点探测器的评估不靠单规则撞锚，而是「锚 vs 候选面」网格：每锚在 −60..+40 bars 窗内逐面扫首火日，双容差读出（±10td 主判 + ±30cal 对照），基线规则**引用不重算**（单源）；实测排序 fast10（10td≥+10%）7/16@±10td（中位 +2td）>> nearlimit7 4/16 > volstart/break60（早火但 |Δ| 散 22/53 = 早期预警面非紧起点）——「点火后首个十日快腿」携带最强起点信息，「单日近涨停」在 ETF 题材面罕见。②**锚双面性律**——CEO 共识锚不是机械起点的天然真值：4/5 窗外火为负 Δ（−30..−56td·机械起点早于叙事锚数周）——起点判据预注册前必须先裁定锚真值口径（叙事共识 vs 机械起点）或采用非对称容差，**禁拿对称 ±N 直接判**（拿滞后锚判早火面=系统性误杀真探测器）。证据=results/theme_ring/theme_ignition_face_probe.json+csv+scripts/theme_ignition_face_probe.py（r665 bm-a·selftest 13/13·16×4 网格）。
- 2026-10-04 08:4x（bm-a r665·题材线 R6 起点探测面网格普查收口窗）：捕获律 append E29 起点探测面网格法+锚双面性律（描述性探针收口步·O-20260924-2100 捕获律 live 实证·零判线零注册宣称）。
"""

treasure_row = """- 2026-10-04 08:4x（bm-a r665·题材线 R6 起点探测面网格普查·考面冻结类）：**入册=题材起点探测面网格 v0.6**〔results/theme_ring/theme_ignition_face_probe.json+csv（16 事件×4 面网格·fast10 7/16@±10td 中位+2td vs 爆发规则 2/16@±30cal·锚双面性 4/5 窗外火为早火 −30..−56td）+scripts/theme_ignition_face_probe.py（selftest 13/13·L1 零网络·确定性）〕——E29 起点面网格法+锚双面性律随批；一刀判决消费须新冻结 prereg+E28 集群分层。T-2026-10-04-165-P1。
"""

with io.open(LIB, "a", encoding="utf-8", newline="") as f:
    f.write(sec9)
with io.open(METHOD, "a", encoding="utf-8", newline="") as f:
    f.write(e29)
with io.open(TREASURE, "a", encoding="utf-8", newline="") as f:
    f.write(treasure_row)
print("appended: LIB sec9 +, METHOD E29 +, TREASURE row +")
