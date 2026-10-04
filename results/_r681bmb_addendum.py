"""r681 bm-b addendum: push-race resolution record (skill 留痕 law) + heartbeat
current_task refresh. Idempotence: marker count==0 gate before append."""
import datetime
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RR = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
HB = os.path.join(ROOT, "fleet", "machines", "bm-b.json")

marker = "round 681 addendum (bm-b)".encode("utf-8")
line = (
    "2026-10-04T16:58:00+08:00 | round 681 addendum (bm-b) | S7 收口撞头实录：push 被 non-FF "
    "拒=bm-c r484 波（66bdc7d07/a3a4b56b8/91abdbb45/14b4007f7·16:39-16:49）与我 r681 收口同窗竞速；"
    "rebase 路被 daemon treadmill 脏面挡死 -> 按 r437 iv 走 merge 净路（真 merge-base=31969e016 daemon "
    "自提交·脏面交集=0·autofill 面预对齐 checkout 后零差异免 absorb）；31 UU 全过分类器（30 分类+1 "
    "UNKNOWN=_attrition_guard_scan 手工裁定=per-run 快照 take-new ts）；resolver=_r681bmb_merge_resolve.py"
    "（r686 血统）：28 快照面全 take-ours（嵌入 ts 16:45-16:47 vs 16:35-16:37·孪生对同侧·daily_scorecard "
    "no-ts 兜底经双侧 blob 手工复核 16:47:12>16:37:07 正确）、compute_audit history union 201+201->203、"
    "x2_watch 行 union 2778+2778->2784、token_usage machines per-key union side_pick=3（r456 断言在位）；"
    "pool_w3_post_assert 过（池面双侧恒等零回退）；merge 后 attrition 扫描 CLEAN 骑 commit；push-verify "
    "DELIVERED（tip==remote a98dc96a6·ahead=0）；后到让路合规=我并他们（fleet/README §4 commit 时序）。"
    "坑录候选：无新坑（全按在册律走·r686 探针文件名错号 680!=686 为上轮会话命名瑕疵零机制面）"
)
data = open(RR, "rb").read()
assert data.count(marker) == 0, "addendum marker already present"
with open(RR, "ab") as fh:
    fh.write(line.encode("utf-8") + b"\n")
assert open(RR, "rb").read().count(marker) == 1

now = datetime.datetime.now().astimezone()
clock = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
hb = json.load(open(HB, encoding="utf-8"))
hb["current_task"] = (
    "r681 closed+DELIVERED (a98dc96a6): S6 38/38 rc0 streak 52; push-race vs bm-c r484 wave "
    "resolved via r437 merge path (31 UU canon-resolved, all regen twins take-ours 16:46>16:37, "
    "ledgers union zero-loss); trio NULLS V853/Q668/D507 of 2000 burning healthy (ETA V 10-06T16/"
    "Q 10-07T09/D 10-08T03); N1-W116 2/12 RAM-gated self-ignite; next grain = FUND-VALUE finalize "
    "候选窗 10-06T15+ (r668 池面双翻律, rehearsal ALL-GREEN)"
)
hb["last_seen"] = clock
hb["ts"] = clock
hb["updated"] = clock
hb["updated_at"] = clock
hb["heartbeat_epoch_utc"] = int(datetime.datetime.now().timestamp())
with open(HB, "w", encoding="utf-8", newline="") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
hb2 = json.load(open(HB, encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int)
print("ADDENDUM OK", clock)
