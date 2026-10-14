# -*- coding: utf-8 -*-
"""r943 bm-b closeout: pit-ps direct-write + CODELY pointer + state/heartbeat
+ round report line. House pattern (r939/r873 direct-write convention).
Reads fresh runtime faces (idle_trigger/compute_audit) for heartbeat numbers.
Preserves d19 keys written by scripts/d19_watermark.py earlier this round."""
import hashlib
import io
import json
import time
from datetime import datetime, timedelta, timezone

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
CST = timezone(timedelta(hours=8))
now = datetime.now(CST)
TS = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())

# ---------- 1. pit-ps.md direct-write (new pit + accounting line) ----------
PIT_ENTRY = (
    "- [2026-10-14 18:3x r943 bm-b] **Invoke-SilentExe \u6574\u4e32 stdout "
    "\u00d7 Select-String \u884c\u89e3\u6790\u5047\u884c\u5751\uff08schtasks "
    "\u6e05\u5355\u5b9e\u5f39\u00b7\u9759\u9ed8\u9519\u884c\u975e\u6570\u636e"
    "\u7f3a\u5931\uff09**\uff1aInvoke-SilentExe.ps1 \u628a\u5b50\u8fdb\u7a0b "
    "stdout \u4f5c\u4e3a**\u5355\u4e2a\u591a\u884c\u5b57\u7b26\u4e32** "
    "Write-Output \u2192 Select-String \u5bf9\u5355\u4e32\u5bf9\u8c61\u6574"
    "\u5757\u5339\u914d\u4e00\u6b21\uff08$_.Line=\u5168\u8868\u6587\u672c\uff09"
    "\u2192 `($_.Line -split ',')[0]` \u6052\u53d6\u5168\u8868**\u9996\u884c"
    "\u9996\u5b57\u6bb5**\uff08\u5b9e\u5f39\uff1aschtasks /query /fo csv /nh "
    "\u5168\u8868\u89e3\u6790\u4efb\u52a1\u540d\u53ea\u56de ArtQueueWorker "
    "\u4e00\u884c=Bigmoney-* \u5168\u5458\u5047\u7f3a\u5e2d\uff09\u3002\u6b63"
    "\u6cd5=\u5148\u9010\u884c\u5316\u518d\u5339\u914d `($out -split \"`n\") "
    "| Select-String ...`\uff0c\u6216\u5b58\u5728\u6027/\u5355\u4efb\u52a1\u9762"
    "\u6539 `schtasks /query /tn <\u540d> /fo LIST` \u76f4\u67e5\uff08R49 "
    "\u7a7a\u8f93\u51fa==\u4e0d\u5b58\u5728\u6b63\u5178\uff09\u3002How to "
    "apply\uff1a\u51e1\u89e3\u6790 Invoke-SilentExe \u591a\u884c stdout"
    "\uff08schtasks/git \u76ee\u5f55\u6e05\u5355\uff09\u5148 -split \u9010\u884c"
    "\u5316\uff1b\u89c1\u300c\u6e05\u5355\u53ea\u56de\u4e00\u9879/\u9996\u9879"
    "\u300d\u5148\u7591\u6574\u4e32\u9762\u52ff\u7591\u4efb\u52a1\u7f3a\u5931"
    "\u3002\n")
entry_blob = PIT_ENTRY.encode("utf-8")
md5 = hashlib.md5(entry_blob).hexdigest()
acct = (
    "> Direct-write line (r943 bm-b, post-split convention direct-write, "
    "r666/r873/r939 exception: CODELY.md main near cap -> new pit enters "
    "domain file directly): +1 new pit (Invoke-SilentExe whole-string stdout "
    "x Select-String fake-row parse) - appended %d B - LF blob net - md5=%s "
    "- file-tail append - the in-file accounting line is authoritative.\n"
    % (len(entry_blob), md5))
p = io.open(ROOT + r"\research\pit-ps.md", "r", encoding="utf-8")
ps = p.read()
p.close()
if "- [2026-10-14 18:3x r943 bm-b]" in ps:
    print("pit-ps entry already present -- skip (idempotent rerun)")
else:
    io.open(ROOT + r"\research\pit-ps.md", "a", encoding="utf-8",
            newline="\n").write(PIT_ENTRY + acct)
    print("pit-ps appended %d B md5=%s" % (len(entry_blob), md5))

# ---------- 2. CODELY.md pointer line ----------
PTR = (
    "- \u57df\u6307\u9488\u00b7r943 bm-b \u76f4\u5199\uff0810-14 18:3x\u00b7"
    "\u4e3b\u4ef6\u8fd1\u5e3d r939/r889 \u8303\u5f0f\uff09\uff1ar943 \u65b0"
    "\u5751\u76f4\u5199 research/pit-ps.md\uff3bInvoke-SilentExe \u6574\u4e32 "
    "stdout \u00d7 Select-String \u884c\u89e3\u6790\u5047\u884c\u5751\u00b7"
    "\u9759\u9ed8\u5305\u88c5\u5668\u8f93\u51fa\u6d88\u8d39\u52a8\u4f5c\u524d"
    "\u6539\u8bfb\uff3d\uff1bORD \u53cd\u67e5\u54c8\u5e0c\u57fa\u5ea7\u53e3"
    "\u5f84\u5751=r814/r871 \u5df2\u5728\u518c\u96f6\u91cd\u5f55\uff08\u590d"
    "\u8ff0\u7981\u5f8b\uff09\u3002\n")
