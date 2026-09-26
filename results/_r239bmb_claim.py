import io

CLAIMS = [
    ("74", "takeover per O-1730: bm-a heartbeat stale 09:23:45 >20min at 10:05; bm-a plate full (T-76 CN-schools + T-70 C-arm supervision)"),
    ("75", "takeover per O-1730: bm-a heartbeat stale 09:23:45 >20min at 10:05; s1 script+first report+DECISIONS canon+wiring delivered same round"),
]

for tid, note in CLAIMS:
    p = "fleet/tasks/T-2026-09-26-%s-P1.json" % tid
    with io.open(p, "r", encoding="utf-8", newline="") as f:
        raw = f.read()
    eol = "\r\n" if "\r\n" in raw else "\n"
    anchor = ' "status": "open",'
    assert anchor in raw, "status anchor not found in " + p
    repl = (
        ' "status": "claimed",' + eol
        + ' "claimed_by": "bm-b (OS iteration loop, round 239; CEO immediate claim-and-start same round per O-1730 law; ' + note + ')",' + eol
        + ' "claimed_at": "2026-09-26 10:05",'
    )
    new = raw.replace(anchor, repl, 1)
    with io.open(p, "w", encoding="utf-8", newline="") as f:
        f.write(new)
    print(p, "claimed OK, eol=", repr(eol))
