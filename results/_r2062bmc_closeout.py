"""r2062 closeout: append the round-report line, bump state round_no, refresh the heartbeat.

Only this machine's own files are touched (round_reports-bm-c.md / state-bm-c.json /
fleet/machines/bm-c.json).  No other shared face is written.
"""
import json
import os
import re
import time
import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)

now = datetime.datetime.now().astimezone()
stamp = now.strftime("%Y-%m-%dT%H:%M:%S%z")
stamp = stamp[:-2] + ":" + stamp[-2:]          # +08:00 form
epoch = int(time.time())

LINE = (
    "{stamp} | r2062 | bm-c | watermark 绿（red=false·lane=healthy）；孤儿面=0（探针面本轮未重跑·"
    "沿用 r2061 py_faces=6/orphans=0）；**S0 竞争探针 rc=3 CONTENTION**——2 宿主（interactive "
    "pid 79608 自 2026-11-24T22:39 起 146.7min + 本窗），轮首前 17 张共享面由别宿主写过"
    "（research/INGEST/* 八件、ARBITER-BOARD、fleet/machines/bm-c.json、results/arbiter/STATE.json 族），"
    "重叠窗内不可归因 0 张（证据 results/_repo_write_contention.bm-c.json）→ 按 r1907/r1927 "
    "本轮只落**新增文件面**：未改共享面、未重跑 S6 链。 | 本轮产品=**34 条红腿的根因面**："
    "新建 scripts/smoke_red_root_cause.py（selftest 12/12）+ results/smoke_red_root_cause.json + "
    "research/SMOKE-RED-ROOT-CAUSE.md。问题不是「哪条先修」（r2061 已答顺序），而是「34 条是不是 "
    "34 个缺陷」。 | **判词 PERMISSION_UNREADABLE_BECAUSE_IDENTITY_BROKEN**：29/34 红腿在书家族，"
    "根因链=etf_book_size_rulers_decision 自报 IDENTITY_BROKEN（identity leg ticket_k_reproduced "
    "在 2026-10-23 bar 上比、票面决定在 2026-11-11）→ etf_book_rebalance_permission 的 "
    "baseline_published k=0.460253452 ≠ 票面 k_rule=0.458463 判 identity 断 → 该读数不可分类 → "
    "**permitted_k=null** → etf_book_cut_order_gap 输出 UNREADABLE/incomplete_receipts（不写 gap_k）→ "
    "下游尺寸/票面/阶梯腿成片红。 | **反事实读数**（算术，非许可）：三条可读 path 读数 "
    "window 0.747086 / universe 0.435003 / window_x_universe 0.667665 → permitted_k=0.435003"
    "（binding=universe），在册 k=0.435003、容差 0.005 → **KEEP_ALLOWED**——这张面今天什么都不说，"
    "而它本可以说「允许保持尺寸」。 | 另一条实测：`python scripts/etf_book_size_rulers_decision.py --check` "
    "rc=1 打印「7 field(s) re-derived, 1 mismatch: verdict receipt='IDENTITY_BROKEN' "
    "rederive='SIZE_IS_A_RULER_CHOICE'」——**identity 现在已经成立**（只读重算不写面），"
    "即重生一次 rulers 面即可让整族重新拿到一个可读的 permitted_k。 | 验证：selftest 12/12；run rc0；"
    "check rc0；**负控 6/6 实弹**（手改 md 一格→rc1 CHECK FAILED 且不带 STALE 前缀 r1934；删 json→"
    "rc3 STALE face missing；run 复原 json 逐字节相同、md 逐字节相同）；证据=qa/smoke-red-root-cause-r2062.md。"
    " | S0.5 双扫：fleet/orders 117 件（本机口径 63 件，其中待回执 **0**；他机 54 件）；集团 "
    "origin/main:docs/decisions.md 原生字节（git cat-file 落盘·无 2>&1）250,586B sha256 79e3083b85c1… "
    "== 自持水位 → **零新决策零动作**；fleet/inbox 无件。 | 未验证（如实）：①红腿取自 "
    "logs/smoke_legs.json 的 2026-11-24T20:12:28 读数（285.9min 旧），本轮未重跑全量冒烟（连续第 10 轮）；"
    "②cash_roll_today 的 KeyError 'cash_cny' 可能另有二因，本面未证同根；③5 条家族外红腿本面不表态；"
    "④重建链写共享面，本轮未执行，重生后必须重跑冒烟才算数；⑤S6 链连续第 10 轮未跑（竞争窗）。"
    " | 下轮指针：(a) 竞争解除后按 rebuild_chain 顺序重生四张面（rulers→permission→k_gap→order），"
    "再 --only=etf_book 族跑冒烟验红腿是否成片转绿；(b) 把「identity leg 用哪根 bar 比」写进 rulers 面"
    "的 --check 输出（现在只印 mismatch 不印 bar 对），让下一次读者一眼看出是代差还是真断；"
    "(c) main 合入 + S6 分批补跑。 | **CEO 三行**：当前活=把积压 34 条冒烟红腿从「一条条修」改成"
    "「找到那张停答的面」——现在知道是 1 张面卡住了 29 条腿｜最近实物="
    "K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\research\\SMOKE-RED-ROOT-CAUSE.md（{stamp}·"
    "selftest 12/12·负控 6/6）｜下个里程碑=无竞争窗时按四步重生链解开整族红+冒烟验证（≤48h）。"
    "| 记账：本行 1 处。\n"
).format(stamp=stamp)

rep = os.path.join(BASE, "round_reports-bm-c.md")
with open(rep, "ab") as fh:
    fh.write(LINE.encode("utf-8"))

# --- state: bump round_no only (text level, so the 1.27MB file keeps its shape)
sp = os.path.join(BASE, "state-bm-c.json")
with open(sp, "r", encoding="utf-8", newline="") as fh:
    raw = fh.read()
new_raw, n = re.subn(r'("round_no"\s*:\s*)2061', r"\g<1>2062", raw, count=1)
if n != 1:
    raise SystemExit("state round_no bump failed (n=%d)" % n)
with open(sp, "w", encoding="utf-8", newline="") as fh:
    fh.write(new_raw)
chk = json.load(open(sp, encoding="utf-8"))
print("state round_no", chk.get("round_no"), "keys", len(chk))

# --- heartbeat: this machine's own face only
hp = os.path.join(BASE, "fleet", "machines", "bm-c.json")
hb = json.load(open(hp, encoding="utf-8"))
before = len(hb)
hb["last_seen"] = stamp
hb["ts"] = stamp
hb["clock_read"] = stamp
hb["heartbeat_epoch_utc"] = int(epoch)
hb["round_no"] = 2062
hb["current_task"] = ("r2062 smoke 红腿根因面：34 红中 29 条同根于 permission "
                      "permitted_k=null（identity_broken）")
hb["verdict"] = "CONTENTION 只落新增文件面（scripts/smoke_red_root_cause.py 三件套）"
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
with open(hp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
back = json.load(open(hp, encoding="utf-8"))
assert isinstance(back["heartbeat_epoch_utc"], int), "epoch must be int"
print("heartbeat keys", before, "->", len(back), "epoch int", back["heartbeat_epoch_utc"])
print("stamp", stamp)
