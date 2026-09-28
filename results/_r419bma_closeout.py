"""r419 bm-a S7 closeout writer: state, round report, heartbeat, CODELY entry."""
import json
import time
import datetime as dt

NOW = dt.datetime.now().astimezone()
ISO = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())

# ---- state-bm-a.json ----
st = json.load(open("state-bm-a.json", encoding="utf-8"))
st["round_no"] = 419
st["last_round_ts"] = ISO
json.dump(st, open("state-bm-a.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("state round_no ->", st["round_no"])

# ---- round report line ----
REPORT = "logs/iteration-loop/round_reports-bm-a.md"
line = (
    f"{ISO} | r419 bm-a (dept:工程+舰队) | did: 水位绿（red=false lane healthy·next_pick=claimed advisory 在位）；"
    f"**S0 merge-back 落地=r416 addendum-3 既定首启动作（3 轮延迟后本轮破局）**：3 次降级轮=r400 live-window 判据下 rebase 重放结构性活锁"
    f"（活机 10min 推频永真+每降级轮再堆 1 本地 commit=冲突面只增不减）→ 本轮改单次 merge（21 面冲突一次解）+两步竞态安全式"
    f"（先推 machine/bm-a-r419 逃生分支零竞态承运→再原子 FF 推 main）——**main push 12fa3e709..6eb3da16f fast-forward 落链**，"
    f"r416-r418 滞留产物（W6-SCREEN prep 修复/坑律 89 批/死窗 salvage/T-105 面）全数上链；21 面正典解：7 ALL_FACES lane-union"
    f"（runnable_pool 110 id-union done-吸收/compute_audit history 188 行 ts-key union）+4 host=bm-a 面取本机+2 ts 探针 snapshot"
    f"+3 孪生对 generated_at 深探同侧字节拷+CODELY 条目级 union（batch-71 撞号再编 89→90 我侧让路·双侧指针行并含 r328）+水位律当窗整编"
    f"（11362→9078B·r173 范式合并 09-28 老指针 6 行→1 行·批内容零删）+archive 尾追 union 363+15+15=393 行零丢失；"
    f"orders 122/122 双扫差集=0；decisions.md 03:20 无新行 P-32 零动作；smoke 26/26；任务板无 open 新票（bm-a 既有 claimed 3 张）"
    f"零认领（窗口被 merge-back 占用·bandit claimed 非可领）；S6 33 腿全跑（dualrun ZERO-DRIFT streak 3/3·audit 旗 standing-honest"
    f"（supply_floor ready=1<3·bm-b 车道供给面窗内）·probe insufficient_history n=1 窗重启·clock ORANGE_COOL sleeves=4 activated=0"
    f"·moneyflow rank pass detached spawn+AH refresh spawn 在飞·promo eligible=0/22 诚实·其余 no-op/幂等）；无新 bar 3 腿合法跳"
    f"（live.paper/t35_open_fill/t24_prospect_paper·cutoff 09-28）；runner 注记=PS Start-Process 不回填 $LASTEXITCODE（rc 面以产物 tail"
    f"+status JSON 双证·无 Traceback） | verify: 21 面 git add 后 UU=0；merge commit 6eb3da16 落 main（12fa3e709..6eb3da16f FF）；"
    f"CODELY 9078B≤10KB+kept-lines 零丢失断言过；archive 393 行=363+15+15；orders 差集 0 | next: 常规轮序恢复（bm-a 回链后首可用窗）——"
    f"试用劳动力常设线起草下一波候选大考批（板空+池饿 standing）；supply_gap 三旗=bm-b W6-JUDGE 窗内尾留观察；r420 5x HANDOVER"
)
with open(REPORT, "a", encoding="utf-8") as fh:
    fh.write(line + "\n")
print("report line appended", len(line), "B")

# ---- heartbeat ----
hb = json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))
hb["last_seen"] = ISO
hb["current_task"] = ("r419: S0 merge-back LANDED (merge-not-rebase 21-face canonical + escape-branch-first + "
                      "atomic FF main push 12fa3e709..6eb3da16f) - r416-r418 stranded products on-chain; "
                      "S6 33 legs ran (dualrun streak 3/3, audit flags standing-honest); orders 122/122; smoke 26/26")
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = ISO
json.dump(hb, open("fleet/machines/bm-a.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
back = json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))
assert isinstance(back["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178)"
assert "T" in back["clock_read"], "clock_read must be T-separated (R262)"
print("heartbeat ok epoch-int:", back["heartbeat_epoch_utc"])

# ---- CODELY 坑律 entry (one matter, <=1KB) ----
C = "CODELY.md"
text = open(C, encoding="utf-8").read()
entry = ("- [2026-09-29 07:5x r419 bm-a] 坑律九十一批（merge-back 破活锁两步式：单次 merge 代逐 commit 重放+逃生分支先行+原子 FF 推 main）："
         "多轮滞留链的回迁若沿用 pull --rebase 逐 commit 重放=结构性活锁——活机窗判据（origin HEAD 落龄<10min）在机群 10min 推频下永真，"
         "且每降级轮再堆 1 本地 commit 冲突面只增不减（r417/r418/r419 三连实证）。正解=git merge origin/main 单次合并（N commit 冲突一次解）"
         "→先推 machine/<id>-rN 新 ref 逃生分支（零竞态承运）→再原子 FF 推 main（落或拒皆无害，拒=下轮增量 merge 即 trivial）。"
         "配方脚本 merge_lane_views.py resolve 的 stage 语义在 merge 下不变（:2:=HEAD 侧=base_side，union/take-new 均对称）。"
         "How to apply：连续 2 轮以上 S0 撞同型 UU 即弃 rebase 改此两步式；撞号批（batch-71 律）后到侧让号重编。\n")
assert len(entry.encode("utf-8")) < 1100
text = text.rstrip("\n") + "\n" + entry
nb = len(text.encode("utf-8"))
assert nb <= 10240, f"CODELY over hard line: {nb}"
open(C, "w", encoding="utf-8", newline="").write(text)
print("CODELY entry added,", nb, "B (<=10KB)")
