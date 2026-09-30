# -*- coding: utf-8 -*-
"""_r466bma_w13_sections_build.py -- W13 surgeon sections 12-15 builder
(bm-a r466; continuation of r465 sec11 builder, same mechanized-anchor
paradigm).

Consumes the r465 anchor library (results/_r465bma_w13_harvest.json --
every non-miss `new` payload verified verbatim inside the live
scripts/trial_labor_w12.py = r464 surgeon-anchor law mechanized) and
EMITS four new section functions into the in-tree surgeon
results/_r464bma_w13_surgeon.py:

  sec12_screen  -- harvest rows at surgeon lines 1722-1978 (screen
                   slice: csv/cell/prep/shard/finalize sumn wiring)
  sec13_judge   -- rows 1982-2299 (judge slice: stop-disclosure/
                   cell/final sumn wiring + intake docstring)
  sec14_selftest-- rows 2310-2777 (L6/L7g/L7i/L8/L9/L10/L12/L13/L14/
                   L15 sixteen-tuple faces)
  sec15_residual-- W12 r445bmb surgeon step-15 mirror adapted for
                   W12->W13 (protected: @@TL12IMPORT@@ + the four
                   w12_* source-key strings; berths NOT blanket-renamed
                   -- historical W12 berth references stay; overreach
                   guard tl12.*_w13 -> tl12.*_w12)

The 2 harvest MISS rows (judge prep per-leg structure / L9a) are
LIVE-READ at build time from scripts/trial_labor_w12.py per the r465
miss-bucket law (payload drift flagged -> build-time live read).

After splice the builder re-runs the surgeon (fresh from SRC =
idempotent re-take), verifying sections 1-15 land with py_compile
PASS on the regenerated draft + W12-mirror step-16 guards.
"""
from __future__ import annotations
import json
import os
import py_compile
import subprocess
import sys

ROOT = os.getcwd()
HARVEST = os.path.join("results", "_r465bma_w13_harvest.json")
SURGEON = os.path.join("results", "_r464bma_w13_surgeon.py")
LIVE_W12 = os.path.join("scripts", "trial_labor_w12.py")

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# ------------------------------------------------------------- helpers
def R(old, pairs, what):
    """Sequential count-verified replaces (each pair must hit >=1)."""
    for o, n in pairs:
        if o not in old:
            raise SystemExit(
                "TRANSFORM-FAIL %s: pair target not in payload: %r"
                % (what, o[:90]))
        old = old.replace(o, n)
    if old == _payloads[what]:
        raise SystemExit("TRANSFORM-FAIL %s: no-op" % what)
    return old


def lines_of(text):
    return text.split("\n")


def indent_of(line):
    return line[:len(line) - len(line.lstrip())]


def mirror_after(old, needle, add_text, what):
    """Insert add_text (single line, same indent as needle line) after
    the unique line containing needle."""
    ls = lines_of(old)
    hits = [i for i, l in enumerate(ls) if needle in l]
    if len(hits) != 1:
        raise SystemExit("MIRROR-AFTER-FAIL %s: %d hits for %r"
                         % (what, len(hits), needle[:80]))
    i = hits[0]
    ls.insert(i + 1, indent_of(ls[i]) + add_text)
    return "\n".join(ls)


def mirror_block_after(old, start_needle, n_lines, what, extra_swaps=()):
    """Copy n_lines starting at the line with start_needle, apply the
    rsqr->sumn mirror (+extra swaps), append after the block."""
    ls = lines_of(old)
    hits = [i for i, l in enumerate(ls) if start_needle in l]
    if len(hits) != 1:
        raise SystemExit("MIRROR-BLOCK-FAIL %s: %d hits" % (what, len(hits)))
    i = hits[0]
    block = ls[i:i + n_lines]
    if len(block) != n_lines:
        raise SystemExit("MIRROR-BLOCK-FAIL %s: short block" % what)
    mir = []
    for l in block:
        m = M(l)
        for a, b in extra_swaps:
            m = m.replace(a, b)
        mir.append(m)
    return "\n".join(ls[:i + n_lines] + mir + ls[i + n_lines:])


def append_lines_after(old, needle, add_lines, what):
    """Append explicit lines (exact strings, indent included) after the
    unique line containing needle."""
    ls = lines_of(old)
    hits = [i for i, l in enumerate(ls) if needle in l]
    if len(hits) != 1:
        raise SystemExit("APPEND-FAIL %s: %d hits for %r"
                         % (what, len(hits), needle[:80]))
    i = hits[0]
    return "\n".join(ls[:i + 1] + add_lines + ls[i + 1:])


def M(t):
    """rsqr -> sumn identity mirror (order matters)."""
    for a, b in (("RSQR", "SUMN"), ("rsqr", "sumn"), ("gvvvsktsamsr",
                "gvvvsktsamsrn"), ("rqf", "nqf"), ("rz2", "nz2"),
                ("rz", "nz")):
        t = t.replace(a, b)
    return t


# ------------------------------------------------- harvest + live load
_h = json.load(open(HARVEST, encoding="utf-8"))
_rows = _h["rows"]
_payloads = {r["what"]: r for r in _rows}


def rows_between(lo, hi):
    return [r for r in _rows if lo <= r["line"] <= hi]


# ============================================================ SEC12 spec
# screen slice (surgeon lines 1722-1978)

def t_csv_cols(old):
    return mirror_after(old, '"rsqr_face", "rsqr_zeroed",',
                        '"sumn_face", "sumn_zeroed",', "csv cols")


def t_cell_unpack(old):
    return R(old, [("dz, rz = run_candidate_curve_w12(",
                    "dz, rz, nz = run_candidate_curve_w12(")],
               "screen+judge cell unpack")


def t_cell_state_args(old):
    # append-arg: rsqr_state=st.get("rsqr_state"))  ->  + sumn line
    ls = lines_of(old)
    hits = [i for i, l in enumerate(ls)
            if 'rsqr_state=st.get("rsqr_state"))' in l]
    if len(hits) != 1:
        raise SystemExit("cell-state-args: %d hits" % len(hits))
    i = hits[0]
    ls[i] = ls[i].replace('"rsqr_state"))', '"rsqr_state"),')
    ls.insert(i + 1, indent_of(ls[i]) + 'sumn_state=st.get("sumn_state"))')
    return "\n".join(ls)


def t_screen_row(old):
    return R(old, [('"rsqr_zeroed": int(rz)}',
                    '"rsqr_zeroed": int(rz),\n'
                    '            "sumn_face": cand["axis"][15],\n'
                    '            "sumn_zeroed": int(nz)}')],
             "screen row")


G_SUMN_PREP_GATE = (
    "\n    # G-SUMN on the raw full-history face (prereg sec.2 probe "
    "basis =\n"
    "    # data/daily/sh510300.csv; 120-bar warmup + probe anchors\n"
    "    # decidable 3,363 / open 387 / sumn10 3363/368 + slope split\n"
    "    # 387/0 + nine-gate 512-cell 103/409 law + mirror-twin\n"
    "    # 387/0-xor + zero-co-open exact mad60/rsv60/mom)\n"
    "    sumn_state_full, sumn_err = _sumn_state_full()\n"
    "    if sumn_err:\n"
    '        print(f"PREP-GATE FAIL: G-SUMN {sumn_err}")\n'
    "        return 1\n"
    "    sumn_meta_core = sumn_state_full[2]")


def t_prep_gate(old):
    tail = "\n" if old.endswith("\n") else ""
    return old + G_SUMN_PREP_GATE + tail if tail else old + G_SUMN_PREP_GATE


