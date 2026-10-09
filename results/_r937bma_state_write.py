import json, time, datetime, subprocess

now_iso = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
epoch = int(time.time())

def ram_facts():
    try:
        import ctypes, ctypes.wintypes
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [('dwLength', ctypes.wintypes.DWORD), ('dwMemoryLoad', ctypes.wintypes.DWORD),
                        ('ullTotalPhys', ctypes.c_ulonglong), ('ullAvailPhys', ctypes.c_ulonglong),
                        ('ullTotalPageFile', ctypes.c_ulonglong), ('ullAvailPageFile', ctypes.c_ulonglong),
                        ('ullTotalVirtual', ctypes.c_ulonglong), ('ullAvailVirtual', ctypes.c_ulonglong),
                        ('ullAvailExtendedVirtual', ctypes.c_ulonglong)]
        m = MEMORYSTATUSEX(); m.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
        return round(m.ullAvailPhys / 1e9, 1), int(m.dwMemoryLoad)
    except Exception:
        return None, None

ram, load = ram_facts()
vram = None
try:
    out = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
                          capture_output=True, text=True, timeout=10).stdout.strip().splitlines()
    vram = round(sum(int(x) for x in out) / 1024, 1)
except Exception:
    vram = None

did = ("r937: S0-1 anchor bm-a + orphan probe 2->1 (ComfyUI 8188 MV-lane exempt no-kill; http.server:8000 weight-transfer lane SUPERSEDED by bm-c r824 ModelScope trio hash-gate PASS -> surgical kill 79412, lane closed) ; S0 E42 writer-pause window (4 daemon schtasks disable -> churn absorb x2 -> rebase onto 6edbeb2f9 zero-conflict -> re-enable, burn state persisted zero loss) ; S0.5 local orders 0-new (acked through O-20261010-0010) + group ORD e286f842->0ddb01d9 consumed (2 status-flips on known rows only: 0025 bm-c weights received ModelScope + 0040 executed gaming lane; zero new orders), DEC b87a92b1 UNCHANGED ; S1 smoke 49/49 PASS ; S2 board empty, tickets T-2026-10-10-180/181 open-unclaimed P1 (top of next agenda) ; S3 engine ALIVE rc0 (first rc1 = PS pipe-truncation artifact, clean rerun 0) + W203 burn COMPLETE 12/12 shards (193rd engine wave) landed to git + watermark RED runnable-work-idle-low-cpu consumed (work cands = T-180/181 session-drafting + W203 finalize, not pool batches; GPU saturated by jman LoRA training O-20261009-2330 ETA ~08:00 = py-CPU low expected) ; r934 S6 chain receipt absorbed (39 legs; update_daily rc2 = Sat ~02:00 source down, cutoff already correct 10-09; update_astock_daily rc1 = asyncio windows_utils TypeError under driver spawn only, direct run rc0 clean, r937 chain rerun = empirical verdict) ; S6 r937 driver rolled from r934 bloodline, launched detached PID 32264 (receipt next round) ; S7 quartet GREEN (loop pin=8 no-op / watchdog -Force / precommit+prepush claws LF-norm) + attrition CLEAN (4 ledgers) + state heal 933->937 honest (r934 S6 chain / r935 estate absorbed r936 / r936 W203 freeze chain on origin b2bb60963)")

nxt = ("r938: W203 FINALIZE (burn complete 12/12, five-face gates, anchor chain verified r936) + claim+start T-2026-10-10-181 overlay prereg (P1 GM-signed) or T-180 dual-arm wiring + absorb r937 S6 driver receipt (update_astock_daily driver-context TypeError verdict) + HANDOVER 5x overdue discharge + PARKING-P1 burn due 10-14 12:00")

ver = "green (r937: W203 193rd wave burn COMPLETE 12/12 shards landed; E42 rebase clean; smoke 49/49; engine ALIVE; attrition CLEAN; watermark RED consumed honestly with jman-training GPU-saturation rationale; state heal 933->937 via origin commit lineage)"

p = 'state-bm-a.json'
d = json.load(open(p, encoding='utf-8'))
d.update({
    "round_no": 937, "round": 937, "loop_round": 937, "last_round": 937,
    "clock_read": now_iso, "ts": now_iso, "updated": now_iso,
    "last_round_at": now_iso, "last_round_closed": now_iso, "last_run": now_iso, "last_seen": now_iso,
    "heartbeat_epoch_utc": epoch, "last_heartbeat_epoch_utc": epoch,
    "did": did, "current": nxt, "task": nxt, "next": nxt, "now_active": nxt,
    "next_milestone": "r938: W203 finalize + T-181 prereg claim; PARKING-P1 burn due 10-14 12:00",
    "last_action": "r937 closeout: W203 burn-complete landing + E42 rebase + superseded transfer lane wound down",
    "last_artifact": "results/p2cal_ext/n1_w203/ 12/12 shards (193rd engine wave burn complete, landed) + r937 S6 driver (r934 bloodline, detached PID 32264)",
    "latest_artifact": "results/p2cal_ext/n1_w203/ 12/12 shards (193rd engine wave burn complete, landed) + r937 S6 driver (r934 bloodline, detached PID 32264)",
    "verify": ver, "verdict": ver,
    "last_orders_sha": "0ddb01d9aca7588382fb4341651f6d7548503070d4a12cf98c2774346d48276e",
    "last_orders_seen": "O-20261010-0025 status-flip (bm-c r821 executing; weights trio received via ModelScope hash-gate PASS = bm-a transfer lane superseded, wound down r937) + O-20261010-0040 status-flip executed (gaming lane); ZERO new order rows",
    "last_orders_ts": now_iso, "last_orders_at": "2026-10-10",
    "orphan_faces": 1,
    "idle_rounds": 0, "agenda_starved": False,
})
notes_r937 = (" r937: state heal 933->937 honest (r934 ran S6 chain 01:31-01:35 receipt absorbed; r935 probe estate absorbed by r936; "
              "r936 W203 five-face FREEZE chain on origin b2bb60963; zero state writes in those windows). E42 writer-pause used with W203 burn in flight: "
              "disable->absorb->rebase->enable, queue persisted zero loss. PS pipe-truncation false rc1 on engine status (Select-Object -First closes pipe): "
              "re-run without pipe for true rc. r934-chain update_astock_daily rc1 = asyncio windows_utils TypeError under driver spawn only; direct run rc0; "
              "r937 chain rerun = empirical verdict next round.")
if isinstance(d.get('notes'), str):
    d['notes'] = d['notes'] + ' |' + notes_r937
else:
    d['notes'] = notes_r937
json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

hp = 'fleet/machines/bm-a.json'
h = json.load(open(hp, encoding='utf-8'))
h.update({
    "last_seen": now_iso, "ts": now_iso, "clock_read": now_iso,
    "heartbeat_epoch_utc": epoch,
    "current_task": nxt,
    "cpu_cores": 32, "ram_free_gb": ram, "ram_load_pct": load, "gpu_free_vram_gb": vram,
    "verdict": ver,
    "idle_rounds": 0, "agenda_starved": False,
})
acks = h.get('orders_ack') or []
for a in ["O-20261010-0010-bm-c.md"]:
    if a not in acks:
        acks.append(a)
h['orders_ack'] = acks
json.dump(h, open(hp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

hh = json.load(open(hp, encoding='utf-8'))
assert isinstance(hh['heartbeat_epoch_utc'], int), 'epoch must be int'
print('STATE+HEART written; epoch int verified; ram_free=', ram, 'ram_load=', load, 'vram_free=', vram)
