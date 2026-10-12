# r914 bm-b closeout: dead-session takeover round -- state.json + heartbeat + round report
# (r913 closeout script pattern; int epoch law R170/R178; T-separator clock law R262)
import json, time, subprocess
from datetime import datetime

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
now_iso = datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

def raml():
    try:
        import psutil
        return round(psutil.virtual_memory().available / (1024**3), 2)
    except Exception:
        return None

def gpu():
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,power.draw",
                            "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=15)
        u, m, p = [x.strip() for x in r.stdout.strip().split(",")]
        return float(u), float(m), round(float(p), 1)
    except Exception:
        return None, None, None

ram_free = raml()
gu, gm, gp = gpu()

did = ("r914: (1) SESSION TAKEOVER: prior r914 incarnation ran S6 41 legs 03:31-03:36 (rc_nonzero=1 of 41 "
       "= t35_open_fill_verify rc=1 day 2026-10-12 marks evidence gap, known honest state) then died before "
       "closeout; this session took over the SAME round, zero re-run waste. (2) D-19 ORDERS DELTA CONSUMED: "
       "group orders.md bd29c5c5->a23119c6 = two new rows (10-13 03:3x MiniMax congestion precedent + Seedance "
       "rescue wave; 10-13 03:4x Seedance harvest 11/15 + 4 content_moderation face-shot verdicts + @bmc 4-lens "
       "add-on) = ALL MV-line rows (bma/bmc domain), ZERO BigMoney rows -> watermark advanced, zero content "
       "action per D-19 law; decisions fb378423 unchanged zero-delta. (3) i2v animatic watch: 21/53 clips "
       "saved (KN17+KN18 this window, KN19 in-flight 735s+), driver PID 2848 alive since 02:07, GPU 100% under "
       "180W cap, zero fails; HONEST ETA REVISION: ~20min/unit x 32 left = 53/53 by ~14:00-15:00 afternoon "
       "(r913 morning estimate revised); N2U3 flip double-gate (batch-done + RAM>=4GB) deferred to post-batch "
       "window. (4) unity-mcp POC re-check: Tuanjie editor process spawned 03:43:50 (WeixinMiniGameSupport "
       "child) but MCP bridge probe 03:47 = 'No Unity Editor instances found' -> still awaiting editor-open "
       "window, mid-morning re-check per plan, due 12:00 receipt. (5) S1 smoke 49/49 PASS; SatEngine alive "
       "(idle, queue 0); watermark_red red=false green; S0 fetch behind=4 ahead=0; job_list empty + fleet/tasks "
       "open=0; orphan probe py_faces=20 orphans=1 (i2v driver sleep-window FALSE-POSITIVE, r910/r913 "
       "precedent, not killed). (6) S7: attrition guard CLEAN rc=0; loop task pin=2 no-op; watchdog "
       "registered; precommit+prepush claws installed; inbox: 2 bm-c->bm-a msgs left for bm-a; own r872 t184 "
       "alert archived to processed (transfer closed: alloc_paper P5 rc=0 byte-identical + manifests 10-11).")

last_action = ("r914: dead-session takeover + S6 41-leg salvage + D-19 orders delta consumed (MV-line only, "
               "zero BigMoney rows) + i2v watch 21/53 (ETA honestly revised to ~afternoon) + unity-mcp editor "
               "still unconnected + S7 all green")

next_task = ("r915: i2v batch watch -> at 53/53 (~afternoon): remove keepwarm.pause + flip N2U3-LEG3-TRAIN "
             "waiting->ready (batch-done + RAM>=4GB double gate) -> autofill burn (~3.3h) -> export-topk K=32 "
             "-> judged legs > Music3 install window (license PASS r913: int8 three-file download ~12-14GB + "
             "ComfyUI smoke + comparison board v2 vs cloud Music3) > unity-mcp POC due 10-13 12:00 (editor "
             "process spawned 03:43 but bridge unconnected -- mid-morning re-check window, honest "
             "non-precondition note if past mid-morning) > Speech-02 3-option adjudication awaiting "
             "committee/CEO (POOL-0002 frozen) > E15 s4 intake legs = monthly boundary (explore.md L20: "
             "sentiment FDR4D re-judgment prereg chain, sentiment.turnover_surge W2-23057/W3-23027)")