def t_member_loops(old):
    ls = lines_of(old)
    hits = [i for i, l in enumerate(ls) if '(RSQR_MEMBER, "rsqr")):' in l]
    if len(hits) != 1:
        raise SystemExit("member-loops: %d hits" % len(hits))
    i = hits[0]
    ind = indent_of(ls[i])
    ls[i] = ls[i].replace('(RSQR_MEMBER, "rsqr")):',
                          '(RSQR_MEMBER, "rsqr"),')
    ls.insert(i + 1, ind + '(SUMN_MEMBER, "sumn")):')
    return "\n".join(ls)


SUMN_PREP_LEGL = (
    "    _n20o, _n20d, sumn_meta, _n10o, _n10d = "
    "sumn_state_series(prices)\n"
    "    if not _sumn_structure_pass(sumn_meta):\n"
    '        print(f"PREP-GATE FAIL: G-SUMN leg-L structural "\n'
    '              f"invariants broken {sumn_meta} -- honest refuse")\n'
    "        return 1")


def t_prep_legl(old):
    tail = "\n" if old.endswith("\n") else ""
    add = "\n" + SUMN_PREP_LEGL + tail
    return old + add


def t_prep_payload_gate(old):
    return mirror_block_after(old, '"G-RSQR": {"pass": True,', 3,
                             "prep payload G-RSQR")


def t_prep_payload_meta(old):
    return mirror_after(old, '"rsqr_meta": rsqr_meta,',
                        '"sumn_meta": sumn_meta,', "prep payload meta")


def t_prep_print(old):
    ls = lines_of(old)
    hits = [i for i, l in enumerate(ls)
            if "{rsqr_meta['rsqr10_open_days']}\")" in l]
    if len(hits) != 1:
        raise SystemExit("prep-print: %d hits" % len(hits))
    ind_hits = [i for i, l in enumerate(ls)
                if "G-RSQR {rsqr_meta['open_days']}open" in l]
    if len(ind_hits) != 1:
        raise SystemExit("prep-print indent probe: %d hits" % len(ind_hits))
    ind = indent_of(ls[ind_hits[0]])
    i = hits[0]
    ls[i] = ls[i].replace(
        "f\"{rsqr_meta['rsqr10_open_days']}\")",
        "f\"{rsqr_meta['rsqr10_open_days']}; \"\n"
        + ind + "f\"G-SUMN {sumn_meta['open_days']}open/\"\n"
        + ind + "f\"{sumn_meta['closed_days']}closed decidable \"\n"
        + ind + "f\"{sumn_meta['decidable_days']} sumn10-open \"\n"
        + ind + "f\"{sumn_meta['sumn10_open_days']}\")")
    return "\n".join(ls)


def t_shard_state_init(old):
    return mirror_after(old, "rsqr_state = rsqr_state_series(prices)",
                        "sumn_state = sumn_state_series(prices)",
                        "shard state init")


def t_shard_st(old):
    ls = lines_of(old)
    hits = [i for i, l in enumerate(ls) if '"rsqr_state": rsqr_state}' in l]
    if len(hits) != 1:
        raise SystemExit("shard-st: %d hits" % len(hits))
    i = hits[0]
    ind = indent_of(ls[i])
    ls[i] = ls[i].replace('"rsqr_state": rsqr_state}',
                          '"rsqr_state": rsqr_state,')
    ls.insert(i + 1, ind + '"sumn_state": sumn_state}')
    return "\n".join(ls)


def t_fin_counts_init(old):
    return mirror_after(old, "rsqr_counts = {}", "sumn_counts = {}",
                        "finalize counts init")


def t_fin_segs_init(old):
    return R(old, [("std_seg, rsqr_seg, gvvvsktsamsr_seg = {}, {}, {}",
                    "std_seg, rsqr_seg, sumn_seg, gvvvsktsamsrn_seg"
                    " = {}, {}, {}, {}")], "finalize segs init")


def t_fin_face_read(old):
    return mirror_after(old, 'rqf = r["rsqr_face"]',
                        'nqf = r["sumn_face"]', "finalize face read")


def t_fin_counts_loop(old):
    return mirror_after(
        old, "rsqr_counts[rqf] = rsqr_counts.get(rqf, 0) + 1",
        "sumn_counts[nqf] = sumn_counts.get(nqf, 0) + 1",
        "finalize counts loop")


def t_fin_seg_loop_a(old):
    return mirror_after(old, "(rsqr_seg, rqf),", "(sumn_seg, nqf),",
                       "finalize seg loop a")


def t_fin_seg_loop_b(old):
    ls = lines_of(old)
    hits = [i for i, l in enumerate(ls) if "(gvvvsktsamsr_seg," in l]
    if len(hits) != 1:
        raise SystemExit("fin-seg-loop-b: %d hits" % len(hits))
    i = hits[0]
    ind = indent_of(ls[i])
    ls.insert(i, ind + "(sumn_seg, nqf),")
    out = "\n".join(ls)
    out = out.replace("gvvvsktsamsr_seg,", "gvvvsktsamsrn_seg,")
    out = R(out, [('f"{stf}|{rqf}")):', 'f"{stf}|{rqf}|{nqf}")):')],
             "finalize seg loop b")
    return out


def t_fin_rate_loop(old):
    return R(old, [
        ("rsqr_seg, gvvy_seg", "rsqr_seg, sumn_seg, gvvy_seg"),
        ("gvvvsktsamsr_seg):", "gvvvsktsamsr_seg, gvvvsktsamsrn_seg):"),
    ], "finalize rate loop")


def t_fin_meta_read(old):
    return mirror_after(old, 'rsqr_meta = prep.get("rsqr_meta")',
                        'sumn_meta = prep.get("sumn_meta")',
                        "finalize meta read")


def t_fin_payload_counts(old):
    return mirror_after(old, '"rsqr_face_counts": rsqr_counts,',
                        '"sumn_face_counts": sumn_counts,',
                        "finalize payload counts")


def t_fin_payload_segs(old):
    return mirror_after(old, '"rsqr_segmented_survival": rsqr_seg,',
                        '"sumn_segmented_survival": sumn_seg,',
                        "finalize payload segs")


def t_fin_payload_interaction(old):
    return append_lines_after(
        old,
        '"gate_vol_yang_vconf_streak_tstate_amp_mom_std_rsqr'
        '_interaction_"',
        ['            "gate_vol_yang_vconf_streak_tstate_amp_mom_std_'
         'rsqr_sumn_interaction_"',
         '            "survival": gvvvsktsamsrn_seg,'],
        "finalize payload interaction")


def t_fin_na_bars(old):
    return mirror_block_after(old, '"rsqr_na_window_bars"', 2,
                             "finalize na bars")


def t_fin_draw_order_a(old):
    return R(old, [('"MOM/STD/RSQR -> signal matrix (frozen "',
                    '"MOM/STD/RSQR/SUM -> signal matrix (frozen "')],
             "finalize draw order a")


def t_fin_draw_order_b(old):
    return R(old, [('"vconf+streak+tstate+amp+mom+std+rsqr "',
                    '"vconf+streak+tstate+amp+mom+std+rsqr+sum "')],
             "finalize draw order b")


def t_fin_audit_order(old):
    return R(old, [
        ('AMP -> MOM -> STD -> "\n'
         '                             "RSQR -> initial-stop);',
         'AMP -> MOM -> STD -> "\n'
         '                             "RSQR -> SUM -> initial-stop);'),
    ], "finalize audit order")


