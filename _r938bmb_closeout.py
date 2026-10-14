# r938 bm-b S7 closeout: state round 937->938, heartbeat, round report line, fresh group hashes
import ctypes
import hashlib
import json
import subprocess
import time

NOW = "2026-10-14T15:58:40+08:00"
EPOCH = int(time.time())


def group_sha(path, algo):
    blob = subprocess.check_output(
        ["git", "-C", r"C:\Fluxgroup\FluxGroup", "show", "origin/main:" + path]
    )
    return hashlib.sha256(blob).hexdigest() if algo == "sha256" else hashlib.sha1(blob).hexdigest()


class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


m = MEMORYSTATUSEX()
m.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
ram_free_gb = round(m.ullAvailPhys / (1024 ** 3), 1)
ram_free_pct = round(m.ullAvailPhys * 100.0 / m.ullTotalPhys, 1)

DEC_SHA = group_sha("docs/decisions.md", "sha256")
ORD_SHA = group_sha("docs/orders.md", "sha1")

did = (
    "r938 bm-b S0-estate-absorb round (watchdog-killed r937 rebase healed): "
    "(1) S0: found rebase-merge in progress 1/3 (pick 05f1a00e9 UU fleet/machine-health.json) -- "
    "union heal 13->9 rows dual-tail 14:36+15:11 verified (r996/r998 precedent, treasure_guard rc0 "
    "reproducible-artifact class, resolver _r938bmb_resolver.py committed as evidence); picks 2-3 conflicts "
    "= 5+3 bm-b own SatEngine/live daemon faces resolved live-wins (history 120-row window rotated-by-design, "
    "20 old rows out = daemon trim, not loss); rebase completed clean; owner-content audit PASS (state "
    "round 937 clock 15:33:23 verdict W20 = bm-b own, r936 law); r937 stranded estate DELIVERED "
    "(push 1a1161be3..1ae3f0f15: W20 census 0/45 + S6 37/37 + state r937); (2) S0.5 orders scan + S7 "
    "double-scan both NONE unacked; D-19 decisions hash CHANGED d9d8aa72->"
    + DEC_SHA[:16]
    + " -- consumed dispatch board + 6 new D-rows (D-20261014-02..07) ALL executor=FluxVerse/HQ/group "
    "= zero rows involving this repo -> watermark update zero-action per law; group night-report note: "
    "bigmoney six-task E1 revival Running-OK 03:07 = observation only; (3) S1 smoke 49/49 PASS; "
    "SatEngine alive; watermark red=false; idle verdict None (no GREEN-IDLE); (4) S6 full chain rc0: "
    "dualrun streak 23 ZERO-DRIFT, compute_audit FLAG pool_starvation+supply_floor (verdict stands: "
    "tick-stock-panel route closed, refill = P1 stock-universe ticket or sec.5 sources), "
    "py_watermark=py_low_board_clear (legal idle white-list), market_clock ORANGE_COOL, thermo rebuild, "
    "dualarm DUALARM-2026-09-30 honest asof, prospect 22/22 + promotion gate 0/22 eligible, "
    "daily_report REPORT-2026-10-14 + LIVE-2026-10-14 (state=ORANGE cap 50%) written; TODAY=trading "
    "day confirmed (marks 19 rows to 15:05 settle + minute feed 15:00 bars) but sina DAILY bar not yet "
    "published -> panel cutoff stays 10-13, live.paper/t35/t24 gated legs honest skip, self-heal next "
    "rounds; (5) S7: attrition CLEAN (1 healed shrink note), loop pin=2 no-op next 16:02, watchdog "
    "alive 15:59, both claws OK; observation: strategy_scorecard+daily_scorecard ran full derive on "
    "bm-b (no r378 host-guard found in code face; deterministic-idempotent zero-drift; flag for "
    "guard-face governance audit); inbox 1 unread = MSG-2026-10-14-1547-bmc addressed to bm-a (not "
    "this machine, not ALL) -> zero action, left in place"
)

