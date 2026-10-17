# -*- coding: utf-8 -*-
# r997 closeout: heartbeat + state.json + round report append (fresh-read-modify-write)
import json, time, datetime

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())
DID = ("r997: (a) S0 estate absorption: dead r995/r996 sessions absorbed (emergency row d452d780 unpushed; "
       "their S6 chain 43/43 rc0 at 23:05 log results/_r996bmb_s6_log.txt + d19 watermark advance orders->0b991d78 "
       "verified ahead of origin, landed via this push); (b) E1 leg-5 drama delivery: per bm-a MSG-2232 "
       "(tailscaled restarted, inbox empty) re-queued 5 pilot files rc=0 x5 with byte evidence "
       "tx 143537244->162175212 (+18,637,968 bytes) - MSG-20261017-2356-bmb sent; (c) O-20261017-2207 "
       "(CEO UU remote): ack-only, bm-a executed with in-file receipt 22:16, zero bm-b leg, orders_ack updated; "
       "(d) IndexTTS-2.5/voicegen lane YIELDED to live interactive bm-b window per INDEXTTS-LANE-CLAIM-bmb.txt "
       "(chain alive: curl 15108 bigvgan downloading, boot chain PID 18300 pinging, kohya+CSA queue spawned 23:42:46) "
       "zero interference per anti-dual-execution; (e) smoke 49/49, sat engine ALIVE rc0 idle, watermark red=false healthy; "
       "(f) S7 registers: loop pin=2 no-op, watchdog exists, claws byte-identical, attrition 4 CLEAN; "
       "(g) BigHouse T-3 honest-defer; O-2110 CDN leg still named-blocked (TJ-MCP window)")
NEXT = ("r998: 1) bm-a pickup verification watch (reply to MSG-2356) 2) IndexTTS lane harvest watch (interactive "
        "window: boot f2 RESULT + voicegen trio outdir media/drama-tts-out/) 3) BigHouse T-3 4) S0 rebase heal: "
        "local d452d780 divergence content already landed via r997 push, round_reports.md conflict resolved origin-side "
        "5) O-2110 CDN leg if TJ-MCP window appears")
VERDICT = ("GREEN: E1 leg-5 drama pilot 5-file re-queue DELIVERED with byte evidence (+18.6MB tx, rc=0x5) per bm-a "
           "MSG-2232; O-2207 acked (bm-a executed, zero bm-b leg); IndexTTS/voicegen lane yielded to live interactive "
           "window (chain alive, bigvgan in flight); dead r995/r996 estate absorbed (S6 43-leg rc0 + d19 advance landed); "
           "smoke 49/49; S7 registers green; watermark red=false healthy")
CURR_TASK = "r997: delivery (taildrop re-queue + MSG-2356) + estate-absorb closeout"

# ---- heartbeat ----
hp = ROOT + r"\fleet\machines\bm-b.json"
with open(hp, encoding="utf-8") as f:
    hb = json.load(f)
hb["last_seen"] = now_iso
hb["ts"] = now_iso
hb["clock_read"] = now_iso
hb["heartbeat_epoch_utc"] = epoch
hb["task"] = CURR_TASK
hb["current_task"] = "r998: pickup verify watch + IndexTTS lane harvest watch + BigHouse T-3 + S0 rebase heal"
hb["did"] = ("r997: 当前活=E1 leg-5 剧试片 5 件重投已交付（字节级证据 +18.6MB·rc=0x5·MSG-2356 已发）；最近实物="
             "fleet/inbox/MSG-20261017-2356-bmb-dramaredrop.md（23:56）+ d19 水位 orders->0b991d78 落链；"
             "下个里程碑=bm-a 取件验证回执（≤10-18 10:00）→ CEO 看片通道解锁；孤儿面=10/0；watermark=red=false healthy")
hb["last_action"] = "r997: drama 5-file re-queue delivered (tx +18.6MB verified) + dead-r995/r996 estate absorbed + O-2207 acked"
hb["last_action_at"] = now_iso
hb["latest_artifact"] = "fleet/inbox/MSG-20261017-2356-bmb-dramaredrop.md + taildrop 5-file transfer (tx 143537244->162175212)"
hb["verdict"] = VERDICT
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["round_no"] = 997
hb["round"] = 997
hb["next"] = NEXT
if "O-20261017-2207-bm-c.md" not in hb.get("orders_ack", []):
    hb["orders_ack"].append("O-20261017-2207-bm-c.md")
hb["note"] = ("r997: IndexTTS/voicegen/kohya GPU lane owned by live interactive bm-b window per "
              "INDEXTTS-LANE-CLAIM-bmb.txt - this headless round yielded, zero interference; taildrop delivery "
              "verified byte-level (tx counter law); dead r995/r996 estates absorbed")
