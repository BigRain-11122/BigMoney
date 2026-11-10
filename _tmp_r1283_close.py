import json, os, time
from datetime import datetime

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
os.chdir(ROOT)

now = datetime.now().astimezone()
iso = now.strftime("%Y-%m-%dT%H:%M:%S%z")
iso = iso[:-2] + ":" + iso[-2:]
epoch = int(time.time())

# ---- 1) methodology card (E518) ----
card = """
### E518 · 同一根 bar 两个 k：差的是分母，不是仓位（r1283 bm-a）

**一张面把同一天的账写了两遍，两个 k 都对，但读者只有一个数可用。** `results/etf_book_positions.json` 里
`accrual.last`（换手前持仓，按本 bar 收盘价估值，NAV ¥1,007,455.39 随当日 +0.7455% 滚动）与
`ledger_row`（换手后持仓，同一组收盘价，NAV 钉在政策本金 ¥1,000,000，现金 = 本金 − 风险腿）都写着
bar `2026-11-10`。手数差 690/925/487/674 → 693/891/473/677 共 ¥7,618.40 由换手解释；NAV 差 ¥7,455.39 =
风险腿差 + 现金腿差。于是同一个风险腿除滚动 NAV 得 k=0.397063、除钉住本金得 k=0.392405，差 0.004658
（按前账 NAV 折 ¥4,693 名义额）。

**正法**：不是让两本账相减，而是说清每句话除的是什么——「k 相对当日 NAV」与「k 相对政策本金」是两个量，
任何只印一个 k 的句子都要点名分母；换手前/换手后的账分立披露，且 ROI 只存在于随收益滚动的那一本。

**证据**：`scripts/etf_book_base_basis_audit.py` selftest **14/14** + `check` CHECK_OK（从已发布行重算判词）；
S6 腿 `etf_book_base_basis_audit`（排在 `etf_book_order` 之后）+ 产物 `results/etf_book_base_basis_audit.json`
+ `docs/live_book/BASE-BASIS.md`（逐只分解手数差、指名票面 `base_k_executed` 读的是换手前那一本）。

**How**：任何「同一账户同一天两个比例」的读数，先问分母是不是同一个（滚动 NAV / 政策本金 / 名义额），
再问分子是不是换手同一侧的持仓；两问有一个不同，相减出来的数就不是资金差错。
"""

with open("knowledge/METHODOLOGY_ASSETS.md", "r", encoding="utf-8") as fh:
    _cards = fh.read()
if "### E518" not in _cards:
    with open("knowledge/METHODOLOGY_ASSETS.md", "a", encoding="utf-8") as fh:
        fh.write(card)

# ---- 2) round report line ----
row = (
    "\n| %s | r1283 | **继承窗（launcher 死于静默闸）**：上一窗在 20:50 起的 `s6_chain_bma.py 1283` 是孤儿但仍在推进，"
    "按「死窗遗产不是孤儿」律等它跑完而不是抢跑；它跑到第 70/191 腿（`etf_book_sleeve_paths`）后进程消失，"
    "全链未完成，如实记。**PRODUCT（本轮新面）**：`scripts/etf_book_base_basis_audit.py` —— CEO 一页纸上的 k 与账户实际比例"
    "差 0.004658（¥4,693 名义额），根因不是仓位错而是**分母不同**：`accrual.last` 的 NAV ¥1,007,455.39 随当日 +0.7455% 滚动，"
    "`ledger_row` 的 NAV 被钉在政策本金 ¥1,000,000、现金是残差；两账手数差 690/925/487/674→693/891/473/677 共 ¥7,618.40 由换手解释，"
    "NAV 差 ¥7,455.39 = 风险腿差 + 现金腿差。面按手数×收盘价逐只分解、指名票面 `base_k_executed`=0.397063 读的是换手前那一本，"
    "并把「别把两个 k 相减当资金差错」写成方法论卡 E518。**VERIFY**：selftest 14/14（含「票面读后账时不得再指控」与「不同收盘价必须改名」两条负控）"
    "+ `check` 从已发布行重算 CHECK_OK + S6 腿 `etf_book_base_basis_audit` 已接线并在 `--list` 中实见（排 `etf_book_order` 之后，"
    "本窗以同一条命令直跑验证 rc0，链内首跑归下一轮）。CEO 可见面按最终树重出 5 腿全 rc0："
    "`LIVE-BOOK-20261110`（order 5 names / book 392,536 / cash 607,464）、`REPORT-2026-11-10`、`LIVE-2026-11-10`、`scorecard_daily`、`build_status`。"
    "**OPS**：orphan 面 2（D:\\FluxGroup 两个吸嘟嘟 python，非本仓车道→只报不杀）；orders 114 文件 / 123 ack / 0 未回执；"
    "D-19 decisions `2ffcc70c` 水位未动（零新行）；饱和引擎 alive（queue_depth 0）；watermark red=false / lane healthy。"
    "**STILL OPEN（如实）**：继承链 121 腿未跑（含 `etf_book_exposure_timing` 之后的研究面），全链 rc 记录停在 70/191；"
    "本窗只定向提交本轮自有件与 CEO 可见面，其余 ~500 个链产物仍未提交（下一轮要么续跑要么定向收口）。"
    "**NEXT**：①用 `--only` 续跑 71→191 腿并收口全链记录；②把 `next_order_base` / `ledger_row` 的分母口径写进票面头行（E518 的消费面）。"
).replace("{TS}", iso)