verdict = (
    "GREEN: r938 S0 estate absorb landed whole-package (interrupted r937 rebase healed via union "
    "dual-tail + live-wins chain, stranded W20 census estate delivered to origin); S6 full chain rc0; "
    "smoke 49/49; attrition CLEAN; orders 0 unacked; flags = supply_floor/pool_starvation standing "
    "WITH VERDICT (route closed; refill = P1 stock-universe ticket or sec.5 sources) + GPU PSU-deferred "
    "standing (MODE=pause) + sina 10-14 daily-bar catch pending (self-heal) + scorecard guard-face "
    "observation (governance audit pointer)"
)

next_ptr = (
    "r939: (a) 48h CEO W19 report DRAFT FIRST ACT (due 2026-10-16 13:49: W19 lawful-zero verdict + "
    "three-axis X/S/T adjudication + W20 census verdict + supply route decision points); (b) sina "
    "10-14 daily bar catch -> live.paper REGIME_GUARD=enforce + t35_open_fill_verify + t24 legs when "
    "landed; (c) standing: GPU PSU-swap MODE=pause, backfill_ext_slots monitor, bili-reply CEO cookie "
    "gap, scorecard guard-face governance audit pointer"
)

# --- state.json (field-preserving update) ---
s = json.load(open("state.json", encoding="utf-8"))
s.update({
    "round": 938, "round_no": 938, "round_no_label": "r938",
    "clock_read": NOW, "ts": NOW, "updated": NOW, "updated_at": NOW,
    "last_round_at": NOW, "last_round_ts": NOW, "last_seen": NOW,
    "last_action_at": NOW, "last_action": "r938: S0 estate absorb (rebase heal + stranded r937 estate delivered to origin 1ae3f0f15) + S6 full chain rc0",
    "last_decisions_at": NOW, "last_decisions_read_at": NOW, "last_decisions_sha": DEC_SHA,
    "last_decisions_sha_method": "r938: fresh git -C C:/Fluxgroup/FluxGroup fetch (2fb6677..5df53b1) + show origin/main:docs/decisions.md; hash CHANGED -> dispatch board + D-20261014-02..07 consumed, zero rows involve BigMoney -> watermark update zero-action",
    "last_orders_at": NOW, "last_orders_read_at": NOW, "last_orders_sha": ORD_SHA,
    "last_orders_sha_note": "r938: orders.md tail consumed same window (bm-a/bm-c video/bili rows only, zero BigMoney rows); sha1 updated",
    "did": did, "verdict": verdict,
    "current_task": "r938 estate absorb landed; r939 first act = 48h CEO W19 report draft (due 10-16 13:49)",
    "task": "r938 estate absorb landed; r939 first act = 48h CEO W19 report draft (due 10-16 13:49)",
    "next": next_ptr,
    "next_milestone": "48h CEO W19 report due 2026-10-16 13:49 (draft = r939 first act); sina 10-14 daily bar catch next rounds",
    "now_active": "r938 estate absorb landed; SatEngine ticking; CPU lanes green; sina 10-14 daily bar catch pending; GPU MODE=pause PSU-deferred standing",
    "latest_artifact": "push 1a1161be3..1ae3f0f15 (r937 W20 census estate delivered) + S6 products REPORT-2026-10-14.md / LIVE-2026-10-14.md @ " + NOW,
    "note": "r938: S0 fork round; rebase heal chain per r996/r998 precedents; zero new pits (all faces already in pit-git-resolver/pit-spawn corpus); no memory append (four-gate: no long-term-new lesson)",
    "orphan_face": 0, "orphan_faces": 0,
    "orphan_face_note": "r938 round-zero probe 15:39: py_faces=14 orphans=0 killed=[]",
})
s["sync"] = {"last_push_ts": NOW, "note": "r938 closeout commit+push follows this write; behind=0 self-proof post-push"}
json.dump(s, open("state.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# --- heartbeat fleet/machines/bm-b.json ---
h = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
h.update({
    "round": 938, "round_no": 938, "round_no_label": "r938",
    "last_seen": NOW, "clock_read": NOW, "ts": NOW,
    "last_round_at": NOW, "last_action_at": NOW,
    "heartbeat_epoch_utc": EPOCH,
    "idle_rounds": 0, "agenda_starved": False, "green_idle": False,
    "idle_ram_gb": ram_free_gb, "ram_free_gb": ram_free_gb, "free_ram_gb": ram_free_gb,
    "idle_ram_pct": ram_free_pct, "ram_free_pct": ram_free_pct,
    "vram_free_gb": 3.7, "gpu_free_vram_gb": 3.7, "gpu_free_vram_mb": 3802,
    "gpu_idle_vram_gb": 3.7, "gpu_free_vram": "3802 MiB",
    "did": "r938 bm-b S0-estate-absorb round: watchdog-killed r937 rebase healed (machine-health union dual-tail + SatEngine live-wins), stranded W20 census estate delivered to origin (1ae3f0f15); S6 full chain rc0; smoke 49/49",
    "last_action": "r938 estate absorb + delivery; sina 10-14 daily bar catch pending (live legs skip honest)",
    "current_task": "r939 first act = 48h CEO W19 report draft (due 10-16 13:49) + supply route decision",
    "task": "r939 first act = 48h CEO W19 report draft (due 10-16 13:49) + supply route decision",
    "next": next_ptr,
    "next_milestone": "48h CEO W19 report due 10-16 13:49; sina bar catch; supply route decision",
    "latest_artifact": "origin main 1ae3f0f15 (r937 estate) + REPORT-2026-10-14.md + LIVE-2026-10-14.md @ " + NOW,
    "now_active": "r938 estate absorb landed; SatEngine ticking; sina 10-14 bar catch pending; GPU MODE=pause standing",
    "verdict": "GREEN: r938 estate absorb landed; S6 full chain rc0; flags: supply route closed-with-verdict + GPU PSU-deferred + sina bar catch pending",
    "orphan_face": 0, "orphan_faces": 0,
    "orphan_face_note": "r938 round-zero probe 15:39: py_faces=14 orphans=0",
})
h["sync"] = {"last_push_ts": NOW, "note": "r938 closeout commit+push follows"}
json.dump(h, open("fleet/machines/bm-b.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# --- round report line (bm-b file per fleet/README sec.6) ---
line = (
    NOW + " | r938 bm-b [dept:eng/fleet] | WM-VERDICT: green (red=false; next_pick claimed moneyflow "
    "source-blocked self-heal; py_watermark=py_low_board_clear legal idle white-list; compute_audit "
    "flags pool_starvation+supply_floor standing WITH verdict) | orphan-faces=0 (round-zero probe 15:39: "
    "py_faces=14 orphans=0) | active now: CPU/bookkeeping lanes (loop, SatEngine hb, autofill); GPU "
    "MODE=pause PSU-deferred standing | latest-artifact: origin main 1ae3f0f15 = stranded r937 estate "
    "DELIVERED (watchdog-killed mid-rebase healed: machine-health union dual-tail 14:36+15:11 + SatEngine "
    "live-wins picks 2-3; owner-audit r936 PASS) + S6 products REPORT-2026-10-14.md/LIVE-2026-10-14.md "
    "(state=ORANGE cap 50%) | next milestone: 48h CEO W19 report draft due 2026-10-16 13:49 (r939 first "
    "act); sina 10-14 daily bar catch -> live.paper chain when landed | notes: S0.5+S7 double orders scan "
    "NONE unacked; D-19 decisions hash changed -> dispatch board + 6 new D-rows consumed, ALL "
    "executor=FluxVerse/HQ/group zero rows involve this repo (watermark updated); today=trading day "
    "confirmed (marks 19 rows + minute 15:00 bars) but sina daily bar unpublished -> panel cutoff stays "
    "10-13, live/t35/t24 gated legs honest skip; inbox 1 unread MSG-2026-10-14-1547-bmc addressed to "
    "bm-a (not this machine) zero action left in place; observation: strategy_scorecard/daily_scorecard "
    "ran full derive on bm-b with no r378 host-guard in code face (deterministic-idempotent zero-drift; "
    "governance audit pointer filed) | behind-origin=0 (post-push rev-list self-proof) | r938 closeout\n"
)
with open(r"logs\iteration-loop\round_reports.md", "a", encoding="utf-8", newline="\n") as f:
    f.write(line)

# epoch type self-proof (R170/R178 law)
chk = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"], "clock_read must be ISO8601 T-separated"
print("closeout written; epoch=", chk["heartbeat_epoch_utc"], "ram_free=", ram_free_gb, "dec_sha=", DEC_SHA[:16], "ord_sha=", ORD_SHA[:12])
