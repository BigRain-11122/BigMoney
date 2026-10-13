# r976 bm-a closeout: state + heartbeat + round report (fresh read-modify-write, single-writer per file)
import json, time, datetime

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())
verdict = ("green (seat chain queue-depth-2: W237 declared bm-c M12 freeze-unblocked + W238 declared bm-a "
           "seat 3e551d846; satengine ALIVE idle post-W236-finalize; smoke 49/49; S6 38-leg chain in-flight pid 130152)")
did = ("r976: S0 estate absorb r975 W236-finalize MSG + W237 seat processed move + daemon churn (eb669b3ab, pull --rebase 1) "
       "+ W238 SEAT PUBLISHED (bm-a 122nd owned 228th wave; A 538_404..540_403 staircase-98 / B 540_404..540_603 W141; "
       "probe ADMIT seed_admit_gate FREE x2 + vacancy four-check; commit 3e551d846; W239+ leg4 NEW seed face 541500/542000) "
       "+ smoke 49/49 + D-19/ORD dual FALSE + loop pin8 no-op + watchdog + attrition CLEAN")
artifact = "results/_w238bma_20261014_probe_receipt.json (W238 seat ADMIT, 07:4x)"
nxt = ("r977: S6 chain product absorb (pid 130152 products) + W237 freeze watch (bm-c M12 chain) + "
       "W238 freeze-prep waits-upstream W237 finalize + D-19/ORD watermark + S6 chain")

# --- state-bm-a.json ---
sp = ROOT + r"\state-bm-a.json"
with open(sp, encoding="utf-8") as f:
    st = json.load(f)
st["round_no"] = 976
st["round"] = 976
st["last_round"] = 976
st["current"] = "r976 closeout done"
st["now_active"] = nxt
st["current_task"] = nxt
st["task"] = nxt
st["did"] = did
st["last_action"] = "r976 W238 seat published + estate absorb closeout"
st["last_artifact"] = artifact
st["latest_artifact"] = artifact
st["recent_artifact"] = artifact
st["next"] = nxt
st["next_milestone"] = ("W237 freeze+finalize (bm-c M12 chain, unblocked post-W236-finalize) -> W238 freeze-prep "
                        "(bm-a, waits-upstream W237 finalize); O-1725 P0 matrix delivery 10-13/14; "
                        "month-boundary first exam 10-31 (T-143 assembly 10-29)")
st["verdict"] = verdict
st["verify"] = "green (W238 seat landed 3e551d846 + smoke 49/49 + watermark dual FALSE + attrition CLEAN)"
st["last_round_at"] = now_iso
st["last_round_closed"] = now_iso
st["last_round_ts"] = now_iso
st["last_run"] = now_iso
st["last_seen"] = now_iso
st["ts"] = now_iso
st["updated"] = now_iso
st["updated_at"] = now_iso
st["clock_read"] = now_iso
st["heartbeat_epoch_utc"] = epoch
st["heartbeat_epoch_utc_type_int"] = isinstance(epoch, int)
st["last_heartbeat_epoch_utc"] = st.get("heartbeat_epoch_utc", epoch)
st["idle_rounds"] = 0
st["agenda_starved"] = False
st["orphan_face"] = 1
st["orphan_faces"] = 1
st["last_orders_seen"] = ("r976 consume: D-19/ORD dual FALSE (dec 86187eff / ord 348eaf34 hold, probe _r686bmb_d19_check "
                          "rc0 07:3x; zero new group rows; fleet orders 84 O-files sweep → ack face unchanged, zero unacked)")
st["last_decisions_seen"] = "r976: DEC 86187eff content UNCHANGED (probe == watermark, zero re-consume)"
st["push_verified"] = {"ahead_behind": "0/0", "origin_tip": "3e551d846", "ts": now_iso,
                        "note": "r976: estate push 12757f518..eb669b3ab + seat push eb669b3ab..3e551d846 verified; 本地未达 origin commit 数=0"}
st["sync"] = st["push_verified"]
notes_add = (" r976: state round_no healed 966->976 per commit lineage (r967-r975 carried by prior sessions, "
             "r975 closeout 16dd2cda0; sequence honest = r976 this window).")
if "r976: state round_no healed" not in st.get("notes", ""):
    st["notes"] = (st.get("notes", "") + notes_add).strip()
with open(sp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# --- heartbeat fleet/machines/bm-a.json ---
hp = ROOT + r"\fleet\machines\bm-a.json"
with open(hp, encoding="utf-8") as f:
    hb = json.load(f)
hb["last_seen"] = now_iso
hb["ts"] = now_iso
hb["clock_read"] = now_iso
hb["heartbeat_epoch_utc"] = epoch
hb["current_task"] = nxt
hb["cpu_cores"] = 32
hb["verdict"] = "green"
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
with open(hp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# --- round report line ---
rp = ROOT + r"\round_reports-bm-a.md"
line = (now_iso + " | r976 | bm-a | dept:工程/研究（r975 遗产收口+W238 席位发布+三绿门）| WM-VERDICT: green (red=false lane=healthy; "
        "satengine ALIVE queue_depth=0 idle post-W236-finalize; seat chain queue-depth-2: W237 declared(bm-c M12 unblocked)+W238 declared(bm-a))"
        "| 孤儿面=1 (round-zero probe 只读报告, killed=[] 按律不动) | "
        "S0: estate absorb r975 W236-finalize MSG+W237 seat processed move+daemon churn (commit eb669b3ab) + pull --rebase 1 (bm-c r989 wait-state) + push 0/0 | "
        "S0.5: D-19/ORD dual FALSE (dec 86187eff/ord 348eaf34 hold·fleet 84 O-file sweep 零未回执) | S1: smoke 49/49 | "
        "S3: **W238 seat published=reserved** (bm-a 122nd owned, 228th wave; A 538_404..540_403 staircase-98 hops=1 / B 540_404..540_603 own-A-reserved W141 hops=1; "
        "pre-seat probe _w238bma_20261014_probe.py ADMIT·seed_admit_gate rc0 FREE x2·vacancy 四查绿; commit 3e551d846; "
        "W239+ leg4 NEW face: live seeds 541500/542000 refuse naive A→first-clean 542_501..544_500 hops=2 诚实入 receipt) | "
        "S6: 38-leg chain in-flight pid 130152 (launched 07:36:47·stdout 块缓冲=已知面·产物由下轮 S0 churn 吸收) | "
        "S7: loop pin=8 no-op + watchdog registered + attrition 4 files CLEAN + 双爪在位（本窗 2 笔干净 commit+push=实证）| "
        "验证: probe ADMIT receipt + seat push 3e551d846 + smoke 49/49 + watermark dual FALSE | "
        "本轮产品积分:2（W238 席位=能跑实物 probe+seat 上链·queue-depth 供给 depth-2）·记账预算:4（state/心跳/轮报告/S6 链件）| "
        "本地未达 origin commit 数=0（push+fetch+rev-list 自证）| [r976 bm-a]\n")
with open(rp, "a", encoding="utf-8", newline="\n") as f:
    f.write(line)

# self-verify epoch int
chk = json.load(open(sp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch not int"
chk2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk2["heartbeat_epoch_utc"], int), "hb epoch not int"
assert "T" in chk["clock_read"], "clock_read not T-separated"
print("CLOSEOUT OK round_no=", chk["round_no"], "epoch=", chk["heartbeat_epoch_utc"], "clock=", chk["clock_read"])
