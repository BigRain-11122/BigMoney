"""r899: template candidate test -- find the f-string form rendering '"bm-c"}, \\'."""
W210 = {"engine_owner": "bm-c"}

candidates = [
    ("B format", lambda: '                                    "engine_owner": "{}"}}, \\'.format(W210.get("engine_owner"))),
]
target = '"bm-c"}, \\'
for name, fn in candidates:
    try:
        out = fn()
        ok = out.endswith(target)
        print(f"{name}: {out!r} -> {'OK' if ok else 'FAIL'}")
    except Exception as e:
        print(f"{name}: EXC {type(e).__name__}: {e}")
