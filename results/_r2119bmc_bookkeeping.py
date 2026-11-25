"""r2119 bm-c bookkeeping: report row, state keys, heartbeat.

Fresh read-modify-write on every file (multi-writer shared faces, r109/r2111 law), and the
heartbeat keeps every pre-existing key -- it only updates the fields the loop owns.
"""
import datetime as _dt
import io
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
assert os.path.isdir(os.path.join(ROOT, ".git")), "ROOT must be the repo root (r2114 lesson)"
MACHINE = "bm-c"
ROUND = 2119


def _now():
    return _dt.datetime.now().astimezone().replace(microsecond=0)


def _read(path):
    with io.open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _write(path, doc):
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    os.replace(tmp, path)


row = (
    "| 2026-11-26 07:0x | {ROUND} | **PRODUCT（产品优先律·watermark=绿 red=false lane=healthy·孤儿面=0·"
    "竞争窗 rc=0 CLEAN）**：全量冒烟用**分离进程**跑起来（r2115 遗留指针：上一轮被 5 分钟无输出上限杀掉→"
    "改 `pythonw -m smoke_test` 落 `logs/smoke_full_r2119.out`，本轮跑到 632 行仍在飞，**不宣称总数**）。"
    "边跑边修掉它吐出的红：①两张 CHECK FAIL 是**面比回执旧一代**不是算错——`etf_book_supply_gate_decision`"
    "（`CHECK FAIL 6/9 drift=money_constructions_that_are_gifts,cross_receipt_agreement,sources`→重生→"
    "`CHECK OK 9/9 CALIBER_IRRELEVANT_TO_MONEY`）、`etf_book_live_size_provenance`（`check 11/12`→`12/12`）；"
    "②**活书页每个日词都有日期，仍有 4 个日期没人认领**：两句话各印两个日子（源面被定价那天 + 本页被定价那天），"
    "`CLAIM_RULES` 无规则认领→`PRINTED_BUT_UNANCHORED / claims 21 ok 21 unmapped 4`。按 r1849 正法补两条规则"
    "（每条日期指向它自己的来源字段 `premium_forward.face_asof` / `floor_provenance.evidence_cutoff`，第二个日期"
    "都指向页面自己的 `priced_bar`），判据零改动 → `ANCHORED / claims 25 ok 25 unmapped 0`，`--selftest 46/46`，"
    "并加一条负控腿（源面缺席时这两个日子必须读 `unverifiable`，页面自己的价日仍 2 ok）；③六张落后一代的面重生"
    "并逐张复核 rc0（`do_or_wait 13/13`、`premium_persistence CHECK_OK`、`premium_forward ledger OK`、"
    "`label_census ok:true`、`ticket_band BOTH_LINES_HOLD_AT_SIGNED`、`cash_roll_today GC007 1.124%/yr`）；"
    "④`成本带`读者被自己上游的新词判死（`status='no_control' is not in the page's vocabulary`）——"
    "页面**本来就会印**这个词（「未通过控制臂」），是探针与渲染器两张手抄词表漂移了：改成单一来源"
    "`_NEEDS_VERIFY_STATUS_WORDS`，页面自检 476/477→**477/477**；⑤`etf_book_reader_faces check` rc0。"
    "**本轮主产品=第三种状态**：`idx_fut_carry_one_lot_ruler` 原判 `CONSUMERS_ONE_GENERATION_BEHIND`（三张 11-23 的面"
    "仍印旧代一手成本 IC 1,124,479 / IM 1,152,596，与今日尺差 **7,666 / 8,565 元**）→ 三张面全部重生；剩下的"
    "`tradeable_hedge_capital` 只差 **0.02 / 0.03 元**（相对 1.8e-8）却被判 `DISAGREE`——它和权威面是同一个测量，"
    "只是累加顺序不同。新增 `PRECISION_ONLY`，阈值有来历：指数报价存 4 位小数 × 乘数 200 = **0.02 元一个 tick**，"
    "再加一分钱显示舍入；超出仍判 `DISAGREE`（自检腿钉死「两个半 tick 必红」）→ "
    "`ONE_RULER_UP_TO_ONE_TICK / 10 consumers / rebuilt 0`，`--selftest 16/16`、`check CHECK_OK`。"
    "｜未做（如实）：①`Tools/s6_chain_bmc.py` 与 `smoke_test.py` **未接线**（开工即他人未提交脏面 +45 行，且 "
    "`pythonw Tools\\s6_chain_bmc.py 2117` 04:15 起一直在跑）→ 本窗不跑 S6 全链、不碰共享面；②冒烟日志里另有 "
    "~15 条面代差/语言面红（`etf_book_forward ledger`、`year_concentration_money`、`toll-ladder`、`premium_swap`、"
    "`phase_atlas_arms`（6:55 链上正在写）、`CEO one-pager` 等）**未逐条处理**，属链仍在推进的同一代差；"
    "③未改任何判据线去「修绿」。"
    "｜S0：machine.json=**bm-c**｜`orphan_face_probe` py_faces=8 **orphans=0**（resident_servers=2）｜"
    "`repo_write_contention --lookback-min 45` **rc=0 CLEAN**（单 codely 宿主 pid 97748）｜fetch 后 ahead=0 behind=0｜"
    "S0.5：`fleet/orders` **unacked=0**；集团 `origin/main:docs/decisions.md` 原生字节 **250,586 B sha256 79e3083b…** "
    "== 自持水位 → **零新决策零动作**（`git cat-file blob` 直落字节、不带 2>&1、不经 PS 字符串往返）｜"
    "S3：水位 **red=false / lane=healthy**（`results/watermark_red.json` 06:44）｜"
    "S7：孤儿面=0；IterationLoop/Watchdog/hooks 未触碰（脏树轮不做自愈）｜"
    "**CEO 三行**：当前活＝把「页面每个日词都有日期却仍有 4 个日期没人认领」补上规则，并把「一个 tick 不是两个答案」"
    "做成一等状态｜最近实物=`K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\qa\\daywords-two-date-r2119.md`"
    "（07:0x·活书页 ANCHORED 25/25·一手尺 ONE_RULER_UP_TO_ONE_TICK 16/16·9 条冒烟腿逐条转绿）｜"
    "下个里程碑＝等链跑完后用 `logs/smoke_full_r2119.out` 出**一次完整套件总数**，并把一手尺接进链与冒烟腿（≤48h）| "
    "记账：轮报告 1 处 + QA 1 件 + state/心跳 2 处 = 4\n"
).replace("{ROUND}", str(ROUND))

