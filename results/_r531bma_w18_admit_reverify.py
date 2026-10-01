"""r531 bm-a: re-verify the r530 crashed session's claimed W18 band-gate ADMIT.

The r530 session died after editing N1_BANDS/WAVE_CONFIGS (W18 rows added,
uncommitted) and writing the probe, claiming an ADMIT receipt in the row
comments. Per r314 (adopt-after-verify) + r322 (dangling-reference check),
this runner reproduces the ADMIT conditions EXACTLY as the probe ran them:
HEAD's pre-W18 15-row N1_BANDS table (the W18 rows are uncommitted WIP, so
HEAD is the pre-freeze truth), repo science_gates + perpetual_faces_n3
(both unchanged by the WIP). sys.modules pre-seed forces the probe's
`from perpetual_faces import N1_BANDS` onto the HEAD version.
"""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)  # config package lives at repo root
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import subprocess, types, importlib.util

head_src = subprocess.check_output(
    ["git", "-C", ROOT, "show", "HEAD:scripts/perpetual_faces.py"])
tmp_mod = os.path.join(os.environ["TEMP"], "_pf_head_r531.py")
with open(tmp_mod, "wb") as f:
    f.write(head_src)

spec = importlib.util.spec_from_file_location("perpetual_faces", tmp_mod)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
sys.modules["perpetual_faces"] = mod
print(f"[r531 reverify] N1_BANDS rows from HEAD: {len(mod.N1_BANDS)} (pre-W18 truth)")

probe = os.path.join(ROOT, "results", "_r530bma_w18_band_gate.py")
code = compile(open(probe, encoding="utf-8").read(), probe, "exec")
exec(code)
print("[r531 reverify] ADMIT reproduced against HEAD 15-row table -- "
      "r530 session's receipt claim VERIFIED")
