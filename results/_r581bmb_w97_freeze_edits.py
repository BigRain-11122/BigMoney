# -*- coding: utf-8 -*-
"""r581 bm-b W97 freeze five-face edits (r560-law generator, r578 five-in-one).

Anchored insertions, idempotent, insertion-not-replace checked:
  1. canon W97 bullet  -> research/PERPETUAL_FACES.md, after the W96 row
  2. pf N1_BANDS[97]   -> scripts/perpetual_faces.py, after the 96 entry
  3. n1 WAVE_CONFIGS[97] -> scripts/perpetual_faces_n1.py, after the 96 entry
  4. n1 selftest W97 materializer leg -> after the W96 leg
  5. n1 selftest PASS-print W97 fragment -> after the W96 fragment
Pure insertion only; any anchor mismatch -> hard abort (r560 FIX-A law).
Byte-level in/out (r530 law). Multi-line assert messages parenthesized
(r580 bracket law).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANON = os.path.join(ROOT, "research", "PERPETUAL_FACES.md")
PF = os.path.join(ROOT, "scripts", "perpetual_faces.py")
N1 = os.path.join(ROOT, "scripts", "perpetual_faces_n1.py")


def rd(p):
    with open(p, "rb") as f:
        return f.read()


def wr(p, b):
    with open(p, "wb") as f:
        f.write(b)


def insert_after(data, needle, block, tag, guard=None):
    i = data.find(needle)
    assert i >= 0, f"{tag}: anchor needle not found: {needle[:60]}"
    j = data.find(b"\n", i) + 1
    assert j > i, f"{tag}: anchor line has no newline"
    nxt = data[j:j + 60]
    if guard:
        assert guard(nxt), f"{tag}: post-anchor guard fail: {nxt[:60]!r}"
    return data[:j] + block + data[j:]


def insert_after_entry(data, needle, block, tag, guard=None):
    """Insert block after the dict ENTRY starting at the needle line,
    walking to the entry's engine_owner close line."""
    i = data.find(needle)
    assert i >= 0, f"{tag}: anchor needle not found: {needle[:60]}"
    j = data.find(b"\n", i) + 1
    k = j
    while True:
        kend = data.find(b"\n", k) + 1
        ln = data[k:kend]
        if ln.strip() == b'"engine_owner": "bm-a"},':
            k = kend
            break
        k = kend
        assert k < len(data), f"{tag}: entry close not found"
    nxt = data[k:k + 40]
    if guard:
        assert guard(nxt), f"{tag}: post-anchor guard fail: {nxt[:40]!r}"
    return data[:k] + block + data[k:]


