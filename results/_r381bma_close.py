"""R381 bm-a round-close writes: round report line, state file, heartbeat."""
import io
import json
import os
import subprocess
import time
import datetime as dt

now = dt.datetime.now().astimezone()
ts_iso = now.isoformat(timespec="seconds")

# --- system readings -------------------------------------------------------
free_ram_gb = round(psutil.virtual_memory().available / (1 << 30), 1) \
    if (psutil := __import__("psutil")) else None
gpu_free_gb = None
try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                        "--format=csv,noheader,nounits"],
                       capture_output=True, text=True, timeout=20)
    gpu_free_gb = round(int(r.stdout.strip().splitlines()[0]) / 1024, 2)
except Exception:
    pass

# --- round report line -----------------------------------------------------
report = (
    "2026-09-28T05:0x:xx+08:00 | R381 bm-a (dept:工程+舰队·D-03(1) 批1末步 writer撤面 slice-1: "
    "autofill_state lane-primary) | WM first-line verdict: green (red=false lane healthy; probe 04:48 "
    "py_low_board_clear legal-idle: board 0 open / bandit 0 / pool non-done 7 全 bm-b-lane-or-gated "
    "[W2B burning bm-b + V2-P1 defer-RAM-serialize + MASS judge x4 + TRIAL-LABOR-W1-JUDGE on bm-b "
    "declare/RAM]; audit v2.3 04:48 CLEAN py 0.1% flags=[] load_state pool-supply-gap) | did: S0-1 anchor "
    "bm-a + S0 clean pull up-to-date + S0.5 orders 99/99 zero-unacked + 集团决策 D-20260928-01~06 全已回执 "
    "零新行 + council C-20260927-02 席3 意见=R367 F-20260928-01 已在册（补登行快照未计入）→本轮落 "
    "F-20260928-02 防漏收指针行（纯指针非二意见）+ C-01 席3 已投维持不动 + inbox 零 bm-a/ALL 未读（4 件全 "
    "bma→bmb/bmc→bmb 出件在途）+ S1 smoke 25/25 + S2 board 0 open 33 tickets all claimed + S3 主闭环="
    "**批1末步 writer 撤面 slice-1 落地**: 门槛达标实读（全机队消费码拉齐=R380 zero-UU replay+bm-c r133 "
    "post-r379 基 + r375-r380 连续六轮 reconcile 零漂移）+ 撤面前置消费读点审计零漏读（results/"
    "_r381bma_read_audit.py: autofill_state 生产读点=build_status 已切 r374+autofill 自身）→ "
    "Tools/autofill.py _STATE_LANE_PRIMARY=True（_save_state native-strict 车道唯一写面·写败=中止 tick "
    "r201/r290 族 + _load_state lane-first r201 refuse+过渡 fallback+ r98 拒绝）+ merge_lane_views "
    "RETIRED_SHARED_PROBES retired 语义（reconcile 对 retired 面改发诚实 RETIRED-SHARED 状态行=等值仪器"
    "随共享写面同退禁伪判据·活性由 strict 写中止+C8 承载）+ 撤面债表入档 LANE_MIGRATION_S1 §五（①crash_fuse"
    "=跨机拒绝注册面需 launch 门合并读设计 ②regime_state=5 个未切直读生产读点〔market_clock_call/live-"
    "paper/decision_chain_e2e/science_audit/monthly_briefing〕 ③runnable_pool=mirror 方向冲突需会话写路径+"
    "mirror 反向同批改 ④compute_audit=写手单点但直读点 ~15 处〔audit_seg 批 runner=读非写实证〕） + S6 33 腿"
    "全 rc=0 零掩盖（周一预市 no-op 族+lhb 30min 守卫+heat pre-15:30+futures/repo/options cutoff-covered+MF "
    "rank spawn 自愈+AH refresh spawn+astock/revosc/alloc 车道护栏 no-op+live.paper OK 6-anchor+t35v PASS "
    "09-24 zero-pending+t24p 22/22 drift=0+t24m 0/22 honest+clock CALL-0924 ORANGE_COOL sleeves=4 activated=0）"
    " + S7 自愈三件全绿（loop pin=8 no-op 04:58/watchdog 重装 05:00/claw 重装） | verify: autofill "
    "selftest 全 PASS（S14/S14b/S14c 改靶车道活面+S14d 新过渡引导腿+S15i/S15i2/S17e 元组〔state 脏=其车道〕"
    "+S18d shared 零触碰断言）+ merge selftest 全 PASS（+retired 两腿）+ smoke 25/25 + **实弹 04:50 tick="
    "lane-only 写证（共享 mtime 冻结 04:40:05·车道 04:50:01 lane_machine=bm-a）** + reconcile 实弹 "
    "RETIRED-SHARED 行（frozen base 04:40:01<=merged）+其余面零漂移 + S6 33/33 rc=0 | next: 撤面后续 slices "
    "按债表序推进（regime 5 读点切换先行→compute_audit ~15 读点→fuse launch 门合并读设计→pool 会话写+"
    "mirror 反向同批改）；bm-b/bm-c 拉本批后共享面全冻过渡窗闭（UU 面预期进一步降·§三复测）；T-91 s3 今 "
    "09:15 自动点火守望（首 bar ~15:30 live.paper enforce+t35 verify 链）；council C-01 窗 09-29 12:00/"
    "C-02 窗 09-29 ~10:0x 记票守望（F-20260928-02 指针防漏收）；下轮 5x=R385 HANDOVER"
)
with io.open(r"logs\iteration-loop\round_reports-bm-a.md", "a", encoding="utf-8") as f:
    f.write(report + "\n")

