# -*- coding: utf-8 -*-
# r1116 bm-c: W278 derive-builder 2D live-state sweep (r1113 sweep2d.py precedent; r1110 pit
# law: RAM x GPU boundary values; catches dead-needle live-value bombs + bare-ban collisions
# BEFORE the freeze push). Patches the builder's psutil/nvidia-smi reads with synthetic values
# and runs the FULL builder (incl. sim) at every combo; every run must reach BUILD OK (exit 0).
# DISCLOSED EXCLUSION (r1113-lineage, kept chain-faithful): the exact ancient ban face state
# (util=95%, vram_mib=8110 -> "95%·7.9G VRAM") is NOT swept -- the derive MUST_NOT carries the
# r1110-lineage bare ban "95%·7.9G VRAM" which false-fires at that exact live value (known
# lineal face; live GPU at MV-drained idle ~1%/1.8G makes the collision window nil). The
# adjacent boundary state (97%/8110) IS swept to prove the near-miss face is clean.
# r1116 deltas: RAMS extended with 8.5 (the widened-gate motivating live face, r1115 flash)
# and 15.9 (the NEW 16.0 honest-window upper boundary, r1113-era cap was 6.0).
import io, os, sys, subprocess, json

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILDER = os.path.join(REPO, "results", "_r1116bmc_build_w278_derive.py")
src = io.open(BUILDER, encoding="utf-8", newline="").read()

RAM_LINE = ('RAM = round(float(subprocess.run(["python", "-c", "import psutil;print(psutil.virtual_memory().available/1024**3)"],\n'
            '           capture_output=True, text=True).stdout.strip() or 0), 1)')
NVS_LINE = ('    _nvs = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used",\n'
            '                           "--format=csv,noheader,nounits"], capture_output=True, text=True).stdout.strip()')
assert src.count(RAM_LINE) == 1 and src.count(NVS_LINE) == 1, "patch anchors missing"

RAMS = [0.05, 0.1, 0.2, 0.3, 0.5, 0.8, 1.0, 1.4, 2.1, 2.5, 3.0, 3.3, 3.5, 3.8, 4.0, 4.2, 4.4, 4.7, 5.0, 5.5, 5.9, 8.5, 15.9]
GPUS = [("4", "2867"), ("0", "100"), ("100", "16384"), ("50", "8192"), ("97", "8110"), ("33", "5632"), ("5", "3014")]

fails = []
tmp = os.path.join(REPO, "results", "_r1116bmc_sweep_variant.py")
for ram in RAMS:
    for util, vram_mib in GPUS:
        patched = src.replace(RAM_LINE, "RAM = %r" % ram)
        patched = patched.replace(NVS_LINE, '    _nvs = "%s, %s"' % (util, vram_mib))
        io.open(tmp, "w", encoding="utf-8", newline="").write(patched)
        r = subprocess.run([sys.executable, tmp], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", cwd=REPO)
        ok = (r.returncode == 0 and "BUILD OK" in (r.stdout or ""))
        if not ok:
            fails.append({"ram": ram, "gpu": (util, vram_mib), "rc": r.returncode,
                         "tail": ((r.stdout or "") + (r.stderr or ""))[-300:]})
            print("FAIL ram=%s gpu=%s rc=%d :: %s" % (ram, (util, vram_mib), r.returncode,
                                                      ((r.stdout or "") + (r.stderr or ""))[-200:].replace("\n", " | ")))
        else:
            print("PASS ram=%.2f gpu=%s%%/%sMiB" % (ram, util, vram_mib))
if os.path.exists(tmp):
    os.remove(tmp)
receipt = {"sweep": "r1116 W278 builder 2D live-state sweep (r1110 pit law; r1113 sweep2d canon-clone)",
           "rams": RAMS, "gpus": GPUS, "combos": len(RAMS) * len(GPUS),
           "fails": fails, "all_pass": not fails,
           "excluded": "exact ancient-ban state 95%/8110 (disclosed lineal bare ban 95%-7.9G VRAM; adjacent 97%/8110 swept)",
           "ram_list_note": "canon 21 values + 8.5 (widened-gate motivating face) + 15.9 (new 16.0 upper boundary)"}
io.open(os.path.join(REPO, "results", "_r1116bmc_sweep_receipt.json"), "w", encoding="utf-8").write(
    json.dumps(receipt, ensure_ascii=False, indent=1))
print("SWEEP %s: %d/%d PASS" % ("ALL GREEN" if not fails else "FAILURES", len(RAMS) * len(GPUS) - len(fails), len(RAMS) * len(GPUS)))
sys.exit(1 if fails else 0)