# --- 1. canon W97 bullet -------------------------------------------------------
CANON_BLOCK = (
    "- N1 \u6ce297\uff08r581 bm-b \u51bb\u00b7prereg \u65f6\u5c55\u884c\uff09\uff1a"
    "**\u7b2c\u516b\u5341\u4e03\u679a\u5f15\u64ce\u6ce2\u00b7bm-b \u7b2c\u4e09\u5341\u4e09\u679a\u81ea\u6709\u6ce2"
    "\u3014\u673a\u9762 derive\uff1aengine_owner \u884c 86+\u672c\u5019\u9009\uff0f"
    "engine_owner==bm-b \u884c 32+\u672c\u5019\u9009\u3015**\u00b7engine_owner=bm-b"
    "\u00b7SATURATION_ENGINE_LAW \u00a71/\u00a72 \u540c W10-W96 \u5408\u540c\u00b7\u4e0d\u5165\u6c60"
    "\u00b7\u514d\u9884\u6ce8\u518c\u7a0e\u00b7cmd_supply \u8df3\u8fc7\u95e8\u00b7**\u5f15\u64ce\u53bb\u8282\u6d41"
    "\u4ee4 O-20261001-2355 \u00a7\u4e8c\u81ea\u6709\u8fde\u7eed\u7cfb\u5217**\u00b7\u3010\u672c\u673a bm-b "
    "\u5b9e\u4f8b=tick \u67b6\u6784 r535 \u5f8b\u2014\u2014\u51bb\u7ed3 commit \u540e\u4e0b\u4e00 tick "
    "\u65b0\u8fdb\u7a0b\u91cd\u8bfb\u6d3b\u6811\u81ea\u89c1\u65b0\u884c=\u514d\u6740\u91cd\u542f\u514d\u505a"
    "\u00b7W44/W45/W48/W54/W57/W62/W64/W68/W73/W75/W77/W81/W84/W86/W89/W91/W93/W95 "
    "\u540c\u7a97\u5b9e\u8bc1\u00b7\u70b9\u706b\u9a8c\u8bc1\u552f\u4e00\u8bc1\u636e=\u4ea7\u7269\u589e\u957f"
    "\u9762 r325 \u5f8b\u3011\u00b7\u3010never-dry \u4f9b\u7ed9\u5f8b\u5e38\u8bbe\u6b65\u00b7"
    "**\u6ce2\u53f7 97=\u6ce8\u518c\u8868 W96 \u884c\u540e\u9996\u4e2a\u81ea\u7531\u53f7"
    "\uff08\u96f6\u5e2d\u4f4d\u7a7a\u6863\uff1aW2..W96 \u5168\u884c\u5df2\u6ce8\u518c\u00b7\u5355\u6001"
    "\uff3br511 \u8868\u5c3e\u9501\u4f8b\u51bb\u7ed3\u524d fetch \u5b9e\u6838\u8868\u5c3e\u65f6 W97 "
    "\u53f7\u4f4d\u51c0\u7a7a\u00b7pf \u884c+WAVE_CONFIGS+prereg \u8def\u5f84\u4e09\u67e5+leg0b "
    "\u5168 inbox/processed/ \u626b\u63cf W97 \u5e2d\u4f4d\u96f6\u5916\u673a\u547d\u4e2d\u673a\u9a8c"
    "\u00b7\u672c\u673a\u5e2d\u4f4d\u516c\u793a\u8c41\u514d=MSG-20261002-1545-bmb \u5df2\u63a8 "
    "origin a47ad46dd \u5148\u4e8e\u672c\u51bb\u7ed3 r565 \u5f8b\uff3d\uff09**\uff1b"
    "**\u5e2d\u4f4d\u516c\u793a=MSG-20261002-1545-bmb**\uff08published=reserved r518-\u2460 \u5f8b"
    "\u00b7\u5148\u4e8e\u51bb\u7ed3 commit \u63a8 origin r565 \u65e9\u53ef\u89c1\u6027\u5f8b\uff09\uff1b"
    "\u5e26\u4f4d=**A-ext seed=237_004..239_003**\uff08==W96 \u884c A \u5c3e 237_003+1 \u8d77"
    "\u00b7\u6b65\u957f 2_000\u00b7**CLEAN \u96f6\u62d2\u7edd\u70b9\u00b7\u53cc\u4fa7\u7b97\u672f\u7eed\u5e26**"
    "\uff09+**B-ext exit seed=58_001..58_200**\uff08W96 \u884c B \u5c3e\u7b97\u672f\u4f4d "
    "57_901..58_100 \u649e **SEED_REGISTRY im_ic_pair=58_000** \u5e26\u5185**\u4e2d\u4f4d**"
    "\u547d\u4e2d\u3014\u96f6\u7d22\u5f15 99/199 \u975e\u8fb9\u7f18\u3015\u2192**D-20261002-05 "
    "\u96c6\u56e2\u9489\u6b7b\u884c=\u8d8a hit \u8d77\u7a97** hit+1 \u91cd\u542f 58_001..58_200 "
    "CLEAN\u00b7\u7a97\u6b65\u94fe\u8bfb\u6cd5 58_101..58_300 \u62ab\u9732\u4e0d\u53d6"
    "\u3014\u9489\u6b7b\u884c\u6b63\u65ad\u8a00\u951a=W68-B 50_501..50_700 \u540c\u6784\u00b7"
    "W91-B 56_501..56_700 \u540c\u578b\u5148\u4f8b\u3015\u00b7\u8df3\u4f4d\u88ab\u8feb\u6027 R250 "
    "\u975e\u81ea\u7531\u6311\uff09\uff1bADMIT \u56de\u6267=results/_r581bmb_w97_band_gate.py "
    "rc0\uff08\u5355\u6001 94 \u884c\u8868\u00b7\u626b\u63cf\u9762=pre-W97 \u5168\u884c\u6ce8\u518c\u5e26"
    "+W1 ext+v1 \u5728\u7528\u5e26+SEED_REGISTRY \u5168\u952e 160 \u503c+N3-R1 \u5df2\u7528\u79cd\u5b50"
    "\u5e26 70_000..70_005 MSG-183x r529 \u5f3a\u5236\u817f+runner \u8bbe\u8ba1\u63a2\u9488\u79cd\u5b50"
    "\u7c07 95_000..95_003 r335 \u817f+N2/N4 \u63a2\u9488\u70b9+N2-W15 \u8349\u6848\u63a2\u9488\u70b9"
    "+lfc/options \u5b9e\u9645\u6d41\u907f\u8ba9\u817f\uff09\uff1bper-wave prereg="
    "research/PERPETUAL_N1_W97_PREREG.md\uff08\u9884\u6d4b\u951a=W91 finalize \u5b9e\u6d4b\u503c"
    "\u00b7\u951a\u6eda\u52a8\u5f8b\u81ea W76 \u6eda\u52a8\u81f3 W91\u00b7\u672c\u6ce2=\u96f6\u547d\u4e2d "
    "banned gate ADMIT 0 matched\uff09\uff1b**W98+ \u6295\u5f71\uff08gate \u673a\u8bc1\u00b7\u4e0b\u6ce2"
    "\u51bb\u7ed3\u65b9\u5fc5\u590d\u6838\u975e\u8f6c\u6284\uff09**\uff1aA 239_004..241_003 **CLEAN**"
    "\uff1bB 58_201..58_400 **CLEAN**\u3002\n"
).encode("utf-8")

