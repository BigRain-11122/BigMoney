# r282 bm-a wrap: CODELY law lines x2 + round report line + state round bump
# + heartbeat (orders_ack += O-20260926-2330 / O-2026-09-26-2335, epoch int,
# clock_read T-sep). Byte faces probed and preserved per r255/r257 law family.
import json
import os
import time
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now = datetime.now()
ts = now.strftime("%Y-%m-%d %H:%M:%S")
iso = now.astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

LAW1 = (
    "- [2026-09-27 01:2x] 坑律（bm-a R282·autofill 认领 push 拒绝饿死面·r199/r279 家族新参·E1 池烧期自捕）：**tick 认领 commit 的 push 被拒（origin 移动=他机在推）时直接 yield 不发射=结构饿死——00:30/00:40/00:50 三 tick 连续让路、py 0-4% 池有 ready 批，REV-OSC 填充延迟 29.1min 违 O-2100 10min 目标**；正律=push 被拒先 pull --rebase + push 重试一次（S7 纪律移植到 tick；00:30 树净窗回放=可省 20min），脏树/冲突 fail-safe：rebase --abort + yield 保持本地认领 commit 等会话 S0 收编（禁 stash 游戏防 r268 面）；夹具=queued-fault stub S15f/g/h。指针=Tools/autofill.py _claim_shard r282 段+logs/autofill.log 00:30-01:00 实录")

LAW2 = (
    "- [2026-09-27 01:2x] 坑律（bm-a R282·REV-OSC beat 面单位病+redo 双 echo 面·r258/r259 家族新参·E1 收割期自捕）：**①p1c_stock cache pct_chg=百分比单位（±10% 带宽面）被当分数消费=EW 代理 ×100 膨胀→beat_rate 全 cell×segment 恒 0.0（prereg s5 预期 deep-bear 0.55-0.75 才露馅）——判读面不受染（价格模拟）、INVVOL sd 尺度不变免疫；正律=修 /100+重 derive（r253 单计）+r258 披露块+夹具百分比面（r117 律）②已上链批的 re-finalize 有双 echo：append_ledger 数据驱动头已含自身（2014 双计）+g1 n_eff 同吃 echo（191873≠原判 189859）——正律=prev_total 复用自身存储链位（原地重写非分叉）+skill_line_v2/g1_prime_v2 additive n_eff_override+attrition 本批行原位替换**。指针=scripts/rev_osc_stock_p1.py AMENDMENT r282+scripts/science_gates.py n_eff_override+results/rev_osc/p1_results.json defect_disclosure")

REPORT = (
    "2026-09-27 01:26:00 | R282 bm-a | WM=GREEN py_low_board_clear (REV-OSC landed 01:01; "
    "CN-TREND claimed bm-b tick; board clear post-harvest) | S0.5 orders double-scan: "
    "O-20260926-2330 + O-2026-09-26-2335 unacked-on-bm-a -> acked this round (execution "
    "already fleet-wide: bm-b r279 cross-validation + refine furnace P1 in-file; bm-a "
    "r280-282 T-87 line runner + judged batch); decisions receipts: D-20260927-04 "
    "(post-review hot-ticket anchor ban -> bm-a self-correction sustained, confirmed), "
    "D-20260927-05 item2 (orders full-file scan face = this repo R13 diff-scan already "
    "compliant), D-20260926-10 (trading-day-gated STALE exemption adopted, tool face = "
    "HQ lane); P0 fix: autofill claim push-reject rebase-retry (r282 fill-starvation "
    "law, live case 00:30/00:40/00:50 triple yield while py 0-4%, selftest 22/22 with "
    "S15f/g/h queued-fault legs); REV-OSC-STOCK-P1 harvested: judged-negative all 7 "
    "cells per prereg s4 (g1 line 13.5951 vs best sharpe 0.3831 x1, CI lower negative, "
    "DSR 0.012, family PBO 0.4) = slot closed + reopen-on-new-evidence (O-2325 s5); "
    "beat-face unit defect found+fixed+re-derived same round (cache pct_chg percent "
    "units consumed as fractional -> EW proxy x100 -> beat 0.0 everywhere vs prereg "
    "s5 band; fixed /100, deep-bear beat now 0.55-0.62 inside expected 0.55-0.75; "
    "judged faces byte-stable, single-count redo guards: append prev_total + "
    "skill_line n_eff_override additive params + attrition own row in-place); pool "
    "flip done per r244 (51/52 done) | science_gates selftest 37/37 + runner selftest "
    "16/16 + smoke 25/25 + ledger 189859 single-count verified + attrition 1 row "
    "total_after 189859 + S6 22 legs rc=0 + push a0425122 (rebase x2: tick-claim "
    "skip moot + pool origin-base reflip preserving bm-b cntrend claim) | next: T-87 "
    "queue #2 prereg draft (SCHOOL_SUPPLY_S1 sec.2) + CN-TREND judgment face on bm-b "
    "land + moneyflow IC reference batch parked source-blocked (30-min self-heal)")

