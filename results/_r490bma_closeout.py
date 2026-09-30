# r490 bm-a closeout: state round_no 490 + heartbeat (epoch int / ISO clock_read)
# + round report line + HANDOVER 5x incremental entry (r486-490 window)
# L1 deterministic, zero network. Evidence file per S3 discipline.
import json, time, datetime, psutil, io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

now = datetime.datetime.now()
ts_min = now.strftime("%Y-%m-%dT%H:%M") + "+08:00"
epoch = int(time.time())
clock_read = now.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"

# --- 1) state-bm-a.json: round_no 489 -> 490 ---
with io.open("state-bm-a.json", "r", encoding="utf-8") as f:
    state = json.load(f)
assert state["round_no"] == 489, f"unexpected round_no {state['round_no']}"
state["round_no"] = 490
state["last_round"] = "2026-09-30 r490: surgical lane-only push to main (r487-489 stranded content delivered: autofill fullburn wiring + MSG-2108 + lane evidence), 37 legs rc0, smoke 47/47"
with io.open("state-bm-a.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(state, f, ensure_ascii=False, indent=2)
    f.write("\n")

# --- 2) heartbeat fleet/machines/bm-a.json ---
vm = psutil.virtual_memory()
cpu_pct = psutil.cpu_percent(interval=1.0)
try:
    import subprocess
    gout = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                          capture_output=True, text=True, timeout=10)
    gpu_free_gb = round(float(gout.stdout.strip().splitlines()[0]) / 1024.0, 2)
except Exception:
    gpu_free_gb = None
with io.open("fleet/machines/bm-a.json", "r", encoding="utf-8") as f:
    hb = json.load(f)
hb["last_seen"] = clock_read
hb["current_task"] = "10-01 month-first trio (science_audit/monthly_briefing/self_review) + REGIME_GUARD v3 auto-activate + fullburn window open (wiring delivered to main r490) + banned-gate landing watch (7th window)"
hb["cpu_cores"] = 32
hb["cpu_pct"] = round(cpu_pct, 1)
hb["free_ram_gb"] = round(vm.available / (1024**3), 1)
if gpu_free_gb is not None:
    hb["gpu_free_vram_gb"] = gpu_free_gb
hb["round_no"] = 490
hb["verdict"] = ("healthy: r490 done -- surgical lane-only push landed main (r487-489 stranded delivery: "
                 "autofill.py fullburn wiring + MSG-2108 + lane evidence; 30 intersection shared faces zero-touch), "
                 "S6 37 legs rc0, dualrun ZERO-DRIFT streak 51, WM py_low_board_clear legal-idle (D-41 Face B = bm-b lane burning), "
                 "orders 129/129, decisions zero-new, smoke 47/47, self-heal trio green, attrition CLEAN healed-4")
