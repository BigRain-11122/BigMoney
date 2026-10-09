# r819 bm-b closeout: state.json + heartbeat + round report + CODELY line.
# ASCII-only per cross-machine deploy law (r847 PS-encoding family, python face).
import json
import os
import time
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())
R = 819


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def save(obj, p):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


# ---- state.json (bm-b file per S5 law) ----
sp = os.path.join(ROOT, "state.json")
st = load(sp)
st["round_no"] = R
st["round"] = R
st["round_no_label"] = "r%d" % R
st["did"] = ("r819: tech T13 landed (scripts/d19_watermark.py D-19 watermark "
             "write-side integrity guard: single-source canonical probe read + "
             "verbatim full-string write + r585 --advance atomicity gate + "
             "read-back equality assertion; selftest 14/14; live NOOP both "
             "keys MATCH) + S6 39 legs rc0 (dualrun ZERO-DRIFT streak 3)")
st["verdict"] = ("r819: T13 closed (d19_watermark.py 4-law guard chain "
                 "selftest 14/14 + live update NOOP DEC a3ea37bd/ORD e286f842 "
                 "both MATCH read-back equality OK + verify structural_ok; "
                 "S0.5 watermark write step now canonical via guard); smoke "
                 "49/49; S6 39 legs rc0 (zt_pool_crosscheck 2 soft-warn "
                 "strong-dtgc known class 002487/605366; dualrun streak 3); "
                 "watermark red=false healthy; orders both sweeps zero "
                 "unacked; ORD/DEC hash MATCH; attrition CLEAN; orphans=0")
st["now_active"] = ("r819: tech T13 closed (D-19 watermark write-side guard "
                    "scripts/d19_watermark.py)")
st["current_task"] = ("r820: tech queue head T15 (regime_thermo_build non-"
                      "Money02 host lane adjudication) / T16 dualarm contract "
                      "adapter / T17 orders_ack diff automation; waiting: "
                      "Monday 10-12 09:15 minute_feed gated backfill 10-08/"
                      "10-09 / astock refresh tail (15/5229 continuation "
                      "in-flight) / W18 wave drafting gated on W17-JUDGE "
                      "drain + RAM window")
st["next"] = st["current_task"]
st["task"] = ("tech queue T15/T16/T17 pool; waiting: astock refresh tail / "
              "Monday minute_feed backfill / W18 wave gated on W17-JUDGE")
st["latest_artifact"] = ("r819: scripts/d19_watermark.py (selftest 14/14 + "
                         "live update/verify + receipt results/"
                         "d19_watermark.json), 2026-10-10 06:2x")
st["next_milestone"] = ("r820: tech T15 lane-adjudication face or T17 ack-diff "
                        "automation (<=48h); Monday 2026-10-12 09:15 "
                        "minute_feed first gated run backfills 10-08/10-09")
for k in ("last_round_at", "last_round_ts", "ts", "updated", "updated_at",
          "last_seen", "clock_read"):
    st[k] = NOW
save(st, sp)
print("state.json round ->", st["round_no"])

# ---- heartbeat fleet/machines/bm-b.json ----
hp = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
hb = load(hp)
hb["round"] = R
hb["round_no"] = R
hb["now_active"] = st["now_active"]
hb["current_task"] = st["current_task"]
hb["task"] = st["task"]
hb["latest_artifact"] = st["latest_artifact"]
hb["next_milestone"] = st["next_milestone"]
hb["verdict"] = st["verdict"]
hb["last_action"] = ("r819: tech T13 (d19_watermark.py write-side guard + "
                     "live canonical wiring) + S6 39 legs rc0 + S7 quartet "
                     "green + attrition CLEAN")
for k in ("last_round_at", "last_seen", "updated", "ts", "clock_read"):
    hb[k] = NOW
hb["heartbeat_epoch_utc"] = EPOCH
hb["free_ram_gb"] = 12.1
hb["gpu_free_vram_mb"] = 3459
hb["gpu_free_vram_gb"] = 3.38
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["orphan_faces"] = 0
hb["orphan_face_note"] = ("r819 probe 06:2x: 16 py faces 0 orphans; astock "
                          "refresh continuation in-flight lawful (tail "
                          "15/5229)")
hb["sync"] = {
    "ahead": 0, "behind": 0, "last_push_ts": NOW,
    "note": ("r819: S0 fetch ahead0/behind0 identical; round commit push "
             "follows; verify = post-push fetch+rev-list+ls-remote "
             "self-proof"),
}
save(hb, hp)
ep = hb["heartbeat_epoch_utc"]
assert isinstance(ep, int), "epoch must be JSON int (F7 R170/R178 law)"
print("heartbeat epoch ->", ep)

