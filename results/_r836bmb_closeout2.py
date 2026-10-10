#!/usr/bin/env python
# -*- coding: utf-8 -*-
# r836 bm-b closeout v2 (this session 17:52): fixes dead-session script (ascii-decl+CJK parse bomb;
# orphan probe face 17->11; honest ~25-window wording; WM-VERDICT + CEO three-line added; D19 advance
# completed this session after dead session's refused-without---advance receipt).
import json, time, datetime
ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

# --- state.json (bm-b face) ---
sp = ROOT + r"\state.json"
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 836
st["round"] = 836
st["round_no_label"] = "r836"
st["last_round_at"] = now
st["ts"] = now
st["updated"] = now
st["updated_at"] = now
st["last_seen"] = now
st["clock_read"] = now
st["now_active"] = "r836 closeout: M-1 regime axis freeze v1.0 + dead r836 estate absorbed + 2 CEO orders consumed + D19 ord watermark advanced"
st["did"] = ("r836: O-20261010-1645 backtest-continuity ack + O-20261010-1725 M-1 schedule row 10-11 delivered 1 day early "
             "(regime axis freeze v1.0: REGIME_AXIS_M1_FREEZE.md + scripts/regime_axis_m1.py selftest 7/7 + panic_windows.json "
             "25 panic days / 12 event windows, P>=1000 x20 + icepoint-exclusive x5) + ticket T-182 opened+claimed+done same round; "
             "first r836 session killed at 25min cap pre-closeout -> this session absorbed estate (r803/r809 churn law); "
             "D19 ord watermark ADVANCED cc3f32c7 via guard (dead session's update had been refused without --advance); "
             "S6 37-leg chain absorbed from dead session (dualrun ZERO-DRIFT streak 20)")
st["verdict"] = ("r836: GREEN-ish; compute_audit standing flags supply_gap+ignition_sla (TRIAL-LABOR-W17-JUDGE bm-c lane, "
                 "standing observation per O-1645 enforcement face); alloc_paper rc=2 = known P5 stale-leg 510880 (s3 review face); "
                 "smoke 49/49; regime_axis_m1 selftest 7/7")
st["latest_artifact"] = "r836: research/REGIME_AXIS_M1_FREEZE.md + scripts/regime_axis_m1.py + results/regime_axis_m1/panic_windows.json (25 panic days/12 event windows, selftest 7/7), 2026-10-10 17:3x"
st["next_milestone"] = ("r837+: C-20260909-03 bm-b workspace baseline wiring receipt (due <=10-11 14:30) + M-1 P0 slicing claim "
                        "10-13/14 -> matrix v1 plain report to CEO 10-16 (O-1725 schedule, <=48h window)")
q = ("r837 queue: (1) C-20260909-03 bm-b workspace baseline wiring receipt (<=24h from r835); "
     "(2) M-1 P0 slicing face -- research-dept claim per O-1725 schedule 10-13/14 (slicing uses frozen axis: "
     "REGIME5 labels + panic_windows.json; candidate slices: 4-asset core book / lowvol family / 6 employees / "
     "SYSTEM-V1 / oversold trio / theme rider); (3) O-1645 enforcement: F1-BULL-COND prereg same-window draft "
     "(T-177 leg-2 rank-1) when W17 verdict lands -> W18 prereg same window (physical dependency on W17-JUDGE drain, "
     "bm-c lane, noted per order sec.2); (4) r834 root-cause forensics continued (USN journal window dump + zombie git 24568)")
st["current_task"] = q
st["task"] = q
st["next"] = q
st["last_action"] = "r836: M-1 regime axis freeze v1.0 (O-1725 schedule item 10-11, 1 day early) + dead-estate absorb + two-order consumption + D19 ord advance"
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# --- heartbeat fleet/machines/bm-b.json (load-modify-field, r818 law) ---
hp = ROOT + r"\fleet\machines\bm-b.json"
hb = json.load(open(hp, encoding="utf-8"))
hb["round"] = 836
hb["round_no"] = 836
hb["now_active"] = "r836 closeout: M-1 regime axis freeze + O-1645/O-1725 consumed + dead-estate absorbed + D19 ord advanced"
hb["current_task"] = q
hb["task"] = q
hb["next"] = q
hb["last_round_at"] = now
hb["last_seen"] = now
hb["updated"] = now
hb["updated_at"] = now
hb["ts"] = now
hb["clock_read"] = now
hb["heartbeat_epoch_utc"] = epoch
hb["latest_artifact"] = st["latest_artifact"]
hb["next_milestone"] = st["next_milestone"]
hb["verdict"] = st["verdict"]
hb["last_action"] = st["last_action"]
ack = hb.get("orders_ack", [])
for o in ("O-20261010-1645-bm-a.md", "O-20261010-1725-bm-a.md"):
    if o not in ack:
        ack.append(o)
