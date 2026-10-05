import io

n1 = io.open(r"scripts\perpetual_faces_n1.py", encoding="utf-8").read()
wc = ('                            "shard_subdir": "n1_w134", "out_name": "n1_w134_results.json",\n'
      '                            "engine_owner": "bm-a"},\n'
      '                       }')
print('wc_anchor count:', n1.count(wc))
prose = 'W134 row, r739 bm-a] "\n          "+ T-141 s2 "'
print('prose_anchor count:', n1.count(prose))
fa = ('        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"\n'
      '    finally:\n'
      '        _set_wave(2)\n'
      '    # --- T-141 s2 lane face')
print('face_anchor count:', n1.count(fa))
pf = io.open(r"scripts\perpetual_faces.py", encoding="utf-8").read()
w134_row = ('    134: {"a": (311_004, 313_003), "b_exit": (69_302, 69_501),\n'
            '         "engine_owner": "bm-a"},\n'
            '}')
print('pf w134 row+brace count:', pf.count(w134_row))
print('pf row135 already present:', '135: {"a": (313_004' in pf)
