"""r485 bm-a one-shot: state + heartbeat writes (epoch int law R170/R178,
clock_read T-sep law R262)."""
import datetime as dt
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now = dt.datetime.now()
ts = now.isoformat(timespec="seconds")
epoch = int(time.time())

did = ("r485: 09-30 bar 源端诊断闭环轮: sina ETF 日线面节前发布滞后实证 "
       "(四腿探针 _r485bma_sina_wrapper_probe: akshare 包装器尾 09-29==原始 "
       "klc_kl.js 尾 09-29 双源一致=包装器无罪; 股票面 sh600519 已有 09-30; "
       "tencent 已有; hq 实时面活=sina ETF 面单侧滞后非宕机) -> update_daily "
       "诚实 no-op 等自动挂钩为正解; S6 36+ 腿全 rc0 (dualrun ZERO-DRIFT "
       "51/3; lhb cutoff 09-30 检疫态终; CALL/LIVE/REPORT-2026-09-30 再生 "
       "ORANGE cap50 COOL; paper 锚 OK; t35 PASS 0 例; prospect 22/22; "
       "marks 幂等 no-op x4); orders 127/127 双扫零未回执; decisions "
       "mtime 17:22 零新增 (D-37~41 已 r479~483 回执); smoke 47/47; "
       "attrition CLEAN; HANDOVER 485 核对入册; bm-b r472/473 五提交 "
       "rebase 并合")
verify = ("smoke 47/47; S6 全 rc0 (audit 旗=pool_starvation+supply_floor "
          "RW-5 冻结合法 idle 同 r484 态; WM py_low_board_clear; 车道守卫 "
          "x5 诚实 no-op; ah 分离刷新 spawn 节流在途); probe 四腿 JSON 证据 "
          "results/_r485bma_sina_wrapper_probe.json; 心跳 epoch int 自证")
nxt = ("r486: 09-30 bar 落地观察续 (sina ETF 面发布即条件块自动挂钩); 10-01 "
       "月首轮三件套 (science_audit/monthly_briefing/self_review); "
       "REGIME_GUARD v3 日期门 10-01 自动激活 hands-off; RW-5 外审 10-03->"
       "解冻->D-41#1 跨起点 prereg (待并发会话 banned-gate 落地)")

sp = os.path.join(ROOT, "state-bm-a.json")
with open(sp, encoding="utf-8-sig") as fh:
    st = json.load(fh)
st["round_no"] = 485
st["did"] = did
st["verify"] = verify
st["next"] = nxt
st["last_round_at"] = ts
st["current_task"] = ("10-01 month-first trio + 09-30 bar landing watch "
                      "(sina ETF face lag) + RW-5 external review 10-03")
st["updated"] = ts
with open(sp, "w", encoding="utf-8") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=2)

hp = os.path.join(ROOT, "fleet", "machines", "bm-a.json")
with open(hp, encoding="utf-8-sig") as fh:
    hb = json.load(fh)
hb["last_seen"] = ts
hb["current_task"] = st["current_task"]
hb["verdict"] = "healthy: r485 done, S6 all rc0, WM board-clear"
hb["heartbeat_epoch_utc"] = epoch  # python int, R170/R178 law
hb["clock_read"] = ts               # T-sep ISO 8601, R262 law
with open(hp, "w", encoding="utf-8") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=2)

with open(hp, encoding="utf-8-sig") as fh:
    back = json.load(fh)
assert isinstance(back["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in back["clock_read"], "clock_read must be T-separated"
orders_dir = os.path.join(ROOT, "fleet", "orders")
orders = sorted(os.path.basename(p) for p in os.listdir(orders_dir)
                if p.startswith("O-"))
unacked = [o for o in orders if o not in set(back.get("orders_ack", []))]
print(json.dumps({"state_round": st["round_no"], "epoch": back[
    "heartbeat_epoch_utc"], "epoch_is_int": isinstance(
    back["heartbeat_epoch_utc"], int), "clock": back["clock_read"],
    "orders": len(orders), "unacked": len(unacked)}, ensure_ascii=False))
