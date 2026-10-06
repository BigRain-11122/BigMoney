# _r798bma_patch_machine_state.py -- bm-a v1.1 hardening: "ollama app" tray respawner
# must die in pause path (live-fire 23:10 residue race, O-20261006-2110 receipt evidence).
import io

P = r"C:\Users\sjs20\Desktop\FluxGroup\.codely-cli\machine-state.ps1"
s = io.open(P, encoding="utf-8").read()

KILL_OLD = ('    Get-Process ollama -ErrorAction SilentlyContinue | Stop-Process -Force\n'
            '    Get-Process llama-server -ErrorAction SilentlyContinue | Stop-Process -Force')
KILL_NEW = (KILL_OLD + '\n'
            '    Get-Process "ollama app" -ErrorAction SilentlyContinue | Stop-Process -Force'
            '  # bm-a v1.1: tray app respawns serve (live-fire 23:10 residue race)')
RES_OLD = '    $residue = Get-Process llama-server,ollama -ErrorAction SilentlyContinue'
RES_NEW = '    $residue = Get-Process llama-server,ollama,"ollama app" -ErrorAction SilentlyContinue'
LOOP_OLD = '        Get-Process llama-server,ollama -ErrorAction SilentlyContinue | Stop-Process -Force'
LOOP_NEW = '        Get-Process llama-server,ollama,"ollama app" -ErrorAction SilentlyContinue | Stop-Process -Force'

for old, new, tag in [(KILL_OLD, KILL_NEW, "kill"), (RES_OLD, RES_NEW, "residue"), (LOOP_OLD, LOOP_NEW, "loop")]:
    assert old in s, "anchor missing: " + tag
    s = s.replace(old, new)

io.open(P, "w", encoding="utf-8", newline="").write(s)
chk = io.open(P, encoding="utf-8").read()
print("patched bytes:", len(chk.encode("utf-8")), "| ollama-app kills:", chk.count('"ollama app"'))
