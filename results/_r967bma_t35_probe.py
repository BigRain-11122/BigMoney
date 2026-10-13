# r967: DROUGHT-CE-01 512400 marks timeline (entry-day fill vs today's watch)
import json, os

d = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\results\paper\marks"
for day in ("20261009", "20261012", "20261013"):
    p = os.path.join(d, f"marks-{day}.jsonl")
    if not os.path.exists(p):
        print(day, "MISSING"); continue
    n_pw_512400 = 0
    first_pw = None
    pos_512400_seen = None
    for line in open(p, encoding="utf-8"):
        try:
            t = json.loads(line)
        except Exception:
            continue
        tr = (t.get("traders") or {}).get("DROUGHT-CE-01")
        if not tr:
            continue
        pw = tr.get("pending_watch") or {}
        if "512400" in pw:
            n_pw_512400 += 1
            if first_pw is None:
                first_pw = (t.get("ts"), pw["512400"])
        for pos in tr.get("positions", []):
            if pos.get("symbol") == "512400":
                if pos_512400_seen is None:
                    pos_512400_seen = (t.get("ts"), pos.get("cost_price"), pos.get("session_open"), pos.get("marked"))
    print(f"== {day}: pw_512400_ticks={n_pw_512400} first_pw={first_pw} first_pos={pos_512400_seen}")

# paper state hold days / entry context
st = json.load(open(r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\results\paper\DROUGHT-CE-01_paper.json", encoding="utf-8"))
print("state cutoff:", st.get("cutoff"), "updated:", st.get("updated"))
for p in st.get("open_positions", []):
    if p.get("symbol") == "512400":
        print("state pos:", json.dumps(p, ensure_ascii=False))
