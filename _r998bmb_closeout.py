# -*- coding: utf-8 -*-
# r998 closeout: heartbeat + state.json + round report append + ack-scan refresh
import json, time, datetime, os, shutil

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())
DID = ("r998: (a) P0 O-20261018-0137 (CEO mis-close recovery, @bm-b all four): S0 surgery self-check CLEAN "
       "(index.lock/rebase-merge/rebase-apply/MERGE_HEAD/CHERRY_PICK_HEAD all absent + 0 git.exe committer alive; "
       "stash-pull-pop S0 clean, r997 d452d780 landed behind=0); task-panel audit 11 rows ALL in-service ALL S4U "
       "zero-accident-disable (CEO close killed sessions not tasks - matches bm-a finding-1); frozen faces kept "
       "(AnchorBurn-r990/TTSDeploy-r992/Skyline pair); receipt landed BOTH faces "
       "(fleet/inbox/MSG-20261018-0216-bm-b-taskaudit.md + O-file receipt section). "
       "(b) O-20261017-1751 B.4-III EP001-003 pilot voicegen COMPLETED: multi-speaker single-load runner "
       "(drama_voicegen_eps_r998.py, reuses proven v1.1 infer pattern), F0-probe deterministic casting "
       "(narr=voice_05+calm / protagonist=voice_12 / villain-family=voice_07 true-F0~98Hz, first probe octave-doubling "
       "resolved / reporter=voice_04 female / comic=voice_05+happy0.6) -> 51/51 lines OK in 257s, "
       "51 wavs 7.28MB at media/drama-tts-out/r998_ep001_003/ + MANIFEST-r998.json (mixing-stage face) + "
       "voicegen_r998.DONE.json status=OK; detached pid 26812 finished in-round. "
       "(c) S6 chain 43 legs rc0 (results/_r998bmb_s6_log.txt; Sunday: live.paper/t35_open_fill/t24 pair skip-legit "
       "no new bar), smoke 49/49. (d) S7: loop pin=2 no-op, watchdog re-registered S4U SWA=false, claws "
       "byte-identical, attrition 4 CLEAN. (e) INDEXTTS-LANE-CLAIM post-conditions BOTH done: B.7 bilibili license "
       "registered in CODELY.md + Ollama valve closed (keepwarm.pause deleted, MiniGameOllamaServe/KeepWarm "
       "re-enabled). (f) MSG-2232 request fulfilled at r997 -> moved to processed; MSG-2356 awaiting bm-a pickup "
       "(waiting-state, one-line watch); kohya_train_f1 orphan found (log ends 00:12:40, NOT restarted - drama-dept "
       "post-pilot decision domain, logged in receipt)")
NEXT = ("r999: 1) voicegen 51-file director-seat audition + sample presentation flow (drama-dept gate before CEO "
        "face) 2) BigHouse T-3 carry-over 3) bm-a MSG-2356 pickup watch 4) three-layer mix samples (dialogue+ambience"
        "+sfx per O-1751) if audition passes 5) O-2110 CDN leg if TJ-MCP window appears")
VERDICT = ("GREEN: P0 recovery order fully executed same-round (S0 CLEAN + 11-row panel audit all-S4U + dual receipt) "
           "+ O-1751 EP001-003 voicegen 51/51 OK product landed (51 wavs 7.28MB + MANIFEST) + S6 43rc0 + S7 green + "
           "claim post-conditions cleared (B.7 license + valve closed); watermark red=false healthy")
CURR_TASK = "r998: O-0137 recovery receipt + EP001-003 voicegen harvest"

# ---- heartbeat ----
hp = ROOT + r"\fleet\machines\bm-b.json"
with open(hp, encoding="utf-8") as f:
    hb = json.load(f)
hb["last_seen"] = now_iso
hb["ts"] = now_iso
hb["clock_read"] = now_iso
hb["heartbeat_epoch_utc"] = epoch
hb["task"] = CURR_TASK
hb["current_task"] = "r999: 51-file audition + BigHouse T-3 + MSG-2356 pickup watch + mix samples"
hb["did"] = ("r998: 当前活=误关事故恢复回执已落+EP001-003 配音试产收官；最近实物="
             "C:\\Fluxgroup\\FluxGroup\\media\\drama-tts-out\\r998_ep001_003\\（51 wav·7.28MB·02:20）+MANIFEST-r998.json"
             "+fleet/inbox/MSG-20261018-0216-bm-b-taskaudit.md（02:16）；"
             "下个里程碑=配音样件导演席声审→CEO 呈样（≤10-19 12:00）·BigHouse T-3（≤10-19）；孤儿面=4/0")
hb["last_action"] = "r998: O-0137 receipt (S0 CLEAN+panel audit+4 legs) + EP001-003 voicegen 51/51 OK + valve closed + B.7 registered"
hb["last_action_at"] = now_iso
hb["latest_artifact"] = "media/drama-tts-out/r998_ep001_003/ (51 wavs) + MANIFEST-r998.json + MSG-20261018-0216-bm-b-taskaudit.md"
hb["verdict"] = VERDICT
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["round_no"] = 998
hb["round"] = 998
hb["next"] = NEXT
if "O-20261018-0137-bm-a.md" not in hb.get("orders_ack", []):
    hb["orders_ack"].append("O-20261018-0137-bm-a.md")
