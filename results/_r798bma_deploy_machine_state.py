# _r798bma_deploy_machine_state.py -- O-20261006-2110 §1-2 kit deployment for bm-a
# Reads machine-state.template.ps1 from origin/main blob (fresh-read law), localizes
# the three ##LOCALIZE blocks per bm-a self-audit, writes machine-state.ps1.
import os, subprocess

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup"
CLI = os.path.join(ROOT, ".codely-cli")

tpl_b = subprocess.run(
    ["git", "-C", ROOT, "show", "origin/main:cph4/fleet/machine-state-kit/machine-state.template.ps1"],
    capture_output=True, check=True).stdout
tpl = tpl_b.decode("utf-8")

old1 = '$tasks = @("<LOCALIZE: your GPU production task names>")'
old2 = ('$ollamaExe = "<LOCALIZE: ollama.exe full path>"\n'
        '$pinModel  = "<LOCALIZE: resident model, e.g. qwen3-8b / qwen3.8:4b>"\n'
        '$keepAliveTask = "<LOCALIZE: ComfyUI/keepalive task name>"')
assert old1 in tpl and old2 in tpl, "LOCALIZE anchors missing"

loc1 = ('$tasks = @("BigCompute-OSLoop","BigCompute-OSLoop-PM","BigCompute-GPU-IdleWatch",'
        '"BigCompute-CleanWindowProbe","BigCompute-OrderSentinel","BigCompute-ResidentQA",'
        '"MiniGameOllamaKeepWarm","MiniGameOllamaServe")')
loc2 = ('$ollamaExe = "C:\\Users\\sjs20\\AppData\\Local\\Programs\\Ollama\\ollama.exe"\n'
        '$pinModel  = "qwen3-8b-ud:q4_k_xl" # O-20261006-2110 bm-a=qwen3-8b; installed face qwen3-8b-ud:q4_k_xl (resident at deploy time = legacy qwen2.5:7b-instruct, honest note in receipt)\n'
        '$keepAliveTask = $null # no ComfyUI/keepalive task on bm-a (honest declaration)')

n = tpl.replace(old1, loc1).replace(old2, loc2)
n = n.replace(
    "# machine-state.template.ps1 - CEO 用机让路律 single-machine switch (fleet kit template)",
    "# machine-state.ps1 - CEO 用机让路律 bm-a deployed switch (fleet kit, O-20261006-2110, receipt r798)")

out = os.path.join(CLI, "machine-state.ps1")
with open(out, "w", encoding="utf-8", newline="") as f:
    f.write(n)

# cleanup the bytes-temp written earlier by S0 deploy step
tmp = os.path.join(CLI, "gamewin_cron_suspend.py-template-raw")
if os.path.exists(tmp):
    os.remove(tmp)

print("localized ps1 bytes:", len(n.encode("utf-8")))
print("LOCALIZE residue:", n.count("<LOCALIZE"))
print("py deployed:", os.path.exists(os.path.join(CLI, "gamewin_cron_suspend.py")))
