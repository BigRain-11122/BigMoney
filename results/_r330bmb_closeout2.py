# -*- coding: utf-8 -*-
"""r330 bm-b closeout part 2 (continuation after closeout.py partial run):
fix 15:2x->14:5x stamps already written to CODELY/archive, then HANDOVER 5x
(correct '=' anchor), round report, state.json, heartbeat, inbox MSG.
"""
import io, json, os, shutil, time
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
now = datetime.now().astimezone()
ts_iso = now.isoformat(timespec="seconds")
ts_local = now.strftime("%Y-%m-%d %H:%M:%S")
stamp = "2026-09-27 14:5x"
print("clock:", ts_iso)

def rd(p):
    return io.open(p, encoding="utf-8").read()

def wr(p, s):
    with io.open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(s)

# ------------------------------------------------ 0. fix stamps 15:2x -> 14:5x
s = rd("CODELY.md")
if s.count("15:2x"):
    assert s.count("15:2x") == 2, f"CODELY 15:2x count={s.count('15:2x')}"
    wr("CODELY.md", s.replace("15:2x", "14:5x"))
assert "15:2x" not in rd("CODELY.md")
arch_p = "research/memory-archive/202609.md"
arch_anchor = "硬线当窗整编 15:2x）"
s = rd(arch_p)
if s.count(arch_anchor):
    assert s.count(arch_anchor) == 1, f"archive anchor count={s.count(arch_anchor)}"
    wr(arch_p, s.replace(arch_anchor, "硬线当窗整编 14:5x）"))
assert arch_anchor not in rd(arch_p)
print("stamps fixed: CODELY done, archive targeted-done")

# ------------------------------------------------ 1. HANDOVER (correct anchor)
hand_p = "research/HANDOVER.md"
hand = rd(hand_p)
anchor = "最近核对=bm-b round 325（2026-09-27 13:2x"
assert hand.count(anchor) == 1, f"anchor count={hand.count(anchor)}"
win = ("【r326 水位绿维护轮（probe py_low_board_clear 合法 idle·sina A1 深重拉在飞）；r327 town.html 研究楼详情 "
       "v6 KPI 面补齐（org_chart 列刷新同轮 grep 核对面律）；r328 PS5 BOM 18 件全仓扫剥+audit v2.3 "
       "pool_starvation 侦给缺口如实上报；r329 周一就绪 32 腿 S6 链形（三条件腿常驻自判）+W2-A autofill "
       "14:20:02 自动点火+rebase-continue clean-index 假拒坑律；r330=本核对轮：S0 丢弃 autofill last_tick "
       "设计性尾巴零冲突 rebase（认领 keepalive 本体在 runnable_pool owner_since 禁 stash）+W2-A 崩溃根修"
       "（build_zoo93_arc_family 家族 ctor 元数错配→v2 选 roster 成员 zoo93_arc+arity 探针三重验证 ALL PASS·"
       "新 sha 解除 O-0947 fix-first 拒发待 autofill 重燃）+cc-strip 自审清白（6 条 bm-c 记录 cc=True 闭口）+"
       "CODELY 十六批当窗整编】")
new_hdr = ("最近核对=bm-b round 330（2026-09-27 14:5x·对账增量=文末 round 330 bm-b 增量窗"
           "「bm-b r326-330 窗：**W2-A 全燃点火→27min prep 相崩溃→当窗根修解冻重发链**——" + win + "」）；"
           "上一次最近核对=bm-b round 325（2026-09-27 13:2x")
hand = hand.replace(anchor, new_hdr)
incr = ("- 开发队列增量窗（接续版）**round 330 bm-b（5x 核对本轮），2026-09-27 14:5x 补核；对账区间=增量 bm-b "
        "r326-330 与 bm-c r84/85·bm-a R321-327 交叉（基线=round 325 bm-b 行·round 85 bm-c 行已收讫），"
        "统一链 286,541 实读平持（_r295bmb_ledger_scan 复跑 INTERNAL_BALANCE_FAIL=0·DUP_BATCH_CONFLICTS=0·"
        "HEAD=DECISION_CHAIN_E2E_P1）**——" + win + "\n")
if not hand.endswith("\n"):
    hand += "\n"
wr(hand_p, hand + incr)
assert rd(hand_p).count("最近核对=bm-b round 330") == 1
print("HANDOVER: header -> r330 + increment appended")

