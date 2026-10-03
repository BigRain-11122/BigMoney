import io, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

for p in ("results/regime_state.json", "results/token_usage.json", "results/update_status.json"):
    t = io.open(p, encoding="utf-8", errors="replace").read()
    hunks = re.findall(r"<<<<<<< HEAD\r?\n(.*?)\r?\n=======\r?\n(.*?)\r?\n>>>>>>> origin/main", t, re.S)
    print("==", p, "hunks:", len(hunks))
    for o, b in hunks[:3]:
        print("  OURS   :", " ".join(o.strip().split())[:170])
        print("  THEIRS :", " ".join(b.strip().split())[:170])
        for side, txt in (("ours", o), ("theirs", b)):
            m = re.search(r'"ts"\s*:\s*"([^"]+)"', txt)
            if m:
                print("   ", side, "ts=", m.group(1))
