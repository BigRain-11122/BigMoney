"""r671 supply probe: newest fleet tickets + watchlist + G2 tail state."""
import json, glob, os
REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
w = open(r"C:\Users\sjs20\AppData\Local\Temp\r671_supply.txt", "w", encoding="utf-8")

# newest tickets by mtime
tk = sorted(glob.glob(REPO + r"\fleet\tasks\*.json"), key=os.path.getmtime, reverse=True)[:10]
w.write("== newest 10 tickets ==\n")
for f in tk:
    try:
        j = json.load(open(f, encoding="utf-8"))
        w.write(f"{j.get('id','?')} | {j.get('status','?')} | claimed_by={str(j.get('claimed_by','?'))[:60]} | title={str(j.get('title', j.get('subject','')))[:90]}\n")
    except Exception as e:
        w.write(f"{os.path.basename(f)} parse fail {e}\n")

# POTENTIAL_WATCHLIST
for p in (r"\knowledge\POTENTIAL_WATCHLIST.md", r"\firm\POTENTIAL_WATCHLIST.md", r"\research\POTENTIAL_WATCHLIST.md"):
    fp = REPO + p
    if os.path.exists(fp):
        w.write(f"\n== watchlist ({p}) tail ==\n")
        w.write("\n".join(open(fp, encoding="utf-8", errors="replace").read().splitlines()[-25:]) + "\n")
w.close()
print("written")