hb["orders_ack"] = ack
hb["orders_ack_count"] = len(ack)
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["orphan_faces"] = 0
hb["orphan_face_note"] = "r836 orphan probe 17:42:46 py_faces=11 orphans=0 (pythonw backfill_ext_slots = live detached collector, lawful)"
hb["sync"] = {"last_push_ts": now,
              "note": "r836 closeout; post-push fetch+ls-remote self-proof in S7 shell step"}
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
assert isinstance(hb["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178 law)"

# --- round report line ---
rp = ROOT + r"\logs\iteration-loop\round_reports.md"
line = (
    "%s | r836 bm-b | dept:研究（M-1 政体轴冻结·O-1725 排程 10-11 项提前 1 日落地）+dept:工程（死会话遗产吸收+D19 水位两步收口） | "
    "WM-VERDICT: green（red=false @18:08 watchdog derive·lane healthy；py tail 1.2/0.5/0.5 低位但板/池/bandit 全零=周六合法 board_clear；next_pick claimed=moneyflow IC parked source-blocked） | "
    "孤儿面=0（probe 17:42:46 py_faces=11 orphans=0；pythonw backfill_ext_slots=活跃分离采集器合法非孤儿） | "
    "CEO three-line: 当前活=r836 收口：死 r836 会话遗产吸收 + M-1 政体轴冻结 v1.0 交付 + 2 CEO 令消费 + D19 ord 水位推进；"
    "最近实物=research/REGIME_AXIS_M1_FREEZE.md + scripts/regime_axis_m1.py + results/regime_axis_m1/panic_windows.json（25 恐慌日=P 判据 20 天+冰点独占 5 天·12 事件窗·锚 5/5 机器验证·selftest 7/7·2026-10-10 17:3x）；"
    "下个里程碑=P0 切片认领 10-13/14 → 矩阵 v1 白话报告呈 CEO 10-16（O-1725 排程·窗 <=48h） | "
    "did: 前一 r836 会话（~17:25 起）25min 击杀死于 closeout 前，本会话（17:52 起）进程普查（唯一并活=PhantomEscapeGo 异仓+本会话·round.lock 本会话持有）→ r803/r809 死会话吸收律 add-A（attrition CLEAN rc0 前置闸）；"
    "S0.5 令双扫 62 件 unacked=2 全消费：O-20261010-1645 回测不停机令 ack（执法面：satengine 活跃 tick face 17:57+pool ready 2=W17 bm-c 车道在烧+perpetual N1 连续；供给侧=F1-BULL-COND prereg 起草以 W17 verdict 落地为物理依赖按令 §二泊位开放条款同窗起草·r837 队列留痕）+ "
    "O-20261010-1725 M-1 排程令同轮交付排程表 10-11 项=政体轴冻结 v1.0（REGIME-5 v1.0 标签指针+恐慌窗操作定义：P=单日跌停封板>=1000 ∪ I 冰点=n_sealed<=30 且 down>=800 并集=25 恐慌日/12 事件窗——令文估值 ~25 窗按日数吻合·窗数按 10 交易日聚类如实披露；2024-10-09 临界日不入并集=冰点双条件诚实代价零阈值回填；幂等重跑字节恒等）；"
    "票 T-182 开+认领+done 同轮（反重复：板扫 max=T-181 零 M-1 认领）；"
    "D19：dec 零 delta·ord delta 消费后 ADVANCED cc3f32c7 走守卫（死会话 17:35:43 update 无 --advance 被拒=r585 原子门实证·本会话补完两步=r819 律）；"
    "S1 smoke 49/49；regime_axis_m1 selftest 7/7（含锚 5/5+并集 25+冰点子条件 5/5+确定性）；"
    "S6=死会话 37 腿链吸收（dualrun ZERO-DRIFT streak 20·419 entries；compute_audit 常设 flags supply_gap+ignition_sla=W17 SHARD/JUDGE bm-c 车道非本机违例如实披露；alloc_paper rc=2=已知 P5 stale-leg 510880 s3 评审面；market_clock ORANGE_COOL sleeves=4 activated=0；期权道 RETIRED 诚实 no-op per O-20260909-1105；scorecard/report/live_usage/dashboard 17:33 重建）；"
    "S7 四件套见下 | "
    "evidence: results/regime_axis_m1/panic_windows.json + research/REGIME_AXIS_M1_FREEZE.md + fleet/tasks/T-2026-10-10-182-P1.json + selftest 7/7 + smoke 49/49 + results/d19_watermark.json（ADVANCED ord=cc3f32c7）+ results/pool_dualrun.bm-b.jsonl streak 20 + results/_attrition_guard_scan.json CLEAN + results/_r836bmb_closeout2.py（utf-8 声明版；死会话 ascii 声明版=parse bomb 本会话接住未爆） | "
    "score: 2（冻结轴=能跑（派生器+selftest）能看（冻结档+恐慌窗 JSON 25 日 12 窗）能用（P0 切片消费面就绪）实物） | "
    "记账预算: 4/5（state+心跳+轮报+T-182 票；S6 产出不计账） | "
    "宝藏捕获: 零新方法零新宝藏（派生器范式=zt_pool FIRST_DATE 钉死先例复用；closeout 脚本 coding 声明坑已入轮报不另立正式件） | "
    "unacked_orders=0 | 本地未达 origin commit 数=0（push 后 fetch+rev-list+ls-remote 自证·见 addendum） | "
    "下轮指针: r837=C-20260909-03 bm-b baseline wiring 回执（due <=10-11 14:30）+P0 切片认领（10-13/14）+F1-BULL-COND prereg W17 verdict 落地即同窗起草+W17-JUDGE drain 观察 | [r836 bm-b]\n"
) % now
with open(rp, "a", encoding="utf-8") as f:
    f.write(line)
print("closeout v2 written: state r836, heartbeat ack+2 (%d total), round report line, epoch=%d int-verified" % (len(ack), epoch))
