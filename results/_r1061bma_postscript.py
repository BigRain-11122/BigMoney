# -*- coding: utf-8 -*-
# r1061 postscript: delivery self-verify + push_verified/sync write-back + pit-nuance note
import json, time
from datetime import datetime, timezone, timedelta

CST = timezone(timedelta(hours=8))
now_iso = datetime.now(CST).isoformat(timespec="seconds")
epoch = int(time.time())

pv = {
    "ts": now_iso,
    "origin_tip": "dc67ead077",
    "ahead_behind": "0/0",
    "note": ("r1061 push delivered after three-round race handling: (1) first push rejected (bm-b r1008+postscript "
             "landed mid-window) -> rebase 19 UU regen faces resolved newer-wins ALL-mine (my S6 chain 16:50-16:52 "
             "vs bm-b base 16:30-16:32, token combined face = superset by construction); (2) rebase --continue "
             "ghost-refusal deadloop x2 (r1048/r1008 family) -> r1032 law quit + commit -C straight-through "
             "dc67ead077; (3) push still rejected -> root-cause: commit -C landed on DETACHED HEAD (rebase --quit "
             "leaves HEAD at base; main stayed at old-base original 6f7e68bfd4 -> push pushed stale-base ref = "
             "phantom race) -> reflog-checked (zero foreign writers) -> update-ref main dc67ead077 + push "
             "a56df48331..dc67ead077 delivered; local-unpushed=0; group-repo ruling a695c06 delivered earlier "
             "first-try; orphaned twin 6f7e68bfd4 = same-message pre-rebase original, harmless")
}

sp = "state-bm-a.json"
with open(sp, "r", encoding="utf-8") as f:
    st = json.load(f)
st["push_verified"] = pv
st["sync"] = dict(pv)
st["last_delivery_verified_at"] = now_iso
st["heartbeat_epoch_utc"] = epoch
st["heartbeat_epoch_utc_type_int"] = True
prev_note = st.get("notes_r1061", "")
st["notes_r1061"] = prev_note + ("; (5) postscript pit-nuance (r1032-family extension): `git rebase --quit` leaves "
                                 "HEAD DETACHED at the base -- a follow-up `git commit -C <sha>` builds the rebuilt "
                                 "commit on detached HEAD while main still points at the PRE-rebase original; "
                                 "`git push origin main` then pushes the stale-base ref and looks like a repeated "
                                 "non-FF race. Pre-push assertion after any quit+commit sequence: `git rev-parse "
                                 "main HEAD` must be EQUAL and `git rev-list --count origin/main..main` must match "
                                 "the rebuilt-commit count; if diverged -> reflog main check -> update-ref main "
                                 "<rebuilt> -> push. Live-fire: this window 3 wasted push rounds on phantom race.")
st["ts"] = now_iso
st["updated"] = now_iso
st["updated_at"] = now_iso
st["last_seen"] = now_iso
st["clock_read"] = now_iso
with open(sp, "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
    f.write("\n")

# heartbeat mirror touch (epoch + ts only, mirrors synced)
hp = "fleet/machines/bm-a.json"
with open(hp, "r", encoding="utf-8") as f:
    hb = json.load(f)
hb["heartbeat_epoch_utc"] = epoch
hb["heartbeat_epoch_utc_type_int"] = True
hb["last_heartbeat_epoch_utc"] = st.get("last_heartbeat_epoch_utc", epoch - 60)
hb["ts"] = now_iso
hb["clock_read"] = now_iso
hb["updated"] = now_iso
hb["updated_at"] = now_iso
hb["last_seen"] = now_iso
hb["sync"] = {"ts": now_iso, "origin_tip": "dc67ead077", "ahead_behind": "0/0",
              "note": "r1061 push delivered dc67ead077 (postscript mirror)"}
with open(hp, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write("\n")

for p in (sp, hp):
    with open(p, "r", encoding="utf-8") as f:
        d = json.load(f)
    e = d.get("heartbeat_epoch_utc")
    assert isinstance(e, int) and not isinstance(e, bool), p + " epoch must be JSON int"
print("POSTSCRIPT_OK", now_iso, "epoch", epoch)
