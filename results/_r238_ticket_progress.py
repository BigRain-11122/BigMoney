# r238 (bm-a): T-70 ticket progress_r238 text-level insertion (r230 law:
# byte-anchored minimal diff, format preserved; PS quoting trap -> file face).
import io, json

p = "fleet/tasks/T-2026-09-26-70-P0.json"
t = io.open(p, encoding="utf-8", newline="").read()
assert t.count("progress_r238") == 0, "already inserted"
assert t.endswith("loop)\"\r\n}"), repr(t[-40:])

field = ('  "progress_r238": "C-arm (local+self-fix loop<=3) instruction '
         'received mid-round via MSG-20260926-0925-bm-a (bm-c session, CEO '
         'order continuation O-20260925-2313); claim-and-start same round '
         'per CEO immediate law: prereg research/R-20260926-bma-pilot-C-arm.md '
         'FROZEN in commit 8fd9c836 BEFORE any C run (interpretation lines '
         'transcribed verbatim from MSG, zero re-derivation; batch-1 A/B '
         'faces untouched append-only); runner scripts/pilot_c_client.py '
         '(self-fix loop, B-transport imported not reimplemented, 7-assert '
         'offline selftest green) + orchestrator scripts/pilot_c_batch.py '
         '(sequential 01-10 checkpoint-resume, ledger append arm=C_selffix '
         'rows, status mirror C_batch_status.json); detached batch spawned '
         'pid 61908 @09:3x, RAM gate 48.3GB>30GB passed, board clear/pool 0 '
         'weekend yield-face idle; supervision next rounds via mirror + '
         'C_batch.log"')

t2 = t[:-3] + ",\r\n" + field + "\r\n}"
io.open(p, "w", encoding="utf-8", newline="").write(t2)
back = json.load(io.open(p, encoding="utf-8-sig"))
assert "progress_r238" in back and "progress_r208" in back
print("ticket updated OK, fields:", len(back))
