# -*- coding: utf-8 -*-
# r975 closeout: state + heartbeat + round report writes (bloodline of
# _r974bmc_closeout.py per bm-c closeout lineage).
import json, time, datetime
sys_tz = datetime.datetime.now().astimezone()
now = datetime.datetime.now()
# UTC offset face: strftime("%z") -> "+0800" -> insert colon (ISO 8601, smoke F7 contract).
# PIT (fixed this window): strftime("%H:%M") returns wall time, NOT the offset.
_zoff = sys_tz.strftime("%z")
assert _zoff == "+0800", f"unexpected offset {_zoff}"
iso = now.strftime("%Y-%m-%dT%H:%M:%S") + _zoff[:3] + ":" + _zoff[3:]
import psutil
ram_free = round(psutil.virtual_memory().available / 1e9, 1)

DID = ("r975: (1) S0-1 anchor bm-c + round-zero probe py_faces=6 orphans=2 zero-kill; origin 0/0 at open "
       "(tree=7 own runtime JSONs only); (2) S0.5 dual-delta FALSE both (dec fb5825cb / ord a20281ea, unacked=0) "
       "+ S7 double-scan zero new rows; (3) S1 smoke 49/49; satengine ALIVE (W233 burn complete 12/12 local+remote); "
       "S2 boards CLEAR (jobs 0, queues CLEAR, collision probe CLEAR); (4) PRODUCT = W234 prereg derive PREP landed "
       "(r971-precedent honest split, seat-law first action): facts machine-frozen results/_w234bmc_facts.json "
       "(W233 finalize anchors ledger 936,389/prev 934,189+2,200/K 510,520/mu -0.09276956/sigma 0.24506207/"
       "w233-only -0.09893318/absdiff 0.0062/p95 0.3027/KL -0.0002 line 1.1922 pre 1.1924 n_eff 934,189/se_mu 0.000343 "
       "+ W234 bands A 529604_531603/B 531604_531803 per ADMIT receipt + base blob 933e3ceea 25606B sha16 79be261672844184 "
       "+ W233 RAM ~1.1/win 2026-10-13 18:4x faces + hygiene inbox W234 foreign=0/pf rows 0/prereg-on-origin 0) + "
       "R34 authored 46/46 groups (results/_w234bmc_r34_data.py: all values machine-anchored zero transcription; "
       "@L32@/@T32@ heritage tokens; NINETY-FOURTH staircase; W235+ projections 531_604..533_603/531_804..532_003; "
       "chain leg W233 splice 0ca920362 dead-r973 + finalize 19:5x r974; seat MSG-20261013-1955-bmc origin 260217d39) + "
       "subgen m31 bloodline clone results/_w234bmc_subgen.py (SUB33 extract 46 from committed _w233bmc_prereg_derive.py "
       "with 4-var resolution) + SUB BLOCK EMITTED results/_w234bmc_sub_block.py 21654B py_compile PASS + 14 anchor "
       "spot-checks green (A-ext/B-ext seeds, staircase-94 x2, proj235 x2, @L32@ x7, 936,389 x3, 512,720, BinOp specials); "
       "(5) PITFALL r958 3rd instance caught+fixed same-window: ast.Dict.keys attribute-vs-call transcription slip in "
       "cloned resolve_node (node.keys() TypeError silently converted to fake extract-fail by except) -- EXC-print gate "
       "added to subgen extract (silent-except conversion now visible), dbg probes _r975bmc_dbg_sub{,2}.py committed as "
       "evidence (r958 lineage: _w228bmc_dbg17 family); (6) S6 light: dualrun ZERO-DRIFT streak 51 (cutoff 10-11) + "
       "compute_audit FLAG pool_starvation/supply_floor structural ANSWERED-BY-SEAT (W234 seat published r974 + prereg "
       "derive prep in-flight this window = never-dry supply line; engine lane is the CPU supply face) + py_watermark "
       "insufficient_history (window n=2 span 14.4min) honest + bars_present=false 10-13 sina-lag face unchanged; "
       "(7) attrition 4 CLEAN (1 healed row noted); (8) S7 quad green (loop pin=5 no-op + watchdog registered + "
       "precommit/prepush claws installed); commit 51f663b64 pushed b93ee8653..51f663b64 clean fast-forward "
       "(b93ee8653=r974 closeout, zero dead window between); counter 975->976")
