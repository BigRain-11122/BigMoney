import json, datetime as dt

P = "logs/iteration-loop/state.json"
s = json.load(open(P, encoding="utf-8-sig"))
now = dt.datetime.now().astimezone().isoformat(timespec="seconds")
s["round_no"] = 270
s["did"] = ("r270: post_review sha-anchor machine-face oscillation P0 fixed (producers EOL-normalize x4 sites + "
            "criteria 4 anchors re-encoded LF canonical, reviewer 28 YES/0 NO); T-76 face (a) channels weekly "
            "machine-diff delivered = wave-10 five-face closure")
s["verdict"] = "green"
s["next"] = ("r271: 09-28 Monday window (T-76 channels run-6/10/4 + jin-gong 260928 verify + T-78 GRID marks); "
             "MF_IC gate on EM panel self-heal; 10-01 month-first trio")
s["last_round_ts"] = now
s["last_result"] = "ok"
s["current_task"] = ("r270 done: sha-oscillation P0 + T-76 face (a) closure; next: Monday-window standing "
                     "channels + marks on new bar")
s["last_tick"] = now[11:16]
s["updated_at"] = now
s["last_seen"] = now[:19]
json.dump(s, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("state round_no ->", s["round_no"], "| ts:", now)
