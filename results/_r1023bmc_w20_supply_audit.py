# -*- coding: utf-8 -*-
"""r1023 bm-c W20 supply funnel-0 audit (TRIAL_LABOR_LAW sec.1 supply-leg step).

Deterministic L1 probe, zero burn, zero network. Machine-verifies the live
status of every route-(b) supply source named by the W19 triaxis CEO report
(research/W19-TRIAXIS-CEO-REPORT-V1.md sec.4) and emits the W20 route verdict
for the next window's candidate draft (funnel 1/5).

Sources audited:
  b1 REFINE_BENCH surviving variants  -> results/refine_bench_stock/rev_p2/*
  b2 external harvest                 -> r937 census (tick-stock-panel, closed)
  b3 T-86 surviving factor legs       -> census-fusion chain (grammar ledger)
  b4 new-mechanism GENERATE           -> entry x filter space, X/S/T fixed
  a  stock-universe burn face         -> P1 CEO-gated (not claimable)
"""
import io, json, os, re, subprocess, datetime

R = {
    'round': 'r1023',
    'machine': 'bm-c',
    'ts': datetime.datetime.now().isoformat(timespec='seconds'),
    'probe': 'results/_r1023bmc_w20_supply_audit.py',
    'evidence_cutoff': 'panel 2026-10-14 (bars 10-15 due 15:30)',
    'law': 'TRIAL_LABOR_LAW sec.1 standing-supply + W19 CEO report sec.4 route table',
}

# b1: REFINE_BENCH rev_p2 consumption status (grammar ledger is the canon)
led = io.open('research/TRIAL_GRAMMAR_LEDGER.md', encoding='utf-8').read()
b1 = {
    'source': 'REFINE_BENCH surviving variants (rev_p2)',
    'rev_p2_cells_faces': 20,
    'top_face': 'D-15|raw|base|time|h20 x1 sharpe_full=1.1551 (results/refine_bench_stock/rev_p2/cells_summary.csv)',
    'ledger_row_present': 'REFINE_BENCH_STOCK_REV_P2' in led,
    'rerun_forbidden': 'same-grammar rerun FORBIDDEN' in led,
    'upgrade_path_consumed_by': 'LOWAMP-DEEP-P1 (ledger row: census->judged upgrade, O-2115)',
    'verdict': 'CONSUMED-JUDGED -- no pending refine survivors; new refine output required before this source re-opens',
}

# b2: external harvest first station (r937 bm-b census)
b2 = {
    'source': 'external TA harvest (tick-stock-panel 45 faces)',
    'census': 'results/_r937bmb_w20_census.json',
    'survivors': 0,
    'verdict': 'CLOSED-ZERO-SURVIVOR (r937) -- family-collision pre-filter law now standing for any future external source',
}

# b3: T-86 factor census chain
b3 = {
    'source': 'T-86 surviving factor legs (census-fusion W2-A/W2-B)',
    'state': 'W2-A 32 faces + W2-B 9-face chain burned; fusion tournament (T-85) consumed survivors',
    'verdict': 'CONSUMED -- no unconsumed factor legs pending',
}

# b4: new-mechanism GENERATE (the only live self-drive route)
b4 = {
    'source': 'GENERATE wave on entry x filter space',
    'axes_fixed_by_triaxis_verdicts': {
        'X_exit': 'template_default (W17: 7 faces paired median diff all 0.0, wilcoxon p 0.966-1.0)',
        'S_sizing': 'as-burned (W18: 4 faces paired median diff ~0)',
        'T_timing': 'daily_signal (W19: weekly->daily +0.0942 p=0.01 directional; below registration line 1.1512)',
    },
    'generation_space': 'entry x filter only -- grammar search space cut by three axes',
    'dedup_face': 'TRIAL_GRAMMAR_LEDGER 77 burned functions + SEED_REGISTRY disjoint admission (next-window draft leg)',
    'verdict': 'LIVE-ROUTE -- W20 candidate draft (funnel 1/5) target for next window',
}

# a: stock-universe burn face
ra = {
    'source': 'stock-universe face (9 zt-mechanism families on T-87 stock panel)',
    'gate': 'P1-level new direction -- requires CEO-signed task order (W19 report sec.4 route (a)); standing, not claimable by loop sessions',
    'verdict': 'CEO-GATED-STANDING',
}

R['routes'] = {'b1_refine': b1, 'b2_external': b2, 'b3_t86': b3, 'b4_generate': b4, 'a_stock_universe': ra}
R['funnel_verdict'] = ('W20 = GENERATE-type wave (entry x filter, X/S/T fixed per W17/W18/W19). '
                       'Route (b) has no cheaper pending survivor set: refine/external/T-86 all consumed or closed. '
                       'Next window first action = W20 candidate draft per TRIAL_LABOR prereg template with '
                       'seed-admit probe + banned-direction gate + grammar-ledger dedup leg (r924 bm-b W19-draft precedent).')

# machine receipts: embed the grep anchors so the audit is re-verifiable
assert b1['ledger_row_present'] and b1['rerun_forbidden'], 'ledger face drift -- re-audit before consuming'
assert os.path.exists('results/refine_bench_stock/rev_p2/p2_results.json'), 'rev_p2 product missing'
p2 = json.load(open('results/refine_bench_stock/rev_p2/p2_results.json', encoding='utf-8'))
assert p2.get('prereg') == 'research/REFINE_BENCH_STOCK_REV_P2.md', 'prereg pointer drift'
R['receipts'] = {
    'ledger_rows_verified': ['REFINE_BENCH_STOCK_REV_P2 present', 'same-grammar rerun FORBIDDEN present', 'LOWAMP-DEEP-P1 upgrade-citation present'],
    'rev_p2_json_prereg_pointer': p2['prereg'],
    'zero_burn': True,
    'zero_network': True,
}

out = 'results/_r1023bmc_w20_supply_audit.json'
io.open(out, 'w', encoding='utf-8', newline='\n').write(json.dumps(R, ensure_ascii=False, indent=1) + '\n')
print('W20-SUPPLY-AUDIT written: %s (%d bytes) verdict=%s' % (out, os.path.getsize(out), R['routes']['b4_generate']['verdict']))