def t_audit_warmups(old):
    return R(old, [
        ('"mom 139-bar warmup / std 120-bar warmup / rsqr "',
         '"mom 139-bar warmup / std 120-bar warmup / rsqr / sumn "'),
        ("mom/std/rsqr_na_window_bars); ",
         "mom/std/rsqr/sumn_na_window_bars); "),
    ], "audit warmups")


def t_audit_erratum(old):
    ls = lines_of(old)
    ind = indent_of(ls[-1])
    return R(old, [
        ('open AND decidable (same erratum law); "',
         'open AND decidable (same erratum law); sumn20_lo/sumn10_lo '
         'keep "\n' + ind + '"face = open AND decidable (same '
         'erratum law); "'),
    ], "audit erratum")


def t_finalize_prints(old):
    ls = lines_of(old)
    hits = [i for i, l in enumerate(ls) if "rsqr segmented survival" in l]
    if len(hits) != 1:
        raise SystemExit("finalize-prints: %d hits" % len(hits))
    i = hits[0]
    ind = indent_of(ls[i])
    out = "\n".join(ls)
    return out + "\n" + ind + (
        'print(f"sumn segmented survival: {json.dumps(sumn_seg, '
        'sort_keys=True)}")\n') + ind + (
        'print(f"gate x vol x yang x vconf x streak x tstate x amp '
        'x mom x "\n') + ind + (
        '      f"std x rsqr x sumn interaction survival: "\n') + ind + (
        '      f"{json.dumps(gvvvsktsamsrn_seg, sort_keys=True)[:400]}")')


SEC12 = [
    ("csv cols", t_csv_cols),
    ("screen+judge cell unpack", t_cell_unpack),
    ("screen cell state args", t_cell_state_args),
    ("screen row", t_screen_row),
    ("prep G-RSQR gate", t_prep_gate),
    ("member loops", t_member_loops),
    ("prep legL structure", t_prep_legl),
    ("prep payload G-RSQR", t_prep_payload_gate),
    ("prep payload meta", t_prep_payload_meta),
    ("prep print", t_prep_print),
    ("shard state init", t_shard_state_init),
    ("shard st", t_shard_st),
    ("finalize counts init", t_fin_counts_init),
    ("finalize segs init", t_fin_segs_init),
    ("finalize face read", t_fin_face_read),
    ("finalize counts loop", t_fin_counts_loop),
    ("finalize seg loop a", t_fin_seg_loop_a),
    ("finalize seg loop b", t_fin_seg_loop_b),
    ("finalize rate loop", t_fin_rate_loop),
    ("finalize meta read", t_fin_meta_read),
    ("finalize payload counts", t_fin_payload_counts),
    ("finalize payload segs", t_fin_payload_segs),
    ("finalize payload interaction", t_fin_payload_interaction),
    ("finalize na bars", t_fin_na_bars),
    ("finalize draw order a", t_fin_draw_order_a),
    ("finalize draw order b", t_fin_draw_order_b),
    ("finalize audit order", t_fin_audit_order),
    ("audit warmups", t_audit_warmups),
    ("audit erratum", t_audit_erratum),
    ("finalize prints", t_finalize_prints),
]


# ============================================================ SEC13 spec
# judge slice (surgeon lines 1982-2299)

def t_dual_nulls_doc_a(old):
    return R(old, [("W12 unc-berth seed", "W13 unc-berth seed")],
             "dual nulls docstring a")


def t_dual_nulls_doc_b(old):
    return R(old, [
        ("W12 unc-berth seed binding [20321500, cell_idx]",
         "W13 unc-berth seed binding [20324000, cell_idx]"),
    ], "dual nulls docstring b")


def t_stop_disc_sig(old):
    return R(old, [("rsqr_state):", "rsqr_state, sumn_state):")],
             "stop disclosure sig")


def t_stop_disc_docstring(old):
    return R(old, [
        ("with the W12 composition order",
         "with the W13 composition order"),
        ("RSQR -> initial-stop; MSG-0440",
         "RSQR -> SUM -> initial-stop; MSG-0440"),
        ("tl11._overlay_stop_disclosure_w11 with the rsqr overlay",
         "tl12._overlay_stop_disclosure_w12 with the sumn overlay"),
    ], "stop disclosure docstring")


def t_stop_disc_chain(old):
    return R(old, [
        ("    _, ev = tl2.stop_exit_overlay(RQ, prices, stop_key, atr20)",
         "    NQ = sumn_zero_mask(SD, cand[\"axis\"][15], sumn_state)\n"
         "    _, ev = tl2.stop_exit_overlay(NQ, prices, stop_key, "
         "atr20)"),
    ], "stop disclosure chain")


def t_judge_cell_out(old):
    return R(old, [
        ('"rsqr_face": cand["axis"][14]}',
         '"rsqr_face": cand["axis"][14],\n'
         '            "sumn_face": cand["axis"][15]}'),
    ], "judge cell out face")


def t_judge_cell_state_read(old):
    return mirror_after(old, 'rq = st[f"rsqr_state_{leg}"]',
                        'nq = st[f"sumn_state_{leg}"]',
                        "judge cell state read")


def t_judge_cell_unpack2(old):
    return R(old, [
        ("az2, mz2, dz2, rz2 = run_candidate_curve_w12(",
         "az2, mz2, dz2, rz2, nz2 = run_candidate_curve_w12("),
    ], "judge cell unpack 2")


def t_judge_cell_curve1(old):
    return R(old, [("std_state=sd,\n"
                    "                                                 "
                    "rsqr_state=rq)",
                    "std_state=sd,\n"
                    "                                                 "
                    "rsqr_state=rq,\n"
                    "                                                 "
                    "sumn_state=nq)")],
             "judge cell curve states 1")


def t_judge_cell_curve2(old):
    return R(old, [
        ("mom_state=mo, std_state=sd, rsqr_state=rq)",
         "mom_state=mo, std_state=sd, rsqr_state=rq, sumn_state=nq)"),
    ], "judge cell curve states 2")


def t_judge_degenerate(old):
    return mirror_block_after(old, '"rsqr_zeroed": 0,', 2,
                             "judge degenerate legs")


def t_judge_legs_dict(old):
    return mirror_block_after(old, '"rsqr_zeroed": int(rz),', 2,
                             "judge legs dict")


def t_stop_disc_call(old):
    return R(old, [("ts, ap, mo, sd, rq)", "ts, ap, mo, sd, rq, nq)")],
             "stop disc call")


def t_judge_cmd_gate(old):
    add = (
        "\n    sumn_state_full, sumn_err = _sumn_state_full()\n"
        "    if sumn_err:\n"
        '        print(f"JUDGE-GATE: {sumn_err} (prereg sec.2 G-SUMN "\n'
        '              "fail-closed) -- refuse")\n'
        "        return 2")
    return old + add


def t_judge_cmd_perleg(old):
    add = (
        "\n        nst = sumn_state_series(prices)\n"
        '        state[f"sumn_state_{leg}"] = nst\n'
        '        state[f"sumn_meta_{leg}"] = nst[2]')
    return old + add


def t_judge_prep_gate(old):
    add = (
        "\n    sumn_state_full, sumn_err = _sumn_state_full()\n"
        "    if sumn_err:\n"
        '        print(f"JUDGE-PREP-GATE FAIL: G-SUMN {sumn_err}")\n'
        "        return 1")
    return old + add


def t_judge_prep_metas(old):
    return mirror_after(old, "rsqr_meta = {}", "sumn_meta = {}",
                        "judge prep metas init")