data = rd(CANON)
if "- N1 \u6ce297\uff08r581 bm-b \u51bb".encode("utf-8") in data:
    print("SKIP canon: already present")
else:
    data2 = insert_after(
        data, "- N1 \u6ce296".encode("utf-8"), CANON_BLOCK, "canon",
        guard=lambda nxt: not nxt.startswith(b"- N1 "))
    assert data2.count(CANON_BLOCK) == 1
    wr(CANON, data2)
    print("canon: W97 bullet inserted (+%d bytes)" % len(CANON_BLOCK))

# --- 2. pf N1_BANDS[97] --------------------------------------------------------
PF_BLOCK = (
    "    # EIGHTY-SEVENTH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r581 bm-b\n"
    "    # freeze): engine_owner rows 86 + candidate; bm-b's\n"
    "    # thirty-third owned per machine-derive (engine_owner==bm-b\n"
    "    # rows 32 + candidate). Wave 97 = first free number after the\n"
    "    # registered W96 row (zero seat gaps: W2..W96 all registered;\n"
    "    # single state, no skip-past-published chain).\n"
    "    # W1..W91 finalizes ALL LANDED (landed chain head 564,748 = W91\n"
    "    # bm-b r579 one-pass; K=198,120 merged pool). FIVE in-flight\n"
    "    # upstream seats (W92 bm-c 12/12 burned finalize-pending + W93\n"
    "    # bm-b 12/12 burned finalize-pending + W94 bm-a burn in flight +\n"
    "    # W95 bm-b 12/12 burned finalize-pending + W96 bm-a burn in\n"
    "    # flight, ALL REGISTERED) -- finalize merge loop stays\n"
    "    # FAIL-CLOSED r307 at run time.\n"
    "    # A = arithmetic continuation from the registered W96 A tail,\n"
    "    # CLEAN zero refusal points (honest forward walk).\n"
    "    # B = D-20261002-05 pinned: arithmetic 57_901..58_100 REFUSED at\n"
    "    # SEED_REGISTRY im_ic_pair=58_000 in-window MEDIAN hit (99/199\n"
    "    # non-edge) -> hit+1 restart 58_001..58_200 CLEAN (window-step\n"
    "    # chain reading 58_101..58_300 disclosed NOT taken; frozen\n"
    "    # precedent W68-B 50_501..50_700).\n"
    "    # Machine-verified at prereg time\n"
    "    # (results/_r581bmb_w97_band_gate.py ADMIT receipt rc0 single\n"
    "    # state vs the 94-row pre-W97 table + live SEED_REGISTRY values\n"
    "    # + probe cluster 95_000..95_003 r335 discovery leg + N3-R1\n"
    "    # used-seed band 70_000..70_005 MSG-183x r529 mandatory leg;\n"
    "    # origin slot vacancy machine-checked; seat published=reserved\n"
    "    # MSG-20261002-1545-bmb pushed BEFORE this freeze per r565\n"
    "    # law). W98+ projection: A 239_004..241_003 CLEAN; B\n"
    "    # 58_201..58_400 CLEAN (next freezer must re-derive).\n"
    "    # NOT a re-pick (R250: W97 bands were never assigned).\n"
    "    97: {\"a\": (237_004, 239_003), \"b_exit\": (58_001, 58_200),\n"
    "         \"engine_owner\": \"bm-b\"},\n"
).encode("utf-8")

