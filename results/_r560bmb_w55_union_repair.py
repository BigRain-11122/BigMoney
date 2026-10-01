# -*- coding: utf-8 -*-
"""r560 bm-b: W55 registration union repair (r519-family 6th occurrence cure).

bm-a r559 W54 freeze commit bdc36af9e positionally anchored its canon/script
inserts at the "after W53 row" position, which since the bm-b r559 freeze
(c2a72a755, 2 min earlier) held bm-b's REGISTERED W55 rows -> 1:1 replacement
clobber across 5 faces:
  1. research/PERPETUAL_FACES.md       W55 canon row
  2. scripts/perpetual_faces.py        N1_BANDS[55]
  3. scripts/perpetual_faces_n1.py     WAVE_CONFIGS[55]
  4. scripts/perpetual_faces_n1.py     selftest W55 materializer leg
  5. scripts/perpetual_faces_n1.py     selftest summary print segment

Cure (r519 holding-commit route + r531 union + r307 two-state upgrade):
  - extract bm-b W55 content verbatim from holding commit c2a72a755
  - re-insert AFTER bm-a's legitimate W54 content (both waves coexist,
    band-disjoint per r531)
  - two-state upgrades (W54 registered since the freeze):
      a. prior-wave-set assertion list appends 54
      b. pinned declared-band constants gain registered-row parity assert
      c. prior-wave disjointness loops append 54
Byte-safe LF splicing only (r530 law). Idempotent: refuses if W55 face already
present (re-run after repair = no-op honest exit).
"""
import subprocess
import sys

HOLD = "c2a72a755"  # bm-b r559 W55 freeze commit (the holding commit)

FILES = {
    "canon": "research/PERPETUAL_FACES.md",
    "pf": "scripts/perpetual_faces.py",
    "n1": "scripts/perpetual_faces_n1.py",
}


