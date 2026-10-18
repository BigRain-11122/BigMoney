# -*- coding: utf-8 -*-
# r1090: d19 selftest unpack-site fixer (upd->4-tuple, mkfix->6-tuple) + L18/L19/L20 legs.
import io, re, ast

P = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\scripts\d19_watermark.py"
t = io.open(P, encoding="utf-8").read()

fixes = [
    ("rc, sp, rec = upd(new_ev, advance=True, state=dict(base_state))",
     "rc, sp, rec, _hb = upd(new_ev, advance=True, state=dict(base_state))"),
    ("rc, sp, _ = upd(new_ev, advance=False,",
     "rc, sp, _, _hb = upd(new_ev, advance=False,"),
    ("rc, sp, _ = upd(new_ev, advance=True,",
     "rc, sp, _, _hb = upd(new_ev, advance=True,"),
    ('rc, sp, _ = upd({"decisions_sha": "a3ea37bd", "orders_sha": TRUE_ORD},',
     'rc, sp, _, _hb = upd({"decisions_sha": "a3ea37bd", "orders_sha": TRUE_ORD},'),
    ('rc, sp, _ = upd({"decisions_sha": "z" * 40, "orders_sha": TRUE_ORD},',
     'rc, sp, _, _hb = upd({"decisions_sha": "z" * 40, "orders_sha": TRUE_ORD},'),
    ('rc, sp, _ = upd({"err": "synthetic fault"}, advance=True,',
     'rc, sp, _, _hb = upd({"err": "synthetic fault"}, advance=True,'),
    ("mid, sp, pj, rec = mkfix(state=dict(base_state))",
     "mid, sp, pj, rec, _mj, _hb = mkfix(state=dict(base_state))"),
]
n = 0
for old, new in fixes:
    c = t.count(old)
    assert c >= 1, "fix-target missing: %r (count=%d)" % (old[:60], c)
    t = t.replace(old, new)
    n += c

# mkfix direct call sites with state={**base_state ...} (L10/L11/L14) -- two variants
pat = re.compile(r"mid, sp, pj, rec = mkfix\(state=\{\*\*base_state([^\n]*)\)\n")
t, k = pat.subn(lambda m: "mid, sp, pj, rec, _mj, _hb = mkfix(state={**base_state%s)\n" % m.group(1), t)
print("mkfix regex fixes:", k)

# L7's explicit-Namespace legs need machine_json for the (unreached) sync path -- add defensive attr
t = t.replace(
    """        o = argparse.Namespace(state=sp, probe_json=pj, receipt=rec,
                               advance=True, probe_evidence=pj)
        rc = cmd_update(o)""",
    """        o = argparse.Namespace(state=sp, probe_json=pj, receipt=rec,
                               advance=True, probe_evidence=pj,
                               machine_json=_mj, heartbeat=_hb)
        rc = cmd_update(o)""")

# append the three new legs before the fails-summary
NEW_LEGS = '''
    # L18/L19/L20 r1090 two-face law: heartbeat mirrors ride the same update,
    # read-back asserted; absent heartbeat = honest skip; zero fabrication
    def l18():
        rc, sp, rec, hb = upd(new_ev, advance=True, state=dict(base_state))
        assert rc == 0, "rc=%s" % rc
        h2 = _load_json(hb)
        assert h2["last_orders_sha"] == TRUE_ORD and h2["last_decisions_sha"] == TRUE_DEC, \\
            "heartbeat mirrors not synced"
        assert h2["extra_foreign_key"] == "keep-me", "foreign key must be preserved"
        r = _load_json(rec)
        assert r["heartbeat_sync"]["readback_ok"] is True
        assert r["heartbeat_sync"]["synced"]["last_orders_sha"]["to"] == TRUE_ORD
    leg("L18 heartbeat mirrors synced in same update + read-back (r1052 in-tool)", l18)

    def l19():
        rc, sp, rec, hb = upd(new_ev, advance=True, state=dict(base_state),
                              mkheartbeat=False)
        assert rc == 0, "absent heartbeat must not fault: rc=%s" % rc
        assert not os.path.isfile(hb)
        r = _load_json(rec)
        assert "skipped" in (r["heartbeat_sync"]["note"] or ""), \\
            "expected honest skip note, got %r" % r["heartbeat_sync"]
    leg("L19 absent heartbeat = honest skip (never a fault)", l19)

    def l20():
        st_min = {DEC_KEY: OLD_DEC, ORD_KEY: OLD_ORD, "round_no": 7,
                  "last_orders_read_at": "t0", "last_decisions_read_at": "t0",
                  "last_decisions_at": "t0"}  # NO last_orders_at/*_seen keys in state
        rc, sp, rec, hb = upd(new_ev, advance=True, state=st_min)
        assert rc == 0, "rc=%s" % rc
        h2 = _load_json(hb)
        assert h2["last_orders_seen"] == "stale", \\
            "keys absent from state must not be fabricated/overwritten in heartbeat"
        assert h2["last_orders_read_at"] == "t0", "present state keys must mirror"
        r = _load_json(rec)
        assert "last_orders_seen" not in r["heartbeat_sync"]["synced"], \\
            "absent-in-state key must not appear in synced map"
    leg("L20 zero fabrication: only state-present keys mirrored", l20)

'''
anchor = "    fails = [l for l in legs if not l[1]]"
assert anchor in t, "fails-summary anchor missing"
t = t.replace(anchor, NEW_LEGS + anchor)

io.open(P, "w", encoding="utf-8", newline="").write(t)
ast.parse(t)
print("total unpack fixes:", n, "| AST OK | bytes:", len(t.encode("utf-8")))
