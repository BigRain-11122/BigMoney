"""r2122 bm-c: append one round-report row (fresh read -> append -> write)."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "round_reports-bm-c.md")

ROW = """
| 2026-11-26 08:3x | 2122 | **PRODUCT（产品优先律·watermark=绿 red=false lane=healthy·孤儿面=0·竞争窗 rc=0 CLEAN 单宿主)**: ①**把一句早就印在页上的「8%」补上价钱**——CEO 一页纸 §⑦ 一直写着「先咬住的是 8% 波动尺」，却从没印过这本书实测多少、把钱压到 8% 要多少本钱。新段四个 bullet：账本 1052 根 bar 实测年波动 **14.05%**（= 一年 **140,528 元**的波动钱，比 8% 高 6.05pp）；要真等于 8%，资本得是 **1,756,600 元**（净值 1.76 倍），代价是账面年化 27.19% → **15.48%**（夏普不变——8% 是尺码不是质量）；这笔资本摆不摆得下看权益袖 1% ADV 线：最松的 session 容得下（窗口 [1,756,600, 2,436,420]）、中位只到 1,142,112、最紧 784,076；**两种读法并列不合并**（同尺寸读法在最紧的一天 = 那条线的 127.54%）。②**关掉一个「链腿点名了一个没进 git 的脚本」的洞**（r1783 族实证）：`scripts/carry_risk_dial_vs_book.py` 被 `Tools/s6_chain_bmc.py` 一条链腿 + `smoke_test.py` 两腿点名，而脚本/面/页三件从未进过 git——本机全绿，任何新克隆跑三腿打空。三件已交付，并**把这条洞变成机械检查**：`smoke_test.py` 新增 `unwired_script_problems()` + 两条腿（正判：每个被腿点名的脚本要么在 origin/main、要么已 staged；负控：假名字必须被报出）。③**一页纸第一段「先读这个」的 20 处日期此前无规则可核**（含 lane 尾日、欠的会话、结论句两处参照日、r2121 许可段三处）→ 补 7 条映射规则 + 3 个如实分类桶（owed_sessions / provisional_bars / receipt_ledger / quoted_producer_sentence，均计数照印不计入已核）→ 现在 **136 处日期逐句对上引用面、0 判不了、0 无规则可核**（判词 PRINTED_DATES_AGREE）。④顺带关一条面代差红：`etf_book_promotion_provenance` STALE → run → **CHECK_OK**。｜证据：dial 面 `--selftest` **20/20**、`check` **CHECK_OK**；日词审计 run **PRINTED_DATES_AGREE** / check rc0 / `--selftest` **30/30**；`ceo_live_usage.py selftest` **ALL PASS**；`page_repeat_guard scan` 4 face **0 repeated**；接线守卫修前报出该脚本、暂存后 POSITIVE none 且负控仍说话（`results/_r2122bmc_unwired_probe.py` rc0）。QA=`qa/dial-on-the-page-r2122.md`。｜未做（如实）：①**全量冒烟本轮未跑完**——分离进程跑到 675 行仍在飞，6 条 FAIL 全属 r2121 已登记 carried（paper book NAV 身份 / lane appended nothing / k-gap 面代差 / phase_atlas_arms 9 腿 / toll-ladder / 一条本轮已修），**不宣称套件总数**；②k-gap 面（2026-11-20 vs 票面 11-25）仍无链腿重跑它；phase_atlas_arms 三臂需重烧；`paper book` 的 navdev=6.5e-09 被判 NAV_IDENTITY_BROKEN——容差来历未查清前不擅放宽；③未改任何判据线去「修绿」。｜S0：machine.json=**bm-c**｜`orphan_face_probe` py_faces=4 **orphans=0**（resident_servers=2）｜`repo_write_contention --lookback-min 45` **rc=0 CLEAN**（单宿主 pid 15272）｜fetch 后 ahead=0 behind=0｜S0.5：`fleet/orders` 117 件 vs 心跳 orders_ack → **未回执 0**；集团 `origin/main:docs/decisions.md` 原生字节 **250,586 B sha256 79e3083b…** == 自持水位 → **零新决策零动作**（`git cat-file blob` 直落字节、不带 2>&1、不经 PS 字符串往返）｜S3：水位 **red=false / lane=healthy**；饱和引擎 `status` **rc0 alive**（last_verdict=idle·struct_wait 0）｜S7：`register_loop_task` 幂等 no-op（pin=0·当前 0·PT5H·首火 08:30）；`register_watchdog_task` 重注册 OK 但 **S4U XML 翻转仍被拒（拒绝访问）**（carried·非本轮引入）；pre-commit / pre-push 两爪重装（LF 归一）；`attrition_ledger_guard scan` **CLEAN**（4 账本·3 处历史缩行 healed 照录）｜**CEO 三行**：当前活＝把「8% 波动」这句话的价钱印到一页纸上，并堵上「链腿点名了没进 git 的脚本」｜最近实物=`K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\docs\\live_usage\\LIVE-2026-11-26.md`（§⑦ 旋钮段·14.05% 实际 vs 1,756,600 元才等于 8%）｜下个里程碑＝k-gap 面与 toll-ladder 两条 carried 红关掉 + 分离进程出一次完整套件总数（≤48h）｜记账：轮报告 1 处 + QA 1 件 + state 1 处 + 心跳 1 处 = 4 |
"""

with io.open(PATH, "r", encoding="utf-8", newline="") as fh:
    text = fh.read()
if not text.endswith("\n"):
    text += "\n"
with io.open(PATH, "w", encoding="utf-8", newline="") as fh:
    fh.write(text + ROW.lstrip("\n"))
print("appended %d bytes -> %s" % (len(ROW), PATH))