def t_judge_prep_member(old):
    ls = lines_of(old)
    hits = [i for i, l in enumerate(ls) if '(RSQR_MEMBER, "rsqr")):' in l]
    if len(hits) != 1:
        raise SystemExit("judge-prep-member: %d hits" % len(hits))
    i = hits[0]
    ind = indent_of(ls[i])
    ls[i] = ls[i].replace('(RSQR_MEMBER, "rsqr")):',
                          '(RSQR_MEMBER, "rsqr"),')
    ls.insert(i + 1, ind + '(SUMN_MEMBER, "sumn")):')
    return "\n".join(ls)


SUMN_JUDGE_PREP_PERLEG = (
    "        _n20o, _n20d, sumneta, _n10o, _n10d = "
    "sumn_state_series(prices)\n"
    "        if not _sumn_structure_pass(sumneta):\n"
    '            print(f"JUDGE-PREP-GATE FAIL: leg-{leg} G-SUMN '
    'structural "\n'
    '                  f"invariants broken {sumneta} -- honest '
    'refuse")\n'
    "            return 1\n"
    "        # per-leg slope-sign disclosure (mirror of the full-face\n"
    "        # sec.2(e) computation in _sumn_state_full; same frozen\n"
    "        # runner face, additive disclosure key -- not a gate "
    "input)\n"
    "        _c20 = _sumn_faces_raw(prices)[9]\n"
    "        _nmopen = _n20o & _n20d & _c20.notna()\n"
    '        sumneta["slope_sign_split"] = {\n'
    '            "up_slope_days": int((_nmopen & (_c20 > 0)).sum()),\n'
    '            "down_slope_days": int((_nmopen & (_c20 <= 0)).sum()),\n'
    '            "note": "BETA20 sign from the same frozen runner; "\n'
    '                    "up-dominant windows are slope-up-heavy BY "\n'
    '                    "CONSTRUCTION (direction-loaded up-share '
    'axis) "\n'
    '                    "-- the split quantifies how much; direction "\n'
    '                    "conditioning still lives in burned axes "\n'
    '                    "(GATE/YANG/STREAK/MOM), redundancy '
    'measured "\n'
    '                    "in adjacency cells"}\n'
    "        sumn_meta[leg] = sumneta")


def t_judge_prep_fullraw(old):
    return mirror_after(
        old, 'rsqr_meta["full_raw_face"] = rsqr_state_full[2]',
        'sumn_meta["full_raw_face"] = sumn_state_full[2]',
        "judge prep full_raw_face")


def t_prep_vacuous(old):
    return mirror_after(old, '"rsqr_meta": rsqr_meta,',
                        '"sumn_meta": sumn_meta,', "prep vacuous payload")


def t_prep_main_payload(old):
    return mirror_after(old, '"rsqr_meta": rsqr_meta,',
                        '"sumn_meta": sumn_meta,', "prep main payload")


def t_judge_prep_print(old):
    ls = lines_of(old)
    hits = [i for i, l in enumerate(ls)
            if "rsqr meta L 120-bar-warmup" in l]
    if len(hits) != 1:
        raise SystemExit("judge-prep-print: %d hits" % len(hits))
    ind = indent_of(ls[hits[0]])
    block = [
        ind + 'print(f"sumn meta L 120-bar-warmup "',
        ind + "      f\"{sumn_meta['L']['open_days']}open/\"",
        ind + "      f\"{sumn_meta['L']['closed_days']}closed decidable \"",
        ind + "      f\"{sumn_meta['L']['decidable_days']} sumn10-open \"",
        ind + "      f\"{sumn_meta['L']['sumn10_open_days']} slope-split \"",
        ind + "      f\"{sumn_meta['L']['slope_sign_split']}\")",
    ]
    return "\n".join(ls + block)


def t_judge_final_sums_init(old):
    return append_lines_after(
        old, "gvvvsktsamsr_sum = {}",
        ["    sumn_sum = {}", "    gvvvsktsamsrn_sum = {}"],
        "judge final sums init")


def t_judge_final_face_read(old):
    return mirror_after(old, 'rqf = r.get("rsqr_face", "none")',
                        'nqf = r.get("sumn_face", "none")',
                        "judge final face read")


def t_judge_final_seg_a(old):
    return mirror_after(old, "(rsqr_sum, rqf),", "(sumn_sum, nqf),",
                       "judge final seg loop a")


def t_judge_final_seg_b(old):
    ls = lines_of(old)
    hits = [i for i, l in enumerate(ls) if "(gvvvsktsamsr_sum," in l]
    if len(hits) != 1:
        raise SystemExit("judge-final-seg-b: %d hits" % len(hits))
    i = hits[0]
    ind = indent_of(ls[i])
    ls.insert(i, ind + "(sumn_sum, nqf),")
    out = "\n".join(ls)
    out = out.replace("gvvvsktsamsr_sum,", "gvvvsktsamsrn_sum,")
    out = R(out, [('|{stf}|{rqf}")):', '|{stf}|{rqf}|{nqf}")):')],
             "judge final seg loop b")
    return out


def t_judge_final_payload_sums(old):
    return mirror_after(old, '"rsqr_face_judgment": rsqr_sum,',
                        '"sumn_face_judgment": sumn_sum,',
                        "judge final payload sums")


def t_judge_final_payload_int(old):
    return append_lines_after(
        old,
        '"gate_vol_yang_vconf_streak_tstate_amp_mom_std_rsqr_'
        'interaction_"',
        ['            "gate_vol_yang_vconf_streak_tstate_amp_mom_std_'
         'rsqr_sumn_interaction_"',
         '            "judgment": gvvvsktsamsrn_sum,'],
        "judge final payload interaction")


def t_judge_final_audit(old):
    return R(old, [
        ('"tstate + amp + MOM + STD + RSQR overlays carried "',
         '"tstate + amp + MOM + STD + RSQR + SUM overlays carried "'),
        ('AMP -> MOM -> STD -> "\n'
         '                             "RSQR -> initial-stop; "',
         'AMP -> MOM -> STD -> "\n'
         '                             "RSQR -> SUM -> initial-stop; "'),
    ], "judge final audit")


def t_judge_final_prints(old):
    return mirror_after(
        old,
        'print(f"rsqr-face judgment: {json.dumps(rsqr_sum, '
        'sort_keys=True)}")',
        'print(f"sumn-face judgment: {json.dumps(sumn_sum, '
        'sort_keys=True)}")',
        "judge final prints")


def t_judge_final_stop_note(old):
    return R(old, [
        ('"std+rsqr overlays inserted before stop arming "',
         '"std+rsqr+sumn overlays inserted before stop arming "'),
        ("(W11/W12 composition law); gate_flip_days_legL",
         "(W12/W13 composition law); gate_flip_days_legL"),
    ], "judge final audit stop note")


def t_intake_docstring(old):
    return R(old, [
        ('"""s4 D6 binding gate (W2 cmd_intake precedent on the W11 '
         "file",
         '"""s4 D6 binding gate (W2 cmd_intake precedent on the W12 '
         "file"),
    ], "intake docstring")


