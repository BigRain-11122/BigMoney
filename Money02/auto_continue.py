"""Auto-continue after full-history backfill: wait for backfill completion ->
build_cache -> full walk-forward revalidation -> re-enable tick. Idempotent.

PowerShell '>' redirects write UTF-16LE: all log reads here are BOM-aware.
All logging goes to logs/auto_continue.log via Python utf-8 appends only.
"""
import re
import subprocess
import time

import config as C

LOG = C.LOGS_DIR / "backfill_full.log"
OWN_LOG = C.LOGS_DIR / "auto_continue.log"
DONE_RE = re.compile(r"update_data: \{")


def out(msg):
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(OWN_LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def read_log_bom_aware(path):
    raw = path.read_bytes()
    if raw.startswith(b"\xff\xfe"):
        return raw.decode("utf-16-le", errors="replace")
    if raw.startswith(b"\xef\xbb\xbf"):
        return raw.decode("utf-8-sig", errors="replace")
    return raw.decode("utf-8", errors="replace")


def wait_backfill(timeout_s=3.5 * 3600):
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        try:
            txt = read_log_bom_aware(LOG)
            m = DONE_RE.search(txt)
            if m:
                out(f"backfill done: {txt[m.start():m.start() + 80].splitlines()[0]}")
                return True
        except Exception as e:  # noqa: BLE001
            out(f"wait read error: {e}")
        time.sleep(60)
    out("backfill wait timeout")
    return False


def main():
    if not wait_backfill():
        return
    # 1) rebuild the panel cache with full history
    import data as D
    meta = D.build_cache()
    out(f"build_cache: {meta}")
    # 2) force full cycle: reset state so run_daily does the full revalidation
    state_p = C.RESULTS_DIR / "state.json"
    if state_p.exists():
        state_p.unlink()
    p = subprocess.run(["pythonw", str(C.ROOT / "run_daily.py")],
                       cwd=str(C.ROOT), capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    out(p.stdout[-2500:] if p.stdout else "(run_daily no stdout)")
    if p.returncode != 0:
        out(f"run_daily FAILED rc={p.returncode}")
        out((p.stderr or "")[-2000:])
        return
    # 3) re-enable the 10-min evolution tick (CREATE_NO_WINDOW: never flash)
    subprocess.run(["powershell", "-NoProfile", "-Command",
                    "Enable-ScheduledTask -TaskName MoneyQuantTick"],
                   capture_output=True, creationflags=0x08000000)
    out("tick re-enabled - full-history system live")


if __name__ == "__main__":
    main()
