"""bm-c saturation-engine entry point -- a shim onto the single real engine.

Why this file is 20 lines and not 1,200: two generations of this engine were both
callable, and they keep their state in two different files.  The generation that
the scheduled task actually runs lives in `scripts/saturation_engine.py` and writes
`results/saturation_engine/state_bm-c.json` (it ticks every minute).  This older
copy under `Tools/` reads and writes `state/saturation_engine_state.bm-c.json`,
which stopped being written on 2026-11-11 -- so `python Tools/saturation_engine.py
status` spent nine days reporting a heartbeat of ~750,000 seconds while the engine
was alive and burning nothing.

Two readers of one engine must not be able to disagree.  The old body is preserved
in git history (`git log -- Tools/saturation_engine.py`) and in
`results/_r883bmc_sync_backup/`; nothing here re-implements it, this delegates.
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REAL = os.path.join(os.path.dirname(HERE), "scripts", "saturation_engine.py")

_spec = importlib.util.spec_from_file_location("saturation_engine_real", REAL)
if _spec is None or _spec.loader is None:
    raise SystemExit("FATAL: cannot load the real engine at %s" % REAL)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["saturation_engine_real"] = _mod
_spec.loader.exec_module(_mod)

if __name__ == "__main__":
    sys.exit(_mod.main())