SEC13 = [
    ("dual nulls docstring a", t_dual_nulls_doc_a),
    ("dual nulls docstring b", t_dual_nulls_doc_b),
    ("stop disclosure sig", t_stop_disc_sig),
    ("stop disclosure docstring", t_stop_disc_docstring),
    ("stop disclosure chain", t_stop_disc_chain),
    ("judge cell out face", t_judge_cell_out),
    ("judge cell state read", t_judge_cell_state_read),
    ("judge cell unpack 2", t_judge_cell_unpack2),
    ("judge cell curve states 1", t_judge_cell_curve1),
    ("judge cell curve states 2", t_judge_cell_curve2),
    ("judge degenerate legs", t_judge_degenerate),
    ("judge legs dict", t_judge_legs_dict),
    ("stop disc call", t_stop_disc_call),
    ("judge cmd G-RSQR gate", t_judge_cmd_gate),
    ("judge cmd per-leg state", t_judge_cmd_perleg),
    ("judge prep G-RSQR gate", t_judge_prep_gate),
    ("judge prep metas init", t_judge_prep_metas),
    ("judge prep member loop", t_judge_prep_member),
    ("judge prep per-leg structure", None),   # MISS -> live-read
    ("judge prep full_raw_face", t_judge_prep_fullraw),
    ("prep vacuous payload", t_prep_vacuous),
    ("prep main payload", t_prep_main_payload),
    ("judge prep print", t_judge_prep_print),
    ("judge final sums init", t_judge_final_sums_init),
    ("judge final face read", t_judge_final_face_read),
    ("judge final seg loop a", t_judge_final_seg_a),
    ("judge final seg loop b", t_judge_final_seg_b),
    ("judge final payload sums", t_judge_final_payload_sums),
    ("judge final payload interaction", t_judge_final_payload_int),
    ("judge final audit", t_judge_final_audit),
    ("judge final prints", t_judge_final_prints),
    ("judge final audit stop note", t_judge_final_stop_note),
    ("intake docstring", t_intake_docstring),
]


# ============================================================ SEC14 spec
# selftest (surgeon lines 2310-2777)

def t_selftest_docstring(old):
    return R(old, [
        ("G-RSQR probe anchors (nine-gate 512-cell 124/388 +\n"
         "    slope split 213/128 + core48 spread)",
         "G-SUMN probe anchors (nine-gate 512-cell 103/409 +\n"
         "    slope split 387/0 + core48 spread)"),
        ("24-source exclusion loader", "25-source exclusion loader"),
    ], "selftest docstring")


def t_L6a(old):
    return R(old, [
        ('"L6a axis_combos == 94,058,496 (31,352,832 x 3 rsqr-axis "',
         '"L6a axis_combos == 282,175,488 (94,058,496 x 3 sumn-axis "'),
        ('"values; W11 std-face combos x len(AXIS_RSQR))"',
         '"values; W12 rsqr-face combos x len(AXIS_SUMN))"'),
        ('g["axis_combos"] == 94058496',
         'g["axis_combos"] == 282175488'),
        ("== tl11.AXIS_COMBOS * len(AXIS_RSQR))",
         "== tl12.AXIS_COMBOS * len(AXIS_SUMN))"),
    ], "L6a")


def t_L6b(old):
    return R(old, [
        ('"L6b fifteen axes present, rsqr == frozen three-value",',
         '"L6b sixteen axes present, sumn == frozen three-value",'),
        ('len(g["axes"]) == 15 and g["axes"]["rsqr"] == AXIS_RSQR)',
         'len(g["axes"]) == 16 and g["axes"]["sumn"] == AXIS_SUMN)'),
    ], "L6b")


def t_L6c(old):
    return R(old, [
        ('"L6c W12 seeds == SEED_REGISTRY berths (20320500/20321000/"',
         '"L6c W13 seeds == SEED_REGISTRY berths (20323000/20323500/"'),
        ('"20321500 berths held, no re-pick)"',
         '"20324000 berths held, no re-pick)"'),
    ], "L6c text")


def t_L6d(old):
    return R(old, [
        ("distinct from W1/MASS/W2-W11\",",
         "distinct from W1/MASS/W2-W12\","),
        ("sha != tl11.FROZEN_SHA16,", "sha != tl12.FROZEN_SHA16,"),
    ], "L6d")


def t_L6e(old):
    return R(old, [
        ('"L6e exclusion face rows rsqr=none-padded to 15-long axis",',
         '"L6e exclusion face rows sumn=none-padded to 16-long axis",'),
        ('all(len(r["axis"]) == 15 and r["axis"][-1] == "none"',
         'all(len(r["axis"]) == 16 and r["axis"][-1] == "none"'),
        ('["stop_gate_vol_yang_vconf_streak_tstate_amp_mom_std_'
         'rsqr_none_face"]))',
         '["stop_gate_vol_yang_vconf_streak_tstate_amp_mom_std_'
         'rsqr_sumn_none_face"]))'),
    ], "L6e")


def t_L7g_L7i(old):
    return R(old, [
        ("rstate2, rerr2 = _rsqr_state_full()",
         "nstate2, nerr2 = _sumn_state_full()"),
        ('"(r447 determinism law: every computed RSQR-face cell "',
         '"(r456 determinism law: every computed SUMN-face cell "'),
        ("rerr2 is None", "nerr2 is None"),
        ('rstate2[2]["nine_gate_512cells"]',
         'nstate2[2]["nine_gate_512cells"]'),
        ('rerr2 or "rsqr-face cells == probe facts")',
         'nerr2 or "sumn-face cells == probe facts")'),
        ("# core48 member-level rsqr20 open-rate spread (r447 probe",
         "# core48 member-level sumn20 open-rate spread (r456 probe"),
        ("# method verbatim; frozen-runner RSQR verbatim)",
         "# method verbatim; frozen-runner SUMN verbatim)"),
        ("op2, wdec2, _ = rsqr_state_series({RSQR_MEMBER: d2})[:3]",
         "op2, wdec2, _ = sumn_state_series({SUMN_MEMBER: d2})[:3]"),
        ('cf2 = RSQR_ANCHOR["core48_rsqr20_open_rate"]',
         'cf2 = SUMN_ANCHOR["core48_sumn20_open_rate"]'),
        ('"L7i core48 rsqr20-open-rate spread (n 48 / min 0.0891 / "',
         '"L7i core48 sumn20-open-rate spread (n 48 / min 0.0728 / "'),
        ('"median 0.1009 / max 0.1183; r447 probe face)"',
         '"median 0.1012 / max 0.1171; r456 probe face)"'),
    ], "L7g+L7i")


def t_L8a(old):
    return R(old, [
        ('"candidate incl. the std+rsqr axes, fifteen-tuple)"',
         '"candidate incl. the rsqr+sumn axes, sixteen-tuple)"'),
        ('len(c1[1]["axis"]) == 15)', 'len(c1[1]["axis"]) == 16)'),
    ], "L8a")


def t_L8b(old):
    return R(old, [
        ("fifteen = [rng_a.integers(0, 4, n) for _ in range(15)]",
         "sixteen = [rng_a.integers(0, 4, n) for _ in range(16)]"),
        ("thirteen = [rng_b.integers(0, 4, n) for _ in range(13)]",
         "fourteen = [rng_b.integers(0, 4, n) for _ in range(14)]"),
        ('"L8b STD+RSQR append AFTER AMP in the rng stream (first '
         'thirteen "',
         '"L8b RSQR+SUM append AFTER AMP in the rng stream (first '
         'fourteen "'),
        ('"axis arrays == W10-order stream verbatim, zero '
         'disturbance)"',
         '"axis arrays == W11-order stream verbatim, zero '
         'disturbance)"'),
        ("zip(fifteen, thirteen)", "zip(sixteen, fourteen)"),
    ], "L8b")


def t_L9b(old):
    return R(old, [("prereg sec.1 TWELVE ", "prereg sec.1 THIRTEEN ")],
             "L9b text")


