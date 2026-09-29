"""r431 bm-a S7 closeout: state/heartbeat/round-report writes via file-face (CJK-safe), orders re-scan, inbox check."""
import datetime
import glob
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(datetime.datetime.now().timestamp())

# 1) state-bm-a.json -> round 431
s = json.load(open("state-bm-a.json", encoding="utf-8"))
s.update({
    "round_no": 431, "round": 431, "loop_round": 431,
    "last_round": 430, "last_round_ts": s.get("last_round_at", ""),
    "did": ("r431: S0 double-rebase storm passed (16-UU canon-resolved: 7 ALL_FACES merge_lane_views + "
            "10 snapshot/twin/js _r430bma_resolve2 deep-ts all :2: origin-new-side parse-verified) + "
            "r430+r430-addendum merge-back pushed origin/main per pit-93 pointer; "
            "T-102 lane-4 FORUMS digest landed (DIGEST-20260929-t102-lane4-forums.md: taoguba full-text 7-node "
            "decision tree + jisilu KongManZi corpus + three-knows/four-sources/three-principles convergence) "
            "+ B12 half-verified flip + v4 forum-lane arms x3 = T-102 four lanes 4/4 wave-close"),
    "verify": ("smoke 26/26; S6 37 legs rc=0 (dualrun ZERO-DRIFT 115 streak 12/3; regime ORANGE; clock "
               "ORANGE_COOL; live.paper OK; t35 open-fill PASS 6 zero-pending; promotion 0/22; REPORT-0929 "
               "faces=5; token L2 0); tasks: loop Running/pin=8, watchdog Ready, IntradayMarks Ready next "
               "09-30 09:25, pre-commit claw byte-equal"),
    "next": ("r432: (a) T-102 v0.2 finalization slice (gap-list finalize + v4 arm list as doc -> ticket "
             "done-flip); (b) W8 JUDGE chain watch; (c) trading-day 15:00-15:10 settle-tick manual; "
             "(d) 10-01 month-first triple + pool wave-1 flip quiet window; next 5x = bm-a r435"),
    "last_round_at": NOW, "current_task": "r431 closed: T-102 4/4 wave-close; next=v0.2 finalization + W8 watch",
    "updated": NOW,
})
json.dump(s, open("state-bm-a.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# 2) heartbeat fleet/machines/bm-a.json (epoch MUST be int)
h = json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))
h["last_seen"] = NOW
h["verdict"] = ("py_low_board_clear legal idle (board 0 open + pool 115/115 done + W8 screen in-flight "
                "bm-b/bm-c; r431 product = T-102 lane-4 wave-close)")
h["heartbeat_epoch_utc"] = EPOCH
h["clock_read"] = NOW
if "cpu_cores" not in h:
    h["cpu_cores"] = 32
json.dump(h, open("fleet/machines/bm-a.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ck = json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))
assert isinstance(ck["heartbeat_epoch_utc"], int), "epoch must be int (smoke F7)"

# 3) round report line append (file-face, UTF-8)
line = (
    f"{NOW} | r431 | dept:研究 (T-102 lane-4 论坛道·收波件) | "
    "WM-VERDICT: 绿 red=false lane healthy py 0.7-2.7% py_low_board_clear 合法闲置 "
    "(板 0 open+池 115/115 done+W8 screen 在飞 bm-b/bm-c) | "
    "did: (1) S0 双 rebase 风暴通过——16-UU 批正典解 (7 ALL_FACES merge_lane_views + 10 snapshot/twin/js "
    "_r430bma_resolve2 深探针全取 :2: origin 新侧 parse-verified) + r430+addendum merge-back 推上 "
    "origin/main c25577b88..5d6a6f55c (pit-93 指针兑现) + 陈旧 09-28 autostash 遗留发现 (Money02 面) 不 pop 留痕; "
    "(2) S0.5 令差集 122/122 全枚举零未回执+集团 decisions 无新行; "
    "(3) S3 产品=T-102 lane-4 论坛道 digest 落地 (DIGEST-20260929-t102-lane4-forums.md: 22 收割→6 簇→3 全文验——"
    "淘股吧 m.tgb.cn 全文可达东江炒家 7 节点决策树 [首分 vs 二分动作分化+二分清仓律 10:1 宣称未实证+T+1 双区间约束"
    "+买点三阶梯+反常行情诚实披露=第七信号阳性] + 孔曼子摊大饼 30 章 TOC + 三知道/四来源/三原则跨载体收敛 "
    "[四来源→四袖全覆盖旁证·三原则==D6 相关性帽/KPI 期望双列同构]; 雪球 WAF/知乎 403 两墙如实披露) "
    "+ B12 翻半验 + v4 论坛道增量臂 x3 (二分清仓律臂/情绪阶段→仓位前置腿/题材梯队判据组) = **T-102 四道 4/4 收波**; "
    "(4) S6 37 legs rc=0 (dualrun ZERO-DRIFT 115 streak 12/3; regime ORANGE breadth .83; clock ORANGE_COOL; "
    "live.paper OK; t35 open-fill PASS zero-pending 6; promotion 0/22; REPORT-0929 faces 5; token L2 0) | "
    "verify: smoke 26/26; tasks loop Running/针位 8/watchdog Ready/IntradayMarks Ready next 09-30 09:25; "
    "pre-commit claw byte-equal | "
    "next: r432 (a) T-102 v0.2 定稿片 (缺口定稿+v4 臂清单成文→ticket done 翻面) (b) W8 JUDGE 链盯 "
    "(c) 交易日 15:00-15:10 settle-tick 手动腿 (d) 10-01 月首轮三件套+池 wave-1 flip 静窗; next 5x=bm-a r435\n"
)
with open("logs/iteration-loop/round_reports-bm-a.md", "a", encoding="utf-8", newline="\n") as f:
    f.write(line)

# 4) orders second scan (S7 double-scan law)
ack = set(h.get("orders_ack", []))
files = set(os.path.basename(p) for p in glob.glob("fleet/orders/O-*.md"))
unacked = sorted(files - ack)
print("orders rescan:", len(files), "total,", len(unacked), "unacked", unacked if unacked else "")

# 5) inbox check
inbox = [p for p in glob.glob("fleet/inbox/*") if os.path.isfile(p) and "processed" not in p]
print("inbox unprocessed:", len(inbox), [os.path.basename(p) for p in inbox])
print("S7 writes done: state 431, heartbeat epoch", EPOCH, "| report line appended |", NOW)
