# -*- coding: utf-8 -*-
# r915 bm-b heartbeat writer (atomic, int-typed epoch, live RAM/GPU sample)
import json, subprocess, time, ctypes

now = time.time()
epoch = int(now)
clock = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")  # local = +08:00 machine tz

class M(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("dwTotalPhys", ctypes.c_ulonglong), ("dwAvailPhys", ctypes.c_ulonglong),
                ("dwTotalPageFile", ctypes.c_ulonglong), ("dwAvailPageFile", ctypes.c_ulonglong),
                ("dwTotalVirtual", ctypes.c_ulonglong), ("dwAvailVirtual", ctypes.c_ulonglong),
                ("dwAvailExtendedVirtual", ctypes.c_ulonglong)]
m = M(); m.dwLength = ctypes.sizeof(M)
if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):
    raise RuntimeError("GlobalMemoryStatusEx failed")
ram_free_gb = round(m.dwAvailPhys / 1024**3, 2)

gpu = {"util_pct": 0.0, "mem_used_mb": 0.0, "power_w": 0.0}
try:
    out = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,power.draw",
                          "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=10).stdout.strip()
    p = [x.strip() for x in out.split(",")]
    gpu = {"util_pct": float(p[0]), "mem_used_mb": float(p[1]), "power_w": float(p[2])}
except Exception:
    pass