def t_L10b(old):
    return R(old, [
        ('"axis": [*hit_key["axis"][:14],',
         '"axis": [*hit_key["axis"][:15],'),
        ('"rsqr20_hi"]},', '"sumn20_lo"]},'),
        ('"L10b rsqr in {rsqr20_hi, rsqr10_hi} = new-syntax legal '
         'cell, ',
         '"L10b sumn in {sumn20_lo, sumn10_lo} = new-syntax legal '
         'cell, '),
    ], "L10b")


def t_L12_rq3(old):
    return mirror_after(old, "rq3 = rsqr_state_series(frames3)",
                        "nq3 = sumn_state_series(frames3)", "L12 rq3")


def t_L12_rq5(old):
    return mirror_after(old, "rq5 = rsqr_state_series(frames5)",
                        "nq5 = sumn_state_series(frames5)", "L12 rq5")


def t_L13_base(old):
    return R(old, [('"none", "none"]}', '"none", "none", "none"]}')],
             "L13 base axis fifteen")


def t_L12_gs3_none(old):
    return R(old, [
        ('"none", "none", "none", "none", "none", "none", gs3',
         '"none", "none", "none", "none", "none", "none", "none", '
         "gs3"),
        ("ss3, rq3)", "ss3, rq3, nq3)"),
    ], "L12 mask calls gs3 none")


def t_L12_gs3_mom(old):
    return R(old, [
        ('"mom_oversold", "none", "none", gs3',
         '"mom_oversold", "none", "none", "none", gs3'),
        ("ss3, rq3)", "ss3, rq3, nq3)"),
    ], "L12 mask calls gs3 mom")


def t_L12_gs5_none(old):
    return R(old, [
        ('"none", "none", "none", "none", "none", "none", gs5',
         '"none", "none", "none", "none", "none", "none", "none", '
         "gs5"),
        ("ss5, rq5)", "ss5, rq5, nq5)"),
    ], "L12 mask calls gs5 none")


def t_L12_gs5_mom(old):
    return R(old, [
        ('"mom_oversold", "none", "none", gs5',
         '"mom_oversold", "none", "none", "none", gs5'),
        ("ss5, rq5)", "ss5, rq5, nq5)"),
    ], "L12 mask calls gs5 mom")


def t_L13a(old):
    return R(old, [
        ("sdz10, rz10 = \\", "sdz10, rz10, nz10 = \\"),
        ("std_state=ss3, rsqr_state=rq3)",
         "std_state=ss3, rsqr_state=rq3, sumn_state=nq3)"),
    ], "L13a")


def t_L13b_check(old):
    return R(old, [
        ('"16-tuple return shape (rsqr_zeroed carried)",',
         '"17-tuple return shape (sumn_zeroed carried)",'),
        ("and rz10 == 0)", "and rz10 == 0\n        and nz10 == 0)"),
    ], "L13b check")


def t_L13b_call(old):
    return R(old, [
        ("_, _ = \\", "_, _, _ = \\"),
        ("std_state=ss3,\n            rsqr_state=rq3)",
         "std_state=ss3,\n            rsqr_state=rq3, sumn_state=nq3)"),
    ], "L13b call")


def t_L13c(old):
    return R(old, [
        ("mz5n, _, _ = \\", "mz5n, _, _, _ = \\"),
        ("std_state=ss5,\n            rsqr_state=rq5)",
         "std_state=ss5,\n            rsqr_state=rq5,\n"
         "            sumn_state=nq5)"),
    ], "L13c")


def t_L13d(old):
    return R(old, [
        ("mz5o, _, _ = \\", "mz5o, _, _, _ = \\"),
        ('"none", "none"]), None,', '"none", "none", "none"]), None,'),
        ("std_state=ss5, rsqr_state=rq5)",
         "std_state=ss5, rsqr_state=rq5, sumn_state=nq5)"),
    ], "L13d")


def t_L13e(old):
    return R(old, [
        ("mz3o, _, _ = \\", "mz3o, _, _, _ = \\"),
        ('"none", "none"]), None,', '"none", "none", "none"]), None,'),
        ("std_state=ss3, rsqr_state=rq3)",
         "std_state=ss3, rsqr_state=rq3, sumn_state=nq3)"),
    ], "L13e")


def t_L14(old):
    return R(old, [
        ('"L14 null-axis draw determinism + FIFTEEN-tuple with '
         'std+rsqr "',
         '"L14 null-axis draw determinism + SIXTEEN-tuple with '
         'rsqr+sumn "'),
        ('"in the frozen domains (W12 null berth 20321000)"',
         '"in the frozen domains (W13 null berth 20323500)"'),
        ("len(ax1) == 15", "len(ax1) == 16"),
        ("        and ax1[14] in AXIS_RSQR\n",
         "        and ax1[15] in AXIS_SUMN\n"
         "        and ax1[14] in AXIS_RSQR\n"),
    ], "L14")


def t_L15b_dom(old):
    return R(old, [
        ("               and ax0[14] in AXIS_RSQR\n",
         "               and ax0[15] in AXIS_SUMN\n"
         "               and ax0[14] in AXIS_RSQR\n"),
        ("len(ax0) == 15)", "len(ax0) == 16)"),
    ], "L15b dom")


def t_L15b_call1(old):
    return R(old, [
        ("mzn, _, rzn = \\", "mzn, _, rzn, nznn = \\"),
        ("std_state=ss3, rsqr_state=rq3, rng_matrix=mat0, p_on=p_on0)",
         "std_state=ss3, rsqr_state=rq3, sumn_state=nq3, "
         "rng_matrix=mat0, p_on=p_on0)"),
    ], "L15b call 1")


def t_L15b_call2(old):
    return R(old, [
        ("mznb, _, rznb = \\", "mznb, _, rznb, nznb = \\"),
        ("std_state=ss3, rsqr_state=rq3, rng_matrix=mat0b, "
         "p_on=p_on0b)",
         "std_state=ss3, rsqr_state=rq3, sumn_state=nq3, "
         "rng_matrix=mat0b, p_on=p_on0b)"),
    ], "L15b call 2")


def t_L15b_check(old):
    return R(old, [
        ('"L15b null-cell engine path: fifteen-tuple null draw "',
         '"L15b null-cell engine path: sixteen-tuple null draw "'),
        ('"deterministic + rsqr axis in-domain + engine 16-tuple '
         'return "',
         '"deterministic + sumn axis in-domain + engine 17-tuple '
         'return "'),
        ("and rzn == rznb)", "and rzn == rznb\n"
         "        and nznn == nznb)"),
    ], "L15b check")


def t_L15c(old):
    return R(old, [
        ('"L15c screen CSV contract carries the mom+std+rsqr columns '
         'in the "',
         '"L15c screen CSV contract carries the mom+std+rsqr+sumn '
         'columns in the "'),
        ('"frozen order (cell_id/candidate_id head + rsqr pair '
         'before "',
         '"frozen order (cell_id/candidate_id head + sumn pair '
         'before "'),
        ('[-3:] == ["rsqr_face", "rsqr_zeroed",',
         '[-3:] == ["sumn_face", "sumn_zeroed",'),
        ('"mom_zeroed", "std_zeroed", "rsqr_zeroed"} <= '
         'set(csv_cols_screen_w12))',
         '"mom_zeroed", "std_zeroed", "rsqr_zeroed", "sumn_zeroed"} '
         '<= set(csv_cols_screen_w12))'),
    ], "L15c")


