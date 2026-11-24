"""r2074 closeout (bm-c): append the round line and bump state-bm-c.json, byte-minimally.

Runs under the r1907/r1927 contention branch (another codely body, pid 79608, is alive in
this tree), so this script touches ONLY the two ruled targets -- the machine's own round
report line and its own state keys -- and never rewrites a whole shared face.

  python results/_r2074bmc_closeout.py
"""
import io
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
REPORT = os.path.join(REPO, "round_reports-bm-c.md")
STATE = os.path.join(REPO, "state-bm-c.json")

ROUND = 2074
STAMP = "2026-11-25T05:43:31+08:00"

ACTIVITY = (u"r2074 · 新增文件面（竞争窗 r1907/r1927）：把「0.94pp 到底是不是超帽」变成可算的分辨率问题——"
            u"单窗 306 根 β 读数抽样抖动 0.141809 是差额的 6.56 倍，要让差额自己 95% 可辨需 50,541 根日线"
            u"（207.1 年），一次读数最小只看得见 12.091pp／120,907 元；1σ 抖动 61,687 元 = 要削掉的 19,543 元的 3.16 倍")

LINE = (
    u"2026-11-25T05:43:31+08:00 | r2074 | bm-c | **PRODUCT（产品优先律·watermark 绿（red=false·lane=healthy·"
    u"next_pick 他机 claimed）·孤儿面=0（py_faces=4 / orphans=0 / resident_servers=2）·竞争窗 rc=3 CONTENTION"
    u"〔对端 codely.exe pid 79608 自 2026-11-24T22:39 起仍活、最后写入 2026-11-25T05:31:43 的 "
    u"research/ARBITER-BOARD.md、23 张共享面在轮首前被动过，证据 results/_repo_write_contention.bm-c.json〕"
    u"→ 按 r1907/r1927 只落新增文件面：未改共享面、未重跑 S6 链、未跑全量冒烟、未改心跳面（对端在写））**："
    u"前两面把这件事算到了钱（20.941% vs 20%、该卖 19,543 元、整手 144 手、往返 31.27 元），也都说了「差额在噪声里」——"
    u"可没人算过**这点差额要多少历史才量得出来**。本面把它算成三个数：①**要多少根日线**——β 估计抖动按 1/√n 收缩，"
    u"单窗 306 根的抽样抖动 0.141809（β 单位）是差额 0.021627 的 **6.56 倍**，要让差额本身在 95% 下可辨需 "
    u"**50,541 根日线 ≈ 207.1 年**（判据线 20 年）→ `UNRESOLVABLE_BY_MEASUREMENT`；②**一次读数最小能看见多大的超帽**——"
    u"窗口钉在 306 根时是 **12.091pp / 120,907.12 元**，是今天差额的 12.8 倍，任何比这更小的「超帽/回帽」都只是尺子在抖；"
    u"③**这笔抖动多少钱**——票面仓位固定口径 1σ = **61,687.30 元**（要削掉的差额 19,543.03 元的 **3.16 倍**），"
    u"帽隐含仓位口径 ±12.239pp = 122,386.05 元，帽子面行文口径（β 当量）±5.892pp = 58,920.00 元，两口径差 +4.70% "
    u"并列不混算。第四段把「尺子在抖 vs 世界在动」拆开并**自曝弱点**：69 窗互叠 90%，1669 根只够 5.45 个独立窗、"
    u"自由度 4.45，路径离散度换算出的「真实漂移」区间是 **[0.0000, 0.2572]**（β），下端连零都排除不了——"
    u"所以这一段只是颜色，判词只吃单窗抖动与差额两个数。结论落在一句话上：**这不是测量问题，是规矩问题——"
    u"把尺子钉死、按日历复核，别按读数复核**；三种读数（全史 19.999% / 当窗 20.941%）并列印出、`adopted: false`，本面不选。｜"
    u"证据：scripts/etf_book_cap_beta_power.py（selftest **17/17 OK**·run rc0·--check **CHECK OK** rc0 "
    u"重算 facts 逐字段相等 + 页面 marker 块逐字相等）+ results/etf_book_cap_beta_power.json + "
    u"research/ETF_BOOK_CAP_BETA_POWER.md + qa/cap-beta-power-r2074.md + 负控 "
    u"results/_r2074bmc_cap_beta_power_negctl.py **8/8 PASS**（改 bars_needed→rc3 含 CHECK FAILED 且点名字段且**不含** STALE／"
    u"改 verdict→点名 verdict／动 inputs_digest→STALE 且不含 CHECK FAILED／改页面判词行→点名 page block（先断言该行真在页面里，防真空腿）／"
    u"删收尾 marker→page block unreadable／删面→STALE face missing／复原→CHECK OK 且两张上游面 sha256 恒等=零污染）。"
    u"**自捕两枚**：①首版把「差额折 pp」用了 cap/β 口径而差额本身用票面 k 口径，混算后 1σ 抖动被写成 58,916 元——"
    u"当场改为同一个 k 口径（61,687 元）并把帽子面 β 当量口径单列；②自检里一条 `assert ... in blk[:0]` 是恒真假腿"
    u"（r1935 同族），当场换掉，改为断言页面块必须印出本面自己的判词与日线数。｜"
    u"未做（如实）：`ceo_live_usage.py` 帽子行未接（共享面）——建议改法=补一句「±0.94pp 在本书历史的分辨率之下，需 5 万根日线，见 ETF_BOOK_CAP_BETA_POWER」；"
    u"本面未接冒烟腿/S6 腿（共享面）；全量冒烟连续第 19 轮未跑（红腿读数仍是 2026-11-24T20:12:28 的 765 腿/34 红）；"
    u"S6 链连续第 19 轮未跑；心跳面由对端 05:28 写过，本窗不覆盖。｜"
    u"S0.5 双扫：fleet/orders **117 件**、心跳 orders_ack 331 条、**未回执 44 件（2026-11 内 0 件）**"
    u"（44 件全为他机 lane 广播，按 r2066 判例不逐令补 ack）；集团 origin/main:docs/decisions.md 原生字节 **250,586B "
    u"sha256 79e3083b85c130b8…**（git cat-file 直落临时件再 Get-FileHash，不经 PS 字符串往返，r1911/r2048 律）"
    u"**== 自持水位** → 零新决策零动作；fleet/inbox 空。｜"
    u"S7：orphan_face_probe 已跑（py_faces=4 / orphans=0 / resident_servers=2）；schtasks 自愈本轮未触碰（对端在飞，重注册会打断）；"
    u"attrition tripwire 未跑（竞争窗，与冒烟/S6 同列延后）。｜"
    u"**本地未达 origin commit 数**：本轮 commit 前实测 origin/main…HEAD = 1/32（本行 commit 后再 +1；自指计数差 1 按 r2062 addendum-2 判例）。｜"
    u"下轮指针：(a) 静窗后把「这个差额在本书历史的分辨率之下（6.56 倍抖动 / 50,541 根 / 207 年）」接进 CEO 一页纸帽子行（共享面，一句披露非新判据）；"
    u"(b) 给本面接一条冒烟腿（判据=bars_needed/years/verdict 必须同代，面 stale 即红）；(c) 全量冒烟 + S6 分批补跑（连续第 19 轮）。｜"
    u"**CEO 三行**：当前活＝回答「0.94pp 是不是超帽、值不值得为它调仓」——数据判不了：尺子抖 6.56 倍，要 50,541 根日线（207 年），"
    u"一次读数最小只能看见 12.09pp｜最近实物=K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\research\\ETF_BOOK_CAP_BETA_POWER.md"
    u"（2026-11-25T05:43·selftest 17/17·负控 8/8·--check rc0）｜下个里程碑＝接 CEO 一页纸帽子行 + 接冒烟腿（≤48h）。| "
    u"记账：轮报告 1 处 + state 1 处 = 2（心跳面由对端写、本窗不改；无方法论新增：把「差额超出历史分辨率」做成可复核读数属证据与载体）。"
)


