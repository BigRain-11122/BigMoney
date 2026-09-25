import io, sys
sys.stdout.reconfigure(encoding="utf-8")
lines = io.open("logs/moneyflow_refresh.log", encoding="utf-8", errors="replace").read().splitlines()
print("total log lines:", len(lines))
print("--- head 15:")
for l in lines[:15]: print(" ", l[:180])
print("--- rank-related lines (all):")
for l in lines:
    if "rank" in l.lower():
        print(" ", l[:180])