# 1) CODELY.md append (LF, trailing NL preserved)
p = os.path.join(ROOT, "CODELY.md")
raw = open(p, "rb").read()
nl = b"\r\n" if raw.count(b"\r\n") * 2 > raw.count(b"\n") else b"\n"
add = nl.join([LAW1.encode("utf-8"), LAW2.encode("utf-8")])
if not raw.endswith(b"\n"):
    raw += nl
open(p, "wb").write(raw + add + nl)
print("CODELY:", os.path.getsize(p), "bytes (threshold 50KB)")

# 2) round report append (CRLF ledger, trailing NL)
p = os.path.join(ROOT, "logs/iteration-loop/round_reports-bm-a.md")
raw = open(p, "rb").read()
nl = b"\r\n" if raw.count(b"\r\n") * 2 > raw.count(b"\n") else b"\n"
if not raw.endswith(b"\n"):
    raw += nl
open(p, "wb").write(raw + REPORT.encode("utf-8") + nl)
print("report appended, trailing-nl ok")


def face_write(path, obj):
    raw = open(path, "rb").read()
    bom = raw.startswith(b"\xef\xbb\xbf")
    crlf = raw.count(b"\r\n") * 2 > raw.count(b"\n")
    trail = raw.endswith(b"\n")
    s = json.dumps(obj, ensure_ascii=False, indent=1)
    s = s.replace("\n", "\r\n") if crlf else s
    data = s.encode("utf-8")
    if trail and not data.endswith(b"\n"):
        data += b"\r\n" if crlf else b"\n"
    if not trail and data.endswith(b"\n"):
        data = data[:-1]
    if bom:
        data = b"\xef\xbb\xbf" + data
    with open(path + ".tmp", "wb") as fh:
        fh.write(data)
    os.replace(path + ".tmp", path)


# 3) state bump (probe face first)
p = os.path.join(ROOT, "state-bm-a.json")
st = json.load(open(p, encoding="utf-8-sig"))
st["round_no"] = 282
st["did"] = ("R282: autofill claim push-reject rebase-retry fix (r282 fill-starvation "
             "law, selftest 22/22) + REV-OSC-STOCK-P1 harvest (judged-negative all 7 "
             "cells, slot closed O-2325 s5) + beat-face unit defect fixed+re-derived "
             "(deep-bear 0.55-0.62 in prereg band) + single-count redo guards "
             "(prev_total/n_eff_override/attrition in-place) + orders 2330/2335 acked "
             "+ S6 22 legs rc=0")
st["verdict"] = "ok"
st["next"] = ("T-87 queue #2 prereg draft (SCHOOL_SUPPLY_S1 sec.2); CN-TREND judgment "
              "on bm-b land; moneyflow IC batch parked source-blocked")
st["ts"] = iso
st["last_round_ts"] = ts
face_write(p, st)
print("state round_no ->", json.load(open(p, encoding="utf-8-sig"))["round_no"])

# 4) heartbeat
p = os.path.join(ROOT, "fleet/machines/bm-a.json")
hb = json.load(open(p, encoding="utf-8-sig"))
ack = set((hb.get("orders_ack") or "").split())
ack |= {"O-20260926-2330-bm-a", "O-2026-09-26-2335-bm-a"}
hb["orders_ack"] = " ".join(sorted(ack))
hb["last_seen"] = iso
hb["heartbeat_epoch_utc"] = epoch          # JSON int (R170/R178 law)
hb["clock_read"] = iso                      # T-sep (R262 law)
hb["round_no"] = 282
hb["current_task"] = ("R282 wrap: REV-OSC harvested (judged-negative + beat-face unit "
                      "fix re-derived, pool flipped done); autofill claim rebase-retry "
                      "landed (r282 fill-starvation fix)")
hb["verdict"] = "py_low_board_clear"
import psutil
hb["cpu_pct"] = psutil.cpu_percent(interval=0.5)
hb["free_ram_gb"] = round(psutil.virtual_memory().available / 1e9, 1)
face_write(p, hb)
chk = json.load(open(p, encoding="utf-8-sig"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in chk["clock_read"], "clock_read must be T-sep ISO"
print("hb ok: epoch int", chk["heartbeat_epoch_utc"], "| ack_n", len(ack),
      "| clock", chk["clock_read"])
