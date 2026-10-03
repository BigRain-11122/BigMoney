# -*- coding: utf-8 -*-
"""r654 bm-b closeout: state.json round increment + first-time last_orders_sha
(group orders.md blob) + heartbeat + round report line append.
Programmatic writes only (json.dump), json.loads self-verify after every write
(r645 state trailing-comma law; R170/R178 epoch-int law)."""
import datetime
import hashlib
import json
import os

RB = os.getcwd()
NOW = datetime.datetime.now().astimezone().replace(microsecond=0)
CLOCK = NOW.isoformat()
EPOCH = int(NOW.timestamp())


def jload(p):
    with open(p, "rb") as f:
        return json.loads(f.read().decode("utf-8"))


def jdump(p, obj):
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=True, indent=1)
        f.write("\n")
    back = jload(p)
    assert isinstance(back.get("heartbeat_epoch_utc", EPOCH), int), "epoch not int"


# ---------- 1) state.json ----------
sp = os.path.join(RB, "state.json")
st = jload(sp)
st["round_no"] = st.get("round_no", 0) + 1
st["round_no_label"] = "round %d (bm-b)" % st["round_no"]
st["last_round_at"] = st["ts"] = st["updated"] = st["last_seen"] = st["clock_read"] = CLOCK
st["last_orders_sha"] = "82A0CEF99F147C6F0000000000000000000000000000000000000000000000"  # placeholder, fixed below
# raw-blob sha of group orders.md from the S0.5 sparse-clone scan (written via
# git show bytes, not a checkout copy -> byte-identical by construction; assert prefix)
blob_path = os.path.join(RB, "results", "_r654bmb_d19_orders.md")
with open(blob_path, "rb") as f:
    o_sha = hashlib.sha256(f.read()).hexdigest().upper()
assert o_sha.startswith("82A0CEF99F147C6F"), "orders sha prefix mismatch: %s" % o_sha[:16]
st["last_orders_sha"] = o_sha
st["note"] = ("r654: watch/readiness round -- S0 clean FF merge origin 3-commit bm-c r449 wave "
              "(empty intersection with dirty daemon faces, treadmill merge-law r437); S0.5 orders 152/152 zero-diff + "
              "D-19 decisions MATCH zero-consume + group orders.md first-time sha recorded (%s..., prior key absent; "
              "O-20261003-1210 bm-b shares re-verified complete in-file r618); S1 47/47; S2 board 0 open (165 tickets all "
              "done/claimed/yielded, zero open); S3 gates green (WM red=false; engine alive rc0 idle; trio NULLS burns "
              "in-flight so trial-labor default not triggered; next_pick moneyflow IC claimed-by-other); readiness probe "
              "07:0x Q465/V615/D333 dup_k=0 integrity=T rehearsal-green x3 G1=F G2/G3=T G4=PENDING, D ETA 84.3h in-window, "
              "burn pids 34396/57116/30208 alive; S6 34 legs rc0 (dualrun streak 46; LHB real quarter fetch landed 11/11; "
              "weekend no-op family; t35_paper_export/daily_scorecard/build_status stale-takeover derive per STALE_MIN law); "
              "post_review prior-run YES=45 NO=0; attrition CLEAN; S7 loop pin=2 no-op + watchdog registered + precommit/"
              "prepush claws reinstalled." % o_sha[:16])
jdump(sp, st)
print("state.json round_no ->", st["round_no"], "| orders_sha ->", o_sha[:16])

# ---------- 2) heartbeat ----------
hp = os.path.join(RB, "fleet", "machines", "bm-b.json")
hb = jload(hp)
hb["last_seen"] = hb["ts"] = hb["updated"] = hb["clock_read"] = CLOCK
hb["heartbeat_epoch_utc"] = EPOCH
hb["round_no"] = st["round_no"]
hb["round_no_label"] = st["round_no_label"]
hb["current_task"] = ("FUND trio NULLS burn watch (Q465/V615/D333 of 2000 advancing dup_k=0, V/Q ETA ~10-05 05:54/08:24, "
                      "D lumpy ETA ~10-07/10-08 all in finalize window 10-05..10-09; finalize fires on mechanical_ready w/ "
                      "r638 fallback; G-SEG GM ruling G4 PENDING) + r654 watch round: readiness probe 07:0x, S6 34 legs rc0, "
                      "S0 FF-merge bm-c r449 wave, S7 claws+watchdog green")
hb["verdict"] = ("GREEN (smoke 47/47; D-19 decisions MATCH zero-consume + orders.md first-sha recorded; fleet orders 152/152; "
                 "WM red=false; engine alive rc0 idle; dualrun ZERO-DRIFT streak 46; S6 34 legs rc0; attrition CLEAN; "
                 "trio burns healthy dup_k=0 x3-pids alive 34396/57116/30208; W14-GENERATE governance-parked one-line)")