def blob_bytes(path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{HOLD}:{path}"])


def die(msg: str) -> None:
    print(f"REPAIR-FAIL: {msg}")
    sys.exit(1)


def must_count(hay: bytes, needle: bytes, n: int, what: str) -> None:
    c = hay.count(needle)
    if c != n:
        die(f"{what}: expected {n} occurrence(s) of needle, found {c}")


def main() -> int:
    # ---------- 1. canon md row ----------
    cur = open(FILES["canon"], "rb").read()
    if "N1 波55".encode("utf-8") in cur:
        print("canon: W55 row already present (idempotent skip)")
    else:
        mine = blob_bytes(FILES["canon"])
        s = mine.find("- N1 波55".encode("utf-8"))
        if s < 0:
            die("holding commit lacks W55 canon row")
        e = mine.find(b"\n", s)
        row = mine[s:e]  # the W55 row line, no trailing newline
        if b"A-ext seed=153_004..155_003" not in row:
            die("canon row lacks A band declaration")
        if b"47_001..47_200" not in row:
            die("canon row lacks B band declaration")
        # current anchor: end of the bm-a W54 row line
        a54 = cur.find("- N1 波54".encode("utf-8"))
        if a54 < 0:
            die("current canon lacks W54 row (unexpected base)")
        e54 = cur.find(b"\n", a54)
        if cur[e54 + 1:e54 + 2] != b"\n":
            die("canon W54 row not followed by blank line")
        ins = e54 + 1  # position right after W54 row's newline
        cur = cur[:ins] + b"\n" + row + cur[ins:]
        open(FILES["canon"], "wb").write(cur)
        print("canon: W55 row restored after W54 row")

    # ---------- 2. pf.py N1_BANDS[55] ----------
    cur = open(FILES["pf"], "rb").read()
    if b"55: {\"a\": (153_004, 155_003)" in cur:
        print("pf: N1_BANDS[55] already present (idempotent skip)")
    else:
        mine = blob_bytes(FILES["pf"])
        s = mine.find(b"    # r559 bm-b freeze: wave 55 = first FREE number after the registered\n")
        if s < 0:
            die("holding commit lacks pf W55 comment block")
        e = mine.find(b"         \"engine_owner\": \"bm-b\"},\n", s)
        if e < 0:
            die("holding commit lacks pf W55 entry end")
        e += len(b"         \"engine_owner\": \"bm-b\"},\n")
        block = mine[s:e]
        must_count(block, b"153_004", 1, "pf block A")
        must_count(block, b"47_001", 1, "pf block B")
        anchor = b"    54: {\"a\": (151_004, 153_003), \"b_exit\": (46_601, 46_800),\n         \"engine_owner\": \"bm-a\"},\n}"
        must_count(cur, anchor, 1, "pf current W54 entry + dict close")
        cur = cur.replace(anchor, anchor[:-1] + b"\n" + block + b"}")
        open(FILES["pf"], "wb").write(cur)
        print("pf: N1_BANDS[55] restored after 54")

    # ---------- 3. n1.py WAVE_CONFIGS[55] ----------
    cur = open(FILES["n1"], "rb").read()
    if b"55: {\"batch\": \"PERPETUAL-N1-W55\"" in cur:
        print("n1: WAVE_CONFIGS[55] already present (idempotent skip)")
    else:
        mine = blob_bytes(FILES["n1"])
        s = mine.find(b"                       # FORTY-FOURTH ENGINE-OWNED WAVE (r559 bm-b freeze):\n")
        if s < 0:
            die("holding commit lacks n1 WAVE_CONFIGS W55 comment")
        e = mine.find(b"                            \"engine_owner\": \"bm-b\"},\n", s)
        if e < 0:
            die("holding commit lacks n1 WAVE_CONFIGS W55 entry end")
        e += len(b"                            \"engine_owner\": \"bm-b\"},\n")
        block = mine[s:e]
        must_count(block, b"n1_w55", 2, "n1 entry shard paths")
        anchor = b"                       }\nPREREG = WAVE_CONFIGS[2][\"prereg\"]"
        must_count(cur, anchor, 1, "n1 WAVE_CONFIGS close + PREREG")
        cur = cur.replace(
            anchor,
            block + b"                       }\nPREREG = WAVE_CONFIGS[2][\"prereg\"]",
        )
        open(FILES["n1"], "wb").write(cur)
        print("n1: WAVE_CONFIGS[55] restored after 54")

    # ---------- 4. n1.py selftest W55 materializer leg (two-state upgraded) ----------
    cur = open(FILES["n1"], "rb").read()
    if b"# --- W55 materializer face" in cur:
        print("n1: W55 materializer leg already present (idempotent skip)")
    else:
        mine = blob_bytes(FILES["n1"])
        s = mine.find(b"    # --- W55 materializer face (r559 bm-b freeze, own-series law\n")
        if s < 0:
            die("holding commit lacks W55 materializer leg")
        fin = b"    finally:\n        _set_wave(2)\n"
        e = mine.find(fin, s)
        if e < 0:
            die("holding commit lacks W55 leg finally")
        e += len(fin)
        leg = mine[s:e]

        # r307 two-state upgrade 1: prior-wave-set assertion appends 54
        old_list = b"             50, 51, 52, 53], \\"
        new_list = b"             50, 51, 52, 53, 54], \\"
        must_count(leg, old_list, 1, "leg set-assertion list")
        leg = leg.replace(old_list, new_list)
        old_msg = (b"            \"incl. 48..53; W54 declared-unregistered honest note)\"")
        new_msg = (b"            \"incl. 48..54; W54 registered by bm-a r559 at the pinned \" \\\n"
                   b"            \"declared bands -- r307 two-state parity)\"")
        must_count(leg, old_msg, 1, "leg set-assertion message")
        leg = leg.replace(old_msg, new_msg)

        # r307 two-state upgrade 2: pinned-declared comment + parity assert
        old_cmt = (b"        # here because W54 is NOT registered at this freeze; if bm-a\n"
                   b"        # registers W54 later, the registered row must equal these.\n")
        new_cmt = (b"        # here because W54 was declared-but-unregistered at this\n"
                   b"        # freeze; W54 has since been REGISTERED by bm-a r559 -- the\n"
                   b"        # registered row must equal these pinned bands (r307).\n")
        must_count(leg, old_cmt, 1, "leg pinned-declared comment")
        leg = leg.replace(old_cmt, new_cmt)
        old_pin = b"        w54_decl_b = set(range(46_601, 46_801))\n"
        new_pin = (b"        w54_decl_b = set(range(46_601, 46_801))\n"
                   b"        assert pf.N1_BANDS[54] == {\"a\": (151_004, 153_003),\n"
                   b"                                   \"b_exit\": (46_601, 46_800),\n"
                   b"                                   \"engine_owner\": \"bm-a\"}, \\\n"
                   b"            \"registered W54 row != pinned declared bands (r307 two-state)\"\n")
        must_count(leg, old_pin, 1, "leg pinned-declared constants")
        leg = leg.replace(old_pin, new_pin)

        # r307 two-state upgrade 3: prior-wave loops append 54 (2 sites:
        # band disjointness loop + shard-dir collision loop)
        old_lp = b"                      44, 45, 46, 47, 48, 49, 50, 51, 52, 53):"
        new_lp = b"                      44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54):"
        must_count(leg, old_lp, 2, "leg prior-wave loops (2 sites)")
        leg = leg.replace(old_lp, new_lp)

        anchor = b"\n    # --- T-141 s2 lane face"
        must_count(cur, anchor, 1, "n1 T-141 s2 marker")
        ins_at = cur.find(anchor)
        cur = cur[:ins_at] + b"\n" + leg + cur[ins_at:]
        open(FILES["n1"], "wb").write(cur)
        print("n1: W55 materializer leg restored (r307 two-state upgraded)")

    # ---------- 5. n1.py selftest summary print segment ----------
    cur = open(FILES["n1"], "rb").read()
    if b"+ W55 materializer face [same guard set" in cur:
        print("n1: W55 summary segment already present (idempotent skip)")
    else:
        mine = blob_bytes(FILES["n1"])
        s = mine.find(b"          \"+ W55 materializer face [same guard set + bm-a-declared-W54 \"\n")
        if s < 0:
            die("holding commit lacks W55 summary segment")
        e = mine.find(b"          \"law sec.4 W55 row, r559 bm-b] \"\n", s)
        if e < 0:
            die("holding commit lacks W55 summary end")
        e += len(b"          \"law sec.4 W55 row, r559 bm-b] \"\n")
        seg = mine[s:e]
        # r307 two-state note in the freeze-window prose
        old_prose = (b"          \"declared-unregistered at freeze window -- two in-flight \"\n")
        new_prose = (b"          \"declared at freeze window then REGISTERED r559 at the \"\n"
                     b"          \"pinned bands (r307 two-state parity) -- two in-flight \"\n")
        must_count(seg, old_prose, 1, "summary freeze-window prose")
        seg = seg.replace(old_prose, new_prose)
        anchor = b"          \"+ T-141 s2 \""
        must_count(cur, anchor, 1, "n1 summary T-141 marker")
        cur = cur.replace(anchor, seg + anchor)
        open(FILES["n1"], "wb").write(cur)
        print("n1: W55 summary segment restored")

    print("REPAIR-OK: all five faces union-restored")
    return 0


if __name__ == "__main__":
    sys.exit(main())