data = rd(PF)
if b'97: {"a": (237_004, 239_003)' in data:
    print("SKIP pf: already present")
else:
    data2 = insert_after_entry(
        data, '96: {"a": (235_004, 237_003)'.encode("utf-8"), PF_BLOCK, "pf",
        guard=lambda nxt: nxt.startswith(b"}"))
    assert data2.count(b'97: {"a": (237_004, 239_003)') == 1
    wr(PF, data2)
    print("pf: N1_BANDS[97] inserted (+%d bytes)" % len(PF_BLOCK))

# --- 3. n1 WAVE_CONFIGS[97] ----------------------------------------------------
N1_CFG_BLOCK = (
    "                       97: {\"batch\": \"PERPETUAL-N1-W97\",\n"
    "                            \"prereg\": (\"research/PERPETUAL_N1_W97_PREREG.md (wave-level frozen \"\n"
    "                                       \"pre-run; design = frozen v1 null calibration verbatim, \"\n"
    "                                       \"new seed bands only; EIGHTY-SEVENTH ENGINE-OWNED WAVE BY \"\n"
    "                                       \"MACHINE-DERIVE (engine_owner rows 86 + candidate), \"\n"
    "                                       \"own-series continuation per O-20261001-2355 sec.2 \"\n"
    "                                       \"(first-free-number law over the registered W96 row, \"\n"
    "                                       \"zero seat gaps: W2..W96 all registered, single state; \"\n"
    "                                       \"seat published=reserved MSG-20261002-1545-bmb PUSHED to \"\n"
    "                                       \"origin a47ad46dd BEFORE this freeze per r565 \"\n"
    "                                       \"early-visibility law), \"\n"
    "                                       \"engine_owner=bm-b, wave 97: A = ARITHMETIC \"\n"
    "                                       \"CONTINUATION from the registered W96 A tail (237_004..\"\n"
    "                                       \"239_003 CLEAN zero refusal points) + B = \"\n"
    "                                       \"D-20261002-05 PINNED SEMANTICS (arithmetic window \"\n"
    "                                       \"57_901..58_100 REFUSED at SEED_REGISTRY \"\n"
    "                                       \"im_ic_pair=58_000 in-window MEDIAN hit 99/199 \"\n"
    "                                       \"non-edge -> hit+1 restart 58_001..58_200 CLEAN; \"\n"
    "                                       \"window-step chain reading 58_101..58_300 disclosed \"\n"
    "                                       \"NOT taken per the pinned law; frozen precedent \"\n"
    "                                       \"W68-B 50_501..50_700 same shape; ADMIT receipt \"\n"
    "                                       \"results/_r581bmb_w97_band_gate.py rc0 single state; \"\n"
    "                                       \"W98+ projection: A 239_004..241_003 CLEAN / B \"\n"
    "                                       \"58_201..58_400 CLEAN, disclosed for the next \"\n"
    "                                       \"freezer); W91 finalize LANDED (net chain head \"\n"
    "                                       \"564,748 = bm-b r579 one-pass, K=198,120 merged \"\n"
    "                                       \"pool) + FIVE IN-FLIGHT UPSTREAM SEATS at this \"\n"
    "                                       \"freeze (W92 bm-c 12/12 burned finalize-pending + \"\n"
    "                                       \"W93 bm-b 12/12 burned finalize-pending + W94 bm-a \"\n"
    "                                       \"burn in flight + W95 bm-b 12/12 burned \"\n"
    "                                       \"finalize-pending + W96 bm-a burn in flight, ALL \"\n"
    "                                       \"REGISTERED -- finalize merge loop stays \"\n"
    "                                       \"FAIL-CLOSED r307 at run time)\"),\n"
    "                            \"a_seed_base\": 237_004,        # law sec.4 W97 A: 237_004..239_003 (arithmetic continuation from W96 A tail)\n"
    "                            \"b_exit_seed_base\": 58_001,   # law sec.4 W97 B: 58_001..58_200 (D-20261002-05 pin at im_ic_pair=58_000, hit+1 restart)\n"
    "                            \"shard_subdir\": \"n1_w97\", \"out_name\": \"n1_w97_results.json\",\n"
    "                            \"engine_owner\": \"bm-b\"},\n"
).encode("utf-8")

