# r238 (bm-a): T-73 claim (CEO immediate ticket per O-20260926-0926, claim-
# and-start same round per O-1730). Text-level field updates, format mirror.
import io, json

p = "fleet/tasks/T-2026-09-26-73-P1.json"
t = io.open(p, encoding="utf-8", newline="").read()
assert '"status": "open"' in t, "status anchor missing"
assert "claimed_by" not in t, "claim fields already present"
anchor = ' "status": "open",\r\n'
assert anchor in t, repr(t[:200])

claim_by = (' "claimed_by": "bm-a (OS iteration loop, round 238; CEO immediate '
            'ticket per O-20260926-0926 + O-1730 claim-and-start same round; '
            's1/s2 web-facing research started same round, s3 portfolio-design '
            'chain follows; C-arm batch supervision on this machine runs in '
            'parallel -- different resource faces (network+writing vs local '
            'inference), zero conflict)",\r\n'
            ' "claimed_at": "2026-09-26T09:45:00+08:00",\r\n')
t2 = t.replace(anchor, anchor + claim_by, 1).replace(
    '"status": "open"', '"status": "claimed"', 1)
io.open(p, "w", encoding="utf-8", newline="").write(t2)
back = json.load(io.open(p, encoding="utf-8-sig"))
assert back["status"] == "claimed" and back["claimed_at"]
print("T-73 claimed by bm-a OK")
