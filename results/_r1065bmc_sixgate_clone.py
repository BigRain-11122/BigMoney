# -*- coding: utf-8 -*-
# r1065 bm-c: clone results/_r1064bmc_w259_sixgate.py -> results/_r1065bmc_w260_sixgate.py
# via COUNT-ASSERTED ORDERED TRANSFORM (E63 canon law, zero hand-transcription).
import io

src = io.open('results/_r1064bmc_w259_sixgate.py', encoding='utf-8').read()

HDR_OLD = """# r1064 bm-c: W259 PRE-FINALIZE six-gate receipt (standing law since W217 debt;
# clone lineage _r1062bmc_w258_sixgate.py W258 pattern). Burn landed by resident
# engine auto-ignite post-W259 splice 89aeea31b (batched ledger appends
# self-committed 12/12, shard files only); finalize not yet run.
# Splice commit 89aeea31b = worktree bytes directly (zero post-splice heal --
# worktree == receipt post == landed blob triple-identity expected for BOTH pf
# and n1 faces; verified live this window pre-sixgate).
# This window = r1064 clean continuation (dead-r1063 pre-built editor + this
# window 4 disclosed gate-list needle heals [w244_a frozen-verbatim / r1064
# freeze-window stamp / 248th anti-gate / 247-129-77 anti-gate] + splice +
# engine self-burn 12/12; this session runs sixgate->finalize->fivekeys->
# sec78->W260 seat->S6->closeout)."""
HDR_NEW = """# r1065 bm-c: W260 PRE-FINALIZE six-gate receipt (standing law since W217 debt;
# clone lineage _r1064bmc_w259_sixgate.py W259 pattern). Burn landed by resident
# engine auto-ignite post-W260 splice e8a9d5d67 (batched ledger appends
# self-committed 12/12, shard files only); finalize not yet run.
# Splice commit e8a9d5d67 = worktree bytes directly (zero post-splice heal --
# worktree == receipt post == landed blob triple-identity expected for BOTH pf
# and n1 faces; verified live this window pre-sixgate).
# This window = r1065 55th-gen absorb continuation (dead-r1065 windows: prereg
# frozen 0f33f9abc + editor pre-built; this window 1 disclosed OUTPUT-GATE
# needle heal [w244_a frozen-verbatim -- builder wrongly rolled +1 AGAIN,
# r1064 same-defect precedent] + splice e8a9d5d67 + engine self-burn 12/12;
# this session runs sixgate->finalize->fivekeys->sec78->W261 seat->S6
# (absorbed dead-window 43/43 10:41)->closeout)."""

