# -*- coding: utf-8 -*-
# r1052 bm-c: jayredo refire6 HARVEST-PUSH (runner w1/w2 pushes FAILed network-window;
# clips local-complete 17/17; deadline 14:05 delivery-watch). Replicates the runner's
# exact w2+w2clips atomic-push spec (ord_row extracted from runner source via ast -- zero transcription).
import os, sys, json, time, ast, subprocess, urllib.request

BASE = r"K:\Fluxgroup\FluxGroup\cph4\fleet\mv0001-handover\outbound\krea2\kf-demo-20261012"
RUNNER = os.path.join(BASE, "jayredo_refire6_r1051.py")
GROUP = r"K:\Fluxgroup\FluxGroup"
ATOMIC = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\.codely-cli\scratch\git-atomic-push-bmc.py"
SPEC = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r1052bmc_jayredo_harvest_spec.json"
RECEIPT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r1052bmc_jayredo_harvest_receipt.json"

CLIPS = ["E01c_first_line.mp4", "SIL2_ots_crowd_v4_s9018.mp4", "SING1_torch_song_v2_s9013.mp4",
         "C01_carver_face.mp4", "B01_weary.mp4", "D01_carver_words.mp4"]

def rel(p):
    return "cph4/fleet/mv0001-handover/outbound/krea2/kf-demo-20261012/" + p

# --- extract ord_row template from runner source (ast; zero hand transcription) ---
src = open(RUNNER, encoding="utf-8").read()
tree = ast.parse(src)
ord_row = None
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id == "ord_row":
                ord_row = eval(compile(ast.Expression(node.value), "<ord_row>", "eval"),
                               {"time": time})
assert isinstance(ord_row, str) and ord_row.startswith("|"), "ord_row extract failed"

files = []
for n in CLIPS:
    files.append({"mode": "full", "path": rel("bmc/i2v/jayredo/" + n),
                  "local": os.path.join(BASE, "bmc", "i2v", "jayredo", n), "expect_origin_blob": "NEW"})
files.append({"mode": "full", "path": rel("bmc/JAY-REDO-QC-SHEET-17-r1051.jpg"),
              "local": os.path.join(BASE, "bmc", "JAY-REDO-QC-SHEET-17-r1051.jpg"), "expect_origin_blob": "NEW"})
files.append({"mode": "full", "path": rel("bmc/jayredo_refire6_r1051_receipt.json"),
              "local": os.path.join(BASE, "bmc", "jayredo_refire6_r1051_receipt.json"), "expect_origin_blob": "NEW"})
files.append({"mode": "full", "path": rel("jayredo_refire6_r1051.py"),
              "local": RUNNER, "expect_origin_blob": "NEW"})
files.append({"mode": "append", "path": "docs/orders.md", "line": ord_row})

spec = {"message": "bm-c r1051-harvest(r1052): jayredo 6 winner-slot i2v refire complete, 17/17 delivered + QC sheet (verdict r1033, INT8 768P audio-stripped) -- runner w1/w2 pushes FAILed in network window, clips local-complete, harvest-push executed by r1052 closeout",
        "retry": 5, "gate_depth": 10, "files": files}
json.dump(spec, open(SPEC, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("spec built: %d files (%d full + 1 append)" % (len(files), len(files) - 1))

r = subprocess.run([sys.executable, ATOMIC, SPEC], capture_output=True, cwd=GROUP, timeout=1200)
out = (r.stdout + b"\n" + r.stderr).decode("utf-8", "replace")
print(out[-2000:])
ok = r.returncode == 0

receipt = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "window": "r1052", "push_ok": ok, "rc": r.returncode}
if ok:
    body = json.dumps({"reason": "jayredo 17/17 clips + QC sheet + receipt on origin (bm-c r1051 harvest by r1052 window), assembly station GO", "tasks": []}).encode()
    req = urllib.request.Request("http://100.110.185.62:8790/poke", data=body,
                                 headers={"Content-Type": "application/json"})
    try:
        resp = json.loads(urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace"))
        receipt["poke_bma"] = resp
        print("poke bm-a OK:", resp)
    except Exception as ex:
        receipt["poke_bma"] = {"ok": False, "err": repr(ex)}
        print("poke bm-a FAIL:", repr(ex))
json.dump(receipt, open(RECEIPT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("HARVEST", "OK" if ok else "FAIL")