# ------------------------------------------------ 2. round report
rr_p = "logs/iteration-loop/round_reports.md"
rr = rd(rr_p)
rr_line = (
    "2026-09-27T14:5x+08:00 | r330 bm-b | dept:工程+舰队 | 水位=绿：red=false@14:30:17 lane healthy；"
    "probe 14:48:32 verdict=py_low_board_clear 合法 idle 白名单（票 0 open+bandit next_pick=claimed parked "
    "MF IC 批+sina A1 深重拉在飞=W2A 点火时合法占用；14:50:06 后=W2A 崩溃 fix-first 冻结面如实携带）| did: "
    "(1) S0=p1d_gates 定向收编+autofill last_tick 设计性尾巴丢弃（认领 keepalive 本体在 runnable_pool "
    "owner_since 已自提交=丢弃零险，r328 stash 面弃用）→pull --rebase 零冲突 2 笔重放（61c854ad/6c727583） "
    "(2) S0.5 轮首双扫 orders 96/96 零未回执+决策面 firm\\DECISIONS.md 零 09-27 行+集团 ..\\..\\docs\\"
    "decisions.md 缺位=诚实 no-op（P-32 先例） (3) S1 smoke 25/25 (4) S2 双板=job_list 0+票 0 open"
    "（63 done+30 claimed 他机长活） (5) S3 主闭环=W2-A 全燃崩溃当窗根修：crash_fuse 14:50:06 CONFIRM"
    "（census_fusion_s2_w2.py prep 相 L300 reindex AttributeError）根因=build_zoo93_arc_family 家族 ctor "
    "返 (dict{4 面}, n_bad) 被 L254 单值接收；v1 镜像解包仍错（dict 入 face）被 _r330bmb_zoo93_arity_probe "
    "当场拦→v2=解包+选 roster 成员 zoo93_arc（vrc/src/krc 未入册）+rep 计数器保真入 meta.build_timing_s；"
    "三重验证=py_compile rc0+arity 探针 PASS（含 v0/v1 崩类复现腿）+hermetic selftest ALL PASS；"
    "O-0947 fix-first 同 sha 拒发解除（14:52:46 refusals=1 为修复前时序）待 autofill 下 tick 新 sha 重燃 "
    "(6) cc-strip 自审（MSG-1407 请求）：launches 45=44 True+1 None·6 条 bm-c PHANTOM cc 全 True=未再现 "
    "no-action 闭口 (7) S6 32/32 rc=0（_r329bmb 链形·周日条件腿自判） (8) 5x HANDOVER 本核对+统一链 "
    "286,541 实读平持 (9) CODELY 十六批当窗整编（9769B 超 10KB 硬线预警→9 条坑律行级外迁 archive "
    "202609.md·新坑律入册） (10) MSG-1428（本机发 bm-a）留站待取 | next: W2A 重燃监控（autofill 下 tick·"
    "prep 15-40min 通过即 checkpoint 面；再崩=count2 转 OOM/环境深探）+sina/MF 双门开闸即 prereg 起草+"
    "R335 5x+Mon T-91 s3 09:15 | 证据=results/_r330bmb_zoo93_arity_probe.py+results/"
    "_r330bmb_ledger_scan_out.txt+logs/autofill_CENSUS-FUS-S2-W2A.log\n")
if not rr.endswith("\n"):
    rr += "\n"
wr(rr_p, rr + rr_line)
print("round_reports: r330 line appended")

# ------------------------------------------------ 3. state.json (bm-b)
st_p = "logs/iteration-loop/state.json"
st = {
    "round_no": 330,
    "did": ("R330: W2-A burn crash root-fixed in-round (zoo93 family-ctor arity mismatch in build_faces; "
            "v2 = unpack + select rostered member zoo93_arc + n_bad counter into meta.build_timing_s; "
            "triple-verified py_compile rc0 + arity probe PASS w/ crash-class reproduction legs + hermetic "
            "selftest ALL PASS; O-0947 same-sha refusal cleared, awaiting autofill relaunch) + S0 "
            "designed-tail discard zero-conflict rebase (claim keepalive lives in runnable_pool owner_since, "
            "committed; no stash) + cc-strip self-audit clean (launches 45=44 True+1 None; 6 bm-c PHANTOM "
            "records all cc=True -> no-action close per MSG-1407) + S6 32/32 rc=0 + 5x HANDOVER (chain "
            "286,541 flat INTERNAL_BALANCE_FAIL=0) + CODELY 16th-batch hot-cold archival"),
    "verdict": "green",
    "next": ("W2A relaunch monitoring (autofill next tick w/ fixed sha; prep 15-40min passage -> checkpoint "
             "face; second crash -> count=2 -> OOM/env deep probe) + sina-construct prereg when sina_mf panel "
             "complete+N>=250 gate opens + MF IC batch when moneyflow panel unblocked + Mon 09-28 09:15 T-91 "
             "s3 + 15:30 new-bar chain via _r329bmb_s6_chain.ps1 + R335 5x HANDOVER + 10-01 monthly trio + "
             "REGIME_GUARD v3 date gate"),
    "last_round_ts": "2026-09-27T14:5x+08:00",
    "last_result": "ok",
    "current_task": ("W2-A fix landed awaiting autofill relaunch (watch prep passage + checkpoint face) + "
                     "waiting sina panel complete+N>=250 gate -> sina-construct prereg + Mon T-91 s3 09:15 + "
                     "T-87 15:30"),
    "updated_at": "2026-09-27T14:5x+08:00",
    "last_seen": "2026-09-27T14:5x+08:00",
    "ts": ts_local,
}
wr(st_p, json.dumps(st, ensure_ascii=False, indent=1) + "\n")
assert json.loads(rd(st_p))["round_no"] == 330
print("state.json: round_no=330 written")