with open(hp, "w", encoding="utf-8", newline="") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
print("heartbeat OK epoch int verified:", chk["heartbeat_epoch_utc"])

# ---- state.json ----
sp = ROOT + r"\state.json"
with open(sp, encoding="utf-8") as f:
    st = json.load(f)
st.update({
    "round_no": 997, "round": 997, "round_no_label": "r997",
    "clock_read": now_iso, "last_seen": now_iso, "ts": now_iso, "updated": now_iso, "updated_at": now_iso,
    "last_round_at": now_iso, "last_round_ts": now_iso, "last_action_at": now_iso,
    "last_orders_at": now_iso, "last_decisions_at": now_iso,
    "current": CURR_TASK, "task": "r997: closeout (state/heartbeat/round-report/push)",
    "current_task": hb["current_task"],
    "did": DID, "next": NEXT, "verdict": VERDICT, "now_active": "r997 closing (surgery push on origin tip e71efb9dae)",
    "last_action": hb["last_action"],
    "orphan_face": 10, "orphan_faces": 10,
    "orphan_face_note": "r997 round-start probe (23:43): 10 py faces / 0 orphans",
    "last_artifact": hb["latest_artifact"],
    "latest_artifact": hb["latest_artifact"],
    "last_orders_read_at": now_iso, "last_decisions_read_at": now_iso,
    "orders_delta_pending": False, "decisions_delta_pending": False,
    "d19_probe_due": False,
    "d19_probe_due_note": "r997: local watermark advanced (orders 0b991d78) ahead of origin (e0dcbd80); landed via r997 push",
    "last_orders_sha": "0b991d78bf4505ca6a9b27908f160e9ae9e51adf1ed96c5eec511ceccb42cc22",
    "last_orders_sha_note": "r997: advanced by dead-session 23:02:33 (scripts/d19_watermark.py update --advance), verified + landed this push",
    "r996_absorb_note": "r996 emergency commit d452d780 (round_reports.md +1 row) unpushed; content included in r997 disk face; local divergence heals next S0 rebase (r988 replay pattern)",
})
st["sat_engine"] = {"status": "alive (r997 S6 status rc=0, last_verdict idle)", "checked_at": now_iso}
st["sync"]["r997_main_push"] = {
    "status": "PENDING (this commit)",
    "pushed_sha": "pending",
    "consumed_at": "pending r998",
    "behind_origin_main": 0,
    "note": ("r997 payload = own faces (state/heartbeat/round report + MSG-2356 + MSG-2203/2216 processed moves + "
             "own machine-suffixed regen faces + d19_watermark.json advance + watermark_red fresh probe + "
             "dead-session work files r995/r996 estate); surgery on fresh origin tip e71efb9dae; docs + shared "
             "non-suffixed faces excluded (anti-regression r982 policy, origin newer from bm-a r1043)")
}
with open(sp, "w", encoding="utf-8", newline="") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
print("state OK round=997")

# ---- round report append ----
rp = ROOT + r"\logs\iteration-loop\round_reports.md"
with open(rp, encoding="utf-8") as f:
    content = f.read()
row = ("{ts} | r997 | WM:red=false healthy（23:53 probe·周末板空合法 idle·真交付在飞 --worked 清零）| "
       "did:{did} | evidence:tx 计数 143537244→162175212=+18,637,968 字节级过线（10-10 律）+rc=0x5/"
       "MSG-20261017-2356-bmb-dramaredrop.md/smoke 49/49/satengine ALIVE rc0 idle/attrition 4 CLEAN/"
       "S6 吸收面=results/_r996bmb_s6_log.txt 43 腿 rc0（死席 r996 23:05 全链·吸收非重跑）/"
       "d19 advance orders→0b991d78 落链/O-2207 ack（bm-a 执行回执在案零 bm-b 腿）/"
       "IndexTTS 车道让路活窗（INDEXTTS-LANE-CLAIM·curl 15108 bigvgan 下载中·boot chain PID 18300 心跳在·kohya+CSA 队列 23:42:46 已起·零干涉）"
       "| 产品计分:2（字节级交付+台账+水位三实物）| 本地未达 origin commit 数=1（d452d780 r996 紧急行·内容随本次推送落链·分叉下轮 S0 rebase 自愈 r988 范式）"
       "| next:{nxt}").format(ts=now_iso, did=DID, nxt=NEXT)
content = content.rstrip("\n") + "\n" + row + "\n"
with open(rp, "w", encoding="utf-8", newline="") as f:
    f.write(content)
print("round report OK row appended")