def t_scope_print(old):
    return R(old, [
        ("W12 rsqr layer + G-RSQR + fifteen-tuple grammar",
         "W13 sumn layer + G-SUMN + sixteen-tuple grammar"),
        ("24-source exclusion loader", "25-source exclusion loader"),
    ], "selftest scope print")


SEC14 = [
    ("selftest docstring", t_selftest_docstring),
    ("L6a", t_L6a),
    ("L6b", t_L6b),
    ("L6c text", t_L6c),
    ("L6d", t_L6d),
    ("L6e", t_L6e),
    ("L7g+L7i", t_L7g_L7i),
    ("L8a", t_L8a),
    ("L8b", t_L8b),
    ("L9a", None),                        # MISS -> live-read
    ("L9b text", t_L9b),
    ("L10b", t_L10b),
    ("L12 rq3", t_L12_rq3),
    ("L12 rq5", t_L12_rq5),
    ("L13 base axis fifteen", t_L13_base),
    ("L12 mask calls gs3 none", t_L12_gs3_none),
    ("L12 mask calls gs3 mom", t_L12_gs3_mom),
    ("L12 mask calls gs5 none", t_L12_gs5_none),
    ("L12 mask calls gs5 mom", t_L12_gs5_mom),
    ("L13a", t_L13a),
    ("L13b check", t_L13b_check),
    ("L13b call", t_L13b_call),
    ("L13c", t_L13c),
    ("L13d", t_L13d),
    ("L13e", t_L13e),
    ("L14", t_L14),
    ("L15b dom", t_L15b_dom),
    ("L15b call 1", t_L15b_call1),
    ("L15b call 2", t_L15b_call2),
    ("L15b check", t_L15b_check),
    ("L15c", t_L15c),
    ("selftest scope print", t_scope_print),
]


# ============================================ MISS live-read handlers
# r465 harvest miss-bucket law: payload drift flagged -> build-time
# LIVE-READ from scripts/trial_labor_w12.py (the actually-run text).

_live = open(LIVE_W12, encoding="utf-8").read()


def live_line(marker):
    i = _live.find(marker)
    if i < 0:
        raise SystemExit("LIVE-READ-FAIL: %r not in live W12" % marker[:70])
    j = _live.find("\n", i)
    return _live[i:j]


MISS_JUDGE_PREP_ANCHOR = live_line("        rsqr_meta[leg] = rsqreta")
if _live.count(MISS_JUDGE_PREP_ANCHOR) != 1:
    raise SystemExit("LIVE-READ-FAIL: judge-prep anchor not unique in live")

L9A_OLD_START = '    _ok("L9a exclusion loader: every row a 15-tuple axis'
_i = _live.find(L9A_OLD_START)
if _i < 0:
    raise SystemExit("LIVE-READ-FAIL: L9a start not in live")
_j = _live.find("<= set(disc10))", _i)
if _j < 0:
    raise SystemExit("LIVE-READ-FAIL: L9a end not in live")
MISS_L9A_OLD = _live[_i:_j + len("<= set(disc10))")]
if _live.count(MISS_L9A_OLD) != 1:
    raise SystemExit("LIVE-READ-FAIL: L9a block not unique in live")

MISS_L9A_NEW = (
    '    _ok("L9a exclusion loader: every row a 16-tuple axis, sumn=none "\n'
    '        "at 15 for ALL rows + rsqr at 14 inside the frozen '
    'three-value "\n'
    '        "domain + W12 real-rsqr rows present (25 sources; W1-W11 "\n'
    '        "sources rsqr=none, W12 survivors/judged carry real '
    'values)",\n'
    '        all(len(r["axis"]) == 16 and r["axis"][15] == "none"\n'
    '            and r["axis"][14] in AXIS_RSQR for r in rows10)\n'
    '        and any(r["axis"][14] in ("rsqr20_hi", "rsqr10_hi")\n'
    '                for r in rows10)\n'
    '        and {"w1_screen_survivors", "mass_screen_survivors",\n'
    '             "w9_screen_survivors", "w9_judge_products",\n'
    '             "w10_screen_survivors", "w10_judge_products",\n'
    '             "w12_screen_survivors", "w12_judge_products",\n'
    '             "w13_screen_survivors", "w13_judge_products",\n'
    '             "judged_supply_weighting"} <= set(disc10))')


# ============================================================ emitter
def emit_section(fn_name, step_note, spec, lo, hi):
    """Build a section function source string from the spec list,
    consuming harvest rows in surgeon-line order."""
    rowset = rows_between(lo, hi)
    by_what = {r["what"]: r for r in rowset}
    spec_whats = [w for w, _ in spec]
    missing_rows = [r["what"] for r in rowset if r["what"] not in
                    spec_whats]
    if missing_rows:
        raise SystemExit("EMIT-FAIL %s: harvest rows without spec: %s"
                         % (fn_name, missing_rows))
    extra = [w for w in spec_whats if w not in by_what]
    if extra:
        raise SystemExit("EMIT-FAIL %s: spec without harvest rows: %s"
                         % (fn_name, extra))
    ordered = sorted(spec, key=lambda kv: by_what[kv[0]]["line"])
    lines = ["def %s(src, steps):" % fn_name]
    for what, fn in ordered:
        r = by_what[what]
        old = r["new_text"]
        if what == "judge prep per-leg structure":
            old = MISS_JUDGE_PREP_ANCHOR
            new = old + "\n" + SUMN_JUDGE_PREP_PERLEG
        elif what == "L9a":
            old = MISS_L9A_OLD
            new = MISS_L9A_NEW
        else:
            if not r.get("new_in_w12_src"):
                raise SystemExit(
                    "EMIT-FAIL %s: %s flagged miss but no handler"
                    % (fn_name, what))
            new = fn(old)
        if new == old:
            raise SystemExit("EMIT-FAIL %s: no-op transform %s"
                             % (fn_name, what))
        if r["kind"] == "subn":
            lines.append("    src = subn(src, %r, %r, %d, %r)"
                         % (old, new, r["n_expected"], what))
        else:
            lines.append("    src = sub1(src, %r, %r, %r)"
                         % (old, new, what))
    lines.append('    steps.append("%s")' % step_note)
    lines.append("    return src")
    return "\n".join(lines) + "\n"