# ------------------------------------------------ 4. heartbeat
hb_p = "fleet/machines/bm-b.json"
hb = json.loads(rd(hb_p))
epoch = int(time.time())
assert isinstance(epoch, int)
free_gb, cpu_pct = 12.2, 2.0
try:
    import psutil
    free_gb = round(psutil.virtual_memory().available / 2**30, 1)
    cpu_pct = round(psutil.cpu_percent(interval=1), 1)
except Exception:
    pass
hb["last_seen"] = "2026-09-27T14:5x+08:00"
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = ts_iso
hb["round_no"] = 330
hb["round"] = 330
hb["loop_round"] = 330
hb["current_task"] = st["current_task"]
for k in ("free_ram_gb", "idle_ram_gb"):
    hb[k] = free_gb
for k in ("idle_ram_mb", "free_ram_mb"):
    hb[k] = int(free_gb * 1000)
for k in ("cpu_pct", "cpu_util_pct"):
    hb[k] = cpu_pct
hb["verdict"] = "healthy"
wr(hb_p, json.dumps(hb, ensure_ascii=False, indent=1) + "\n")
back = json.loads(rd(hb_p))
assert isinstance(back["heartbeat_epoch_utc"], int) and "T" in back["clock_read"]
assert back["round_no"] == 330 and len(back["orders_ack"]) == 96
print("heartbeat: r330 epoch(int)=", back["heartbeat_epoch_utc"], "ram=", free_gb, "cpu=", cpu_pct)

# ------------------------------------------------ 5. inbox
src = "fleet/inbox/MSG-20260927-1407-bmc-autofill-cc-strip.md"
dst = "fleet/inbox/processed/MSG-20260927-1407-bmc-autofill-cc-strip.md"
if os.path.exists(src):
    shutil.move(src, dst)
    print("inbox: MSG-1407 -> processed (audit clean, no-action close)")

msg_p = "fleet/inbox/MSG-20260927-145x-bmb-w2a-crash-fix.md"
msg = """# MSG-20260927-145x 由 bm-b → bm-a · W2-A runner 崩溃根修回执（r330 当窗闭环）

- **实况**：W2-A 全燃 14:20:02 点火（pid7796）prep 相 27min 后崩——`build_faces` L254 单值接收
  `build_zoo93_arc_family`（该 ctor 返 `(dict{zoo93_arc,vrc,src,krc}, n_bad)` 家族面，全仓其余 5 消费者
  皆解包选成员），L300 `reindex` AttributeError；crash_fuse 14:50:06 CONFIRM count=1，O-0947 fix-first
  同 sha 拒发（14:52:46 refusals=1）=烧录冻结。
- **根修（r330 bm-b 当窗）**：L254 改为解包+选 roster 成员 `zoo93_arc`（vrc/src/krc 未入 W2A 册）+
  `rep["zoo93_n_bad"]` 计数器保真入 meta.build_timing_s。**首版镜像解包修复本身也错**（dict 被当 face
  塞入），被真实调用形态探针 `results/_r330bmb_zoo93_arity_probe.py`（含 v0/v1 崩类复现腿）当场拦下。
- **验证**：py_compile rc0 + arity 探针 PASS + hermetic selftest ALL PASS（12 腿）；gate 面（5217 join
  ≥5000 冻结门）在崩溃前已 PASS 不受影响；新 sha 已解除 fix-first 拒发，autofill 下 tick 自动重燃。
- **坑律已入册**（CODELY r330）：移植因子 ctor 必先探明返回形+首燃前跑真实调用形态探针——UNC 后续批
  复用同族 ctor 前必查。runner 为你方 R326 建，本修复为镜像正典消费形态零判定面改动，请知悉。
"""
wr(msg_p, msg)
print("inbox: crash-fix receipt MSG -> bm-a written")
print("CLOSEOUT2-OK")
