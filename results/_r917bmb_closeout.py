# r917 bm-b closeout: state 917->918 + heartbeat + round report line + registry self-checks
import json, time, subprocess, re
from datetime import datetime, timezone, timedelta

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
CST = timezone(timedelta(hours=8))
now = datetime.now(CST)
iso = now.isoformat(timespec="seconds")
epoch = int(time.time())

# ---------- state.json ----------
sp = ROOT + r"\state.json"
st = json.load(open(sp, encoding="utf-8"))
st["round"] = 917
st["round_no"] = 918
st["round_no_label"] = "r917"
st["clock_read"] = iso
st["ts"] = iso
st["updated"] = iso
st["updated_at"] = iso
st["last_seen"] = iso
st["last_round_at"] = iso
st["last_round_ts"] = iso
st["last_action"] = "r917: S0 fork integration (absorb bm-c x2 + replay own r916 closeout, 6 UU resolved per resolver laws) -> push f63639bf4 0/0; smoke 49/49; unity bridge probe#3 unconnected"
st["last_action_at"] = iso
st["current_task"] = "r918: unity bridge diagnosis (plugin/port, probe#4 next editor-open window) + PSU-swap watch (i2v 27/53 160W-clause deferred) + N2U3 chain at batch-done (flip double-gate, RAM leg OK) + S6 full chain at 10-14 15:30 data window"
st["task"] = st["current_task"]
st["next"] = st["current_task"]
st["did"] = ("r917: (1) S0 FORK INTEGRATION = round's main deliverable: round-start behind=2 (bm-c 6edff35ff/b3d66545c) + own r916 closeout unpushed (c7c8d8746, push had failed silently); "
             "absorbed daemon faces pre-rebase (e02578ec5), replayed both commits onto b3d66545c: closeout -> 4437368d4 (2 UU probe faces, ts-newer-wins mine 23:04), absorb -> f63639bf4 "
             "(4 UU: machine-health max-date mine 23:11, satengine face/state daemon live-wins, history_bm-b.jsonl line-union 120+13=133 zero loss); r855 daemon-churn-blocked continue 3x, each cured by same-call add+amend/continue; "
             "auto-merged state.json verified machine_id=bm-b round_no intact; round_reports union verified (own r916 line at tail). Push f63639bf4, delivery self-proof 0/0. "
             "(2) S1 smoke 49/49. (3) S3: SatEngine alive (hb 11s, idle, queue 0), watermark GREEN (red=false, next_pick=claimed moneyflow IC source-blocked), pool_dualrun streak 51 ZERO-DRIFT, "
             "compute_audit flags pool_starvation+supply_floor = N2U3 double-gate known-blocked honest carry (batch 27/53 PSU-deferred); py_watermark insufficient_history (astock_daily refresh lane still in-flight = legal local_batch). "
             "(4) unity-mcp bridge probe #3: STILL unconnected (No Unity Editor instances) = 3rd failure, bridge-level diagnosis queued (plugin presence/port scan, next editor-open window). "
             "(5) S6 quick legs: update_daily no-op OK, daily_report REPORT-2026-10-13 regen faces=5, ceo_live LIVE-2026-10-13 (ORANGE cap50, heat COOL, intraday 15:00 live=0), token_meter 0 L2 tokens today.")
st["note"] = "r917: integration round; product faces = f63639bf4 (r916 estate + S0 resolver receipts) + REPORT/LIVE-2026-10-13 regen"
st["now_active"] = "bm-b CPU/bookkeeping lanes alive (loop parent, SatEngine ticking, astock full-universe refresh in-flight); GPU idle (MODE=pause PSU-deferred, i2v 27/53)"
st["verdict"] = ("GREEN-with-flags: S0 fork integration landed (f63639bf4, 6 UU resolved per documented resolver laws, zero-loss assertions all pass); flags = GPU production deferred per power-loss recipe "
                 "(PSU degraded 3 shutdowns today, ETA=PSU swap/CEO re-order) + unity bridge unconnected (3 probes) + N2U3 chain batch-gated + pool starvation = known-blocked supply face")
st["latest_artifact"] = "f63639bf4 on origin/main (S0 integration: r916 closeout + daemon absorb + resolver receipts _r917bmb_resolve.py/_r917bmb_resolve2.py) + REPORT-2026-10-13 + LIVE-2026-10-13 (ORANGE)"
st["next_milestone"] = "honest: GPU line blocked on PSU swap/CEO re-order; unity bridge diagnosis next editor-open window; N2U3 chain resumes only after i2v 53/53; next data window 2026-10-14 15:30"
st["last_decisions_at"] = iso
st["last_decisions_read_at"] = iso
st["last_orders_at"] = iso
st["last_orders_read_at"] = iso
st["orphan_face"] = 0
st["orphan_face_note"] = "r917 probe 23:1x: py_faces=17 orphans=0 killed=[] (satengine faces + astock refresh worker = legal lanes)"
st["orphan_faces"] = 0
st["sync"] = {"last_push_ts": iso, "note": "r917: S0 integration push f63639bf4 (closeout replay + absorb) delivery self-proof 0/0; closeout commit+push follows this write"}
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---------- heartbeat fleet/machines/bm-b.json ----------
hp = ROOT + r"\fleet\machines\bm-b.json"
try:
    hb = json.load(open(hp, encoding="utf-8"))
except Exception:
    hb = {}
import psutil
ram_free_gb = round(psutil.virtual_memory().available / (1024**3), 1)
ram_free_pct = round(psutil.virtual_memory().available * 100.0 / psutil.virtual_memory().total, 1)
vram_free_gb = None
try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.total,memory.used", "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=10)
    tot, used = [float(x) for x in r.stdout.strip().split(",")]
    vram_free_gb = round((tot - used) / 1024, 1)
