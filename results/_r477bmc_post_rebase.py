"""r477 bm-c post-rebase supplement: append honest receipt line to round
report + update state/heartbeat handoff fields (fleet-silence RESOLVED
in-window by bm-b r674 wave; close push rejected -> rebase 14-UU canon
resolve -> DELIVERED tip b71aeec74). Programmatic json writes with
post-write json.loads self-proof (r645 law). Bytes-mode report append
(r641 law)."""
import datetime
import json
import os

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
STATE = os.path.join(ROOT, "state-bm-c.json")
REPORT = os.path.join(ROOT, "round_reports-bm-c.md")
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")

now = datetime.datetime.now()
now_iso = now.isoformat(timespec="seconds")

rebase_receipt = (" POST-REBASE RECEIPT (in-window): close push rejected "
                  "(origin moved: bm-b r674 wave landed ~14:15 = r674 close "
                  "14-UU canon resolve + autofill keepalive refresh "
                  "b8df8adaf + MSG-1332 closure receipt a69f4254a/9dcab84bd) "
                  "-> FLEET-SILENCE OBSERVATION RESOLVED: bm-b alive (long "
                  "round, not machine death), trio advancing V790/Q613/D459 "
                  "(+8/+4/+5 vs r476 probe) -> pull --rebase: 14-UU canon "
                  "resolve (snap faces = mine fresher 14:10-14:13 vs bm-b "
                  "14:04 via deep-ts probe r100/R350 lineage; tool faces via "
                  "merge_lane_views single-source r351 rebase-aware; twins "
                  "follow; marker probe 75 staged faces 0 hits r644 "
                  "line-start law) + 2 satengine lane-face pick conflicts "
                  "resolved LIVE-WINS (daemon overwrote markers at 14:18:20, "
                  "r630/r440 laws) -> 3 commits replayed (75d9e2e7c close / "
                  "9dbe05e0f absorb / b71aeec74 resolver artifacts) -> "
                  "push_verify DELIVERED tip b71aeec74 ahead=0 behind=0.")

supp_line = (
    now_iso + "+08:00｜r477-补｜dept:工程（收口后补充回执·机队静默观察解案+"
    "rebase 净路收口）｜事实更正=轮报告正行所记「escalation criteria for r478」"
    "已在当窗内解案：bm-b r674 波 ~14:15 落 origin（r674 close 14-UU canon "
    "resolve+autofill keepalive 刷新 b8df8adaf+MSG-1332 闭环回执）——机队静默"
    "=长轮窗口非死机·trio 推进 V790/Q613/D459（vs r476 探针 +8/+4/+5）·keepalive"
    " 自愈实证（owner_since 刷新）｜收口推送被拒（origin 前移）→pull --rebase："
    "14-UU canon 解（snap 面=本侧更新 14:10-14:13 vs bm-b 14:04 深ts探针 r100/"
    "R350 血统·tool 面=merge_lane_views 单源〔r351 rebase-aware〕·twins 跟随·"
    "marker 探针 75 staged 面 0 命中〔r644 行首律·git grep rc=128 旁路〕）+2 "
    "satengine 车道面 pick 冲突 LIVE-WINS 解（daemon 14:18:20 覆写 marker·r630/"
    "r440 律）→三 commit 重放（75d9e2e7c close/9dbe05e0f absorb/b71aeec74 "
    "resolver 证据件）→push_verify DELIVERED（tip b71aeec74·ahead=0·behind=0）"
    "｜r478 读数面：trio 探针按新基线（V790/Q613/D459）计 delta；仅当新静默窗/"
    "keepalive 越阈再现时按原判据升级｜零池面携带 push（本机 3 commit 均不含 "
    "runnable_pool 面·sync_face 豁免）｜本地未达 origin commit 数: 0（push_verify "
    "自证）\n")

with open(REPORT, "ab") as f:
    f.write(supp_line.encode("utf-8"))
with open(REPORT, "rb") as f:
    lines = [ln for ln in f.read().split(b"\n") if ln.strip()]
assert b"r477-补" in lines[-1], "supplement line append failed"
print("REPORT_OK supplement appended")

