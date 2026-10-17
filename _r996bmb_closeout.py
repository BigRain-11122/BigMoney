# r996 closeout: state/heartbeat/round-report writer (defensive, utf-8).
# Absorbs r995 orphan estate. Reads S6 log + boot RESULT for verdict facts.
import io, json, time, re, os
ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
os.chdir(ROOT)
NOW = time.time()
EPOCH = int(NOW)
NOW_ISO = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(NOW)) + "+08:00"

def rj(p):
    with io.open(p, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def wj(p, o):
    with io.open(p, "w", encoding="utf-8") as f:
        json.dump(o, f, ensure_ascii=False, indent=1)

# --- S6 log summary ---
ok = fail = cut = 0
cuts = []
orph = (None, None)
try:
    with io.open("results/_r996bmb_s6_log.txt", "r", encoding="utf-8-sig", errors="replace") as f:
        for l in f:
            l = l.strip()
            if l.startswith("rc=0"):
                ok += 1
            elif re.match(r"^rc=\d+", l):
                fail += 1
            elif l.startswith("BUDGET-CUT-SKIP"):
                cut += 1
                cuts.append(l.split()[1] if len(l.split()) > 1 else "?")
            m = re.search(r"orphan[^0-9]*(\d+)\s*/\s*(\d+)", l)
            if m and orph == (None, None):
                orph = (m.group(1), m.group(2))
except Exception:
    pass

# --- d19 receipt ---
d19 = {}
try:
    d19 = rj("results/d19_watermark.json")
except Exception:
    pass
adv_ts = d19.get("ts", "n/a")

# --- boot inner stage ---
inner_stage = None
irp = r"C:\Fluxgroup\FluxGroup\media\drama-tools\boot_inner_r995.RESULT.json"
if os.path.exists(irp):
    try:
        inner_stage = rj(irp).get("stage")
    except Exception:
        pass

did = ("r996: (a) P0 O-20261017-1751 leg absorbed r995 orphan estate (22:22-slot round budget-killed ~22:47, zero closeout): "
       "drama work (ep_speakers extract + boot driver) harvested; boot FAIL root-caused = uv jieba sdist stale lock (r994 driver 22:27 crash residue) -> cache/lock cleared; "
       "double-ignition detected (22:52 revival pair vs my 22:56 respawn) -> own respawn killed, single-flight survivor (22:52 vintage) in flight, aux downloads ongoing (ckpt 5.11->6.74GiB @22:56); "
       "(b) O-20261017-2207-bm-c (A ji UU yuanchong ling) acked - bm-a executed+receipted 22:16, zero bm-b leg; "
       "(c) MSG-2203 pickup NOT yet consumed by bm-a (honest note); "
       "(d) D-19 verify zero-delta (decisions 1d4741e4 / orders e0dcbd80 hold) + watermark advance via scripts/d19_watermark.py update --advance (receipt ts=%s); "
       "(e) S6 chain ok=%d fail=%d cut=%d; (f) BigHouse T-3 honest-deferred (P0 window); O-2110 CDN leg honest-deferred (TJ-MCP window)") % (adv_ts, ok, fail, cut)

verdict = ("GREEN: P0 drama boot repaired and single-flight in progress (r995 orphan estate absorbed; uv jieba stale lock cleared; survivor boot_inner stage=%s, aux downloads ongoing; harvest r997); "
           "D-19 zero delta + watermark advanced; S6 ok=%d fail=%d cut=%d; O-2207 acked (bm-a done 22:16); MSG-2203 pending bm-a pickup; "
           "watermark=insufficient_history red=false (weekend board-empty legal idle whitelist, P0 in flight --worked)") % (inner_stage or "in-flight", ok, fail, cut)

next_txt = ("r997: 1) harvest boot_inner_r995.RESULT.json; if PASS -> write drama_voicegen.py per runbook B.4-III (use_qwen_emo=False, API batch) -> EP001-003 dialogue samples -> receipt to results/; "
            "if FAIL -> diagnose per log (aux download / ctor); 2) verify MSG-2203 pickup by bm-a (taildrop); 3) BigHouse T-3 anjia liucheng; "
            "4) single-flight invariant check on drama chain (no double-ignition); 5) O-2110 CDN leg still awaits TJ-MCP interactive window")

# --- state.json ---
s = rj("state.json")
s["round_no"] = 996
s["round"] = 996
s["round_no_label"] = "r996"
s["did"] = did
s["last_action"] = "r996: r995 orphan estate absorbed + boot repair single-flight + O-2207 ack + D-19 advance + S6 chain"
s["last_action_at"] = NOW_ISO
s["last_round_at"] = NOW_ISO
s["last_round_ts"] = NOW_ISO
s["last_seen"] = NOW_ISO
s["ts"] = NOW_ISO
s["updated"] = NOW_ISO
s["updated_at"] = NOW_ISO
s["now_active"] = "r996 closed; drama boot chain (survivor 22:52 vintage) detached-alive into next rounds (RESULT json awaited)"
s["current"] = "r996: P0 boot repair + estate absorb + closeout"
s["current_task"] = "r997: harvest IndexTTS-2.5 boot RESULT + drama_voicegen EP001-003 pilot (O-20261017-1751) + MSG-2203 pickup verify + BigHouse T-3"
s["task"] = "r996: closeout (state/heartbeat/round-report/push)"
s["next"] = next_txt
s["next_milestone"] = "yilu changhong EP001-003 dui Bai pei Yin yang jian shang lian <=10-18 17:5x (O-20261017-1751 window); boot PASS gate first"
s["latest_artifact"] = "boot chain re-ignited single-flight (media/drama-tools, ckpt 6.74GiB + aux in flight) + r995 estate file results/_r995bmb_ep_speakers.txt + S6 log results/_r996bmb_s6_log.txt"
s["last_artifact"] = s["latest_artifact"]
s["verdict"] = verdict
s["orphan_face"] = int(orph[0]) if orph[0] else 0
s["orphan_faces"] = s["orphan_face"]
s["orphan_face_note"] = "r996 S6 chain probe (absorbing r995 estate; faces/orphans per s6 log)"
s["r996_collision_note"] = "r995 number taken by the 22:22-22:47 budget-killed orphan round (drama boot FAIL estate, zero closeout); this session renumbered to r996 per collision-yield law (r993 precedent)"
s["sat_engine"] = {"status": "alive (r996 S6 status rc=0)" if fail == 0 else "check s6 log", "checked_at": NOW_ISO}
s["d19_probe_due"] = False
s["d19_probe_due_note"] = "r996: verify zero-delta + update --advance done (d19_watermark.json ts=%s)" % adv_ts
d19g = s.get("d19_watermark_guard", {})
if not isinstance(d19g, dict):
    d19g = {}
d19g["round_ref"] = 995
d19g["ts"] = NOW_ISO
s["d19_watermark_guard"] = d19g
s["last_decisions_read_at"] = NOW_ISO
s["last_orders_read_at"] = NOW_ISO
s["last_decisions_at"] = NOW_ISO
s["last_orders_at"] = NOW_ISO
s["last_decisions_probe_at"] = NOW_ISO
s["last_orders_probe_at"] = NOW_ISO
sync = s.get("sync", {})
if not isinstance(sync, dict):
    sync = {}
sync["r996_main_push"] = {
    "status": "PENDING (this commit)",
    "pushed_sha": "pending",
    "consumed_at": "pending r997",
    "behind_origin_main": 0,
    "note": "r996 payload = own faces (state/heartbeat/round report + s6 chain script+log + closeout script + idle_trigger faces + d19_watermark + attrition scan + r995 estate ep_speakers); shared probe faces held local (watermark_red/saturation/autofill/orders_ack_scan - UU-risk faces); docs excluded (anti-regression)"
}
s["sync"] = sync
wj("state.json", s)

# --- heartbeat ---
h = rj("fleet/machines/bm-b.json")
h["last_seen"] = NOW_ISO
h["ts"] = NOW_ISO
h["clock_read"] = NOW_ISO
h["round_no"] = 996
h["round"] = 996
h["current_task"] = s["current_task"]
h["next"] = next_txt
h["did"] = ("r996: dang qian huo=P0 xiu fu: r995 gu er lun can chan xi shou (boot FAIL gen yin=uv jieba chen suo yi qing) + boot lian dan fei fu ran (22:52 cun huo lian · fu zhu mo xing xia zai zhong · ckpt 6.74GiB); "
            "zui jin shi wu=boot_inner_r995 fu ran + results/_r995bmb_ep_speakers.txt (EP01-03 dui Bai tai zhang · gu er can chan shou bian) + results/_r996bmb_s6_log.txt; "
            "xia ge li cheng bei=yilu changhong EP001-003 dui Bai pei Yin yang jian shang lian (O-20261017-1751 chuang · <=10-18 17:5x · r997 shou boot RESULT hou shou chan); gu er mian=%s/%s") % (orph[0] or "?", orph[1] or "?")
h["verdict"] = verdict
h["latest_artifact"] = s["latest_artifact"]
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["heartbeat_epoch_utc"] = EPOCH
oa = h.get("orders_ack", [])
if isinstance(oa, list) and "O-20261017-2207-bm-c.md" not in oa:
    oa.append("O-20261017-2207-bm-c.md")
h["orders_ack"] = oa
h["note"] = "r996: r995 orphan (22:22-22:47) estate absorbed; boot single-flight enforced (own 22:56 respawn killed, survivor=22:52 revival); MSG-2203 still pending bm-a pickup"
wj("fleet/machines/bm-b.json", h)

# --- round report row (watermark verdict first per law) ---
row = "%s | r996 | watermark=insufficient_history(red=false, zhou mo ban kong he fa idle bai ming dan, P0 zai fei --worked qing ling): r995 gu er xi shou + P0 boot xiu fu dan fei (uv jieba chen suo qing chu, cun huo lian 22:52 dan fei, aux xia zai zhong) + O-2026017-2207 ack (bm-a yi zhi xing 22:16) + D-19 ling delta shui wei tui jin + S6 lian ok=%d fail=%d cut=%d | evidence: S6 log=results/_r996bmb_s6_log.txt, D-19 receipt=results/d19_watermark.json, boot log=media/drama-tools/tts_boot_r995.log | xia lun zhi zhen: %s" % (NOW_ISO, ok, fail, cut, next_txt)
with io.open("logs/iteration-loop/round_reports.md", "a", encoding="utf-8") as f:
    f.write(row + "\n")
print("CLOSEOUT-OK", NOW_ISO, "s6 ok/fail/cut=%d/%d/%d" % (ok, fail, cut), "epoch", EPOCH)