try:
    import psutil
    vm = psutil.virtual_memory()
    hb["free_ram_gb"] = hb["idle_ram_gb"] = round(vm.available / 1e9, 2)
    hb["ram_free_gb"] = hb["ram_avail_gb"] = round(vm.available / 1e9, 2)
    hb["cpu_util_pct"] = psutil.cpu_percent(interval=1)
except Exception:
    pass
jdump(hp, hb)
back = jload(hp)
assert isinstance(back["heartbeat_epoch_utc"], int), "epoch not int"
print("heartbeat epoch ->", back["heartbeat_epoch_utc"])

# ---------- 3) round report line (bytes append, r641 mixed-encoding file) ----------
rp = os.path.join(RB, "logs", "iteration-loop", "round_reports.md")
line_tpl = (
    "\n{clock} | round {rn} (bm-b, dept:数据/交易+研究): watermark verdict=GREEN (red=false; engine alive rc0 idle; "
    "dualrun ZERO-DRIFT streak 46; py 61-85% 有据烧批占用合法)\n"
    "当前活: FUND 三族 NULLS 烧录在飞（Q465/V615/D333 of 2000 推进 dup_k=0；readiness 07:0x 复跑 60s 双证据窗——V/Q 稳速 "
    "ETA ~10-05 05:54/08:24；D 60s 窗 lumpy 实测 0.33/min → ETA ~84.3h ≈ 10-07/10-08 全在 finalize 窗 10-05..10-09 内、"
    "先于 10-09 12:00 提速线；finalize 触发=mechanical_ready=true 且烧尽；G-SEG GM 裁决 G4 PENDING 等待态一行声明；"
    "r638 insufficient-sample fallback armed）\n"
    "最近实物: results/finalize_trio_readiness.json 07:0x 复跑刷新（Q465/V615/D333 dup_k=0 G1=F G2/G3=T G4=PENDING "
    "mechanical_ready=false）+ S6 34 腿 rc0 全绿（evidence results/_r654bmb_s6_evidence.txt；dualrun streak 46；"
    "update_lhb 真拉取 11/11 落账 quarter 窗；REPORT-2026-10-04/LIVE-2026-10-04 派生面再生）\n"
    "下个里程碑: V/Q 两族 NULLS 烧尽 ~10-05（05:54/08:24 实测 ETA）→ mechanical_ready 后 finalize+E1 判决窗 10-05..10-09"
    "（本窗 ≤48h 承诺=烧尽即 finalize；D 族 ETA ~10-07/10-08 同窗收口）\n"
    "做了什么: S0 FF-merge origin 3-commit bm-c r449 wave（脏面交集为空 r437 treadmill merge 净路·零 UU·push 前置）+ "
    "S0.5 双扫 152/152 零差 + D-19 sparse-clone fallback decisions MATCH EB14B510 零消费 + **group orders.md 首次 sha 记录**"
    "（本机 state 旧无 last_orders_sha 键；O-20261003-1210 bm-b 三令回执已在册 r618 完结复核实零新令）+ inbox 0；S1 smoke "
    "47/47；S2 板 165 票 0 open·job_list 空；S3 门面全绿（WM red=false；engine rc0 idle；三族判决批在飞故试用期常设线缺位面"
    "不触发；next_pick moneyflow IC 批 claimed 非本机不碰）；S6 34 腿 rc0（周末 no-op 族诚实+条件三件套跳过 latest=2026-09-30）"
    "+ burnproc 3/3 pids alive（34396/57116/30208）+ attrition 4 ledger CLEAN；S7 loop pin=2 no-op+watchdog 注册+双爪重装幂等\n"
    "验证证据: S6 per-leg 探针清单 34/34 rc=0（evidence _r654bmb_s6_evidence.txt）；smoke 47/47；dualrun ZERO-DRIFT "
    "streak 46（366 entries）；readiness 探针 07:0x 实弹 JSON（Q465/V615/D333 dup_k=0·elapsed 60.0s·ETA 全在窗内）；"
    "BURNPROC pids 34396/57116/30208 三活实证；attrition scan CLEAN（evidence results/_attrition_guard_scan.json）；"
    "state/心跳 json.loads 双自证 epoch int·clock T 分隔\n"
    "下轮指针: r655 = 续烧看位 watch+readiness 复跑（mechanical_ready=true 且烧尽 → 执行 finalize+E1；G-SEG 无裁决走 r638 "
    "fallback）；D lumpy 节奏观察续行，ETA>10-09 12:00 即走合规护栏（非可数文件地方动作 r630 / redo-k-lo/hi 切片 r611）；"
    "W14-GENERATE 治理停泊待 GM 解冻一行声明\n"
    "本地未达 origin commit 数=0（以收尾 push_verify 证据为准；失败则 addendum 留痕）\n"
)
with open(rp, "ab") as f:
    f.write(line_tpl.format(clock=CLOCK, rn=st["round_no"]).encode("utf-8"))
print("round report line appended ->", rp)

# ---------- 4) verify all writes ----------
for p in (sp, hp):
    jload(p)
print("ALL WRITES VERIFIED (json.loads x2 PASS)")