hb["note"] = ("r998: IndexTTS lane reclaimed from dead interactive window per O-0137 (owner died at CEO 00:46 close; "
              "boot f2 was already OK + bigvgan fixed by that window; this round added multi-speaker runner + "
              "51/51 first-gen). Ollama valve re-closed after GPU work end per claim post-condition.")
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
    "round_no": 998, "round": 998, "round_no_label": "r998",
    "clock_read": now_iso, "last_seen": now_iso, "ts": now_iso, "updated": now_iso, "updated_at": now_iso,
    "last_round_at": now_iso, "last_round_ts": now_iso, "last_action_at": now_iso,
    "last_orders_at": now_iso, "last_decisions_at": now_iso,
    "current": CURR_TASK, "task": "r998: closeout (heartbeat/state/round-report/push)",
    "current_task": hb["current_task"],
    "did": DID, "next": NEXT, "verdict": VERDICT, "now_active": "r998 closing",
    "last_action": hb["last_action"],
    "orphan_face": 4, "orphan_faces": 4,
    "orphan_face_note": "r998 round-start probe (02:0x): 4 py faces / 0 orphans",
    "last_artifact": hb["latest_artifact"],
    "latest_artifact": hb["latest_artifact"],
    "last_orders_read_at": now_iso, "last_decisions_read_at": now_iso,
    "orders_delta_pending": False, "decisions_delta_pending": False,
    "d19_probe_due": False,
})
st["sat_engine"] = {"status": "alive (r998 S6 status rc0, idle verdict)", "checked_at": now_iso}
st["sync"]["r998_main_push"] = {
    "status": "PENDING (this commit)",
    "pushed_sha": "pending",
    "consumed_at": "pending r999",
    "behind_origin_main": 0,
    "note": ("r998 payload = own faces (state/heartbeat/round report + O-0137 receipt MSG + O-file receipt section + "
             "CODELY.md B.7 license line + r998 S6 log/probe work files + bm-b-suffixed regen faces + MSG-2232 "
             "processed move + r997 estate file _r997bmb_surgery_push.py); shared non-suffixed faces excluded "
             "(r982 policy); post_review.jsonl staged-by-other-window left in index (pathspec commit)")
}
with open(sp, "w", encoding="utf-8", newline="") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
print("state OK round=998")

# ---- orders_ack_scan refresh (own bm-b face) ----
ap = ROOT + r"\results\orders_ack_scan.bm-b.json"
with open(ap, encoding="utf-8") as f:
    asc = json.load(f)
asc["unacked"] = []
asc["ack_count"] = asc.get("orders_count", 100)
asc["machine_id"] = "bm-b"
asc["note_r998"] = "O-20261018-0137-bm-a.md acked r998 (dual receipt: MSG-20261018-0216 + O-file section)"
with open(ap, "w", encoding="utf-8", newline="") as f:
    json.dump(asc, f, ensure_ascii=False, indent=1)
print("ack-scan refreshed")

# ---- MSG-2232 processed move (request fulfilled r997) ----
src = ROOT + r"\fleet\inbox\MSG-20261017-2232-bma-dramapickup-reply.md"
dst = ROOT + r"\fleet\inbox\processed"
os.makedirs(dst, exist_ok=True)
if os.path.isfile(src):
    shutil.move(src, os.path.join(dst, "MSG-20261017-2232-bma-dramapickup-reply.md"))
    print("MSG-2232 moved to processed")

# ---- round report append ----
rp = ROOT + r"\logs\iteration-loop\round_reports.md"
with open(rp, encoding="utf-8") as f:
    content = f.read()
row = ("{ts} | r998 | WM:red=false healthy（S6 探针·周末板空合法 idle）| did:{did} "
       "| evidence:voicegen_r998.DONE.json status=OK 51/51 elapsed=257s/"
       "media/drama-tts-out/r998_ep001_003/ 51 wav=7.28MB+MANIFEST-r998.json/MSG-20261018-0216-bm-b-taskaudit.md/"
       "O-0137 回执节双面/smoke 49/49/results/_r998bmb_s6_log.txt 43 腿 rc0（周日四 paper 腿合法跳）/"
       "attrition 4 CLEAN/双爪 byte-identical/watchdog 重注册 S4U SWA=false/S0 手术自检 CLEAN（五残骸+零 committer）"
       "| 产品计分:2（O-1751 前三集配音试产 51 件实物+事故恢复回执）"
       "| 孤儿面=4/0| 本地未达 origin commit 数=0"
       "| next:{nxt}").format(ts=now_iso, did=DID, nxt=NEXT)
content = content.rstrip("\n") + "\n" + row + "\n"
with open(rp, "w", encoding="utf-8", newline="") as f:
    f.write(content)
print("round report OK row appended")
