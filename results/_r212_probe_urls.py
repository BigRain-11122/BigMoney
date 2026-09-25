import io, re, sys
sys.stdout.reconfigure(encoding="utf-8")
pat = re.compile(r"https?://[^\s'\"\)]+")
for f in ["scripts/update_moneyflow.py", "scripts/ah_panel_puller.py"]:
    txt = io.open(f, encoding="utf-8").read()
    urls = sorted(set(pat.findall(txt)))
    print(f, "->")
    for u in urls[:10]:
        print("   ", u)