hb["heartbeat_epoch_utc"] = epoch  # python int -> JSON int (R170/R178 law)
hb["clock_read"] = clock_read
# self-verify epoch is int BEFORE write (R170/R178 + R262 laws)
assert isinstance(hb["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in hb["clock_read"] and "+08:00" in hb["clock_read"], "clock_read must be ISO T + offset"
with io.open("fleet/machines/bm-a.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write("\n")
# post-write re-read self-check
with io.open("fleet/machines/bm-a.json", "r", encoding="utf-8") as f:
    chk = json.load(f)
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch roundtrip must be int"
print(f"[closeout] state 489->490 OK; heartbeat epoch={epoch} (int) clock={clock_read} cpu={cpu_pct:.1f}% ram_free={hb['free_ram_gb']}GB")

# --- 3) round_reports-bm-a.md r490 line ---
report_line = (
    ts_min + " | r490 | dept:工程 | WM=py_low_board_clear 绿（板 open=0·bandit 0·可跑批=无 bm-a 车道件·D-41 Face B 两票 "
    "lane_owner=bm-b=他机在飞·O-1901 闸4 合法 idle 白名单·red=False healthy）| 并发会话避让轮第七窗+滞留破局轮："
    "(1)S0 分止单向投递破局：behind 19/ahead 3（r487-489 滞留本地+machine 分支在案）+GM 会话四件 in-flight（CODELY.md/"
    "Money02-CODELY/PREREG_TEMPLATE staged/BANNED_DIRECTIONS untracked）零触碰→r486 律①失效窗（ahead>0 ff 不可用）→"
    "**外科提交净路**（GM 19:01 正典·ahead>0 扩展适用）：临时索引 read-tree origin/main+hash-object 仓内件+commit-tree -p "
    "origin/main+push <sha>:main 纯快进零触碰工作树——投递面=仅本机车道件+Tools/autofill.py（r487 O-1858 fullburn 窗接线="
    "fleet 主干可见）+fleet/inbox/MSG-2108（bm-c 泊位回执消费路径打通）+r487-489 车道证据；30 交集共享面文件零触碰"
    "（远端较新版保留·本地再生面留待全量同步窗合流）；本地 pathspec 偏提交照 r486 律② "
    "(2)S0.5 双扫=orders 129/129 零未回执（本地 127+origin-only 2=ghost 非欠账·对账全集 129）+decisions 尾行 D-41"
    "（r472-479 已回执）零新行·D-41#1 Face A RETAINED（bm-c r284·跨 122 月起点 pos_share 1.000）+Face B 烧窗已开"
    "（bm-b r285·lane_owner=bm-b·本机零冲突=MSG-2108 已投递佐证） "
    "(3)S1 smoke 47/47 "
    "(4)S6 37 腿 rc0（dualrun ZERO-DRIFT streak 51/3·audit 旗 pool_starvation+supply_floor=合法 idle 面〔在飞烧批均他机车道〕·"
    "WM py_low_board_clear·update_daily rc0·regime ORANGE d4·CALL-2026-09-30 ORANGE_COOL·采集器 no-op/节流族诚实"
    "（lhb cutoff 覆盖/heat 当日已采/futures-repo-options 09-29 覆盖/moneyflow 30min 节流/AH 30min 节流/ths 当日已采/"
    "fundamental 8.7h fresh·四 bm-b/bm-c 车道守卫 no-op）·promotion 0/22 NOT-ELIGIBLE 合法·aggr/grid/system_v1 cutoff 09-29 "
    "幂等 no-op·alloc=bm-b 车道诚实 no-op·t35_export 差分幂等·LIVE-2026-09-30 ORANGE/50%/COOL+REPORT-2026-09-30+dscore+"
    "build_status 再生（单机执笔守卫 host=bm-a 本机执笔）·token delta 0·无新 bar=live.paper/t35v/t24paper 门跳过·"
    "月首轮三件套非本月窗零动作·治理 Q4 槽位已 discharge 零双跑） "
    "(5)S7 自愈三件套绿（pin=8 no-op·watchdog Ready 重注册幂等·claw MATCH）+attrition CLEAN（healed-4）+HANDOVER 5x "
    "核对窗（r486-490 增量条落地）+心跳 epoch int+ISO 钟读双验 "
    "| 下轮指针：10-01 月首轮三件套+REGIME_GUARD v3 日期门自动激活 hands-off+fullburn 窗开启（接线已主干可见）+"
    "RW-5 外审复核 10-03→决策线恢复+T-129#1 prereg 仍 deferred（banned-gate 并发落地窗）+09-30 bar 最坏窗 10-09"
)
with io.open("round_reports-bm-a.md", "a", encoding="utf-8", newline="\n") as f:
    f.write(report_line + "\n")
print("[closeout] round report r490 line appended, %d chars" % len(report_line))

# --- 4) HANDOVER 5x incremental entry (insert after title line) ---
handover_entry = (
    "> bm-a round 490 五倍数核对（2026-09-30 20:3x）：增量窗 r486-490=bm-a 侧（**并发避让窗+滞留破局外科投递主线**——"
    "r486 脏树并发窗双同步坑律入册（ff-only 等价律/pathspec 偏提交免疫律/PS ISO strftime 坑）+S0 ff-sync b04ff54f7 落地+"
    "inbox 3 件处理（W14 park 回执 N=0 零烧·bm-c T-130 泊位零冲突）；r487 假期动员双令回执（O-1858/O-1901 ack 127→129）+"
    "**autofill fullburn 窗接线**（O-1858 sec.1 日期窗 10-01..re-open-10-09·窗内 launch nice NORMAL·fullburn_window "
    "launch record·selftest S21 x3 全过）+moneyflow rank-pass/AH 自愈 spawn；r488/r489 等待态守望连窗（S6 全绿·双扫零未回执·"
    "09-30 bar 源未发布 cutoff 09-29 per r485·GM 会话四件 in-flight 零触碰四连窗）+r489 吞件自检同窗修复"
    "（c72b66765 裸 commit 吞 GM 会话 staged PREREG_TEMPLATE→soft-reset+pathspec 部分重提 50 文件·staged 态完整复原·"
    "工作树字节不变）；r490 **滞留破局**：behind 19/ahead 3 且 ahead>0=r486 律①失效窗→外科提交净路（GM 19:01 正典）单向投递主干"
    "——临时索引 read-tree origin/main+commit-tree -p origin/main+push 纯快进，投递面=仅车道件+Tools/autofill.py+"
    "MSG-2108+r487-489 车道证据·30 交集共享面零触碰（远端较新版保留）·本地 pathspec 偏提交照律②〕。产物清单漂移="
    "Tools/autofill.py〔r487 fullburn 接线·r490 投递主干 fleet 可见〕+fleet/inbox/MSG-20260930-2108-bma-bmc-d41-berth-"
    "zero-collision.md〔r489·r490 投递〕+results/_r489bma_{s6.txt,swallow_fix.py}+results/_r490bma_{closeout,surgical_push}"
    ".{py,json}+r487-489 车道证据族（round_reports-bm-a.md/state-bm-a.json/fleet/machines/bm-a.json/pool_dualrun.bm-a.jsonl/"
    "token_usage.bm-a.json/*_status.bm-a.json/compute_audit.bm-a.json/regime_state.bm-a.json/autofill_state.bm-a.json）+再生面"
    "（LIVE/REPORT-2026-09-30/dscore/dashboard——本地当前=CEO 本机可见面·主干面=他机再生版本保留）；统一键 **362,389 实读**"
    "（bm-c r284 锚·D-41 预算消费 308/500〔Face B +2 bm-b r285〕）；指针：**10-01 月首轮三件套（science_audit/"
    "monthly_briefing/self_review）+REGIME_GUARD v3 日期门 10-01 自动激活禁手改+fullburn 窗开启（接线已主干可见）+RW-5 外审复核 "
    "10-03→决策线恢复（M1 真日删 D-30 前置）+T-129#1 D-41 prereg 仍 deferred（banned-gate 并发会话落地窗）+09-30 bar 落地观察"
    "（sina ETF 面发布即 S6 全链自动挂钩·最坏窗 10-09 开市）+治理零双跑（Q4 槽位 09-26 已 discharge·下实例 2027-01-01）**；"
    "下一 5x=bm-a r495\n"
)
with io.open("research/HANDOVER.md", "r", encoding="utf-8") as f:
    lines = f.readlines()
assert lines[0].startswith("# "), "HANDOVER title expected at line 1"
lines.insert(1, handover_entry)
with io.open("research/HANDOVER.md", "w", encoding="utf-8", newline="\n") as f:
    f.writelines(lines)
print("[closeout] HANDOVER r490 5x entry inserted after title; total lines %d" % len(lines))
print("[closeout] ALL DONE rc=0")