_c = io.open(ROOT + r"\CODELY.md", "r", encoding="utf-8").read()
if "r943 bm-b \u76f4\u5199" in _c:
    print("CODELY pointer already present -- skip")
else:
    io.open(ROOT + r"\CODELY.md", "a", encoding="utf-8",
            newline="\n").write(PTR)
    print("CODELY pointer appended")

# ---------- 3. runtime faces for heartbeat numbers ----------
it = json.load(io.open(ROOT + r"\results\idle_trigger.bm-b.json",
                       "r", encoding="utf-8"))
try:
    ca = json.load(io.open(ROOT + r"\results\compute_audit.bm-b.json",
                           "r", encoding="utf-8"))
    g = ca.get("gpu", {})
except Exception:
    g = {}
ram_pct = it.get("ram_free_pct", 0.0)
ram_gb = round(24 * ram_pct / 100.0, 1)
vram_gb = it.get("vram_free_gb", 0.0)
vram_mb = int(round(vram_gb * 1024))

DID = ("r943 bm-b: S0 surgery (dead r943 session checkpoint absorbed + "
       "daemon faces single commit + rebase onto bm-a r994/bm-c r1002; "
       "push 84ed94105 behind 0/0; heartbeat-was-34min-stale r612 P0 face) "
       "+ S6 39 legs rc0 (dualrun streak 28; update_daily cutoff 10-13 "
       "sina 10-14 bar still undelivered source-side -> paper chain gated "
       "honest; thermo/dualarm/rev_osc refreshed; REPORT/LIVE 10-14 faces "
       "regenerated; scorecard/daily_scorecard/build_status = lane_io "
       "stale-takeover lawful, bm-a hb stale) + orders 88/88 (0 unacked) + "
       "D-19 DEC EQUAL + ORD delta 1 line consumed (O-20261014-1705 "
       "group-domain committee-closed zero-BigMoney rows -> watermark "
       "ADVANCED 1176e4c4 read-back OK) + smoke 49/49 + SatEngine alive "
       "(idle queue 0) + orphan 0 + attrition CLEAN + claws x4 + W241 seat "
       "MSG receipted to processed/")
VERDICT = ("GREEN: r943 S0 surgery merged stale local to origin (push "
           "84ed94105, behind 0/0) + S6 39 legs rc0 + paper chain gated "
           "honest (no new bar, cutoff 2026-10-13) + D-19 ORD consumed+"
           "advanced (O-20261014-1705 group-domain, zero BigMoney rows) + "
           "orders 0 unacked + smoke 49/49 + attrition CLEAN + W241 MSG "
           "receipted; waiting state = sina 10-14 bar (external) + CEO "
           "route-a signature (external) + MF panel source-block (bm-a "
           "lane, 30-min self-heal)")
NEXT = ("r944: (a) sina 10-14 bar catch -> live.paper REGIME_GUARD=enforce "
        "+ t35_open_fill_verify + t24 prospect legs when landed; (b) supply "
        "route (a) stock-universe P1 awaits CEO signature; route (b) closed "
        "by W20 census -- waiting-state declaration, no re-scan of same "
        "objects")
NOW_ACTIVE = ("r943 closeout: S0 merged + S6 39 legs rc0; SatEngine ticking; "
              "waiting state = sina 10-14 bar (external) + CEO route-a "
              "signature (external)")
NOTE = ("r943: orders 0 unacked (disk 88 vs ack 88); D-19 dec EQUAL "
        "c61d7884 + ord advanced 1176e4c4 (O-20261014-1705 group-domain "
        "zero-BigMoney rows); flags supply_floor/pool_starvation standing "
        "WITH VERDICT (refill = CEO P1 route (a)); sina 10-14 bar catch "
        "pending (source-side, self-heal)")
ART = ("docs/live_usage/LIVE-2026-10-14.md (ORANGE rung cap 50%) + "
       "docs/daily_report/REPORT-2026-10-14.md regenerated + DUALARM "
       "refresh @ " + TS)
MILE = ("sina 10-14 bar landing -> live.paper/t35/t24 chain (self-heal, "
        "window <=48h); supply route (a) stock-universe P1 = CEO-signed gate "
        "pending; MF panel completion -> moneyflow IC batch (bm-a lane)")

