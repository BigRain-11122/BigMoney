# r275 bm-b: state.json round bump + heartbeat update (S7). Live RAM/VRAM probe.
import json, time, datetime, subprocess

state = {
 "round_no": 275,
 "did": "r275: migration run-3 2nd-ABORT adjudicated via journal (sole holder=leftover shell 4036, now gone) -> executor v2.2 (Gate 0.5 precheck-first zero-mutation wait for unbounded user faces + single-instance PID lock + new-root idempotent early-exit; DryRun 19/19, parser 0 err, two false-blockers self-caught: websockify name-blind face + empty-shell double-block) -> re-armed detached PID 28696, precheck blockers now = 3 Tuanjie editor procs only, auto-triggers when editor closes, window till 09-29 12:00 + T-83 ticket closed done (4 slices, 5 post_review families all YES, byte splice 4+/2-) + S6 25 legs exit 0",
 "verdict": "green",
 "next": "next round FIRST PROBE ROOT: new root E:/Fluxgroup/FluxGroup/quant/bigmoney exists -> five-receipt assembly + old-root backup cleanup + new-root first push; old root alive -> journal tail (3rd ABORT? holder snapshots now in journal) + executor lock liveness check (PID 28696 alive = still precheck-waiting, do NOT double-arm, lock refuses but probe first is honest); editor-closes = auto-migration; window till 09-29 12:00",
 "last_round_ts": "2026-09-26T22:40:00+08:00",
 "last_result": "ok",
 "current_task": "r275 done: migration executor v2.2 armed (precheck-first, editor-gated auto-trigger); next: 09-28 Monday-window new-bar chain + 10-01 month-first trio",
 "last_tick": "22:17",
 "updated_at": "2026-09-26T22:40:00+08:00",
}
with open('logs/iteration-loop/state.json', 'w', encoding='utf-8', newline='\n') as f:
    json.dump(state, f, ensure_ascii=False, indent=1)
    f.write('\n')

# live resource probes
free_kb = None
try:
    out = subprocess.check_output(
        ['powershell', '-NoProfile', '-Command',
         '[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,1)'],
        text=True)
    free_kb = float(out.strip())
except Exception as e:
    free_kb = None
gpu_free = None
try:
    out = subprocess.check_output(
        ['powershell', '-NoProfile', '-Command',
         "nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits"],
        text=True)
    gpu_free = int(out.strip().splitlines()[0])
except Exception:
    gpu_free = None

now = datetime.datetime.now().astimezone()
clock_read = now.isoformat(timespec='seconds')   # T-separator law (R262)
epoch = int(time.time())                          # JSON int law (R170/R178)
hb_path = 'fleet/machines/bm-b.json'
hb = json.load(open(hb_path, encoding='utf-8-sig'))
hb.update({
    "last_seen": clock_read,
    "current_task": "r275: migration executor v2.2 armed precheck-first (PID 28696, editor-gated); T-83 done; S6 green",
    "cores": 16,
    "cpu_cores": 16,
    "free_ram_gb": free_kb,
    "idle_ram_gb": free_kb,
    "gpu_free_vram_mb": gpu_free,
    "gpu_idle_vram_mb": gpu_free,
    "round_no": 275,
    "verdict": "loaded_ok",
    "heartbeat_epoch_utc": epoch,
    "clock_read": clock_read,
})
with open(hb_path, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)   # no trailing newline (blob face)

# self-verify (smoke F7 faces)
hb2 = json.load(open(hb_path, encoding='utf-8-sig'))
assert isinstance(hb2['heartbeat_epoch_utc'], int), 'epoch not int'
assert 'T' in hb2['clock_read'] and '+' in hb2['clock_read'], 'clock_read not T-sep ISO'
print('state.json round 275 + heartbeat written; epoch int OK; clock_read', hb2['clock_read'],
      '| free_ram_gb', free_kb, '| gpu_free_mb', gpu_free)