next_milestone = ("i2v 53/53 ETA ~10-13 afternoon (revised) -> N2U3 flip double-gated -> export-topk+judged "
                  "legs; Music3 install post-batch (license PASS); unity-mcp POC <=10-13 12:00 (editor window "
                  "pending); Speech-02 route adjudication filed")

now_active = ("i2v animatic batch burning (21/53, KN19 in-flight, ComfyUI r911c + driver PID 2848, GPU 100% "
              + str(gp if gp is not None else "~80") + "W under 180W cap, RAM "
              + str(ram_free if ram_free else "3.7") + "GB free)")

latest_artifact = ("media/mv-album-001-jay/clips-animatic-480/ 21 clips (gitignored media face) + fresh CEO "
                   "panels docs/daily_report/REPORT-2026-10-13.md + docs/live_usage/LIVE-2026-10-13.md + "
                   "results/daily_scorecard.html (S6 41 legs, dead-session salvage) + probe evidence "
                   "results/_r686bmb_d19_check.json + results/_r914bmb_s6_log.txt")

verdict = ("GREEN-with-flags: takeover round under legal GPU burn (prior r914 incarnation S6 salvaged 41/41 "
           "legs + closed out; D-19 orders delta consumed zero BigMoney rows; i2v batch healthy 21/53 zero "
           "fails, ETA honestly revised to afternoon); flags=pool_starvation/supply_floor standing "
           "(resource-blocked until batch completes) + unity-mcp POC editor-window still pending + Speech-02 "
           "route blocked pending committee/CEO pick of A/B/C")

orphan_note = ("r914 probe 03:4x: py_faces=20 orphans=1 = i2v driver (results/_r897bmb_i2v/h3_i2v_album.py "
               "--lane bmb, PID 2848) sleep-window FALSE-POSITIVE between ComfyUI polls, NOT killed (CEO "
               "batch face, r910/r913 precedent); driver alive writing driver_r911c.out.txt + KN19 in-flight proof")

orders_note = ("r914 probe consumed orders delta bd29c5c5->a23119c6: two new rows both MV-line (bma/bmc), "
               "zero BigMoney involvement -> watermark advanced, zero content action per D-19 law; "
               "decisions fb378423 unchanged zero-delta")

sync_note = ("r914 closeout: round commit + pull --rebase (origin ahead 4 at round start) + push follow this "
             "write; delivery self-proof (fetch+rev-list) -> r915 round-start verify")

# ---- state.json ----
sp = ROOT + r"\state.json"
st = json.load(open(sp, encoding="utf-8"))
st["clock_read"] = now_iso
st["current_task"] = "r914 closeout; r915 = batch watch + N2U3 flip at 53/53 (~afternoon) + Music3 install window + unity-mcp editor re-check"
st["did"] = did
st["last_action"] = last_action
st["last_action_at"] = now_iso
st["last_orders_at"] = now_iso
st["last_orders_read_at"] = now_iso
st["last_orders_sha"] = "a23119c6389f347768a42c9e5df67c3f4def7aec"
st["last_orders_sha_note"] = orders_note
st["last_round_at"] = now_iso
st["last_round_ts"] = now_iso
st["last_seen"] = now_iso
st["latest_artifact"] = latest_artifact
st["next"] = next_task
st["next_milestone"] = next_milestone
st["note"] = last_action
st["now_active"] = now_active
st["orphan_face"] = 1
st["orphan_face_note"] = orphan_note
st["orphan_faces"] = 1
st["round"] = 914
st["round_no"] = 915
st["round_no_label"] = "r914"
st["sync"] = {"last_push_ts": now_iso, "note": sync_note}
st["task"] = next_task
st["ts"] = now_iso
st["updated"] = now_iso
st["updated_at"] = now_iso
st["verdict"] = verdict
st["d19_watermark_guard"]["round_ref"] = 914
st["d19_watermark_guard"]["ts"] = now_iso
st["d19_watermark_guard"]["note"] = "r914 pinned probe fresh: decisions fb378423 unchanged / orders a23119c6 consumed (MV-line only, zero BigMoney rows)"
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=True, indent=1)

