# R236 bm-a: state file round flip + heartbeat refresh (epoch int law
# R170/R178; clock_read ISO with UTC offset per T-04 F5).
import io
import json
import time
import datetime as dt

# ---- state-bm-a.json: text-level field updates (round_no +1) ----
SP = "state-bm-a.json"
b = open(SP, "rb").read()
t = b.decode("utf-8")
print("state CRLF:", b.count(b"\r\n"), "LF-only:",
      b.count(b"\n") - b.count(b"\r\n"))

now_iso = dt.datetime.now().astimezone().isoformat(timespec="seconds")
did = ("R236: T-72 s3 COMPLETE = ticket CLOSED (R236 amendment landed: "
       "refresh-repull done-reset re-pull semantics + terminal cutoff from "
       "panel bytes -- closes both R235-disclosed latent defects before "
       "~2026-10-27 first re-pull window; selftest S11 green, gate probe "
       "no-op mirror healthy) + s3 S6 wiring landed (update_sina_mf leg after "
       "update_moneyflow in iteration_prompt.txt, byte-precise single-line "
       "insert) + post_review registry row encoded + independent re-derive "
       "T-72 YES 5/5 -> three-state closed (legislated/verified/accepted)")
nxt = ("09-28 Mon new-bar full chain (sina_mf gate leg first bar-day face); "
       "10-01 month boundary trio (science_audit/monthly_briefing/"
       "self_review) + REGIME_GUARD v3 date gate; T-70 midterm verdict 10-09")

s2 = t
s2 = s2.replace('"round_no": 235', '"round_no": 236', 1) if '"round_no": 235' in s2 else s2.replace('"round_no": "235"', '"round_no": "236"', 1)
assert '"round_no": 236' in s2, "round_no flip failed"
s2 = s2.replace('"verdict": "GREEN"', '"verdict": "GREEN"', 1)
# did / next / ts / current_task updates (keys exist once each)
import re


def _swap(txt, key, newval):
    pat = re.compile(r'"' + key + r'": "[^"]*"')
    m = pat.search(txt)
    assert m, key
    return txt[:m.start()] + '"' + key + '": ' + json.dumps(newval, ensure_ascii=False) + txt[m.end():]


for k, v in (("did", did), ("next", nxt), ("ts", now_iso),
             ("updated_at", now_iso), ("current_task",
                                       "r236 done: T-72 closed (s3 wired + "
                                       "post_review YES 5/5); next=09-28 "
                                       "new-bar chain + 10-01 month trio")):
    s2 = _swap(s2, k, v)
open(SP, "wb").write(s2.encode("utf-8"))
d = json.load(open(SP, encoding="utf-8-sig"))
print("state round_no:", d["round_no"], "| verdict:", d["verdict"])

# ---- fleet/machines/bm-a.json heartbeat ----
HP = "fleet/machines/bm-a.json"
hb = json.load(open(HP, encoding="utf-8-sig"))
epoch = int(time.time())
hb["last_seen"] = now_iso[:19]
hb["heartbeat_epoch_utc"] = epoch          # MUST be JSON int (R170/R178)
hb["clock_read"] = now_iso
hb["current_task"] = ("r236 done: T-72 ticket closed (R236 amendment "
                      "refresh-repull done-reset + terminal cutoff from "
                      "panel bytes; s3 S6 wiring update_sina_mf leg landed; "
                      "post_review re-derive YES 5/5)")
hb["verdict"] = "GREEN"
hb["cpu_pct"] = 37.0
hb["round_no"] = 236
# preserve canonical key order + indent via json dump matching existing style
txt = json.dumps(hb, ensure_ascii=False, indent=2)
open(HP, "w", encoding="utf-8", newline="").write(txt + "\n")
back = json.load(open(HP, encoding="utf-8-sig"))
assert isinstance(back["heartbeat_epoch_utc"], int), "epoch must be int"
print("heartbeat epoch:", back["heartbeat_epoch_utc"],
      "isinstance int:", isinstance(back["heartbeat_epoch_utc"], int),
      "| last_seen:", back["last_seen"])
