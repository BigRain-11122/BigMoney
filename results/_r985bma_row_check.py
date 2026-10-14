import io, json, re, sys
n1 = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = n1.find('238: {"batch": "PERPETUAL-N1-W238"')
block = n1[i:i+8000]
seg = block[:block.find('239: {')] if '239: {' in block else block
checks = {
 'a_seed_base_538404': '538404' in seg,
 'b_exit_540404': '540404' in seg,
 'shard_subdir_n1_w238': 'n1_w238' in seg,
 'out_name_w238': 'n1_w238_results.json' in seg,
 'engine_owner_bm_a': 'engine_owner": "bm-a"' in seg,
}
checks['row_faces_match_freeze_receipt'] = all(checks.values())
print(json.dumps(checks, indent=1))
sys.exit(0 if checks['row_faces_match_freeze_receipt'] else 1)