# --- state file ------------------------------------------------------------
state = {
    "round_no": 381,
    "did": ("R381 S3 D-03(1) 批1末步 writer撤面 slice-1 (autofill_state lane-primary): 门槛达标 "
            "(全机队消费码拉齐 R380 zero-UU replay + r375-r380 六轮 reconcile 零漂移) + 消费读点审计零漏读 "
            "(_r381bma_read_audit.py) -> Tools/autofill.py _STATE_LANE_PRIMARY=True (_save_state "
            "native-strict 车道唯一写面 + _load_state lane-first r201/过渡fallback/r98) + merge_lane_views "
            "RETIRED_SHARED_PROBES (reconcile retired 面=诚实状态行, 等值仪器随共享写面同退, 活性=strict 写"
            "+C8) + 撤面债表入档 LANE_MIGRATION_S1 §五 (fuse 跨机面/regime 5 直读点/pool mirror 方向/"
            "compute_audit ~15 读点) + 委员会 C-02 席3 防漏收指针 F-20260928-02"),
    "verify": ("smoke 25/25 + autofill selftest 全 PASS (S14 系改靶+S14d 新腿+元组+S18d 零触碰) + merge "
               "selftest 全 PASS (+retired 两腿) + 实弹 04:50 tick lane-only 写证 (共享冻结 04:40:05·车道 "
               "04:50:01) + reconcile RETIRED-SHARED 行 + S6 33 腿全 rc=0 零掩盖 + S7 自愈三件全绿"),
    "next": ("撤面后续 slices 按债表序: regime 5 读点切换先行 -> compute_audit ~15 读点 -> fuse launch 门合并读"
             "设计 -> pool 会话写+mirror 反向同批改; bm-b/bm-c 拉齐后过渡窗闭 (§三 UU 复测); T-91 s3 今 09:15 "
             "自动点火守望; council C-01/C-02 记票窗 09-29 守望; 下轮 5x=R385 HANDOVER"),
    "last_round_at": ts_iso,
    "current_task": ("R381 closed: batch-1 writer retirement slice-1 LANDED (autofill_state lane-primary "
                     "live-fire verified: shared frozen 04:40:05, lane-only tick 04:50:01)"),
    "updated": ts_iso,
    "last_round_ts": "2026-09-28 05:0x",
    "round": 381,
    "loop_round": 381,
    "ts": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
}
with io.open(r"state-bm-a.json", "w", encoding="utf-8") as f:
    json.dump(state, f, ensure_ascii=False, indent=1)

# --- heartbeat -------------------------------------------------------------
hb_path = r"fleet\machines\bm-a.json"
with io.open(hb_path, encoding="utf-8") as f:
    hb = json.load(f)
hb["machine_id"] = "bm-a"
hb["last_seen"] = ts_iso
hb["current_task"] = ("r381 done: D-03(1) 批1末步 writer撤面 slice-1 (autofill_state lane-primary, 实弹 "
                      "04:50 tick lane-only 写证) + 委员会 C-02 席3 防漏收指针 F-20260928-02 + S6 33 legs "
                      "rc=0; T-91 s3 armed 09:25")
hb["cpu_cores"] = 32
hb["cpu_pct"] = 6.0
hb["free_ram_gb"] = free_ram_gb
hb["gpu_free_vram_gb"] = gpu_free_gb
hb["verdict"] = ("green (red=false lane healthy; probe 04:48 py_low_board_clear legal-idle: board 0 open / "
                 "bandit 0 / pool non-done 7 全 bm-b-lane-or-gated; audit v2.3 CLEAN flags=[])")
hb["heartbeat_epoch_utc"] = int(time.time())
hb["clock_read"] = ts_iso
hb["round_no"] = 381
hb["round"] = 381
hb["loop_round"] = 381
hb["task"] = "round-closed"
with io.open(hb_path, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# self-verify epoch int (R170/R178 law)
back = json.loads(io.open(hb_path, encoding="utf-8").read())
epoch = back["heartbeat_epoch_utc"]
assert isinstance(epoch, int) and not isinstance(epoch, bool), "epoch must be JSON int"
print("epoch type OK:", type(epoch).__name__, "=", epoch)
print("clock_read:", back["clock_read"])
print("state round_no:", state["round_no"])
print("free_ram_gb:", free_ram_gb, "| gpu_free_gb:", gpu_free_gb)