data = rd(N1)
if b'"shard_subdir": "n1_w97"' in data:
    print("SKIP n1 cfg: already present")
else:
    data2 = insert_after_entry(
        data, '"shard_subdir": "n1_w96", "out_name": "n1_w96_results.json",'.encode("utf-8"),
        N1_CFG_BLOCK, "n1cfg")
    assert data2.count(b'"shard_subdir": "n1_w97"') == 1
    wr(N1, data2)
    print("n1: WAVE_CONFIGS[97] inserted (+%d bytes)" % len(N1_CFG_BLOCK))

# --- 4. n1 selftest W97 materializer leg ---------------------------------------
LEG_MARK = "W97 materializer face (r581 bm-b freeze"
N1_LEG_BLOCK = (
    "\n"
    "    # --- W97 materializer face (r581 bm-b freeze, own-series law\n"
    "    #     under CEO de-throttle order O-20261001-2355 sec.2): bm-b's\n"
    "    #     thirty-third owned per machine-derive (engine_owner==bm-b\n"
    "    #     rows 32 + candidate); wave 97 = first free number after the\n"
    "    #     registered W96 row (zero seat gaps: W2..W96 all registered;\n"
    "    #     single state, no skip-past chain). EIGHTY-SEVENTH engine\n"
    "    #     wave BY MACHINE-DERIVE (engine_owner rows 86 + candidate).\n"
    "    #     Seat published=reserved MSG-20261002-1545-bmb pushed to\n"
    "    #     origin a47ad46dd BEFORE this freeze per r565 law. ADMIT\n"
    "    #     receipt results/_r581bmb_w97_band_gate.py rc0 single state\n"
    "    #     (B96 registered W96).\n"
    "    _set_wave(97)\n"
    "    try:\n"
    "        assert WAVE_CONFIGS[97][\"a_seed_base\"] == pf.N1_BANDS[97][\"a\"][0], \\\n"
    "            \"W97 A band drift vs law mirror\"\n"
    "        assert WAVE_CONFIGS[97][\"b_exit_seed_base\"] == \\\n"
    "            pf.N1_BANDS[97][\"b_exit\"][0], \"W97 B band drift vs law mirror\"\n"
    "        assert WAVE_CONFIGS[97].get(\"engine_owner\") == \\\n"
    "            pf.N1_BANDS[97].get(\"engine_owner\") == \"bm-b\", \\\n"
    "            \"W97 engine_owner drift (law mirror parity)\"\n"
    "        w97_a = {A_SEED_BASE + j for j in range(A_N)}\n"
    "        w97_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}\n"
    "        assert not (w97_a & w97_b), \"W97 A/B band overlap\"\n"
    "        assert not (w97_a & reg_ints) and not (w97_b & reg_ints), \\\n"
    "            \"W97 hits SEED_REGISTRY\"\n"
    "        for nm, band in ((\"A\", w97_a), (\"B\", w97_b)):\n"
    "            assert not (band & v1_a) and not (band & v1_b), f\"W97 {nm} hits v1\"\n"
    "            assert not (band & w1_a) and not (band & w1_b), f\"W97 {nm} hits W1\"\n"
    "            assert not (band & probes), f\"W97 {nm} hits probe seeds\"\n"
    "        assert pf.N1_BANDS[92] == {\"a\": (227_004, 229_003),\n"
    "                                   \"b_exit\": (56_701, 56_900),\n"
    "                                   \"engine_owner\": \"bm-c\"}, \\\n"
    "            \"registered W92 row parity drift (r307 two-state; bm-c r370)\"\n"
    "        assert pf.N1_BANDS[93] == {\"a\": (229_004, 231_003),\n"
    "                                   \"b_exit\": (57_101, 57_300),\n"
    "                                   \"engine_owner\": \"bm-b\"}, \\\n"
    "            \"registered W93 row parity drift (r307 two-state; bm-b r579)\"\n"
    "        assert pf.N1_BANDS[94] == {\"a\": (231_004, 233_003),\n"
    "                                   \"b_exit\": (57_301, 57_500),\n"
    "                                   \"engine_owner\": \"bm-a\"}, (\n"
    "            \"registered W94 row parity drift (r307 two-state; bm-a \"\n"
    "            \"r580, heal-restored r580 bm-b)\")\n"
    "        assert pf.N1_BANDS[95] == {\"a\": (233_004, 235_003),\n"
    "                                   \"b_exit\": (57_501, 57_700),\n"
    "                                   \"engine_owner\": \"bm-b\"}, (\n"
    "            \"registered W95 row parity drift (r307 two-state; bm-b \"\n"
    "            \"r580)\")\n"
    "        assert pf.N1_BANDS[96] == {\"a\": (235_004, 237_003),\n"
    "                                   \"b_exit\": (57_701, 57_900),\n"
    "                                   \"engine_owner\": \"bm-a\"}, (\n"
    "            \"registered W96 row parity drift (r307 two-state; bm-a \"\n"
    "            \"r581)\")\n"
    "        for wprev in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + [w for w in range(16, 97)]:\n"
    "            assert not (w97_a & {WAVE_CONFIGS[wprev][\"a_seed_base\"] + j\n"
    "                                 for j in range(A_N)}), f\"W97 A hits W{wprev}\"\n"
    "            assert not (w97_b & {WAVE_CONFIGS[wprev][\"b_exit_seed_base\"] + j\n"
    "                                  for j in range(B_N)}), f\"W97 B hits W{wprev}\"\n"
    "        assert not (w97_a & set(range(235_004, 237_004))) and \\\n"
    "            not (w97_b & set(range(57_701, 57_901))), (\n"
    "            \"W97 bands must clear the W96 registered bands (prior-wave \"\n"
    "            \"loop belt-and-braces)\")\n"
    "        n3r1_used97 = set(range(70_000, 70_006))\n"
    "        assert not (w97_a & n3r1_used97) and not (w97_b & n3r1_used97), \\\n"
    "            \"W97 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)\"\n"
    "        assert not (w97_a & lfc_actual12) and not (w97_b & lfc_actual12), \\\n"
    "            \"W97 bands must clear the lfc actual draw range\"\n"
    "        assert not (w97_a & options_actual12) and \\\n"
    "            not (w97_b & options_actual12), \\\n"
    "            \"W97 bands must clear the options_wave2 actual draw range\"\n"
    "        assert WAVE_CONFIGS[97][\"a_seed_base\"] == 237_004 == 237_003 + 1, (\n"
    "            \"W97 A must be the arithmetic continuation from the \"\n"
    "            \"registered W96 A tail\")\n"
    "        arith_a97 = set(range(237_004, 239_004))\n"
    "        assert not (arith_a97 & reg_ints), \\\n"
    "            \"W97 A window must be CLEAN (arithmetic continuation ADMIT face)\"\n"
    "        assert WAVE_CONFIGS[97][\"b_exit_seed_base\"] == 58_001 == 58_000 + 1, (\n"
    "            \"W97 B must start at the 58_000 hit + 1 (D-20261002-05 pin: \"\n"
    "            \"past-hit start-window; arithmetic window 57_901..58_100 \"\n"
    "            \"REFUSED in-band at im_ic_pair=58_000 median, non-endpoint)\")\n"
    "        assert WAVE_CONFIGS[97][\"b_exit_seed_base\"] != 58_101, (\n"
    "            \"W97 B window-step-chain reading 58_101..58_300 is BANNED \"\n"
    "            \"by D-20261002-05 (past-hit start-window pinned; W68-B \"\n"
    "            \"anchor)\")\n"
    "        arith_b97 = set(range(57_901, 58_101))\n"
    "        b_hit97 = sorted(p for p in arith_b97 if p in reg_ints)\n"
    "        assert b_hit97 == [58_000], (\n"
    "            \"W97 B pre-window must hit exactly [58_000] (median 99/199)\")\n"
    "        assert 58_000 - 57_901 == 99, \"W97 B hit median position drift\"\n"
    "        assert not (w97_b & reg_ints), \\\n"
    "            \"W97 B restart window 58_001..58_200 must be CLEAN\"\n"
    "        assert _entry_shard_of(0, 12) == (\"PERPETUAL-N1-W97-SHARD-0\",\n"
    "                                          \"n1w97-0of12\"), \"W97 entry identity\"\n"
    "        assert _entry_shard_of(11, 12) == (\"PERPETUAL-N1-W97-SHARD-11\",\n"
    "                                          \"n1w97-11of12\")\n"
    "        assert SHARD_DIR.endswith(\"n1_w97\") and OUT.endswith(\n"
    "            \"n1_w97_results.json\"), \"W97 path drift\"\n"
    "        for wprev in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + [w for w in range(16, 97)]:\n"
    "            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(\n"
    "                PATHS.results_dir, \"p2cal_ext\",\n"
    "                WAVE_CONFIGS[wprev][\"shard_subdir\"])), \\\n"
    "                f\"W97 shard dir collides with W{wprev}\"\n"
    "        for _depw in range(17, 92):\n"
    "            assert os.path.exists(os.path.join(\n"
    "                OUT_DIR, WAVE_CONFIGS[_depw][\"out_name\"])), \\\n"
    "                f\"W97 finalize cumulative dep (W{_depw} output) missing\"\n"
    "        # finalize wave-set derivation face (r511 derive law):\n"
    "        # prior-wave set derives from registry keys below 97 (no 15).\n"
    "        # Single state: W2..W96 all registered.\n"
    "        _priors97 = sorted(w for w in WAVE_CONFIGS if w < 97)\n"
    "        assert _priors97 == \\\n"
    "            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\\n"
    "            [w for w in range(16, 97)], (\n"
    "            \"W97 prior-wave set must derive from registry keys (no 15; \"\n"
    "            \"W2..W96 all registered, single state)\")\n"
    "        assert os.path.exists(os.path.join(\n"
    "            PATHS.root, \"research\", \"PERPETUAL_N1_W97_PREREG.md\")), \\\n"
    "            \"W97 per-wave prereg missing (materializer requirement)\"\n"
    "        assert pickle.dumps(_worker_init), \"spawn-carrier unpicklable\"\n"
    "    finally:\n"
    "        _set_wave(2)\n"
).encode("utf-8")