VERDICT = ("green: W234 prereg derive PREP landed full (facts frozen + R34 authored 46/46 + subgen m31 + SUB block "
           "emitted 21654B compile-PASS 14-anchors green) -- r971-precedent split, ONE window ahead of the r971 "
           "milestone (R34 authored+subgen run vs r971's facts+skeleton); r958 pitfall 3rd instance caught same-window "
           "via EXC-print gate; smoke 49/49 + S7 quad green; tplgen phase-A/B + derive full pass = r976 first action")
NEXT = ("r976: (1) W234 prereg derive FULL PASS first action: tplgen phase A (advance committed "
        "_w233bmc_prereg_derive_tpl.py one wave -> _w234bmc_prereg_derive_tpl.py: blob chain +t233 row + RAM/WIN vars "
        "+ SUB33 extract row + OLD33 lvl step with mats @L31@->231/@T31@->32 + preflight pointer + anchors block "
        "n1_w233 values ledger 936,389/K 510,520/mu -0.09276956/sigma 0.24506207/w233-only -0.09893318/p95 0.3027/"
        "KL -0.0002/1.1922/1.1924/n_eff 934,189/se_mu 0.000343 + WIN_LABEL date-assert + STALE/NEW tables per "
        "_r972bmc_tplgen_b.py pair-table method) -> tplgen phase B -> assemble derive (tpl @@SUB_BLOCK@@ + emitted "
        "results/_w234bmc_sub_block.py splice) -> RUN derive -> research/PERPETUAL_N1_W234_PREREG.md + sha16 + "
        "STALE/NEW green -> commit; note derive label face authored r975 (correct per current window; if run slips "
        "past this window correct r975->r97x per r971->r972 precedent); (2) V3 lane: director ten-seat frame review "
        "pending (bm-a) -> sign-off lands fleet/inbox -> bm-c ignites i2v 7 shots INT8 768P (RAM arbitration i2v "
        "priority) -> RIFE V3 assembly; (3) 10-13 bars re-probe (sina lag self-heal window) -> bars fall = papers "
        "full chain; (4) W234 five-face freeze splice after prereg commit (census-first, clone committed W233 editor "
        "per r973 template) -> engine self-burn 12/12 -> PRE-FINALIZE six-gate (W217-debt standing law) -> finalize "
        "one-pass -> five-key + sec.7/8 backfill; (5) W235 seat publish after W234 finalize per seat-first law; "
        "W235+ projection A 531604..533603 / B 531804..532003 NINETY-FIFTH anticipated")

sp = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\state-bm-c.json"
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 976
st["last_round"] = 975
st["clock_read"] = iso
st["ts"] = iso
st["updated"] = iso
st["updated_at"] = iso
st["last_seen"] = now.strftime("%Y-%m-%d %H:%M:%S")
st["last_seen_at"] = iso
st["last_round_at"] = iso
st["last_round_ts"] = int(time.time())
st["heartbeat_epoch_utc"] = int(time.time())
st["current_task"] = "r975 closeout (W234 prereg derive PREP: facts + R34 46/46 + subgen m31 + SUB block emitted)"
st["current_task_at"] = iso
st["did"] = DID
st["verdict"] = VERDICT
st["next"] = NEXT
st["next_pointer"] = NEXT
st["next_milestone"] = ("W234 prereg derive full pass (r976 first action: tplgen A/B + assemble + run) -> splice/burn/"
                        "six-gate/finalize; V3 director sign-off -> i2v 7 shots -> RIFE assembly; 10-13 bars self-heal")
st["latest_artifact"] = ("results/_w234bmc_facts.json + results/_w234bmc_r34_data.py + results/_w234bmc_subgen.py + "
                         "results/_w234bmc_sub_block.py (all in 51f663b64)")
st["last_artifact"] = st["latest_artifact"]
st["recent_artifact"] = st["latest_artifact"]
st["last_round_summary"] = ("r975: W234 prereg derive PREP landed (facts frozen + R34 46/46 authored + subgen m31 "
                            "clone + SUB block emitted 21654B compile-PASS; r958 pitfall 3rd caught via EXC gate); "
                            "counter 975->976")
st["activity_now"] = ("2026-10-13 20:2x-20:3x | r975 | bm-c: W234 prereg derive PREP landed (facts+R34+subgen+sub_block) "
                      "| counter 975->976 | r976 first action=W234 tplgen+derive full pass")