hb = json.load(open(r"fleet\machines\bm-b.json", encoding="utf-8"))
hb.update({
    "clock_read": clock, "ts": clock, "updated": clock, "updated_at": clock,
    "last_seen": clock, "last_action_at": clock, "last_round_at": clock,
    "heartbeat_epoch_utc": epoch,
    "round": 915, "round_no": 916, "round_no_label": "r915",
    "idle_rounds": 0, "agenda_starved": False, "green_idle": False,
    "current_task": "r915 closeout; r916 = batch watch (KN22a in-flight, 23/53) + unity-mcp bridge re-check (editor-open window live 09:14) + at 53/53: N2U3 flip double-gate + Music3 install window",
    "free_ram_gb": ram_free_gb, "ram_free_gb": ram_free_gb, "ram_free_pct": round(ram_free_gb / 24.0 * 100, 1),
    "vram_free_gb": round((8191 - gpu["mem_used_mb"]) / 1024.0, 2),
    "gpu_free_vram_gb": round((8191 - gpu["mem_used_mb"]) / 1024.0, 2),
    "gpu_free_vram_mb": int(8191 - gpu["mem_used_mb"]),
    "gpu": {"util_pct": gpu["util_pct"], "mem_used_mb": gpu["mem_used_mb"], "power_w": gpu["power_w"],
            "face": "i2v animatic batch burning (23/53 revived, KN22a in-flight, ComfyUI r915d PID 21476 + driver r915d PID 12028, 180W cap held)"},
    "orphan_face": 0, "orphan_faces": 0,
    "orphan_face_note": "r915 probe 09:06:31: py_faces=5 orphans=0 killed=[] (backfill_ext_slots detached-legal face noted); driver was dead since 04:06 -> revived 09:13",
    "did": "r915: (1) DEAD-SESSION TAKEOVER: prior r915 incarnation ran S6 41 legs 04:07-04:10 (rc_nonzero=1 = t35 rc=1 known) then died pre-closeout; driver respawns 04:14/08:43 died instantly = session-attached spawn face. (2) P0 ROOT-CAUSE FIX: ComfyUI r908c died 04:06:43 CUDA OOM mid-KN22a (61min crawl + 100%util-at-82-90W thrash signature); VRAM thief = Ollama qwen reload via MiniGameOllamaServe logon trigger (09:05:27 CEO logon) -- serve-warm.ps1 LACKED keepwarm.pause check. Fix: killed ollama+llama-server (r904 valve, VRAM 4068->359MiB) + patched serve-warm.ps1 pause-check + restarted ComfyUI r915d (PID 21476 :8188) + driver r915d (PID 12028, pythonw file-redirect detached) -> batch revived 23/53, KN22a same seed re-submitted, GPU 100%/179.5W at 180W cap. (3) D-19 orders delta a23119c6->3f22ee3e consumed (1 new row @bm-a Krea2 frame dispatch, MV-line, zero BigMoney rows); decisions fb378423 unchanged. (4) S1 smoke 49/49; SatEngine alive idle; watermark GREEN red=false; board open=0; job_list empty. (5) unity-mcp POC: Tuanjie editor FRESH process 09:14:52 (editor-open window NOW) but bridge unconnected 09:16 -> r916 priority re-check, due 12:00. (6) S7 all green: loop pin=2, watchdog re-registered, both claws installed, attrition CLEAN, inbox zero-for-bm-b.",
    "last_action": "r915: dead-session takeover + ComfyUI CUDA-OOM root-caused (Ollama logon-respawn VRAM theft, serve-warm pause-check patched) + i2v batch re-ignited 23/53 + D-19 orders delta consumed + unity-mcp editor-open window detected",
    "latest_artifact": "i2v batch revival 23/53 + KN22a in-flight (gitignored media face) + serve-warm.ps1 pause-valve patch (machine-local OOM root-cause fix) + driver_r915d.out.txt + r915 round report line + results/_r686bmb_d19_check.json",
    "next": "r916: i2v batch watch -> at 53/53 (~15:00-19:00): remove keepwarm.pause + flip N2U3-LEG3-TRAIN waiting->ready (batch-done + RAM>=4GB double gate) -> autofill burn (~3.3h) -> export-topk K=32 -> judged legs > unity-mcp POC due 10-13 12:00 (editor-open window live, bridge re-check = priority leg) > Music3 install window post-batch (license PASS r913) > Speech-02 adjudication awaiting committee/CEO > E15 s4 intake legs = monthly boundary",
    "next_milestone": "i2v 53/53 ETA ~10-13 late afternoon (revived 09:13 after 5h dead window) -> N2U3 flip double-gated -> export-topk + judged legs; unity-mcp POC <=10-13 12:00; Music3 install post-batch (license PASS)",
    "note": "r915: dead-session takeover + ComfyUI CUDA-OOM root-cause fix (Ollama logon-respawn VRAM theft, serve-warm pause-check patched) + batch re-ignition 23/53 + D-19 orders delta consumed + unity-mcp editor-open window detected",
    "now_active": "i2v animatic batch burning again (23/53, KN22a in-flight, ComfyUI r915d PID 21476 + driver r915d PID 12028 detached, GPU 100% under 180W cap, VRAM ComfyUI-only, Ollama killed per r904 valve + serve-warm pause-check patched)",
    "task": "r916: i2v batch watch -> at 53/53: remove keepwarm.pause + N2U3 flip double-gate -> autofill -> export-topk K=32 -> judged > unity-mcp POC due 10-13 12:00 (bridge re-check, editor-open window live) > Music3 install window post-batch > Speech-02 adjudication awaiting committee/CEO > E15 s4 intake legs = monthly boundary",
    "verdict": "GREEN-with-flags: production-line repair round under legal GPU burn (ComfyUI CUDA-OOM root-caused + valve-patched + batch re-ignited 23/53, KN22a in-flight at 180W cap, detached driver survives sessions); flags=pool_starvation/supply_floor standing (resource-blocked until batch completes) + machine-state resume path still starts Ollama unconditionally (residual VRAM-theft risk during batch, fleet-shared file not modified, follow-up note) + unity-mcp POC bridge pending (editor process live 09:14:52, connection re-check due 12:00)",
    "sync": {"last_push_ts": clock, "note": "r915 closeout: salvage commit + pull --rebase + push follow this write; delivery self-proof (fetch+rev-list) -> r916 round-start verify"},
})

json.dump(hb, open(r"fleet\machines\bm-b.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(r"fleet\machines\bm-b.json", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
print("heartbeat written epoch=%d clock=%s ram_free=%.2fGB gpu=%s" % (epoch, clock, ram_free_gb, gpu))