SEC15_SRC = '''def sec15_residual(src, steps):
    """W12 r445bmb step-15 mirror adapted W12->W13.

    Protected from the blanket renames: the frozen import
    (@@TL12IMPORT@@) and the four load-bearing w12_* source-key
    strings (the W11-product source identity -- renaming them would
    collide with the sec8-added w13_* keys reading tl12 files).
    Berths are NOT blanket-renamed: historical W12 berth references
    (e.g. the sec7 distinctness comment) must survive; the legit
    berth label renames were handled by the section subs + one
    targeted pair below.  Overreach guard: module-face calls into
    the FROZEN tl12 keep W12-side names (W12 r445 precedent)."""
    src = src.replace("import trial_labor_w12 as tl12",
                      "import @@TL12IMPORT@@ as tl12")
    src = src.replace(\'"w12_screen_survivors"\', \'"@@W12TAG1@@"\')
    src = src.replace(\'"w12_judge_products"\', \'"@@W12TAG2@@"\')
    src = src.replace(\'"w12_screen_survivor"\', \'"@@W12TAG3@@"\')
    src = src.replace(\'"w12_judged"\', \'"@@W12TAG4@@"\')
    resid = [
        ("csv_cols_screen_w12", "csv_cols_screen_w13"),
        ("_screen_cell_w12", "_screen_cell_w13"),
        ("_cell_list_w12", "_cell_list_w13"),
        ("_overlay_stop_disclosure_w12", "_overlay_stop_disclosure_w13"),
        ("_judge_cell_w12", "_judge_cell_w13"),
        ("_dual_nulls_w12", "_dual_nulls_w13"),
        ("draw_candidate_sobol_w12", "draw_candidate_sobol_w13"),
        ("_load_exclusion_rows_w12", "_load_exclusion_rows_w13"),
        ("_excluded_w12", "_excluded_w13"),
        ("_effective_signal_mask_w12", "_effective_signal_mask_w13"),
        ("run_candidate_curve_w12", "run_candidate_curve_w13"),
        ("_null_axis_draw_w12", "_null_axis_draw_w13"),
        ("build_grammar_w12", "build_grammar_w13"),
        ("TRIAL_LABOR_W12", "TRIAL_LABOR_W13"),
        ("TRIAL_LAB_W12", "TRIAL_LAB_W13"),
        ("TRIAL-LABOR-W12", "TRIAL-LABOR-W13"),
        ("trial_labor_w12", "trial_labor_w13"),
        (\'"W12-\', \'"W13-\'),
        ("W12-NULL", "W13-NULL"),
        ("w12_", "w13_"),
        ("FIFTEEN-tuple", "SIXTEEN-tuple"),
        ("FIFTEEN-gate", "SIXTEEN-gate"),
        ("fifteen-tuple", "sixteen-tuple"),
        ("FIFTEEN-", "SIXTEEN-"),
        ("(MOM+STD+RSQR fifteen-gate wave)",
         "(MOM+STD+RSQR+SUM sixteen-gate wave)"),
        ("24-source", "25-source"),
        ("24 real-reads", "25 real-reads"),
        ("T-124", "T-125"),
        ("seed [20321500, ", "seed [20324000, "),
    ]
    for old, new in resid:
        src = src.replace(old, new)
    src = src.replace(\'"@@W12TAG1@@"\', \'"w12_screen_survivors"\')
    src = src.replace(\'"@@W12TAG2@@"\', \'"w12_judge_products"\')
    src = src.replace(\'"@@W12TAG3@@"\', \'"w12_screen_survivor"\')
    src = src.replace(\'"@@W12TAG4@@"\', \'"w12_judged"\')
    src = src.replace("@@TL12IMPORT@@", "trial_labor_w12")
    # residual-rename overreach guard (W12 r445 precedent): module-face
    # calls into the FROZEN tl12 must keep W12-side names
    import re as _re
    src = _re.sub(r"tl12\\.([A-Za-z_][A-Za-z0-9_]*)_w13\\b",
                  r"tl12.\\1_w12", src)
    steps.append("residual pass: identifiers/payloads "
                 "(screen/judge/intake/selftest legs)")
    return src
'''


# ============================================================ main
def main() -> int:
    sec12 = emit_section("sec12_screen",
                         "screen slice: csv/cell/prep/shard/finalize "
                         "sumn wiring", SEC12, 1722, 1978)
    sec13 = emit_section("sec13_judge",
                         "judge slice: prep/cell/finalize sumn wiring",
                         SEC13, 1982, 2299)
    sec14 = emit_section("sec14_selftest",
                         "selftest: sixteen-tuple faces (L6/L7g/L7i/"
                         "L8/L9/L10/L12/L13/L14/L15)", SEC14, 2310,
                         2777)

    sur = open(SURGEON, encoding="utf-8").read()
    if "def sec12_screen(" in sur:
        print("SECTIONS-BUILD: already spliced (idempotent no-op)")
        return 0

    # splice 1: function defs before main()
    anchor_def = "\ndef main() -> int:"
    if sur.count(anchor_def) != 1:
        raise SystemExit("SPLICE-FAIL: main anchor not unique")
    new_defs = ("\n" + sec12.rstrip("\n") + "\n\n\n"
                + sec13.rstrip("\n") + "\n\n\n"
                + sec14.rstrip("\n") + "\n\n\n"
                + SEC15_SRC.rstrip("\n") + "\ndef main() -> int:")
    sur = sur.replace(anchor_def, new_defs)

    # splice 2: main call chain
    anchor_call = "    src = sec11_generate(src, steps)\n"
    if sur.count(anchor_call) != 1:
        raise SystemExit("SPLICE-FAIL: sec11 call anchor not unique")
    sur = sur.replace(
        anchor_call,
        anchor_call
        + "    src = sec12_screen(src, steps)\n"
        + "    src = sec13_judge(src, steps)\n"
        + "    src = sec14_selftest(src, steps)\n"
        + "    src = sec15_residual(src, steps)\n")

    # splice 3: pending list -> post-surgeon steps + partial flip
    pend_start = sur.find('"sections_pending": [')
    if pend_start < 0:
        raise SystemExit("SPLICE-FAIL: pending list not found")
    pend_end = sur.find("],", pend_start)
    if pend_end < 0:
        raise SystemExit("SPLICE-FAIL: pending list end not found")
    sur = (sur[:pend_start]
           + '"post_surgeon_pending": [\n'
           '            "r446 three-command real-data identity face '
           '(prep/finalize/judge-prep)",\n'
           '            "selftest full run",\n'
           '            "formal land scripts/trial_labor_w13.py",\n'
           '            "catalog runner_exists flip + GENERATE pool '
           'entry",\n'
           '        ],\n'
           '        "partial": False,'
           + sur[pend_end + 2:])

    # splice 4: guards before report write (W12 step-16 mirror)
    anchor_report = "    report = {"
    if sur.count(anchor_report) != 1:
        raise SystemExit("SPLICE-FAIL: report anchor not unique")
    guards_code = (
        "    flags = []\n"
        "    for pat in ('len(axis) == 15', "
        "'axis\"][14] != \"none\"',\n"
        "                \"fifteen-tuple\", \"FIFTEEN-tuple\", "
        "\"FOURTEEN-tuple\"):\n"
        "        hits = src.count(pat)\n"
        "        if hits:\n"
        "            flags.append(\"REVIEW-AT-SLICE-B %s: %d hits\"\n"
        "                        % (pat, hits))\n"
        "    n_axis15 = src.count('cand[\"axis\"][15]')\n"
        "    report = {\n"
        "        \"review_flags\": flags,\n"
        "        \"axis15_refs\": n_axis15,\n")
    sur = sur.replace(anchor_report, guards_code, 1)

    # splice 5: banner
    banner_old = ('print("SURGEON-OK: sections 1-11 landed, draft '
                  'written, py_compile "\n          "PASS")')
    if sur.count(banner_old) != 1:
        raise SystemExit("SPLICE-FAIL: banner anchor not unique")
    sur = sur.replace(
        banner_old,
        'print("SURGEON-OK: sections 1-15 landed, draft written, "\n'
        '          "py_compile PASS")')

    open(SURGEON, "w", encoding="utf-8", newline="\n").write(sur)
    py_compile.compile(SURGEON, doraise=True)

    proc = subprocess.run(
        [sys.executable, SURGEON], capture_output=True, text=True,
        encoding="utf-8", errors="replace", cwd=ROOT)
    print(proc.stdout.strip()[-3000:])
    if proc.returncode != 0:
        print("SECTIONS-BUILD-FAIL: surgeon rerun rc=%d"
              % proc.returncode)
        print(proc.stderr.strip()[-2500:])
        return 2
    if "sections 1-15 landed" not in proc.stdout:
        print("SECTIONS-BUILD-FAIL: banner mismatch in rerun")
        return 2
    print("SECTIONS-BUILD-OK: spliced sec12-15 + surgeon rerun green "
          "(sections 1-15)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