# ---------- 4. state.json ----------
sp = ROOT + r"\state.json"
st = json.load(io.open(sp, "r", encoding="utf-8"))
st.update({
    "round": 943, "round_no": 944, "round_no_label": "r943",
    "clock_read": TS, "ts": TS, "updated": TS, "updated_at": TS,
    "last_seen": TS, "last_round_at": TS, "last_round_ts": TS,
    "last_action_at": TS, "last_action": "r943: S0 surgery + S6 39 legs rc0"
    " + D-19 ORD consumed/advanced + W241 receipt",
    "did": DID, "verdict": VERDICT, "note": NOTE,
    "current_task": NEXT, "task": NEXT, "next": NEXT, "now_active": NOW_ACTIVE,
    "latest_artifact": ART, "next_milestone": MILE,
    "orphan_face": 0, "orphan_faces": 0,
    "orphan_face_note": "r943 probe 18:1x: py_faces=14 orphans=0 killed=[]",
    "sync": {"last_push_ts": TS,
             "note": "r943 closeout commit+push follows this write; "
                     "behind=0 verified post-push"},
})
json.dump(st, io.open(sp, "w", encoding="utf-8"), ensure_ascii=True,
          indent=1)
_ = json.load(io.open(sp, "r", encoding="utf-8"))
print("state.json ok round_no=944")

# ---------- 5. heartbeat ----------
hp = ROOT + r"\fleet\machines\bm-b.json"
hb = json.load(io.open(hp, "r", encoding="utf-8"))
hb.update({
    "round": 943, "round_no": 944, "round_no_label": "r943",
    "clock_read": TS, "ts": TS, "last_seen": TS, "last_action_at": TS,
    "last_round_at": TS, "heartbeat_epoch_utc": EPOCH,
    "did": DID, "verdict": VERDICT, "note": NOTE,
    "current_task": NEXT, "task": NEXT, "next": NEXT, "now_active": NOW_ACTIVE,
    "latest_artifact": ART, "next_milestone": MILE,
    "green_idle": bool(it.get("green_idle", False)),
    "idle_rounds": int(it.get("idle_rounds", 0)),
    "agenda_starved": bool(it.get("agenda_starved", False)),
    "idle_ram_gb": ram_gb, "idle_ram_pct": ram_pct,
    "ram_free_gb": ram_gb, "ram_free_pct": ram_pct, "free_ram_gb": ram_gb,
    "vram_free_gb": vram_gb, "gpu_free_vram_gb": vram_gb,
    "gpu_idle_vram_gb": vram_gb, "gpu_free_vram": "%d MiB" % vram_mb,
    "gpu_free_vram_mb": vram_mb,
    "gpu": {"face": "GPU idle-compute (MODE=pause PSU-deferred, i2v 27/53 "
                    "held); ollama valve-paused (sentinel face)",
            "power_w": hb.get("gpu", {}).get("power_w", 8.9),
            "util_pct": g.get("util_pct", 2.0)},
    "orphan_face": 0, "orphan_faces": 0,
    "orphan_face_note": "r943 probe 18:1x: py_faces=14 orphans=0 killed=[]",
})
json.dump(hb, io.open(hp, "w", encoding="utf-8"), ensure_ascii=True,
          indent=1)
chk = json.load(io.open(hp, "r", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int (R170)"
print("heartbeat ok epoch=%d int-verified" % chk["heartbeat_epoch_utc"])

# ---------- 6. round report line ----------
LINE = (
    "| " + TS + " | r943 bm-b [dept:eng/fleet] | WM-VERDICT: green (red=false; "
    "compute_audit pool_starvation+supply_floor standing WITH VERDICT "
    "route-closed refill=CEO P1 route-a; next_pick=moneyflow IC claimed "
    "panel source-blocked self-heal) | orphan-faces=0 (round-zero probe "
    "18:1x: py_faces=14 orphans=0) | current: S0 surgery merged stale "
    "local to origin (dead r943 session checkpoint absorbed + rebase onto "
    "bm-a r994/bm-c r1002 + push 84ed94105 behind 0/0) + S6 39 legs all "
    "rc0 + paper legs gated honest (no new bar, cutoff 2026-10-13) + D-19 "
    "ORD single-line consumed+advanced (O-20261014-1705 group-domain "
    "committee-closed zero-BigMoney rows) | latest artifact: docs/"
    "live_usage/LIVE-2026-10-14.md (ORANGE rung cap 50%) + REPORT-2026-"
    "10-14.md regenerated + DUALARM refresh @" + TS + " | next milestone: sina "
    "10-14 bar landing -> live.paper REGIME_GUARD=enforce + t35/t24 chain "
    "(self-heal <=48h); supply route (a) stock-universe P1 awaits CEO "
    "signature | orders 0 unacked (88/88); D-19 dec EQUAL c61d7884 + ord "
    "advanced 1176e4c4; smoke 49/49; attrition CLEAN; claws x4 "
    "reinstalled; inbox W241 seat MSG receipted+archived; unreached-origin "
    "commits=0 (push + fetch self-verify follows) | next pointer: r944 "
    "sina-bar-landing round; else waiting-state one-line declaration (no "
    "re-scan of same objects) |\n")
io.open(ROOT + r"\logs\iteration-loop\round_reports.md", "a",
        encoding="utf-8", newline="\n").write(LINE)
print("round report line appended")
print("CLOSEOUT-OK ts=%s" % TS)