st["now_active"] = st["activity_now"]
st["last_action"] = "r975 closeout (W234 prereg derive PREP: facts + R34 + subgen + sub_block landed 51f663b64)"
st["head_sha"] = "quant: 51f663b64 (r975 W234 PREP); parent b93ee8653 (r974 closeout, zero gap)"
st["sync"] = {"origin_tip": "51f663b64 (r975 W234 prereg derive PREP + closeout rides this window)",
              "ts": iso, "ahead_behind": "0/0 pre-closeout (closeout commit+push rides)",
              "note": "r975: clean continuation window (state round_no=975 at open, executed r975, advanced 975->976)"}
st["prod_lanes"] = ("GPU=MV V3 lane: fullres 7/7 burned+relayed, i2v 7-shot ignition GATED on bm-a director ten-seat "
                    "frame review (RAM arbitration i2v priority); CPU=N1 W234 prereg derive PREP LANDED (facts+R34+"
                    "subgen+sub_block), derive full pass = r976 first action (engine daemon ALIVE 12/12 W233 complete)")
st["idle_rounds"] = 0
st["agenda_starved"] = False
st["r975_closeout_note"] = ("r975: clean continuation window (state round_no=975 at open, executed r975, advanced "
                            "975->976 so next=r976); zero absorb owed (r974 closeout b93ee8653 landed clean, zero "
                            "dead window between); product = W234 prereg derive PREP (honest split per r971 precedent: "
                            "facts machine-frozen + R34 authored 46/46 + subgen m31 clone + SUB block emitted+compiled "
                            "+ 14 anchor spot-checks green); pitfall r958 3rd instance (ast.Dict.keys attr-vs-call) "
                            "caught same-window via EXC-print gate added to subgen extract, dbg probes committed; "
                            "S0.5 dual-delta FALSE both windows; S6 light dualrun streak 51 + FLAG structural "
                            "answered-by-seat + wm insufficient_history honest; attrition 4 CLEAN; S7 quad green")
st.pop("r975_absorb_note", None)
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

hp = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\fleet\machines\bm-c.json"
h = json.load(open(hp, encoding="utf-8"))
h["last_seen"] = now.strftime("%Y-%m-%d %H:%M:%S")
h["ts"] = iso
h["clock_read"] = iso
h["current_task"] = "idle: W234 prereg derive PREP landed (r976 first action = tplgen A/B + derive full pass)"
h["cpu_pct"] = round(psutil.cpu_percent(interval=1), 1)
h["ram_free_gb"] = ram_free
h["free_ram_gb"] = ram_free
h["idle_ram_gb"] = ram_free
h["verdict"] = "green: W234 PREP landed (facts+R34 46/46+subgen+sub_block 21654B PASS); r976 = tplgen+derive full pass"
h["heartbeat_epoch_utc"] = int(time.time())
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["round_no"] = 976
h["last_round"] = 975
json.dump(h, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
epoch = h["heartbeat_epoch_utc"]
assert isinstance(epoch, int), "epoch must be int"

rp = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\round_reports-bm-c.md"
line = (f"{iso} | r975 | bm-c: W234 prereg derive PREP landed per seat law first-action (r971-precedent honest split): "
        f"facts results/_w234bmc_facts.json machine-frozen (W233 anchors 936,389/510,520/-0.09276956/0.24506207/"
        f"-0.09893318/0.3027/KL -0.0002/se 0.000343 + W234 bands A 529604_531603/B 531604_531803 + base 933e3ceea "
        f"25606B/79be261672844184) + R34 authored 46/46 + subgen m31 clone + SUB block emitted 21654B py_compile PASS "
        f"14-anchor spot-checks green | verify: commit 51f663b64 pushed b93ee8653..51f663b64 + smoke 49/49 + dualrun "
        f"streak 51 + attrition 4 CLEAN + S7 quad green (pin=5/watchdog/claws) + r958 pitfall 3rd instance caught "
        f"same-window (ast.Dict.keys attr-vs-call, EXC-print gate added, dbg probes committed) | next r976: W234 "
        f"tplgen phase-A/B + derive full pass (SUB block splice at @@SUB_BLOCK@@ + run + STALE/NEW green) then "
        f"five-face splice + burn + six-gate PRE-FINALIZE + finalize + W235 seat; V3 i2v gated on bm-a director "
        f"sign-off; 10-13 bars re-probe\n")
open(rp, "a", encoding="utf-8").write(line)
print("closeout writes OK | epoch int:", isinstance(epoch, int), "| iso:", iso)