data = rd(N1)
if LEG_MARK.encode("utf-8") in data:
    print("SKIP n1 leg: already present")
else:
    i = data.find(b"# --- W96 materializer face")
    assert i >= 0, "leg anchor: W96 leg not found"
    j = data.find(b"_set_wave(2)", i)
    assert j > i, "leg anchor: W96 leg finally not found"
    j_end = data.find(b"\n", j) + 1
    nxt = data[j_end:j_end + 60]
    assert b"T-141 s2" in nxt, \
        f"leg post-anchor guard (must be T-141 s2 lane face next): {nxt[:60]!r}"
    data2 = data[:j_end] + N1_LEG_BLOCK + data[j_end:]
    assert data2.count(LEG_MARK.encode("utf-8")) == 1
    wr(N1, data2)
    print("n1: W97 materializer leg inserted (+%d bytes)" % len(N1_LEG_BLOCK))

# --- 5. n1 selftest PASS-print W97 fragment -------------------------------------
FRAG_MARK = "law sec.4 W97 row, r581 bm-b]"
N1_FRAG_BLOCK = (
    "          \"+ W97 materializer face [same guard set, dep=W17..W91 outputs \"\n"
    "          \"ALL PRESENT (landed chain head 564,748, K=198,120, W91 bm-b \"\n"
    "          \"r579 one-pass; FIVE in-flight upstream seats at freeze: W92 \"\n"
    "          \"bm-c + W93 bm-b + W95 bm-b 12/12 burned finalize-pending + \"\n"
    "          \"W94 bm-a + W96 bm-a burn in flight, ALL REGISTERED, finalize \"\n"
    "          \"merge loop stays FAIL-CLOSED r307 at run time), \"\n"
    "          \"EIGHTY-SEVENTH ENGINE-OWNED WAVE BY MACHINE-DERIVE \"\n"
    "          \"(engine_owner rows 86 + candidate) bm-b's THIRTY-THIRD \"\n"
    "          \"owned claim per machine-derive (engine_owner==bm-b rows 32 \"\n"
    "          \"+ candidate), engine_owner=bm-b per engine de-throttle law \"\n"
    "          \"O-20261001-2355 sec.2 own-continuous-series (wave 97 = first \"\n"
    "          \"FREE number after the registered W96 row, zero seat gaps; \"\n"
    "          \"seat published=reserved MSG-20261002-1545-bmb pushed to \"\n"
    "          \"origin BEFORE the freeze per r565 law), A = ARITHMETIC \"\n"
    "          \"CONTINUATION from the registered W96 A tail (237_004..239_003 \"\n"
    "          \"CLEAN zero refusal points) + B = D-20261002-05 PINNED \"\n"
    "          \"SEMANTICS (arithmetic 57_901..58_100 REFUSED at SEED_REGISTRY \"\n"
    "          \"im_ic_pair=58_000 in-window MEDIAN 99/199 non-edge -> hit+1 \"\n"
    "          \"restart 58_001..58_200 CLEAN; window-step chain reading \"\n"
    "          \"58_101..58_300 disclosed NOT taken per the pinned law; \"\n"
    "          \"frozen precedent W68-B 50_501..50_700 same shape, W91-B \"\n"
    "          \"56_501..56_700 same-type precedent; ADMIT receipt \"\n"
    "          \"results/_r581bmb_w97_band_gate.py rc0 single state; W98+ \"\n"
    "          \"projection A 239_004..241_003 CLEAN / B 58_201..58_400 CLEAN \"\n"
    "          \"disclosed for the next freezer; not a free pick -- R250; \"\n"
    "          \"probe-seed cluster leg, N3-R1 used-seed leg, \"\n"
    "          \"law sec.4 W97 row, r581 bm-b] \"\n"
).encode("utf-8")

data = rd(N1)
if FRAG_MARK.encode("utf-8") in data:
    print("SKIP n1 frag: already present")
else:
    # r581 bm-b note: bm-a's W96 fragment splits its tail across two
    # string literals ("law sec.4 W96 " + "row, r581 bm-a] "), so the
    # anchor is the fragment's final line, not the concatenated phrase.
    anchor = b'"row, r581 bm-a] "'
    i = data.find(anchor)
    assert i >= 0, "frag anchor: W96 fragment end not found"
    j = data.find(b"\n", i) + 1
    nxt = data[j:j + 30]
    assert b'"+ T-141 s2' in nxt, f"frag post-anchor guard: {nxt[:30]!r}"
    data2 = data[:j] + N1_FRAG_BLOCK + data[j:]
    assert data2.count(FRAG_MARK.encode("utf-8")) == 1
    wr(N1, data2)
    print("n1: W97 PASS fragment inserted (+%d bytes)" % len(N1_FRAG_BLOCK))

print("ALL FIVE FACES STAGED OK (canon + pf + n1 cfg + n1 leg + n1 frag)")