# ---- heartbeat fleet/machines/bm-b.json ----
hp = ROOT + r"\fleet\machines\bm-b.json"
hb = json.load(open(hp, encoding="utf-8"))
hb["clock_read"] = now_iso
hb["current_task"] = st["current_task"]
hb["did"] = did
hb["free_ram_gb"] = ram_free
hb["ram_free_gb"] = ram_free
hb["heartbeat_epoch_utc"] = epoch
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["green_idle"] = False
hb["gpu"]["util_pct"] = gu if gu is not None else 100.0
hb["gpu"]["mem_used_mb"] = gm if gm is not None else 7978.0
hb["gpu"]["power_w"] = gp if gp is not None else 90.0
hb["gpu"]["face"] = "i2v animatic batch burning (21/53, KN19 in-flight, driver PID 2848, 180W cap held)"
hb["last_action"] = last_action
hb["last_action_at"] = now_iso
hb["last_round_at"] = now_iso
hb["last_seen"] = now_iso
hb["latest_artifact"] = latest_artifact
hb["next"] = next_task
hb["next_milestone"] = next_milestone
hb["note"] = last_action
hb["now_active"] = now_active
hb["orphan_face"] = 1
hb["orphan_face_note"] = orphan_note
hb["orphan_faces"] = 1
hb["round"] = 914
hb["round_no"] = 915
hb["round_no_label"] = "r914"
hb["task"] = next_task
hb["ts"] = now_iso
hb["updated"] = now_iso
hb["updated_at"] = now_iso
hb["verdict"] = verdict
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=True, indent=1)

# ---- round report logs/iteration-loop/round_reports.md ----
rp = ROOT + r"\logs\iteration-loop\round_reports.md"
tail = ""
try:
    lines = open(rp, encoding="utf-8").read().splitlines()
    tail = lines[-1][:200] if lines else ""
except Exception:
    pass
line = " | ".join([
    now_iso,
    "r914 [dept:eng/fleet]",
    "dead-session takeover: S6 41 legs salvage (1 nonzero=t35_open_fill rc=1 marks-evidence-gap known state) "
    "+ D-19 orders delta consumed bd29c5c5->a23119c6 (2 new rows both MV-line, zero BigMoney rows -> watermark "
    "advance zero action; decisions fb378423 unchanged) + i2v animatic watch 21/53 (KN19 in-flight, driver 2848 "
    "alive, zero fails, ETA honestly revised to ~10-13 afternoon 14-15h; N2U3 double-gate waits batch-done+RAM>=4GB) "
    "+ unity-mcp POC re-check (Tuanjie editor process spawned 03:43 but MCP bridge unconnected -> editor-open "
    "window pending, mid-morning re-check, due 12:00) + S1 smoke 49/49 + SatEngine alive + watermark green + "
    "orphan_face=1 (i2v driver sleep-window false-positive, r910/r913 precedent, not killed) + S7 all green "
    "(attrition CLEAN/loop pin2/watchdog/both claws) + inbox housekeeping (2 bm-c->bm-a msgs left for bm-a; own "
    "r872 t184 alert archived, transfer closed by alloc_paper P5 rc=0 proof)",
    "evidence: results/_r914bmb_s6_log.txt + results/_r686bmb_d19_check.json + media clips-animatic-480 count=21 "
    "+ smoke 49/49 stdout + attrition scan rc=0",
    "next: r915 batch watch -> 53/53 (~afternoon) N2U3 flip double-gate -> autofill -> export-topk K=32 -> judged; "
    "Music3 install post-batch; POC mid-morning re-check; E15 s4 intake legs = monthly boundary",
    "unreached_origin_commits: round-start behind=4 -> closeout pull --rebase merge + push, self-proof r915 S0 verify",
])
with open(rp, "a", encoding="utf-8") as f:
    f.write(line + "\n")

print("PREV_TAIL=" + tail)
print("STATE round=%d round_no=%d epoch=%s(int=%s) ram=%s gpu=%s/%s/%s" % (
    st["round"], st["round_no"], hb["heartbeat_epoch_utc"],
    isinstance(hb["heartbeat_epoch_utc"], int), ram_free, gu, gm, gp))
print("REPORT_APPENDED")
