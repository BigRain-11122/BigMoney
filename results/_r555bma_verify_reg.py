"""r555 helper: verify WAVE_CONFIGS integrity post-edit (W46 intact + W47 registered)."""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import py_compile
py_compile.compile(os.path.join(ROOT, 'scripts', 'perpetual_faces_n1.py'), doraise=True)
print('compile OK')

import importlib
import perpetual_faces_n1 as n1
print('WAVE_CONFIGS keys tail:', sorted(n1.WAVE_CONFIGS)[-4:])
c46 = n1.WAVE_CONFIGS[46]
c47 = n1.WAVE_CONFIGS[47]
print('W46:', c46['a_seed_base'], c46['b_exit_seed_base'], c46['shard_subdir'], c46['engine_owner'])
print('W46 prereg tail:', c46['prereg'][-120:])
print('W47:', c47['a_seed_base'], c47['b_exit_seed_base'], c47['shard_subdir'], c47['engine_owner'])
print('W47 prereg head:', c47['prereg'][:120])

import perpetual_faces as pf
print('N1_BANDS keys tail:', sorted(pf.N1_BANDS)[-3:])
print('N1_BANDS[47]:', pf.N1_BANDS[47])
