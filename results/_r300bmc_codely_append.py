# r300: CODELY.md pit append (byte-safe, CRLF, single line)
import io, os

path = 'CODELY.md'
raw = io.open(path, 'rb').read()
crlf = raw.count(b'\r\n')
lf_only = raw.count(b'\n') - crlf
ending = b'\r\n' if crlf >= lf_only else b'\n'
if raw and not raw.endswith(b'\n'):
    tail_fix = ending
else:
    tail_fix = b''

line = (
    '- [2026-10-01 r300 bm-c] 静态并行分类器库内间接漏扫坑（multicore_census 65→38 大批假阴性实弹·T-134 s1）：'
    '普查分类器只认 runner 源内 multiprocessing/ProcessPoolExecutor/joblib 直用原语，'
    '漏扫库内间接（from parallel_runner import / run_cells_parallel( 调用）——trial_labor_w1~w14 全家'
    '+aggressive_lab/mass_trial 等 27 件实际 ProcessPool 全被误判 single_core，硬律禁入面虚假膨胀'
    '（假 65 vs 真 38）；修正=分类器增库内间接臂+注释行 lstrip(#) 跳过机制化（「命名≠实装」不再靠模式巧合）'
    '+selftest 10/10（含注释抗性双腿）；刷新后 hard-law live 面归零（EXCLUSION/FACEB/W14 三件均实为已转换）。'
    'How to apply: 一切「扫源码判性质」类普查/守卫必须覆盖库内间接面（import 或调用点任一命中即算实装），'
    '注释跳过做机制勿靠模式细节；census 类证据面任选 line 须防 docstring 证据位次假象（evidence[:3] 截断面）。'
).encode('utf-8') + ending

with io.open(path, 'ab') as f:
    f.write(tail_fix + line)

sz = os.path.getsize(path)
print('appended, size now', sz, '| hot-cold 50KB gate:', 'TRIGGER' if sz > 50 * 1024 else 'ok')
