# r531 bm-b: append W40 segment to the selftest PASS prose (r530 convention).
from pathlib import Path

def patch(path, old, new):
    p = Path(path)
    data = p.read_bytes().decode("utf-8")
    old = old.replace("\r\n", "\n")
    new = new.replace("\r\n", "\n")
    assert data.count(old) == 1, f"anchor not unique in {path} (count={data.count(old)})"
    p.write_bytes(data.replace(old, new).encode("utf-8"))
    print(f"patched {path}")

patch(
    r"scripts/perpetual_faces_n1.py",
    '''after W38's claim), r342 bm-c] "
          "+ T-141 s2 "
          "engine-lane claim exemption [law sec.2 pre-claim exempt "
          "face])")''',
    '''after W38's claim), r342 bm-c] "
          "+ W40 materializer face [same guard set, dep=W17..W38 ALL "
          "present (W38 finalize bm-b r530 K=81,520, ledger 446,140 "
          "chain-linear; W39 bm-c burned-12/12 finalize-pending "
          "two-state dep -- finalize runtime FAIL-CLOSED composes "
          "every registry key below 40), BOTH tails arithmetic "
          "continuation clean per law sec.4 W40 row 123_004..125_003 / "
          "43_201..43_400 (W39 row W40+ WARNING projection verified "
          "machine-side, zero skip both sides, ADMIT receipt "
          "results/_r531bmb_w40_band_gate.py), THIRTIETH "
          "ENGINE-OWNED WAVE engine_owner=bm-b per engine de-throttle "
          "law O-20261001-2355 sec.2 own-continuous-series (zero-gap "
          "relay after the W38 full closeout, wave 40 = first free "
          "number after bm-c's W39 claim), r531 bm-b] "
          "+ T-141 s2 "
          "engine-lane claim exemption [law sec.2 pre-claim exempt "
          "face])")''')
print("selftest W40 prose segment appended")
