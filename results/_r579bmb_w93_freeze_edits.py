# -*- coding: utf-8 -*-
"""r579 bm-b W93 freeze five-face edits (r560-law generator; r578 pattern).

FIX-A (r565 law): origin-blob equality assertion on every shared source
file BEFORE editing -- any drift = collision signal -> hard abort.
Anchored insertions, idempotent, insertion-not-replace checked:
  1. canon W93 bullet  -> research/PERPETUAL_FACES.md, after the W92 bullet
  2. pf N1_BANDS[93]   -> scripts/perpetual_faces.py, after the [92] entry
  3. n1 WAVE_CONFIGS[93] -> scripts/perpetual_faces_n1.py, after the 92 entry
  4. n1 selftest W93 materializer leg -> after the W92 leg
  5. n1 selftest PASS-print W93 fragment -> after the W92 fragment
Pure insertion only; any anchor mismatch -> hard abort (r560 FIX-A law).
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANON = os.path.join(ROOT, "research", "PERPETUAL_FACES.md")
PF = os.path.join(ROOT, "scripts", "perpetual_faces.py")
N1 = os.path.join(ROOT, "scripts", "perpetual_faces_n1.py")

MARK = "PERPETUAL-N1-W93"
CREAT = 0x08000000


def rd(p):
    with open(p, "rb") as f:
        return f.read()


def wr(p, b):
    with open(p, "wb") as f:
        f.write(b)


def fix_a(path, own_mark):
    """r565 FIX-A: local HEAD blob must equal origin blob before editing.
    Re-run (idempotent) mode: if the local file already carries THIS
    machine's staged W93 marks (partial previous run) and origin does NOT,
    that is the expected own-staged state -- pass; anything else aborts."""
    r = subprocess.run(["git", "fetch", "origin"], cwd=ROOT,
                       capture_output=True, creationflags=CREAT)
    r = subprocess.run(["git", "show", "origin/main:%s" % path], cwd=ROOT,
                       capture_output=True, creationflags=CREAT)
    assert r.returncode == 0, "FIX-A: origin read failed %s" % path
    local = rd(os.path.join(ROOT, path))
    if r.stdout == local:
        print("FIX-A ok: %s == origin/main blob" % path)
        return
    local_s = local.decode("utf-8", "replace")
    origin_s = r.stdout.decode("utf-8", "replace")
    assert own_mark in local_s and own_mark not in origin_s, \
        "FIX-A ABORT: local %s != origin AND own staged mark state invalid " \
        "(foreign collision signal)" % path
    print("FIX-A ok (own-staged re-run mode): %s" % path)


def insert_after(data, needle, block, tag, guard_banned=(b"94", b"95")):
    i = data.find(needle.encode("utf-8"))
    assert i >= 0, f"{tag}: anchor needle not found: {needle[:60]}"
    j = data.find(b"\n", i) + 1
    assert j > i, f"{tag}: anchor line has no newline"
    nxt = data[j:j + 60]
    for banned in guard_banned:
        assert banned not in nxt, \
            f"{tag}: post-anchor guard tripped ({nxt!r})"
    out = data[:j] + block + data[j:]
    return out


def insert_after_entry(data, needle, block, tag):
    i = data.find(needle.encode("utf-8"))
    assert i >= 0, f"{tag}: anchor needle not found: {needle[:60]}"
    j = data.find(b"\n", i) + 1
    k = data.find(b"\n", j) + 1
    mid = data[j:k]
    assert b"engine_owner" in mid, \
        f"{tag}: line after needle is not an entry close ({mid[:60]!r})"
    nxt = data[k:k + 40]
    assert b"94:" not in nxt, f"{tag}: post-anchor W94 row guard ({nxt!r})"
    out = data[:k] + block + data[k:]
    return out


# --- 1. canon bullet -----------------------------------------------------------
CANON_BLOCK = (
    "\n"
    "- N1 波93（r579 bm-b 冻·prereg 时展行）：**第八十三枚引擎波·bm-b 第三十一枚自有波〔机面 derive：engine_owner 行 82+本候选／engine_owner==bm-b 行 30+本候选〕**·engine_owner=bm-b·SATURATION_ENGINE_LAW §1/§2 同 W10-W92 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-b 实例=tick 架构 r535 律——冻结 commit 后下一 tick 新进程重读活树自见新行=免杀重启免做·W44/W45/W48/W54/W57/W62/W64/W68/W73/W75/W77/W81/W84/W86/W89/W91 同窗实证·点火验证唯一证据=产物增长面 r325 律】·【never-dry 供给律常设步·**波号 93=注册表 W91 行后首个自由号·跳过 bm-c 已公示 W92 席**（MSG-20261002-1447-bmc·published=reserved r518-① 律）；**本机 W92 机闸 derive 逐位同带=r530 确定性交叉验证→zero-cost 让路**（r511 origin-first·让路回执+同窗 W93 席位公示=**MSG-20261002-1510-bmb**〔r565 yield-then-reoccupy 律·先于冻结 commit 推 origin〕）；**W92=bm-c 已注册（r370 五面冻结 08bc6507b）·引擎烧录在飞·finalize 未落账**】·本窗实况=**W91 finalize 已落账（净链头 564,748·K=198,120 合并池·bm-b r579 one-pass）+一在飞上游席（W92 bm-c）=本波 finalize 链序前置在飞（跑时按 registry 键 derive 复核·FAIL-CLOSED r307 两态律）**·**带位（r535 机闸 derive 律·活注册表机证·三态收敛门·ADMIT 回执=results/_r579bmb_w93_band_gate.py 双态 rc0〔A92 席位公示窗/B92 已注册窗〕）**：**A-ext seed=229_004..231_003**（**A 面 skip-past-published 链**==W91 行 A 尾→W92 席位带 227_004..229_003→首净窗·步长 2_000·CLEAN 零拒绝点〔r518-① 先例族〕）；**B-ext exit seed=57_101..57_300**（**B 侧双命中钉死链**：算术位 56_701..56_900==W92 席位带→skip→56_901..57_100 于带内撞 **SEED_REGISTRY xstock_tilt_h20=57_000〔中位 99/199 非边缘端点〕+xstock_tilt_h10=57_100〔上缘端点 199/199〕**→**D-20261002-05 集团钉死=越 hit 起窗** 57_001..57_200 复撞 57_100〔中位 99/199〕→再越 hit 起窗 **57_101..57_300 CLEAN**〔窗步链读法自拒窗起=57_101..57_300 **收敛同解**·57_100=拒窗上缘端点=两读法重启点重合·无分叉面·W63 双命中族零分叉例·W68-B 中位先例族正锚〕）·【机证净空——leg0 九十行注册表形（90 注册行·表尾=W92 bm-c r370）+leg0b 本机 W93 席位 MSG 在场机验+外机 W93 席位零命中+leg1 双侧 skip-past-published/钉死链 CLEAN+leg2 A/B 首净窗==候选恒等+leg3 origin 号位净空机验（pf 行+WAVE_CONFIGS+prereg 路径三查）+SEED_REGISTRY 全键 160 值+N3-R1 已用种子带腿（70_000..70_005·MSG-183x r529 强制）+探针种子簇腿（95_000..95_003·r335 强制）+N2/N4+N2-W15 探针点+lfc/options 实际流腿】·**W94+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 231_004..233_003 **CLEAN**；B 57_301..57_500 **CLEAN**（双侧算术预期零拒绝点）。R250：W93 带从未指派·测量面零结果可钓·banned gate ADMIT 0 matched（W93 prereg §0.5）·per-wave prereg=research/PERPETUAL_N1_W93_PREREG.md（冻结件·本波 §5 锚=W91 finalize 实测值·锚滚动律自 W76 滚动至 W91）·finalize 链序前置=起草窗一在飞上游席（W92 bm-c·FAIL-CLOSED r307 两态律跑时复核）。\n"
).encode("utf-8")

fix_a("research/PERPETUAL_FACES.md", "波93（r579 bm-b 冻")
data = rd(CANON)
if "波93（r579 bm-b 冻".encode("utf-8") in data:
    print("SKIP canon: already present")
else:
    data = insert_after(data, "N1 波92（r370 bm-c 冻", CANON_BLOCK, "canon")
    wr(CANON, data)
    print("canon: W93 bullet inserted (+%d bytes)" % len(CANON_BLOCK))

# --- 2. pf N1_BANDS[93] ---------------------------------------------------------
PF_BLOCK = (
    "    # EIGHTY-THIRD ENGINE-OWNED WAVE BY MACHINE-DERIVE (r579 bm-b\n"
    "    # freeze): engine_owner rows 82 + candidate; bm-b's\n"
    "    # thirty-first owned per machine-derive (engine_owner==bm-b\n"
    "    # rows 30 + candidate). Wave 93 = first free number after the\n"
    "    # registered W91 row SKIPPING the bm-c-declared W92 seat\n"
    "    # (MSG-20261002-1447-bmc, published=reserved r518-1; this\n"
    "    # machine's W92 derive was bitwise-identical -> ZERO-COST YIELD\n"
    "    # per r511 origin-first; yield receipt + W93 seat published\n"
    "    # same-window MSG-20261002-1510-bmb per r565 law).\n"
    "    # W92 registered mid-window by bm-c r370 (08bc6507b), burn in\n"
    "    # flight at this freeze -- ONE in-flight upstream seat, finalize\n"
    "    # merge loop stays FAIL-CLOSED r307 at run time.\n"
    "    # A-SIDE SKIP-PAST-PUBLISHED CHAIN (r518-1): W91 tail 227_003 ->\n"
    "    # W92 seat A 227_004..229_003 -> first clean 229_004..231_003\n"
    "    # (= W92 seat A end + 1) CLEAN.\n"
    "    # B-SIDE DOUBLE-HIT PIN CHAIN: 56_701..56_900 == W92 seat B ->\n"
    "    # skip -> 56_901..57_100 REFUSED in-band at SEED_REGISTRY\n"
    "    # xstock_tilt_h20=57_000 (median position 99/199, non-edge) AND\n"
    "    # xstock_tilt_h10=57_100 (upper-edge endpoint 199/199) ->\n"
    "    # D-20261002-05 pin: PAST-HIT restart 57_001..57_200 REFUSED\n"
    "    # again at 57_100 (median 99/199) -> restart 57_101..57_300\n"
    "    # CLEAN. Window-step-chain reading from the refused arithmetic\n"
    "    # window (57_101..57_300) CONVERGES -- 57_100 sits at the\n"
    "    # refused window upper endpoint, both restart readings coincide,\n"
    "    # no fork face (W63 double-hit family, zero divergence).\n"
    "    # Machine-verified at prereg time\n"
    "    # (results/_r579bmb_w93_band_gate.py ADMIT receipt, dual-state\n"
    "    # rc0 [A92 seat-published window / B92 registered window] vs the\n"
    "    # 90-row pre-W93 table + live SEED_REGISTRY values + probe\n"
    "    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed\n"
    "    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin slot\n"
    "    # vacancy machine-checked). W94+ projection: A 231_004..233_003\n"
    "    # CLEAN; B 57_301..57_500 CLEAN (next freezer must re-derive).\n"
    "    93: {\"a\": (229_004, 231_003), \"b_exit\": (57_101, 57_300),\n"
    "         \"engine_owner\": \"bm-b\"},\n"
).encode("utf-8")

fix_a("scripts/perpetual_faces.py", '93: {"a": (229_004, 231_003)')
data = rd(PF)
if b'93: {"a": (229_004, 231_003)' in data:
    print("SKIP pf: already present")
else:
    data = insert_after_entry(
        data,
        '92: {"a": (227_004, 229_003), "b_exit": (56_701, 56_900),',
        PF_BLOCK, "pf")
    wr(PF, data)
    print("pf: N1_BANDS[93] inserted (+%d bytes)" % len(PF_BLOCK))

# --- 3. n1 WAVE_CONFIGS[93] ------------------------------------------------------
N1_CFG_BLOCK = (
    "                       93: {\"batch\": \"PERPETUAL-N1-W93\",\n"
    "                            \"prereg\": (\"research/PERPETUAL_N1_W93_PREREG.md (wave-level frozen \"\n"
    "                                       \"pre-run; design = frozen v1 null calibration verbatim, \"\n"
    "                                       \"new seed bands only; EIGHTY-THIRD ENGINE-OWNED WAVE BY \"\n"
    "                                       \"MACHINE-DERIVE (engine_owner rows 82 + candidate; prose \"\n"
    "                                       \"ordinal -1 drift disclosed since W80, r359 law), \"\n"
    "                                       \"own-series continuation per O-20261001-2355 sec.2 \"\n"
    "                                       \"(first-free-number law over the registered W91 row \"\n"
    "                                       \"SKIPPING the bm-c-declared W92 seat \"\n"
    "                                       \"MSG-20261002-1447-bmc; this machine's W92 derive was \"\n"
    "                                       \"bitwise-identical -> ZERO-COST YIELD per r511 \"\n"
    "                                       \"origin-first; yield receipt + seat published=reserved \"\n"
    "                                       \"MSG-20261002-1510-bmb PUSHED to origin BEFORE this \"\n"
    "                                       \"freeze per r565 early-visibility law), \"\n"
    "                                       \"engine_owner=bm-b, wave 93: A-SIDE \"\n"
    "                                       \"SKIP-PAST-PUBLISHED CHAIN (W91 tail -> W92 seat A -> \"\n"
    "                                       \"first clean A 229_004..231_003 CLEAN) + \"\n"
    "                                       \"B-SIDE DOUBLE-HIT PIN CHAIN (56_701..56_900 == W92 \"\n"
    "                                       \"seat B -> skip -> 56_901..57_100 REFUSED in-band at \"\n"
    "                                       \"SEED_REGISTRY xstock_tilt_h20=57_000 median position \"\n"
    "                                       \"99/199 non-edge AND xstock_tilt_h10=57_100 upper-edge \"\n"
    "                                       \"endpoint -> D-20261002-05 pin: past-hit restart \"\n"
    "                                       \"57_001..57_200 REFUSED again at 57_100 median -> \"\n"
    "                                       \"restart 57_101..57_300 CLEAN; window-step-chain \"\n"
    "                                       \"reading converges, no fork face; ADMIT receipt \"\n"
    "                                       \"results/_r579bmb_w93_band_gate.py dual-state rc0; \"\n"
    "                                       \"W94+ projection: A 231_004..233_003 CLEAN / B \"\n"
    "                                       \"57_301..57_500 CLEAN, disclosed for the next \"\n"
    "                                       \"freezer); W91 finalize LANDED (net chain head \"\n"
    "                                       \"564,748 = bm-b r579 one-pass, K=198,120 merged \"\n"
    "                                       \"pool) + ONE IN-FLIGHT UPSTREAM SEAT at this \"\n"
    "                                       \"freeze (W92 bm-c registered, burn in flight, \"\n"
    "                                       \"finalize pending -- finalize merge loop stays \"\n"
    "                                       \"FAIL-CLOSED r307 at run time)\"),\n"
    "                            \"a_seed_base\": 229_004,        # law sec.4 W93 A: 229_004..231_003 (skip-past-published chain)\n"
    "                            \"b_exit_seed_base\": 57_101,   # law sec.4 W93 B: 57_101..57_300 (double-hit pin D-20261002-05 at 57_000/57_100)\n"
    "                            \"shard_subdir\": \"n1_w93\", \"out_name\": \"n1_w93_results.json\",\n"
    "                            \"engine_owner\": \"bm-b\"},\n"
).encode("utf-8")

fix_a("scripts/perpetual_faces_n1.py", "PERPETUAL-N1-W93")
data = rd(N1)
if MARK.encode("utf-8") in data:
    print("SKIP n1 cfg: already present")
else:
    data = insert_after_entry(
        data,
        '"shard_subdir": "n1_w92", "out_name": "n1_w92_results.json",',
        N1_CFG_BLOCK, "n1cfg")
    wr(N1, data)
    print("n1: WAVE_CONFIGS[93] inserted (+%d bytes)" % len(N1_CFG_BLOCK))

# --- 4. n1 selftest W93 materializer leg ----------------------------------------
LEG_MARK = "W93 materializer face (r579 bm-b freeze"
N1_LEG_BLOCK = (
    "    # --- W93 materializer face (r579 bm-b freeze, own-series law\n"
    "    #     under CEO de-throttle order O-20261001-2355 sec.2): bm-b's\n"
    "    #     thirty-first owned per machine-derive (engine_owner==bm-b\n"
    "    #     rows 30 + candidate); wave 93 = first free number after the\n"
    "    #     registered W91 row SKIPPING the bm-c-declared W92 seat\n"
    "    #     (MSG-20261002-1447-bmc; this machine's W92 derive was\n"
    "    #     bitwise-identical -> ZERO-COST YIELD per r511 origin-first;\n"
    "    #     yield receipt + W93 seat published=reserved\n"
    "    #     MSG-20261002-1510-bmb pushed to origin BEFORE this freeze\n"
    "    #     per r565 law). EIGHTY-THIRD engine wave BY MACHINE-DERIVE\n"
    "    #     (engine_owner rows 82 + candidate; prose ordinal -1 drift\n"
    "    #     disclosed since W80, r359 law). ADMIT receipt\n"
    "    #     results/_r579bmb_w93_band_gate.py dual-state rc0\n"
    "    #     (A92 seat-published window / B92 registered window).\n"
    "    _set_wave(93)\n"
    "    try:\n"
    "        assert WAVE_CONFIGS[93][\"a_seed_base\"] == pf.N1_BANDS[93][\"a\"][0], \\\n"
    "            \"W93 A band drift vs law mirror\"\n"
    "        assert WAVE_CONFIGS[93][\"b_exit_seed_base\"] == \\\n"
    "            pf.N1_BANDS[93][\"b_exit\"][0], \"W93 B band drift vs law mirror\"\n"
    "        assert WAVE_CONFIGS[93].get(\"engine_owner\") == \\\n"
    "            pf.N1_BANDS[93].get(\"engine_owner\") == \"bm-b\", \\\n"
    "            \"W93 engine_owner drift (law mirror parity)\"\n"
    "        w93_a = {A_SEED_BASE + j for j in range(A_N)}\n"
    "        w93_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}\n"
    "        assert not (w93_a & w93_b), \"W93 A/B band overlap\"\n"
    "        assert not (w93_a & reg_ints) and not (w93_b & reg_ints), \\\n"
    "            \"W93 hits SEED_REGISTRY\"\n"
    "        for nm, band in ((\"A\", w93_a), (\"B\", w93_b)):\n"
    "            assert not (band & v1_a) and not (band & v1_b), f\"W93 {nm} hits v1\"\n"
    "            assert not (band & w1_a) and not (band & w1_b), f\"W93 {nm} hits W1\"\n"
    "            assert not (band & probes), f\"W93 {nm} hits probe seeds\"\n"
    "        assert pf.N1_BANDS[88] == {\"a\": (219_004, 221_003),\n"
    "                                   \"b_exit\": (55_701, 55_900),\n"
    "                                   \"engine_owner\": \"bm-c\"}, \\\n"
    "            \"registered W88 row parity drift (r307 two-state; bm-c r368)\"\n"
    "        assert pf.N1_BANDS[89] == {\"a\": (221_004, 223_003),\n"
    "                                   \"b_exit\": (56_001, 56_200),\n"
    "                                   \"engine_owner\": \"bm-b\"}, \\\n"
    "            \"registered W89 row parity drift (r307 two-state; bm-b r578)\"\n"
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
    "        for wprev in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + [w for w in range(16, 93)]:\n"
    "            assert not (w93_a & {WAVE_CONFIGS[wprev][\"a_seed_base\"] + j\n"
    "                                 for j in range(A_N)}), f\"W93 A hits W{wprev}\"\n"
    "            assert not (w93_b & {WAVE_CONFIGS[wprev][\"b_exit_seed_base\"] + j\n"
    "                                  for j in range(B_N)}), f\"W93 B hits W{wprev}\"\n"
    "        assert not (w93_a & set(range(227_004, 229_004))) and \\\n"
    "            not (w93_b & set(range(56_701, 56_901))), \\\n"
    "            \"W93 bands must clear the W92 seat/registered band (r518-1)\"\n"
    "        n3r1_used93 = set(range(70_000, 70_006))\n"
    "        assert not (w93_a & n3r1_used93) and not (w93_b & n3r1_used93), \\\n"
    "            \"W93 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)\"\n"
    "        assert not (w93_a & lfc_actual12) and not (w93_b & lfc_actual12), \\\n"
    "            \"W93 bands must clear the lfc actual draw range\"\n"
    "        assert not (w93_a & options_actual12) and \\\n"
    "            not (w93_b & options_actual12), \\\n"
    "            \"W93 bands must clear the options_wave2 actual draw range\"\n"
    "        assert WAVE_CONFIGS[93][\"a_seed_base\"] == 229_004 == \\\n"
    "            pf.N1_BANDS[92][\"a\"][1] + 1, \\\n"
    "            \"W93 A must start past the W92 seat/registered band \" \\\n"
    "            \"(skip-past-published chain: W92 A end + 1 = 229_004; \" \\\n"
    "            \"window 229_004..231_003 CLEAN)\"\n"
    "        arith_a93 = set(range(229_004, 231_004))\n"
    "        assert not (arith_a93 & reg_ints), \\\n"
    "            \"W93 A window must be CLEAN (skip-past-published ADMIT face)\"\n"
    "        arith_b93 = set(range(56_901, 57_101))\n"
    "        b_hits93 = sorted(p for p in arith_b93 if p in reg_ints)\n"
    "        assert b_hits93 == [57_000, 57_100], \\\n"
    "            \"W93 B pre-window must hit exactly [57_000, 57_100] \" \\\n"
    "            \"(median 99/199 + upper-edge endpoint)\"\n"
    "        restart1_b93 = set(range(57_001, 57_201))\n"
    "        r1_hits93 = sorted(p for p in restart1_b93 if p in reg_ints)\n"
    "        assert r1_hits93 == [57_100], \\\n"
    "            \"W93 B restart-1 window 57_001..57_200 must hit exactly \" \\\n"
    "            \"[57_100] again (median 99/199)\"\n"
    "        assert WAVE_CONFIGS[93][\"b_exit_seed_base\"] == 57_101 == 57_100 + 1, \\\n"
    "            \"W93 B must start at the 57_100 hit + 1 (D-20261002-05 \" \\\n"
    "            \"pin: past-hit start-window chain, double-hit family)\"\n"
    "        assert not (w93_b & reg_ints), \\\n"
    "            \"W93 B restart window 57_101..57_300 must be CLEAN\"\n"
    "        chain_b93 = set(range(57_101, 57_301))\n"
    "        assert chain_b93 == w93_b, \"W93 B window-step-chain convergence face\"\n"
    "        assert _entry_shard_of(0, 12) == (\"PERPETUAL-N1-W93-SHARD-0\",\n"
    "                                          \"n1w93-0of12\"), \"W93 entry identity\"\n"
    "        assert _entry_shard_of(11, 12) == (\"PERPETUAL-N1-W93-SHARD-11\",\n"
    "                                          \"n1w93-11of12\")\n"
    "        assert SHARD_DIR.endswith(\"n1_w93\") and OUT.endswith(\n"
    "            \"n1_w93_results.json\"), \"W93 path drift\"\n"
    "        for wprev in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + [w for w in range(16, 93)]:\n"
    "            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(\n"
    "                PATHS.results_dir, \"p2cal_ext\",\n"
    "                WAVE_CONFIGS[wprev][\"shard_subdir\"])), \\\n"
    "                f\"W93 shard dir collides with W{wprev}\"\n"
    "        assert sorted(w for w in WAVE_CONFIGS if w < 93) == \\\n"
    "            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\\n"
    "            [w for w in range(16, 93)], \\\n"
    "            \"W93 prior-wave set must derive from registry keys (no 15; \" \\\n"
    "            \"incl. 48..92 -- all registered incl. W90/W91/W92, \" \\\n"
    "            \"FAIL-CLOSED)\"\n"
    "        # W93 finalize cumulative deps: W17..W91 outputs ALL PRESENT\n"
    "        # (landed chain head 564,748, K=198,120, W91 bm-b r579 landed;\n"
    "        # W92 bm-c = ONE in-flight upstream seat -- the finalize merge\n"
    "        # loop derives the wave set from registry keys at run time and\n"
    "        # stays FAIL-CLOSED on the not-yet-finalized seat, r307\n"
    "        # two-state law).\n"
    "        for _depw in range(17, 92):\n"
    "            assert os.path.exists(os.path.join(\n"
    "                OUT_DIR, WAVE_CONFIGS[_depw][\"out_name\"])), \\\n"
    "                f\"W93 finalize cumulative dep (W{_depw} output) missing\"\n"
    "        assert os.path.exists(os.path.join(\n"
    "            PATHS.root, \"research\", \"PERPETUAL_N1_W93_PREREG.md\")), \\\n"
    "            \"W93 per-wave prereg missing (materializer requirement)\"\n"
    "        assert pickle.dumps(_worker_init), \"spawn-carrier unpicklable\"\n"
    "    finally:\n"
    "        _set_wave(2)\n"
    "\n"
).encode("utf-8")

data = rd(N1)
if LEG_MARK.encode("utf-8") in data:
    print("SKIP n1 leg: already present")
else:
    i = data.find("W92 per-wave prereg missing (materializer requirement)"
                  .encode("utf-8"))
    assert i >= 0, "leg anchor: W92 prereg assert not found"
    j = data.find(b"        _set_wave(2)\n", i)
    assert j > i, "leg anchor: W92 finally not found"
    j_end = j + len(b"        _set_wave(2)\n")
    nxt = data[j_end:j_end + 40]
    assert b"W93" not in nxt and b"W94" not in nxt, \
        f"leg post-anchor guard: {nxt!r}"
    out = data[:j_end] + N1_LEG_BLOCK + data[j_end:]
    wr(N1, out)
    print("n1: W93 materializer leg inserted (+%d bytes)" % len(N1_LEG_BLOCK))

# --- 5. n1 selftest PASS-print W93 fragment -------------------------------------
FRAG_MARK = "law sec.4 W93 row, r579 bm-b]"
N1_FRAG_BLOCK = (
    "          \"+ W93 materializer face [same guard set, dep=W17..W91 \"\n"
    "          \"outputs ALL PRESENT (landed chain head 564,748, K=198,120, \"\n"
    "          \"W91 bm-b r579 one-pass; W92 bm-c = ONE in-flight upstream \"\n"
    "          \"seat at freeze (registered, burn in flight; FAIL-CLOSED \"\n"
    "          \"r307 at run time), EIGHTY-THIRD ENGINE-OWNED WAVE BY \"\n"
    "          \"MACHINE-DERIVE (engine_owner rows 82 + candidate; prose \"\n"
    "          \"ordinal -1 drift disclosed since W80, r359 law) bm-b's \"\n"
    "          \"THIRTY-FIRST owned claim per machine-derive (engine_owner==bm-b \"\n"
    "          \"rows 30 + candidate), engine_owner=bm-b per engine de-throttle \"\n"
    "          \"law O-20261001-2355 sec.2 own-continuous-series (wave 93 = \"\n"
    "          \"first FREE number SKIPPING the bm-c-declared W92 seat \"\n"
    "          \"MSG-20261002-1447-bmc; this machine's W92 derive was \"\n"
    "          \"bitwise-identical -> ZERO-COST YIELD per r511 origin-first; \"\n"
    "          \"yield receipt + seat published=reserved MSG-20261002-1510-bmb \"\n"
    "          \"pushed BEFORE the freeze per r565 yield-then-reoccupy law), \"\n"
    "          \"A-SIDE SKIP-PAST-PUBLISHED CHAIN (W91 tail -> W92 seat \"\n"
    "          \"227_004..229_003 -> first clean window 229_004..231_003 \"\n"
    "          \"CLEAN) + B-SIDE DOUBLE-HIT PIN CHAIN per D-20261002-05 \"\n"
    "          \"(arithmetic 56_901..57_100 REFUSED in-band at SEED_REGISTRY \"\n"
    "          \"xstock_tilt_h20=57_000 median position 99/199 non-edge AND \"\n"
    "          \"xstock_tilt_h10=57_100 upper-edge endpoint -> past-hit \"\n"
    "          \"restart 57_001..57_200 REFUSED again at 57_100 median -> \"\n"
    "          \"restart 57_101..57_300 CLEAN; window-step-chain reading \"\n"
    "          \"CONVERGES, no fork face, W63 double-hit family; ADMIT \"\n"
    "          \"receipt results/_r579bmb_w93_band_gate.py dual-state rc0 \"\n"
    "          \"[A92/B92]; W94+ projection A 231_004..233_003 CLEAN / B \"\n"
    "          \"57_301..57_500 CLEAN disclosed for the next freezer; not a \"\n"
    "          \"free pick -- R250), N3-R1 used-seed leg, probe-seed cluster \"\n"
    "          \"leg, law sec.4 W93 row, r579 bm-b] \"\n"
).encode("utf-8")

data = rd(N1)
if FRAG_MARK.encode("utf-8") in data:
    print("SKIP n1 frag: already present")
else:
    # insert BEFORE the T-141 exemption fragment = right after the LAST
    # wave fragment (print order: ...W91, W92, W90, [W93 here], T-141 --
    # bm-c anchored their W92 frag between W91 and W90)
    i = data.find('          "+ T-141 s2 '.encode("utf-8"))
    assert i >= 0, "frag anchor: T-141 fragment start not found"
    pre = data[max(0, i - 120):i]
    assert b"cluster leg, law sec.4 W9" in pre, \
        f"frag pre-anchor guard: {pre!r}"
    out = data[:i] + N1_FRAG_BLOCK + data[i:]
    wr(N1, out)
    print("n1: W93 PASS fragment inserted (+%d bytes)" % len(N1_FRAG_BLOCK))

print("ALL FIVE FACES STAGED OK (canon + pf + n1 cfg + n1 leg + n1 frag)")