with open("round_reports-bm-a.md", "a", encoding="utf-8") as fh:
    fh.write(row)

# ---- 3) state ----
sp = "state-bm-a.json"
with open(sp, "r", encoding="utf-8") as fh:
    st = json.load(fh)
st["round_no"] = 1283
st["updated"] = iso
st["work_r1283"] = ("two books on one bar: accrual.last (pre-trade holdings at this bar's closes, NAV rolls with "
                    "the day's +0.7455%) vs ledger_row (post-trade holdings, same closes, NAV pinned to the policy "
                    "capital 1,000,000 with cash as the residual) -> same risk leg, two denominators, k 0.397063 vs "
                    "0.392405. The audit face decomposes the lot gap per symbol and names which book the ticket's "
                    "base_k_executed read. Inherited orphan chain died at leg 70/191; not raced, reported.")
st["verify_r1283"] = ("etf_book_base_basis_audit selftest 14/14 + check CHECK_OK (recomputed from published rows) + "
                      "run rc0 (SAME_CLOSES_TWO_LOTS risk_gap -7,618.40 k_gap +0.004658 ticket_sized_from "
                      "accrued_pre_trade) | S6 leg wired and visible in --list after etf_book_order (verified by "
                      "running the same command directly; in-chain first run belongs to the next round) | "
                      "CEO faces re-derived on the final tree 5/5 rc0: LIVE-BOOK-20261110 / REPORT-2026-11-10 / "
                      "LIVE-2026-11-10 / scorecard_daily / build_status | inherited chain 70/191 legs, process gone, "
                      "121 legs not run (reported, not claimed) | orphan 2 (both D:\\FluxGroup gimme python, outside "
                      "this repo's lanes -> reported, not killed) | orders 114/123/0 | D-19 decisions 2ffcc70c "
                      "unchanged -> zero action | saturation engine alive queue_depth 0 | watermark red=false")
with open(sp, "w", encoding="utf-8") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)
    fh.write("\n")

# ---- 4) heartbeat ----
hp = "fleet/machines/bm-a.json"
with open(hp, "r", encoding="utf-8") as fh:
    hb = json.load(fh)
hb.update({
    "last_seen": iso,
    "ts": iso,
    "clock_read": iso,
    "heartbeat_epoch_utc": epoch,
    "doing": "r1283: etf_book_base_basis_audit published (two books on one bar, k gap 0.004658); CEO faces re-derived",
    "verdict": "green",
    "idle_rounds": 0,
    "agenda_starved": False,
})
with open(hp, "w", encoding="utf-8") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
    fh.write("\n")

assert isinstance(hb["heartbeat_epoch_utc"], int)
print("ok", iso, epoch)