def append_report():
    with io.open(REPORT, "r", encoding="utf-8") as fh:
        text = fh.read()
    if "| r2074 | bm-c |" in text:
        print("REPORT already has r2074 -- left untouched")
        return False
    sep = "" if text.endswith("\n") else "\n"
    with io.open(REPORT, "a", encoding="utf-8", newline="") as fh:
        fh.write(sep + LINE + "\n")
    print("REPORT appended r2074")
    return True


def patch_state():
    """Line-level byte patch: only the three owned keys move, the rest is untouched."""
    with io.open(STATE, "r", encoding="utf-8", newline="") as fh:
        lines = fh.read().split("\n")
    hits = 0
    for i, ln in enumerate(lines):
        s = ln.strip()
        if s.startswith(u'"round_no":'):
            lines[i] = u' "round_no": %d,' % ROUND
            hits += 1
        elif s.startswith(u'"activity_now_round":'):
            lines[i] = u' "activity_now_round": %d,' % ROUND
            hits += 1
        elif s.startswith(u'"activity_now":'):
            lines[i] = u' "activity_now": %s,' % _json_str(ACTIVITY)
            hits += 1
    assert hits == 3, "expected 3 owned keys, patched %d" % hits
    with io.open(STATE, "w", encoding="utf-8", newline="") as fh:
        fh.write("\n".join(lines))
    print("STATE patched round_no/activity_now_round/activity_now -> %d" % ROUND)


def _json_str(s):
    out = s.replace("\\", "\\\\").replace('"', '\\"')
    return u'"%s"' % out


if __name__ == "__main__":
    t0 = time.time()
    append_report()
    patch_state()
    # self-verify the state still parses and carries an int epoch elsewhere untouched
    import json
    with io.open(STATE, "r", encoding="utf-8") as fh:
        d = json.load(fh)
    assert d["round_no"] == ROUND, d["round_no"]
    assert d["activity_now_round"] == ROUND
    print("OK round_no=%s elapsed=%.2fs" % (d["round_no"], time.time() - t0))
