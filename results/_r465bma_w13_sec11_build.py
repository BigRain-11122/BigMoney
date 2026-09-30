# -*- coding: utf-8 -*-
"""_r465bma_w13_sec11_build.py -- W13 surgeon section 11 (generate-leg)
builder (bm-a r465).

Consumes the r465 anchor library (results/_r465bma_w13_harvest.json --
every `new` payload verified verbatim-inside the live
scripts/trial_labor_w12.py = the r464 surgeon-anchor law mechanized)
and EMITS the sec11_generate() function source into the in-tree
surgeon results/_r464bma_w13_surgeon.py:

  - old anchors == harvest `new_text` (== live W12 text, verified)
  - new payloads == old + sumn-leg append (W12 surgeon rsqr->W13
    sumn mirror; call sites renamed to the w13 faces already defined
    by sections 1-10: _effective_signal_mask_w13; variable names
    stay SRC-side for the section-15 residual pass, W12 r445 law)
  - splice points: sec10 def end (before `def main`) + main call
    chain + report pending list + OK banner

After splice the builder re-runs the surgeon itself (subprocess,
fresh from SRC = idempotent re-take), verifying sections 1-11 land
with py_compile PASS on the regenerated draft.
Products: none of its own beyond the splice + stdout receipt (the
draft/surgeon/report artifacts are the surgeon's).
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

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main() -> int:
    h = json.load(open(HARVEST, encoding="utf-8"))
    subs = [r for r in h["rows"] if r.get("kind")
            and 1500 <= r["line"] <= 1720]
    by_what = {r["what"]: r["new_text"] for r in subs}
    need = ["generate docstring", "G-RSQR gate", "neg_fns key",
            "generate mask call", "counts init", "counts loop",
            "excl note", "dedup note", "payload counts", "payload metas",
            "berth note", "ledger row", "ledger pool row",
            "generate print"]
    missing = [w for w in need if w not in by_what]
    if missing:
        print("SEC11-BUILD-FAIL: harvest missing %s" % missing)
        return 2

    q3 = '"' * 3

    def t_docstring(old):
        return ("    " + q3 + "Frozen prereg sec.3 generate stage (W12 "
                "cmd_generate caliber on\n    the SIXTEEN-tuple face): "
                "per-slot Sobol streams consumed in global\n    "
                "round-robin -> 25-source exclusion -> T-84s3 dedup gate "
                "on the\n    effective signal face (gate + vol + yang + "
                "vconf + streak + tstate\n    + amp + MOM + STD + RSQR "
                "overlays applied, frozen composition\n    order) -> "
                "w13_candidates.json + grammar ledger wave-13 row.  "
                "Zero\n    engine cells burned." + q3)

    def t_gsumn_gate(old):
        return old + (
            "\n    sumn_state, sumn_err = _sumn_state_full()\n"
            "    if sumn_err:\n"
            "        print(f\"GENERATE-GATE: {sumn_err} (prereg sec.2 "
            "G-SUMN \"\n              \"fail-closed) -- refuse\")\n"
            "        return 2")

    def t_neg_fns(old):
        return old.replace(
            "amp_mom_std_rsqr_none_face",
            "amp_mom_std_rsqr_sumn_none_face")

    def t_mask_call(old):
        n = old.replace("_effective_signal_mask_w12",
                        "_effective_signal_mask_w13")
        n = n.replace(
            'cand["axis"][13], cand["axis"][14],\n',
            'cand["axis"][13], cand["axis"][14],\n'
            '                                      cand["axis"][15],\n')
        n = n.replace("std_state, rsqr_state)",
                      "std_state, rsqr_state,\n"
                      "                                      sumn_state)")
        return n

    def t_counts_init(old):
        return old.replace(
            "    rsqr_counts = {}\n",
            "    rsqr_counts = {}\n    sumn_counts = {}\n")

    def t_counts_loop(old):
        n = old.replace(
            '        rsqr_counts[c["axis"][14]] = '
            'rsqr_counts.get(c["axis"][14], 0) + 1\n',
            '        rsqr_counts[c["axis"][14]] = '
            'rsqr_counts.get(c["axis"][14], 0) + 1\n'
            '        sumn_counts[c["axis"][15]] = '
            'sumn_counts.get(c["axis"][15], 0) + 1\n')
        n = n.replace("k10 = (f\"", "k11 = (f\"")
        n = n.replace(
            "              f\"{c['axis'][14]}\")\n",
            "              f\"{c['axis'][14]}|{c['axis'][15]}\")\n")
        n = n.replace("gvvvsktsam_counts[k10] = ",
                      "gvvvsktsam_counts[k11] = ")
        n = n.replace("gvvvsktsam_counts.get(k10, 0)",
                      "gvvvsktsam_counts.get(k11, 0)")
        return n

    def t_excl_note(old):
        return old.replace(
            '"amp, mom, std, rsqr); exclusion face "\n'
            '                                     "= rsqr=none only '
            '(sec.1); prior-wave "\n'
            '                                     "keys '
            'rsqr=none-completed; rsqr in "\n'
            '                                     "{rsqr20_hi, '
            'rsqr10_hi} = "\n'
            '                                     "new-syntax legal '
            'cells"},',
            '"amp, mom, std, rsqr, sumn); exclusion "\n'
            '                                     "face = sumn=none '
            'only (sec.1); prior-wave "\n'
            '                                     "keys '
            'sumn=none-completed; sumn in "\n'
            '                                     "{sumn20_lo, '
            'sumn10_lo} = "\n'
            '                                     "new-syntax legal '
            'cells"},')

    def t_dedup_note(old):
        return old.replace('"+ MOM + STD overlays applied, frozen "',
                          '"+ MOM + STD + RSQR overlays applied, frozen "')

    def t_payload_counts(old):
        return old.replace(
            '               "rsqr_face_counts": rsqr_counts,\n',
            '               "rsqr_face_counts": rsqr_counts,\n'
            '               "sumn_face_counts": sumn_counts,\n'
        ).replace(
            '"gate_vol_yang_vconf_streak_tstate_amp_mom_std_rsqr_face_"\n'
            '               "counts":',
            '"gate_vol_yang_vconf_streak_tstate_amp_mom_std_rsqr_sumn_"\n'
            '               "face_counts":')

    def t_payload_metas(old):
        # append-type anchor (old ends at rsqr_state[2], no trailing nl)
        return old + '\n               "sumn_state_meta": sumn_state[2],'

    def t_berth_note(old):
        n = old.replace('"berths 20320500/"\n'
                        '                         "20321000/20321500 held '
                        'at the freeze commit "',
                        '"berths 20323000/"\n'
                        '                         "20323500/20324000 held '
                        'at the freeze commit "')
        n = n.replace("(bm-b r444 three-step re-verify ALL GREEN, ",
                      "(bm-a r461 three-step re-verify ALL GREEN, ")
        n = n.replace("of the bm-a r447 RSQR candidate whole package ",
                      "of the bm-a r456 SUMN candidate whole package ")
        n = n.replace("per AMP->W9/MOM->W10/STD->W11 adoption lineage)",
                      "per AMP->W9/MOM->W10/STD->W11/RSQR->W12 adoption "
                      "lineage)")
        return n

    def t_ledger_row(old):
        return old.replace(
            '           f"rsqr faces {json.dumps(rsqr_counts, '
            'sort_keys=True)}; "\n',
            '           f"rsqr faces {json.dumps(rsqr_counts, '
            'sort_keys=True)}; "\n'
            '           f"sumn faces {json.dumps(sumn_counts, '
            'sort_keys=True)}; "\n'
        ).replace(
            '           f"x std x rsqr {json.dumps(gvvvsktsam_counts, '
            'sort_keys=True)}) "',
            '           f"x std x rsqr x sumn {json.dumps'
            '(gvvvsktsam_counts, sort_keys=True)}) "')

    def t_pool_row(old):
        return old.replace(
            'f"TRIAL-LABOR-W12-GENERATE, T-124 prereg bm-b r444 frozen / "\n'
            '           f"runner bm-b r445) | "',
            'f"TRIAL-LABOR-W13-GENERATE, T-125 prereg bm-a r461 frozen / "\n'
            '           f"runner bm-a r465) | "')

    def t_print(old):
        return old.replace(
            '          f"rsqr faces: {json.dumps(rsqr_counts, '
            'sort_keys=True)}; "\n',
            '          f"rsqr faces: {json.dumps(rsqr_counts, '
            'sort_keys=True)}; "\n'
            '          f"sumn faces: {json.dumps(sumn_counts, '
            'sort_keys=True)}; "\n'
        ).replace(
            '          f"std x rsqr: "\n',
            '          f"std x rsqr x sumn: "\n')

    order = [
        ("generate docstring", t_docstring),
        ("G-RSQR gate", t_gsumn_gate),
        ("neg_fns key", t_neg_fns),
        ("generate mask call", t_mask_call),
        ("counts init", t_counts_init),
        ("counts loop", t_counts_loop),
        ("excl note", t_excl_note),
        ("dedup note", t_dedup_note),
        ("payload counts", t_payload_counts),
        ("payload metas", t_payload_metas),
        ("berth note", t_berth_note),
        ("ledger row", t_ledger_row),
        ("ledger pool row", t_pool_row),
        ("generate print", t_print),
    ]
    lines = ["def sec11_generate(src, steps):"]
    for what, fn in order:
        old = by_what[what]
        new = fn(old)
        if new == old:
            print("SEC11-BUILD-FAIL: transform no-op for %r" % what)
            return 2
        lines.append("    src = sub1(src, %r, %r, %r)"
                     % (old, new, what))
    lines.append('    steps.append("generate: G-SUMN gate + sixteen-tuple '
                 'dedup + counts")')
    lines.append("    return src")
    sec11_src = "\n".join(lines) + "\n\n\n"

    sur = open(SURGEON, encoding="utf-8").read()
    if "def sec11_generate(" in sur:
        print("SEC11-BUILD-FAIL: sec11 already spliced (idempotent no-op)")
        return 0
    # splice 1: function definition before main()
    anchor_def = "\n\ndef main() -> int:"
    if sur.count(anchor_def) != 1:
        print("SEC11-BUILD-FAIL: main anchor not unique")
        return 2
    sur = sur.replace(anchor_def,
                      "\n\n" + sec11_src.rstrip("\n") + "\ndef main() -> int:")
    # splice 2: main call chain
    anchor_call = "    src = sec10_mask_curve_null(src, steps)\n"
    if sur.count(anchor_call) != 1:
        print("SEC11-BUILD-FAIL: sec10 call anchor not unique")
        return 2
    sur = sur.replace(anchor_call,
                      anchor_call
                      + "    src = sec11_generate(src, steps)\n")
    # splice 3: pending list (remove section-11 entry)
    pend = ('            "11 generate: G-SUMN gate + sixteen-tuple dedup '
            '+ counts",\n')
    if sur.count(pend) != 1:
        print("SEC11-BUILD-FAIL: pending-11 anchor not unique")
        return 2
    sur = sur.replace(pend, "")
    # splice 4: OK banner
    banner = ('print("SURGEON-OK: sections 1-10 landed, draft written, '
              'py_compile "\n          "PASS")')
    if sur.count(banner) != 1:
        print("SEC11-BUILD-FAIL: banner anchor not unique")
        return 2
    sur = sur.replace(banner,
                      'print("SURGEON-OK: sections 1-11 landed, draft '
                      'written, py_compile "\n          "PASS")')
    # splice 5: next pointer
    old_next = ('"next": ("r465: extend surgeon sections 11-15 (generate/"')
    if sur.count(old_next) == 1:
        sur = sur.replace(old_next,
                          '"next": ("r466: extend surgeon sections 12-15 '
                          '(screen/"')
        sur = sur.replace(
            '"screen/judge/selftest/residual) reading the actual "',
            '"judge/selftest/residual) reading the actual "')
    open(SURGEON, "w", encoding="utf-8", newline="\n").write(sur)
    py_compile.compile(SURGEON, doraise=True)

    # re-run the surgeon fresh from SRC (idempotent re-take, now with
    # section 11 in the chain)
    proc = subprocess.run(
        [sys.executable, SURGEON], capture_output=True, text=True,
        encoding="utf-8", errors="replace", cwd=ROOT)
    print(proc.stdout.strip()[-2000:])
    if proc.returncode != 0:
        print("SEC11-BUILD-FAIL: surgeon rerun rc=%d" % proc.returncode)
        print(proc.stderr.strip()[-2000:])
        return 2
    if "sections 1-11 landed" not in proc.stdout:
        print("SEC11-BUILD-FAIL: banner mismatch in rerun")
        return 2
    print("SEC11-BUILD-OK: spliced + surgeon rerun green (sections 1-11)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
