import io

p = 'smoke_test.py'
s = io.open(p, encoding='utf-8', newline='').read()
i = s.index('<<<<<<< HEAD')
j = s.index('>>>>>>> 7d7904d161')
end = s.index('\n', j) + 1
block = s[i:end]
head = block.split('||||||| parent of')[0]
head = head[len('<<<<<<< HEAD\n'):]
extra = '''    # D-20261028-02's other half: the reader can classify, but the PANEL is what a
    # person reads. Assert the face's own verdict reached the payload (a row count
    # cannot tell "three calm machines" from "one readable row and two missing"),
    # and that the gate rides the chain instead of living in a hand run.
    try:
        _bs = json.load(open("results/dashboard_status.json", encoding="utf-8"))
        _fl = ((_bs.get("data") or {}).get("engine")) or {}
        _hf = _fl.get("health_face") or {}
        check("fleet: panel carries the machine-health verdict, not a row count",
              _hf.get("health_face") in ("ok", "legacy_list")
              and _hf.get("health_unknown") is False,
              "face=%s unknown=%s junk=%s" % (_hf.get("health_face"),
                                              _hf.get("health_unknown"),
                                              _hf.get("health_face_junk")))
        _legs = {n for n, _c in importlib.import_module("Tools.s6_chain_bmc").LEGS}
        check("fleet: machine-health gate leg wired into the S6 chain",
              "machine_health_face" in _legs, f"legs={len(_legs)}")
    except Exception as e:
        check("fleet: panel carries the machine-health verdict, not a row count",
              False, str(e))
        check("fleet: machine-health gate leg wired into the S6 chain", False, str(e))
'''
s = s[:i] + head + extra + s[end:]
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('markers left:', s.count('<<<<<<<'), s.count('>>>>>>>'))