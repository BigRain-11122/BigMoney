"""r1015 bm-b: resolve 5 UU files after stash-pop per r1028 ts-newer-wins law.

Context: S0 dirty-tree FF absorb (14 commits) + stash pop -> 5 UU on shared
state faces. Conflict labels: group(1)=Updated upstream (origin side),
group(2)=Stashed changes (local bm-b side). Winner = newer ts; tie or missing
ts on both sides -> upstream (origin is canon).
"""
import re, json, sys

FILES = [
    r"results\token_usage.json",
    r"results\watermark_red.json",
    r"results\lhb_update_status.json",
    r"results\futures_update_status.json",
    r"fleet\machine-health.json",
]

MARK = re.compile(r"<<<<<<<[^\n]*\n(.*?)\n?=======\n(.*?)\n?>>>>>>>[^\n]*", re.S)
TS = re.compile(r'"(?:ts|generated|updated_at|asof|timestamp)"\s*:\s*"([^"]+)"')


def ts_of(block):
    m = TS.search(block)
    return m.group(1) if m else None


def main():
    ok = True
    for p in FILES:
        raw = open(p, encoding="utf-8", errors="replace").read()
        hunks = 0
        while True:
            mm = MARK.search(raw)
            if not mm:
                break
            up, loc = mm.group(1), mm.group(2)
            tu, tl = ts_of(up), ts_of(loc)
            if tu and tl:
                winner = "upstream" if tu >= tl else "stashed"
            elif tu:
                winner = "upstream"
            elif tl:
                winner = "stashed"
            else:
                winner = "upstream"
            block = up if winner == "upstream" else loc
            raw = raw[: mm.start()] + block + raw[mm.end():]
            hunks += 1
        if hunks:
            try:
                json.loads(raw)
                open(p, "w", encoding="utf-8", newline="").write(raw)
                print(f"{p}: hunks={hunks} JSON_VALID resolved")
            except Exception as e:
                print(f"{p}: hunks={hunks} JSON_INVALID {e} NOT WRITTEN")
                ok = False
        else:
            print(f"{p}: NO_MARKERS (already clean)")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
