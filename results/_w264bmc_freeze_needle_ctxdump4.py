# -*- coding: utf-8 -*-
import io
t = io.open('results/_w263bma_freeze_edits.py', encoding='utf-8', newline='').read()
w = io.open('results/_w262bmc_freeze_edits.py', encoding='utf-8', newline="").read()
for tag, needle in [
 ('e1a94b335', 'e1a94b335'),
 ('verified_r1068', 'verified r1068'),
 ('bmc_r1068_splice_window', 'bm-c r1068 splice window e1a94b335'),
 ('r1038_total', 'r1038'),
 ('r1068_total', 'r1068'),
 ('r1040', 'r1040'),
 ('r1039', 'r1039'),
 ('w263_receipt_sha_var', 'w263_receipt_sha'),
 ('freeze_edits_lineage', '_w262bmc_freeze_edits.py template'),
 ('commit_b32f6', 'b32f6bf1c'),
 ('proven_livefire', 'proven live-fire freeze'),
 ('hdr_word_complete', 'cycle COMPLETE bm-c r1068 closeout'),
 ('pre_wave_line', 'TWO HUNDRED AND SIXTY-THIRD ENGINE-OWNED WAVE'),
 ('hdr_engine_wave', 'TWO HUNDRED AND SIXTY-THIRD engine wave'),
 ('pr_engine_wave', 'TWO HUNDRED AND SIXTY-THIRD \\"'),
 ('pr_ord_capline', 'ENGINE-OWNED WAVE BY'),
 ('r522_law', 'r522 law'),
 ('n1_crlf_face', 'detect_eol'),
 ('cohort_main', 'bm-a loop freeze window'),
 ('hdr_exec_line', 'executed in the bm-a loop freeze window'),
 ('ceo_fill_standing', 'CEO fill-order standing 2026-10-08 ~23:5x'),
 ('w262_frozen_tpl', 'frozen W262 template'),
]:
    print(tag, t.count(needle))
print('--- W262 script n3r1 face ---')
print('n3r1_used244_in_w262', w.count('n3r1_used244'))
print('n3r1_used245_in_w262', w.count('n3r1_used245'))
print('w244a_in_w262', w.count('w244_a'))