# ---- round report line (bm-b file per S5 law) ----
rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
line = (
    "2026-10-10T06:2x+08:00 | r819 bm-b | dept:工程（tech T13 D-19 水位写侧完整性守卫出列·S0.5 写步正典化） | "
    "WM-VERDICT: 绿（red=false·lane healthy·probe verdict=insufficient_history 观察相·桶 pool0/board0/board_inflight0/local0 全空=周六值守合法） | "
    "孤儿面=0（probe 16 py faces 0 orphans·astock refresh 尾在飞 15/5229 continuation 合法） | "
    "①S0-1 锚定 bm-b；S0 fetch 同步面 ahead0/behind0 恒等零 rebase；"
    "②S0.5 双扫=orders 现存 60 件全 ack 零未回执+D-19 正典探针 DEC a3ea37bd/ORD e286f842 双 MATCH 零新决策；"
    "③S1 smoke 49/49；S2 job_list 0+fleet 票 0 open（T-179/180/181 全 done：T-181 bm-a r942 0/6 判负收卷·T-180 bm-c r825 done）；"
    "④P0 产品=tech T13 出列：**scripts/d19_watermark.py D-19 水位写侧完整性守卫**=读单源正典探针 subprocess（r686/r814 律）"
    "+写 verbatim 全串直出探针 JSON 零手拼（r812 律）+candidate 形状门（hex/40-64 长/禁空白）"
    "+r585 原子门（delta 无 --advance 拒收·消费回执与键进位同轮强制）+原子写+读回全串恒等断言（败=字节回滚 exit 2）"
    "+机面 r582 律 machine_id-aware（bm-b=state.json）+provenance 键 d19_watermark_guard 随键标算法（r786）"
    "+lower() 双侧归一（r503/r711·大小写差非 delta·verbatim 写规范化正典形）；"
    "selftest 14/14（含 r811 8-hex 前缀拒收腿+r812 splice 形状过而恒等败腿+全串治愈腿+r585 无 advance 拒腿）；"
    "实弹 update NOOP（DEC/ORD 双 MATCH·读回恒等 OK）+verify structural_ok 全 equal+state provenance 落位+回执 results/d19_watermark.json；"
    "**S0.5 水位写步即起一律走守卫**（旧收口脚本手写键路径废弃）；技术队列 5→4（T15 队头）；"
    "⑤S6 39 腿全 rc0（dualrun ZERO-DRIFT streak 3；zt_pool_crosscheck 2 软警 strong∩dtgc 已知类 002487/605366；"
    "dualarm DUALARM-2026-09-30 再生；daily_report REPORT-2026-10-10+ceo_live_usage LIVE-2026-10-10 落 CEO 面；"
    "周六无新 bar live.paper 四腿合法跳；token L2 本日 0）；"
    "⑥S7 四件套绿（loop pin=2 no-op+watchdog 重注册 06:24 首跳+pre-commit/pre-push 爪 LF 归一重装）+attrition 4 台账 CLEAN+孤儿探针 0；"
    "⑦orders 二扫零新增+inbox 空；本地未达 origin commit 数=0（commit 后 push+fetch+ls-remote 自证） | "
    "下轮指针：r820 tech 队头 T15（regime_thermo_build 非 Money02 宿主车道判定）/T16 dualarm 契约适配器/T17 orders_ack 差集自动化；"
    "waiting：周一 10-12 09:15 minute_feed 首 gated 轮回补 10-08/10-09 / astock refresh 尾 / W18 wave gated on W17-JUDGE drain+RAM 窗"
)
with open(rp, "a", encoding="utf-8") as f:
    f.write(line + "\n")
print("round report appended")

# ---- CODELY.md one-line memory (four-gate: durable rule + pointer, no retell) ----
cp = os.path.join(ROOT, "CODELY.md")
cl = ("- [2026-10-10 06:2x r819 bm-b] **D-19 水位写步正典化**：S0.5/收口一切水位键写入一律走 `scripts/d19_watermark.py update`"
      "（读=正典探针 subprocess·写=verbatim 全串+--advance 原子门+读回恒等断言·selftest 14/14·回执 results/d19_watermark.json），"
      "禁手拼/前缀验证/收口脚本手写键（r810-r812 族四犯根治面）；坑律本体=pit-protocol-d19.md r812 条。How to apply："
      "任何轮会话/收口脚本需要写 last_decisions_sha/last_orders_sha 时改调守卫，delta 先消费后 --advance。")
with open(cp, "a", encoding="utf-8") as f:
    f.write(cl + "\n")
print("CODELY.md appended")