with open(STATE, encoding="utf-8-sig") as f:
    st = json.load(f)
st["did"] = st.get("did", "") + rebase_receipt
st["last_round"] = ("r477 bm-c: golden-week watch + fund-trio watch + "
                    "fleet-silence RESOLVED in-window (bm-b r674 wave, trio "
                    "V790/Q613/D459 advancing) + close push rejected -> "
                    "rebase 14-UU canon resolve + live-wins lane faces -> "
                    "DELIVERED tip b71aeec74; zero incident")
st["next"] = ("(a) r478 watch round: trio probe rebased to new baseline "
              "V790/Q613/D459; fleet-silence RESOLVED (bm-b alive; only "
              "escalate on a NEW stall crossing keepalive threshold or "
              "heartbeat >20min + origin silence past watchdog window). "
              "(b) MSG-1332 CLOSED by bm-b receipt 9dcab84bd (consumption "
              "watch done). (c) fund-trio finalize window 10-05 10:30 opens "
              "(bm-b owner; ETA V 10-06 15:00 / Q long-pole 10-07 11:00). "
              "(d) D-20261004-02(1)(2)(3) receipt window 10-06 00:00. "
              "(e) D-06 full closure window 10-07 (bm-c lead). (f) "
              "O-2115/O-2030 acceptance 10-08; market reopen 10-09; next "
              "5x = bm-c r480.")
st["current_task"] = ("当前活: golden-week watch r477 CLOSED (fleet-silence "
                      "RESOLVED in-window: bm-b r674 wave landed, trio "
                      "V790/Q613/D459 advancing; rebase 14-UU canon resolve "
                      "DELIVERED tip b71aeec74) | 最近实物: results/"
                      "_r477bmc_rebase_resolve.py (14-UU canon resolver, "
                      "r674 lineage) + round_reports-bm-c.md r477-补 receipt "
                      "line @ " + now_iso + " | 下个里程碑: fund-trio "
                      "finalize 窗 10-05 10:30 开 (bm-b 正主·ETA V 10-06 "
                      "15:00/Q 长杆 10-07 11:00); D-06 收口 10-07 (bm-c "
                      "lead); 开市 10-09")
st["verify"] = (st.get("verify", "") + " POST-REBASE: push_verify DELIVERED "
                "tip b71aeec74 ahead=0 behind=0; marker probe 75 faces 0 "
                "hits; resolver artifacts committed")
st["updated"] = now_iso
st["updated_at"] = now_iso
st["last_round_at"] = now_iso
st["last_seen"] = now_iso
st["heartbeat_epoch_utc"] = int(now.timestamp())
with open(STATE, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
with open(STATE, encoding="utf-8-sig") as f:
    recheck = json.load(f)
assert recheck["round_no"] == 477
assert isinstance(recheck.get("heartbeat_epoch_utc"), int)
print("STATE_OK supplement round=477")

with open(HB, encoding="utf-8-sig") as f:
    hb = json.load(f)
prev_fields = set(hb.keys())
prev_ack = hb.get("orders_ack")
hb["activity_now"] = ("golden-week watch r477 CLOSED; fleet-silence RESOLVED "
                      "(bm-b r674 wave, trio advancing); rebase 14-UU canon "
                      "resolve DELIVERED")
hb["current_task"] = (hb["activity_now"] + "; next: finalize window 10-05 "
                      "10:30 (bm-b owner)")
hb["latest_artifact"] = ("results/_r477bmc_rebase_resolve.py (14-UU canon "
                        "resolver r674 lineage) + r477-补 receipt line in "
                        "round_reports-bm-c.md")
hb["heartbeat_epoch_utc"] = int(now.timestamp())
hb["last_seen"] = now_iso
hb["updated"] = now_iso
with open(HB, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
with open(HB, encoding="utf-8-sig") as f:
    hbr = json.load(f)
assert set(hbr.keys()) >= prev_fields
assert hbr["orders_ack"] == prev_ack
assert isinstance(hbr.get("heartbeat_epoch_utc"), int)
print("HEARTBEAT_OK supplement fields=" + str(len(hbr)))