R = [
 (HDR_OLD, HDR_NEW, 1, "hdr-block"),
 ("fr = json.load(io.open('results/_w259bmc_freeze_receipt.json', encoding='utf-8'))",
  "fr = json.load(io.open('results/_w260bmc_freeze_receipt.json', encoding='utf-8'))", 1, "fr-load"),
 ("assert i >= 0, 'W259 wave row missing'", "assert i >= 0, 'W260 wave row missing'", 1, "assert-msg"),
 ("i = n1t.find('259: {\"batch\": \"PERPETUAL-N1-W259\"')",
  "i = n1t.find('260: {\"batch\": \"PERPETUAL-N1-W260\"')", 1, "find-target"),
 ("if '260: {' in seg:\n    seg = seg[:seg.find('260: {')]",
  "if '261: {' in seg:\n    seg = seg[:seg.find('261: {')]", 1, "seg-cut"),
 ("    'a_seed_base_585101': '585101' in seg,", "    'a_seed_base_587301': '587301' in seg,", 1, "rf-a"),
 ("    'b_exit_seed_base_587101': '587101' in seg,", "    'b_exit_seed_base_589301': '589301' in seg,", 1, "rf-b"),
 ("    'shard_subdir_n1_w259': 'n1_w259' in seg,", "    'shard_subdir_n1_w260': 'n1_w260' in seg,", 1, "rf-sd"),
 ("    'out_name_n1_w259_results': 'n1_w259_results.json' in seg,", "    'out_name_n1_w260_results': 'n1_w260_results.json' in seg,", 1, "rf-out"),
 ("f1 = 'base=585101 span=2000'", "f1 = 'base=587301 span=2000'", 1, "f1"),
 ("f2 = 'base=587101 span=200'", "f2 = 'base=589301 span=200'", 1, "f2"),
 ("m258 = re.search(r'258: \\{\"batch\": \"PERPETUAL-N1-W258\"', n1t)",
  "m259 = re.search(r'259: \\{\"batch\": \"PERPETUAL-N1-W259\"', n1t)", 1, "m25x"),
 ("w258_seg = n1t[m258.start():m258.start() + 8000] if m258 else ''",
  "w259_seg = n1t[m259.start():m259.start() + 8000] if m259 else ''", 1, "wseg-assign"),
 ("if '259: {' in w258_seg:\n    w258_seg = w258_seg[:w258_seg.find('259: {')]",
  "if '260: {' in w259_seg:\n    w259_seg = w259_seg[:w259_seg.find('260: {')]", 1, "wseg-cut"),
 ("boundary = bool(m258) and '582901' in w258_seg and '584901' in w258_seg",
  "boundary = bool(m259) and '585101' in w259_seg and '587101' in w259_seg", 1, "boundary"),
 ("sd = 'results/p2cal_ext/n1_w259'", "sd = 'results/p2cal_ext/n1_w260'", 1, "sd"),
 ("'--prereg', 'research/PERPETUAL_N1_W259_PREREG.md'],",
  "'--prereg', 'research/PERPETUAL_N1_W260_PREREG.md'],", 1, "banned-prereg"),
 ("r_git = subprocess.run(['git', 'show', '89aeea31b:scripts/perpetual_faces_n1.py'],",
  "r_git = subprocess.run(['git', 'show', 'e8a9d5d67:scripts/perpetual_faces_n1.py'],", 1, "git-show"),
 ("r_git_pf = subprocess.run(['git', 'diff', '89aeea31b', '--', 'scripts/perpetual_faces.py'],",
  "r_git_pf = subprocess.run(['git', 'diff', 'e8a9d5d67', '--', 'scripts/perpetual_faces.py'],", 1, "git-diff"),
 ("    'r1064 window: splice commit 89aeea31b = worktree bytes directly (zero '",
  "    'r1065 window: splice commit e8a9d5d67 = worktree bytes directly (zero '", 1, "note-head"),
 ("w258_finalize_present = os.path.exists('results/perpetual_faces/n1_w258_results.json')",
  "w259_finalize_present = os.path.exists('results/perpetual_faces/n1_w259_results.json')", 1, "wprev-present"),
 ('"freeze-time FREE evidence consumed verbatim from _w259bmc_freeze_receipt.json (both bands); whole-file per-span family faces count-asserted",',
  '"freeze-time FREE evidence consumed verbatim from _w260bmc_freeze_receipt.json (both bands); whole-file per-span family faces count-asserted",', 1, "seedadmit-note"),
 (' "wave": 259,', ' "wave": 260,', 1, "wave-num"),
 ('"phase": "PRE-FINALIZE six-gate (r1064 bm-c clean continuation window; standing law -- engine self-burn 12/12 landed post-W259 splice 89aeea31b via batched ledger appends, finalize not yet run)",',
  '"phase": "PRE-FINALIZE six-gate (r1065 bm-c 55th-gen absorb-continuation window; standing law -- engine self-burn 12/12 landed post-W260 splice e8a9d5d67 via batched ledger appends, finalize not yet run)",', 1, "phase"),
 ('"prior_wave_258_boundary_kept": boundary,', '"prior_wave_259_boundary_kept": boundary,', 1, "boundary-key"),
 ('   "a_seed_base": 585101, "b_exit_seed_base": 587101,',
  '   "a_seed_base": 587301, "b_exit_seed_base": 589301,', 1, "wcr-bases"),
 ('   "shard_subdir": "n1_w259", "out_name": "n1_w259_results.json",',
  '   "shard_subdir": "n1_w260", "out_name": "n1_w260_results.json",', 1, "wcr-names"),
 ("   \"seed_bases_match_freeze_bands\": fr['bands']['A'] == [585101, 587100] and fr['bands']['B'] == [587101, 587300],",
  "   \"seed_bases_match_freeze_bands\": fr['bands']['A'] == [587301, 589300] and fr['bands']['B'] == [589301, 589500],", 1, "bands-match"),
 ('  "w258_finalize_product_present": w258_finalize_present,',
  '  "w259_finalize_product_present": w259_finalize_present,', 1, "wprev-key"),
 ('  "prev_total": 991935, "prev_merged_n": 565520,',
  '  "prev_total": 994135, "prev_merged_n": 567720,', 1, "ledger-prev"),
 ('  "expect_total": 994135, "expect_merged": 567720,',
  '  "expect_total": 996335, "expect_merged": 569920,', 1, "ledger-expect"),
 ('  "anchor": "W258 finalize (r1062 52nd-gen absorb-continuation one-pass 991,935/K=565,520) per freeze receipt w258_upstream face",',
  '  "anchor": "W259 finalize (r1064 54th-gen absorb-continuation one-pass 994,135/K=567,720) per freeze receipt w259_upstream face",', 1, "ledger-anchor"),
 ('      and w258_finalize_present\n', '      and w259_finalize_present\n', 1, "ok-wprev"),
 ("                  'w258_finalize_present': w258_finalize_present,",
  "                  'w259_finalize_present': w259_finalize_present,", 1, "print-wprev"),
 ("io.open('results/_r1064bmc_w259_sixgate.json', 'w', encoding='utf-8').write(",
  "io.open('results/_r1065bmc_w260_sixgate.json', 'w', encoding='utf-8').write(", 1, "out-file"),
]

t = src
for old, new, want, tag in R:
    n = t.count(old)
    assert n == want, "GATE %s: %r count %d != %d" % (tag, old[:60], n, want)
    t = t.replace(old, new)

# residual scan: no stale prior-wave tokens may survive (585101/587101 legitimately
# remain ONLY as the prior-wave boundary face created by the boundary replace)
for bad in ['W258', 'w258', 'n1_w258', '89aeea31b', '991935', '565520', '991,935',
            'K=565,520', '582901', '584901', 'r1062', '_w259bmc', 'r1064 bm-c']:
    assert bad not in t, "RESIDUAL %r survived" % bad

io.open('results/_r1065bmc_w260_sixgate.py', 'w', encoding='utf-8', newline='').write(t)
print("CLONE OK: %d replaces all count-asserted; residual scan clean" % len(R))