rp = os.path.join(ROOT, "round_reports-%s.md" % MACHINE)
with io.open(rp, "a", encoding="utf-8", newline="\n") as fh:
    fh.write(row)

# ---------------------------------------------------------------- state
sp = os.path.join(ROOT, "state-%s.json" % MACHINE)
st = _read(sp)
before = len(st)
st["round_no"] = ROUND
st["last_round_at"] = _now().isoformat()
st["last_decisions_sha"] = ("79e3083b85c130b8b57363d1ce4850520704cfbdf3fc41b8277e7e5ee39d6e16")
st["r2119"] = {
    "what": "day-word rules for the two two-date sentences + PRECISION_ONLY third state on the one-lot ruler",
    "fixed_legs": ["etf_book_supply_gate_decision", "etf_book_live_size_provenance",
                   "live-book day words", "etf_book_do_or_wait", "etf_book_premium_persistence",
                   "etf_book_premium_forward", "etf_label_census", "etf_book_ticket_band",
                   "etf_book_cash_roll_today", "etf_book_reader_faces", "ceo page link walk"],
    "smoke": "com.pythonw -m smoke_test -> logs/smoke_full_r2119.out (still running, no total claimed)",
    "not_done": ["chain wiring (Tools/s6_chain_bmc.py dirty by another host + running)",
                 "~15 remaining stale-generation legs in the mid-chain log"],
}
after = len(st)
assert after >= before, "state keys must not shrink"
_write(sp, st)

# ---------------------------------------------------------------- heartbeat
hp = os.path.join(ROOT, "fleet", "machines", "%s.json" % MACHINE)
hb = _read(hp)
now = _now()
hb["last_seen"] = now.isoformat()
hb["ts"] = now.isoformat()
hb["clock_read"] = now.isoformat()
hb["heartbeat_epoch_utc"] = int(time.time())
hb["round_no"] = ROUND
hb["current_task"] = ("r2119: day-word rules for the two-date sentences (page ANCHORED 25/25) + "
                      "PRECISION_ONLY third state on the one-lot ruler")
hb["verdict"] = "green"
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
_write(hp, hb)

print(json.dumps({
    "report_row_appended": rp,
    "state_keys": [before, after],
    "heartbeat_epoch_type": type(hb["heartbeat_epoch_utc"]).__name__,
    "round": ROUND,
}, ensure_ascii=False))
