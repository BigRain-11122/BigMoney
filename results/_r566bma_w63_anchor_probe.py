import io
t = io.open('scripts/perpetual_faces.py', encoding='utf-8').read()
a1 = '    62: {"a": (167_004, 169_003), "b_exit": (48_601, 48_800),\n         "engine_owner": "bm-a"},\n}\n'
print('edit1 anchor count:', t.count(a1))
t2 = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
a2 = '                            "shard_subdir": "n1_w62", "out_name": "n1_w62_results.json",\n                            "engine_owner": "bm-a"},\n                       }'
print('edit2 anchor count:', t2.count(a2))
print('edit3 anchor count:', t2.count('\n    # --- T-141 s2 lane face'))
a5 = 'law sec.4 W62 row, r565 bm-a] "' + '\n          "+ T-141 s2 '
print('edit5 anchor count:', t2.count(a5))
t4 = io.open('research/PERPETUAL_FACES.md', encoding='utf-8').read()
print('edit4 anchor count:', t4.count('\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'))
print('canon W62 row count:', t4.count('- N1 \u6ce262\uff08'))
print('canon W61 row count:', t4.count('- N1 \u6ce261\uff08'))
print('eol probe pf:', 'CRLF' if t.count('\r\n') * 2 > t.count('\n') else 'LF')
print('eol probe n1:', 'CRLF' if t2.count('\r\n') * 2 > t2.count('\n') else 'LF')
print('eol probe canon:', 'CRLF' if t4.count('\r\n') * 2 > t4.count('\n') else 'LF')
