# -*- coding: utf-8 -*-
"""r580 bm-b W95 freeze five-face edits (r560-law generator, r578 five-in-one).

Anchored insertions, idempotent, insertion-not-replace checked:
  1. canon W95 bullet  -> research/PERPETUAL_FACES.md, after the W94 row
  2. pf N1_BANDS[95]   -> scripts/perpetual_faces.py, after the 94 entry
  3. n1 WAVE_CONFIGS[95] -> scripts/perpetual_faces_n1.py, after the 94 entry
  4. n1 selftest W95 materializer leg -> after the W94 leg
  5. n1 selftest PASS-print W95 fragment -> after the W94 fragment
Pure insertion only; any anchor mismatch -> hard abort (r560 FIX-A law).
Byte-level in/out (r530 law).
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


# --- 1. canon W95 bullet -------------------------------------------------------
CANON_BLOCK = (
    "- N1 \u6ce295\uff08r580 bm-b \u51bb\u00b7prereg \u65f6\u5c55\u884c\uff09\uff1a**\u7b2c\u516b\u5341\u4e94\u679a\u5f15\u64ce\u6ce2\u00b7bm-b \u7b2c\u4e09\u5341\u4e8c\u679a\u81ea\u6709\u6ce2\u3014\u673a\u9762 derive\uff1aengine_owner \u884c 84+\u672c\u5019\u9009\uff0fengine_owner==bm-b \u884c 31+\u672c\u5019\u9009\u3015**\u00b7engine_owner=bm-b\u00b7SATURATION_ENGINE_LAW \u00a71/\u00a72 \u540c W10-W93 \u5408\u540c\u00b7\u4e0d\u5165\u6c60\u00b7\u514d\u9884\u6ce8\u518c\u7a0e\u00b7cmd_supply \u8df3\u8fc7\u95e8\u00b7**\u5f15\u64ce\u53bb\u8282\u6d41\u4ee4 O-20261001-2355 \u00a7\u4e8c\u81ea\u6709\u8fde\u7eed\u7cfb\u5217**\u00b7\u3010\u672c\u673a bm-b \u5b9e\u4f8b=tick \u67b6\u6784 r535 \u5f8b\u2014\u2014\u51bb\u7ed3 commit \u540e\u4e0b\u4e00 tick \u65b0\u8fdb\u7a0b\u91cd\u8bfb\u6d3b\u6811\u81ea\u89c1\u65b0\u884c=\u514d\u6740\u91cd\u542f\u514d\u505a\u00b7W44/W45/W48/W54/W57/W62/W64/W68/W73/W75/W77/W81/W84/W86/W89/W91/W93 \u540c\u7a97\u5b9e\u8bc1\u00b7\u70b9\u706b\u9a8c\u8bc1\u552f\u4e00\u8bc1\u636e=\u4ea7\u7269\u589e\u957f\u9762 r325 \u5f8b\u3011\u00b7\u3010never-dry \u4f9b\u7ed9\u5f8b\u5e38\u8bbe\u6b65\u00b7**\u6ce2\u53f7 95=\u6ce8\u518c\u8868 W94 \u884c\u540e\u9996\u4e2a\u81ea\u7531\u53f7\uff08\u96f6\u5e2d\u4f4d\u7a7a\u6863\uff1aW2..W94 \u5168\u884c\u5df2\u6ce8\u518c\u2014\u2014W94 \u884c\u672c\u7a97\u7531 bm-b r580 \u81ea dead-r579 replay \u9876\u66ff\u4e8b\u6545\u5b57\u8282\u7ea7\u590d\u539f\uff3bheal \u56de\u6267 MSG-20261002-1533-bmb\u00b7\u6301\u6709 commit 9a9d05857 \u63d0\u53d6+r560 \u5b88\u536b\u63d2\u5165+\u5b57\u8282\u6052\u7b49\u9a8c\u8bc1 1/1 \u4e94\u9762\uff3d\uff09**\uff08r511 \u8868\u5c3e\u9501\u4f8b\u51bb\u7ed3\u524d fetch \u5b9e\u6838\u8868\u5c3e\u65f6 W95 \u53f7\u4f4d\u51c0\u7a7a\u00b7pf \u884c+WAVE_CONFIGS+prereg \u8def\u5f84\u4e09\u67e5+leg0b \u5168 inbox+processed/ \u626b\u63cf W95 \u5e2d\u4f4d\u96f6\u5916\u673a\u547d\u4e2d\u673a\u9a8c\uff09\uff1b**\u5e2d\u4f4d\u516c\u793a=MSG-20261002-1536-bmb**\uff3bpublished=reserved r518-\u2460 \u5f8b\u00b7\u5148\u4e8e\u51bb\u7ed3 commit \u63a8 origin 58ee5f0bb=r565 \u65e9\u53ef\u89c1\u6027\u5f8b\uff3d\uff09\u00b7\u672c\u7a97\u5b9e\u51b5=**W91 finalize \u5df2\u843d\u8d26\uff08\u51c0\u94fe\u5934 564,748\u00b7K=198,120\uff09+\u4e09\u5728\u98de\u4e0a\u6e38\u5e2d\uff08W92 bm-c \u5df2\u6ce8\u518c 12/12 \u70e7\u6bd5 finalize \u672a\u843d\u8d26+W93 bm-b \u5df2\u6ce8\u518c 12/12 \u70e7\u6bd5 finalize \u672a\u843d\u8d26+W94 bm-a \u5df2\u6ce8\u518c\u70e7\u5f55\u5728\u98de\uff09=\u672c\u6ce2 finalize \u94fe\u5e8f\u524d\u7f6e\u5728\u98de\uff08\u8dd1\u65f6\u6309 registry \u952e derive \u590d\u6838\u00b7FAIL-CLOSED r307 \u4e24\u6001\u5f8b\uff09**\u00b7**\u5e26\u4f4d\uff08r535 \u673a\u95f8 derive \u5f8b\u00b7\u6d3b\u6ce8\u518c\u8868\u673a\u8bc1\u00b7\u5355\u6001\u6536\u655b\u95e8\u00b7ADMIT \u56de\u6267=results/_r580bmb_w95_band_gate.py rc0\u00b7mode B94 \u8868\u5c3e=W94\uff09**\uff1a**A-ext seed=233_004..235_003**\uff08W94 \u884c A \u5c3e 233_003 \u7b97\u672f\u7eed\u5e26\u00b7\u6b65\u957f 2_000\u00b7**CLEAN \u96f6\u62d2\u7edd\u70b9**\u00b7\u8bda\u5b9e\u524d\u5411\u8d70\u7a97\uff3b\u7b97\u672f\u7eed\u5e26\u5148\u4f8b\u65cf\u00b7W92 r370 \u540c\u5f0f\uff3d\uff09\uff1b**B-ext exit seed=57_501..57_700**\uff08W94 \u884c B \u5c3e 57_500 \u7b97\u672f\u7eed\u5e26\u00b7**CLEAN \u96f6\u62d2\u7edd\u70b9**\u00b7\u65e0 pin \u94fe\u65e0\u8df3\u4f4d\uff09\u3002\u3010\u673a\u8bc1\u51c0\u7a7a\u2014\u2014leg0 \u4e5d\u5341\u4e8c\u884c\u6ce8\u518c\u8868\u5f62\uff0892 \u6ce8\u518c\u884c\u00b7\u8868\u5c3e=W94 bm-a r580 heal-\u590d\u539f\uff09+leg0b \u672c\u673a W95 \u5e2d\u4f4d MSG \u5728\u573a\u673a\u9a8c+\u5916\u673a W95 \u5e2d\u4f4d\u96f6\u547d\u4e2d+leg1 \u53cc\u4fa7\u7b97\u672f\u7eed\u5e26 CLEAN+leg2 A/B \u9996\u51c0\u7a97==\u5019\u9009\u6052\u7b49+leg3 origin \u53f7\u4f4d\u51c0\u7a7a\u673a\u9a8c\uff08pf \u884c+WAVE_CONFIGS+prereg \u8def\u5f84\u4e09\u67e5\uff09+SEED_REGISTRY \u5168\u952e 160 \u503c+N3-R1 \u5df2\u7528\u79cd\u5b50\u5e26\u817f\uff0870_000..70_005\u00b7MSG-183x r529 \u5f3a\u5236\uff09+\u63a2\u9488\u79cd\u5b50\u7c07\u817f\uff0895_000..95_003\u00b7r335 \u5f3a\u5236\uff09+N2/N4+N2-W15 \u63a2\u9488\u70b9+lfc/options \u5b9e\u9645\u6d41\u817f\u3011\u00b7**W96+ \u6295\u5f71\uff08gate \u673a\u8bc1\u00b7\u4e0b\u6ce2\u51bb\u7ed3\u65b9\u5fc5\u590d\u6838\u975e\u8f6c\u6284\uff09**\uff1aA 235_004..237_003 **CLEAN**\uff1bB 57_701..57_900 **CLEAN**\uff08\u53cc\u4fa7\u7b97\u672f\u9884\u671f\u96f6\u62d2\u7edd\u70b9\uff09\u3002R250\uff1aW95 \u5e26\u4ece\u672a\u6307\u6d3e\u00b7\u6d4b\u91cf\u9762\u96f6\u7ed3\u679c\u53ef\u9493\u00b7banned gate ADMIT 0 matched\uff08W95 prereg \u00a70.5\uff09\u00b7per-wave prereg=research/PERPETUAL_N1_W95_PREREG.md\uff08\u51bb\u7ed3\u4ef6\u00b7\u672c\u6ce2 \u00a75 \u951a=W91 finalize \u5b9e\u6d4b\u503c\u00b7\u951a\u6eda\u52a8\u5f8b\u81ea W76 \u6eda\u52a8\u81f3 W91\uff09\u00b7finalize \u94fe\u5e8f\u524d\u7f6e=\u8d77\u8349\u7a97\u4e09\u5728\u98de\u4e0a\u6e38\u5e2d\uff08FAIL-CLOSED r307 \u4e24\u6001\u5f8b\u8dd1\u65f6\u590d\u6838\uff09\u3002\n"
).encode("utf-8")

data = rd(CANON)
if "- N1 \u6ce295\uff08r580 bm-b \u51bb".encode("utf-8") in data:
    print("SKIP canon: already present")
else:
    data2 = insert_after(
        data, "- N1 \u6ce294".encode("utf-8"), CANON_BLOCK, "canon",
        guard=lambda nxt: not nxt.startswith(b"- N1 "))
    assert data2.count(CANON_BLOCK) == 1
    wr(CANON, data2)
    print("canon: W95 bullet inserted (+%d bytes)" % len(CANON_BLOCK))

# --- 2. pf N1_BANDS[95] --------------------------------------------------------
PF_BLOCK = (
    "    # EIGHTY-FIFTH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r580 bm-b\n"
    "    # freeze): engine_owner rows 84 + candidate; bm-b's\n"
    "    # thirty-second owned per machine-derive (engine_owner==bm-b\n"
    "    # rows 31 + candidate). Wave 95 = first free number after the\n"
    "    # registered W94 row (zero seat gaps: W2..W94 all registered;\n"
    "    # W94 restored same window from the dead-r579 replay revert,\n"
    "    # heal receipt MSG-20261002-1533-bmb).\n"
    "    # W1..W91 finalizes ALL LANDED (landed chain head 564,748 = W91\n"
    "    # bm-b r579 one-pass; K=198,120 merged pool). THREE in-flight\n"
    "    # upstream seats (W92 bm-c 12/12 burned finalize-pending + W93\n"
    "    # bm-b 12/12 burned finalize-pending + W94 bm-a burn in flight)\n"
    "    # -- finalize merge loop stays FAIL-CLOSED r307 at run time.\n"
    "    # BOTH SIDES ARITHMETIC CONTINUATION from the registered W94\n"
    "    # tails, CLEAN zero refusal points (honest forward walk, no\n"
    "    # skip, no pin chain; W92 r370 precedent family).\n"
    "    # Machine-verified at prereg time\n"
    "    # (results/_r580bmb_w95_band_gate.py ADMIT receipt rc0 single\n"
    "    # state vs the 92-row pre-W95 table + live SEED_REGISTRY values\n"
    "    # + probe cluster 95_000..95_003 r335 discovery leg + N3-R1\n"
    "    # used-seed band 70_000..70_005 MSG-183x r529 mandatory leg;\n"
    "    # origin slot vacancy machine-checked; seat published=reserved\n"
    "    # MSG-20261002-1536-bmb pushed BEFORE this freeze per r565\n"
    "    # law). W96+ projection: A 235_004..237_003 CLEAN; B\n"
    "    # 57_701..57_900 CLEAN (next freezer must re-derive).\n"
    "    # NOT a re-pick (R250: W95 bands were never assigned).\n"
    "    95: {\"a\": (233_004, 235_003), \"b_exit\": (57_501, 57_700),\n"
    "         \"engine_owner\": \"bm-b\"},\n"
).encode("utf-8")

data = rd(PF)
if b'95: {"a": (233_004, 235_003)' in data:
    print("SKIP pf: already present")
else:
    data2 = insert_after_entry(
        data, '94: {"a": (231_004, 233_003)'.encode("utf-8"), PF_BLOCK, "pf",
        guard=lambda nxt: nxt.startswith(b"}"))
    assert data2.count(b'95: {"a": (233_004, 235_003)') == 1
    wr(PF, data2)
    print("pf: N1_BANDS[95] inserted (+%d bytes)" % len(PF_BLOCK))

# --- 3. n1 WAVE_CONFIGS[95] ----------------------------------------------------
N1_CFG_BLOCK = (
    "                       95: {\"batch\": \"PERPETUAL-N1-W95\",\n"
    "                            \"prereg\": (\"research/PERPETUAL_N1_W95_PREREG.md (wave-level frozen \"\n"
    "                                       \"pre-run; design = frozen v1 null calibration verbatim, \"\n"
    "                                       \"new seed bands only; EIGHTY-FIFTH ENGINE-OWNED WAVE BY \"\n"
    "                                       \"MACHINE-DERIVE (engine_owner rows 84 + candidate; prose \"\n"
    "                                       \"ordinal -1 drift disclosed since W80, r359 law), \"\n"
    "                                       \"own-series continuation per O-20261001-2355 sec.2 \"\n"
    "                                       \"(first-free-number law over the registered W94 row, \"\n"
    "                                       \"zero seat gaps: W2..W94 all registered, W94 restored \"\n"
    "                                       \"same window from the dead-r579 replay revert per \"\n"
    "                                       \"MSG-20261002-1533-bmb; seat published=reserved \"\n"
    "                                       \"MSG-20261002-1536-bmb PUSHED to origin BEFORE this \"\n"
    "                                       \"freeze per r565 early-visibility law), \"\n"
    "                                       \"engine_owner=bm-b, wave 95: BOTH SIDES ARITHMETIC \"\n"
    "                                       \"CONTINUATION from the registered W94 tails (A \"\n"
    "                                       \"233_004..235_003 CLEAN + B 57_501..57_700 CLEAN, \"\n"
    "                                       \"zero refusal points, honest forward walk, no skip, \"\n"
    "                                       \"no pin chain, W92 r370 precedent family; ADMIT \"\n"
    "                                       \"receipt results/_r580bmb_w95_band_gate.py rc0 \"\n"
    "                                       \"single state; W96+ projection: A 235_004..237_003 \"\n"
    "                                       \"CLEAN / B 57_701..57_900 CLEAN, disclosed for the \"\n"
    "                                       \"next freezer); W91 finalize LANDED (net chain head \"\n"
    "                                       \"564,748 = bm-b r579 one-pass, K=198,120 merged \"\n"
    "                                       \"pool) + THREE IN-FLIGHT UPSTREAM SEATS at this \"\n"
    "                                       \"freeze (W92 bm-c 12/12 burned finalize-pending + \"\n"
    "                                       \"W93 bm-b 12/12 burned finalize-pending + W94 bm-a \"\n"
    "                                       \"burn in flight, ALL REGISTERED post-heal -- \"\n"
    "                                       \"finalize merge loop stays FAIL-CLOSED r307 at run \"\n"
    "                                       \"time)\"),\n"
    "                            \"a_seed_base\": 233_004,        # law sec.4 W95 A: 233_004..235_003 (arithmetic continuation from W94 A tail)\n"
    "                            \"b_exit_seed_base\": 57_501,   # law sec.4 W95 B: 57_501..57_700 (arithmetic continuation from W94 B tail)\n"
    "                            \"shard_subdir\": \"n1_w95\", \"out_name\": \"n1_w95_results.json\",\n"
    "                            \"engine_owner\": \"bm-b\"},\n"
).encode("utf-8")

data = rd(N1)
if b'"shard_subdir": "n1_w95"' in data:
    print("SKIP n1 cfg: already present")
else:
    data2 = insert_after_entry(
        data, '"shard_subdir": "n1_w94", "out_name": "n1_w94_results.json",'.encode("utf-8"),
        N1_CFG_BLOCK, "n1cfg")
    assert data2.count(b'"shard_subdir": "n1_w95"') == 1
    wr(N1, data2)
    print("n1: WAVE_CONFIGS[95] inserted (+%d bytes)" % len(N1_CFG_BLOCK))

# --- 4. n1 selftest W95 materializer leg ---------------------------------------
LEG_MARK = "W95 materializer face (r580 bm-b freeze"
N1_LEG_BLOCK = (
    "\n"
    "    # --- W95 materializer face (r580 bm-b freeze, own-series law\n"
    "    #     under CEO de-throttle order O-20261001-2355 sec.2): bm-b's\n"
    "    #     thirty-second owned per machine-derive (engine_owner==bm-b\n"
    "    #     rows 31 + candidate); wave 95 = first free number after the\n"
    "    #     registered W94 row (zero seat gaps: W2..W94 all registered;\n"
    "    #     W94 restored same window from the dead-r579 replay revert,\n"
    "    #     heal receipt MSG-20261002-1533-bmb). EIGHTY-FIFTH engine\n"
    "    #     wave BY MACHINE-DERIVE (engine_owner rows 84 + candidate;\n"
    "    #     prose ordinal -1 drift disclosed since W80, r359 law).\n"
    "    #     Seat published=reserved MSG-20261002-1536-bmb pushed to\n"
    "    #     origin BEFORE this freeze per r565 law. ADMIT receipt\n"
    "    #     results/_r580bmb_w95_band_gate.py rc0 single state\n"
    "    #     (B94 registered W94).\n"
    "    _set_wave(95)\n"
    "    try:\n"
    "        assert WAVE_CONFIGS[95][\"a_seed_base\"] == pf.N1_BANDS[95][\"a\"][0], \\\n"
    "            \"W95 A band drift vs law mirror\"\n"
    "        assert WAVE_CONFIGS[95][\"b_exit_seed_base\"] == \\\n"
    "            pf.N1_BANDS[95][\"b_exit\"][0], \"W95 B band drift vs law mirror\"\n"
    "        assert WAVE_CONFIGS[95].get(\"engine_owner\") == \\\n"
    "            pf.N1_BANDS[95].get(\"engine_owner\") == \"bm-b\", \\\n"
    "            \"W95 engine_owner drift (law mirror parity)\"\n"
    "        w95_a = {A_SEED_BASE + j for j in range(A_N)}\n"
    "        w95_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}\n"
    "        assert not (w95_a & w95_b), \"W95 A/B band overlap\"\n"
    "        assert not (w95_a & reg_ints) and not (w95_b & reg_ints), \\\n"
    "            \"W95 hits SEED_REGISTRY\"\n"
    "        for nm, band in ((\"A\", w95_a), (\"B\", w95_b)):\n"
    "            assert not (band & v1_a) and not (band & v1_b), f\"W95 {nm} hits v1\"\n"
    "            assert not (band & w1_a) and not (band & w1_b), f\"W95 {nm} hits W1\"\n"
    "            assert not (band & probes), f\"W95 {nm} hits probe seeds\"\n"
    "        assert pf.N1_BANDS[90] == {\"a\": (223_004, 225_003),\n"
    "                                   \"b_exit\": (56_201, 56_400),\n"
    "                                   \"engine_owner\": \"bm-a\"}, \\\n"
    "            \"registered W90 row parity drift (r307 two-state; bm-a r579)\"\n"
    "        assert pf.N1_BANDS[91] == {\"a\": (225_004, 227_003),\n"
    "                                   \"b_exit\": (56_501, 56_700),\n"
    "                                   \"engine_owner\": \"bm-b\"}, \\\n"
    "            \"registered W91 row parity drift (r307 two-state; bm-b r578)\"\n"
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
    "        for wprev in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + [w for w in range(16, 95)]:\n"
    "            assert not (w95_a & {WAVE_CONFIGS[wprev][\"a_seed_base\"] + j\n"
    "                                 for j in range(A_N)}), f\"W95 A hits W{wprev}\"\n"
    "            assert not (w95_b & {WAVE_CONFIGS[wprev][\"b_exit_seed_base\"] + j\n"
    "                                  for j in range(B_N)}), f\"W95 B hits W{wprev}\"\n"
    "        assert not (w95_a & set(range(231_004, 233_004))) and \\\n"
    "            not (w95_b & set(range(57_301, 57_501))), (\n"
    "            \"W95 bands must clear the W94 registered bands (prior-wave \"\n"
    "            \"loop belt-and-braces)\")\n"
    "        n3r1_used95 = set(range(70_000, 70_006))\n"
    "        assert not (w95_a & n3r1_used95) and not (w95_b & n3r1_used95), \\\n"
    "            \"W95 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)\"\n"
    "        assert not (w95_a & lfc_actual12) and not (w95_b & lfc_actual12), \\\n"
    "            \"W95 bands must clear the lfc actual draw range\"\n"
    "        assert not (w95_a & options_actual12) and \\\n"
    "            not (w95_b & options_actual12), \\\n"
    "            \"W95 bands must clear the options_wave2 actual draw range\"\n"
    "        assert WAVE_CONFIGS[95][\"a_seed_base\"] == 233_004 == 233_003 + 1, (\n"
    "            \"W95 A must be the arithmetic continuation from the \"\n"
    "            \"registered W94 A tail\")\n"
    "        arith_a95 = set(range(233_004, 235_004))\n"
    "        assert not (arith_a95 & reg_ints), \\\n"
    "            \"W95 A window must be CLEAN (arithmetic continuation ADMIT face)\"\n"
    "        assert WAVE_CONFIGS[95][\"b_exit_seed_base\"] == 57_501 == 57_500 + 1, (\n"
    "            \"W95 B must be the arithmetic continuation from the \"\n"
    "            \"registered W94 B tail\")\n"
    "        arith_b95 = set(range(57_501, 57_701))\n"
    "        assert not (arith_b95 & reg_ints), \\\n"
    "            \"W95 B window must be CLEAN (arithmetic continuation ADMIT face)\"\n"
    "        assert _entry_shard_of(0, 12) == (\"PERPETUAL-N1-W95-SHARD-0\",\n"
    "                                          \"n1w95-0of12\"), \"W95 entry identity\"\n"
    "        assert _entry_shard_of(11, 12) == (\"PERPETUAL-N1-W95-SHARD-11\",\n"
    "                                          \"n1w95-11of12\")\n"
    "        assert SHARD_DIR.endswith(\"n1_w95\") and OUT.endswith(\n"
    "            \"n1_w95_results.json\"), \"W95 path drift\"\n"
    "        for wprev in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + [w for w in range(16, 95)]:\n"
    "            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(\n"
    "                PATHS.results_dir, \"p2cal_ext\",\n"
    "                WAVE_CONFIGS[wprev][\"shard_subdir\"])), \\\n"
    "                f\"W95 shard dir collides with W{wprev}\"\n"
    "        for _depw in range(17, 92):\n"
    "            assert os.path.exists(os.path.join(\n"
    "                OUT_DIR, WAVE_CONFIGS[_depw][\"out_name\"])), \\\n"
    "                f\"W95 finalize cumulative dep (W{_depw} output) missing\"\n"
    "        # finalize wave-set derivation face (r511 derive law):\n"
    "        # prior-wave set derives from registry keys below 95 (no 15).\n"
    "        # Single state: W2..W94 all registered (W94 heal-restored\n"
    "        # this window r580 bm-b after the dead-r579 replay revert).\n"
    "        _priors95 = sorted(w for w in WAVE_CONFIGS if w < 95)\n"
    "        assert _priors95 == \\\n"
    "            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\\n"
    "            [w for w in range(16, 95)], (\n"
    "            \"W95 prior-wave set must derive from registry keys (no 15; \"\n"
    "            \"W2..W94 all registered post-heal, single state)\")\n"
    "        assert os.path.exists(os.path.join(\n"
    "            PATHS.root, \"research\", \"PERPETUAL_N1_W95_PREREG.md\")), \\\n"
    "            \"W95 per-wave prereg missing (materializer requirement)\"\n"
    "        assert pickle.dumps(_worker_init), \"spawn-carrier unpicklable\"\n"
    "    finally:\n"
    "        _set_wave(2)\n"
).encode("utf-8")

data = rd(N1)
if LEG_MARK.encode("utf-8") in data:
    print("SKIP n1 leg: already present")
else:
    i = data.find(b"# --- W94 materializer face")
    assert i >= 0, "leg anchor: W94 leg not found"
    j = data.find(b"_set_wave(2)", i)
    assert j > i, "leg anchor: W94 leg finally not found"
    j_end = data.find(b"\n", j) + 1
    nxt = data[j_end:j_end + 40]
    assert b"W95" not in nxt[:40] and b"T-141" not in nxt[:20] or b"\n" == nxt[:1], \
        f"leg post-anchor guard: {nxt[:40]!r}"
    data2 = data[:j_end] + N1_LEG_BLOCK + data[j_end:]
    assert data2.count(LEG_MARK.encode("utf-8")) == 1
    wr(N1, data2)
    print("n1: W95 materializer leg inserted (+%d bytes)" % len(N1_LEG_BLOCK))

# --- 5. n1 selftest PASS-print W95 fragment -------------------------------------
FRAG_MARK = "law sec.4 W95 row, r580 bm-b]"
N1_FRAG_BLOCK = (
    "          \"+ W95 materializer face [same guard set, dep=W17..W91 outputs \"\n"
    "          \"ALL PRESENT (landed chain head 564,748, K=198,120, W91 bm-b \"\n"
    "          \"r579 one-pass; THREE in-flight upstream seats at freeze: W92 \"\n"
    "          \"bm-c 12/12 burned finalize-pending + W93 bm-b 12/12 burned \"\n"
    "          \"finalize-pending + W94 bm-a burn in flight, ALL REGISTERED \"\n"
    "          \"post-heal, finalize merge loop stays FAIL-CLOSED r307 at run \"\n"
    "          \"time), EIGHTY-FIFTH ENGINE-OWNED WAVE BY MACHINE-DERIVE \"\n"
    "          \"(engine_owner rows 84 + candidate; prose ordinal -1 drift \"\n"
    "          \"disclosed since W80, r359 law) bm-b's THIRTY-SECOND owned \"\n"
    "          \"claim per machine-derive (engine_owner==bm-b rows 31 + \"\n"
    "          \"candidate), engine_owner=bm-b per engine de-throttle law \"\n"
    "          \"O-20261001-2355 sec.2 own-continuous-series (wave 95 = first \"\n"
    "          \"FREE number after the registered W94 row, zero seat gaps; W94 \"\n"
    "          \"registration heal-restored same window after the dead-r579 \"\n"
    "          \"replay revert per MSG-20261002-1533-bmb; seat \"\n"
    "          \"published=reserved MSG-20261002-1536-bmb pushed BEFORE the \"\n"
    "          \"freeze per r565 law), BOTH SIDES ARITHMETIC CONTINUATION \"\n"
    "          \"from the registered W94 tails no skip (A 233_004..235_003 + \"\n"
    "          \"B 57_501..57_700 both CLEAN zero refusal points, honest \"\n"
    "          \"forward walk, W92 r370 precedent family; ADMIT receipt \"\n"
    "          \"results/_r580bmb_w95_band_gate.py rc0 single state; W96+ \"\n"
    "          \"projection A 235_004..237_003 CLEAN / B 57_701..57_900 CLEAN \"\n"
    "          \"disclosed for the next freezer; not a free pick -- R250; \"\n"
    "          \"probe-seed cluster leg, N3-R1 used-seed leg, \"\n"
    "          \"law sec.4 W95 row, r580 bm-b] \"\n"
).encode("utf-8")

data = rd(N1)
if FRAG_MARK.encode("utf-8") in data:
    print("SKIP n1 frag: already present")
else:
    anchor = b"cluster leg, law sec.4 W94 row, r580 bm-a] \""
    i = data.find(anchor)
    assert i >= 0, "frag anchor: W94 fragment end not found"
    j = data.find(b"\n", i) + 1
    nxt = data[j:j + 30]
    assert b'"+ T-141 s2' in nxt, f"frag post-anchor guard: {nxt[:30]!r}"
    data2 = data[:j] + N1_FRAG_BLOCK + data[j:]
    assert data2.count(FRAG_MARK.encode("utf-8")) == 1
    wr(N1, data2)
    print("n1: W95 PASS fragment inserted (+%d bytes)" % len(N1_FRAG_BLOCK))

print("ALL FIVE FACES STAGED OK (canon + pf + n1 cfg + n1 leg + n1 frag)")