except Exception:
    pass
hb.update({
    "machine_id": "bm-b",
    "last_seen": iso,
    "clock_read": iso,
    "ts": iso,
    "heartbeat_epoch_utc": epoch,
    "cpu_cores": psutil.cpu_count(),
    "idle_ram_gb": ram_free_gb,
    "idle_ram_pct": ram_free_pct,
    "gpu_idle_vram_gb": vram_free_gb,
    "current_task": st["current_task"],
    "last_action": st["last_action"],
    "verdict": "GREEN-with-flags (S0 integration landed f63639bf4; GPU PSU-deferred; unity bridge 3-probe unconnected)",
    "idle_rounds": 0,
    "agenda_starved": False,
    "orphan_face": 0,
    "now_active": st["now_active"],
    "latest_artifact": st["latest_artifact"],
    "next_milestone": st["next_milestone"],
})
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178 law)"
assert "T" in chk["clock_read"], "clock_read must be T-separated ISO (R262 law)"

# ---------- round report line ----------
rp = ROOT + r"\logs\iteration-loop\round_reports.md"
line = (f"{iso} | r917 bm-b [dept:eng/fleet] | S0 fork integration round (main deliverable) | "
        f"watermark: GREEN (red=false; next_pick=claimed moneyflow IC source-blocked self-heal; local_batch=1 astock_daily refresh lane) | "
        f"orphan-faces=0 (probe 23:1x: py_faces=17 orphans=0 killed=[]) | "
        f"currently-active: CPU/bookkeeping lanes (loop parent, SatEngine hb 11s, astock full-universe refresh in-flight); GPU idle (MODE=pause PSU-deferred, i2v 27/53) | "
        f"latest-artifact: f63639bf4 on origin/main = S0 integration (r916 closeout replayed 4437368d4 + daemon absorb f63639bf4, 6 UU resolved per resolver laws: probe faces ts-newer-wins, machine-health max-date, satengine daemon live-wins, history jsonl line-union 133 zero-loss) + REPORT-2026-10-13 + LIVE-2026-10-13 (ORANGE cap50) regen | "
        f"next-milestone: PSU swap/CEO re-order -> i2v 53/53 -> N2U3 flip double-gate (RAM leg OK) -> autofill -> export-topk -> judged; unity bridge diagnosis next editor-open window (probe#3 unconnected); data window 10-14 15:30 | "
        f"did: (1) S0: round-start pull --rebase blocked by daemon-dirty tree -> fetch + D-19 probe (orders 91d9fad3 unchanged, zero new); behind=2 (bm-c 6edff35ff/b3d66545c) + own unpushed c7c8d8746 (r916 closeout push had failed silently) -> absorb daemon faces pre-rebase + rebase onto b3d66545c: 1/2 closeout 2 UU (_r686bmb probe faces, r967 ts-newer-wins mine 23:04), 2/2 absorb 4 UU (machine-health 23:11 > 22:36, satengine face/state daemon live-wins r825, history_bm-b.jsonl r756 line-union 120+13=133 per-line-json-OK); r855 daemon churn blocked continue 3x, cured each by same-call add+amend/continue (r696 beat-silenced law); state.json auto-merge verified (bm-b round_no 917 intact), round_reports union verified (r916 line at tail); push f63639bf4 + fetch self-proof 0/0. "
        f"(2) S1 smoke 49/49 PASS. (3) S3: SatEngine alive idle queue 0; watermark GREEN; pool_dualrun streak 51 ZERO-DRIFT; compute_audit FLAG pool_starvation+supply_floor = N2U3 double-gate known-blocked (batch-gated on PSU-deferred i2v, honest carry not a bug); py_watermark insufficient_history (astock lane in-flight); idle_trigger green_idle=false (ram 37.3% < 40), agenda_starved=false, idle_rounds=0. "
        f"(4) unity-mcp bridge probe #3 via MCP tool: No Unity Editor instances found = 3rd consecutive failure -> bridge-level diagnosis (plugin presence/port scan) queued next editor-open window. "
        f"(5) S6 quick legs: update_daily no-op, daily_report REPORT-2026-10-13 faces=5, ceo_live LIVE-2026-10-13 ORANGE, token_meter 0 L2 today. "
        f"| evidence: f63639bf4 push + rev-list 0/0 + _r917bmb_resolve.py/_r917bmb_resolve2.py outputs + smoke 49/49 + results/watermark_red.json + results/idle_trigger.bm-b.json + results/compute_audit.bm-b.json | "
        f"unacked_orders=0 | registry-zero-hit: no sweep/archive/delete actions this round | "
        f"local-unreached-origin-commits: round-start behind=2+own1 -> S0 rebase -> push f63639bf4 0/0; closeout commit carrying this line pushes immediately after | "
        f"next-pointer r918: unity bridge diagnosis (probe#4 plugin/port) > PSU-swap watch (160W clause) > at batch-done: keepwarm.pause removal + N2U3-LEG3-TRAIN flip -> autofill -> export-topk K=32 -> judged > Music3 install post-batch (license PASS r913) > Speech-02 adjudication (CEO/committee) > game-audio batch (O-2245 bm-b face) > E15 s4 intake legs = monthly boundary | [r917 bm-b]\n")
with open(rp, "a", encoding="utf-8", newline="\n") as f:
    f.write(line)

# memory-entry four-question gate (cph4/memory.md): r855 re-recurrence + silent-push-failure lesson
print("CLOSEOUT-WRITE-OK", iso, "epoch", epoch, "ram_free", ram_free_gb, "vram_free", vram_free_gb)
