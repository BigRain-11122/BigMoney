"""r831 final heal: index ledger/pool_core data-line purification + round_reports r831 re-append.

Pollution truth: ledger+pool_core carried REAL line-head conflict markers since the first
rebase segment's live-wins add (worktree was UU-marker state when added). round_reports
'marker' = r511 historical prose citation (false positive, origin-canonical content).
"""
import subprocess, json, io

def show(rev, path):
    return subprocess.run(['git', 'show', f'{rev}:{path}'], capture_output=True).stdout

def heal_jsonl(path, clean_rev):
    idx = subprocess.run(['git', 'show', ':' + path], capture_output=True).stdout
    clean = show(clean_rev, path)
    assert b'<<<<<<< HEAD' not in clean, f'{clean_rev}:{path} polluted?!'
    def data_lines(blob):
        out = []
        for ln in blob.decode('utf-8', 'replace').splitlines():
            s = ln.strip()
            if not s or s.startswith('<<<<<<<') or s.startswith('=======') or s.startswith('>>>>>>>'):
                continue
            try:
                json.loads(s)
                out.append(ln)
            except Exception:
                pass
        return out
    cl, cur = data_lines(clean), data_lines(idx)
    seen = {}
    for src in (cl, cur):
        for ln in src:
            if ln not in seen:
                try:
                    seen[ln] = json.loads(ln).get('ts', '')
                except Exception:
                    seen[ln] = ''
    merged = sorted(seen.keys(), key=lambda l: seen[l])
    with open(path, 'wb') as f:
        for ln in merged:
            f.write((ln + '\n').encode('utf-8'))
    for ln in merged[-5:]:
        json.loads(ln)
    print(f'{path}: clean-rev {len(cl)} + idx-data {len(cur)} -> {len(merged)} lines, zero marker, parse OK')

heal_jsonl('results/saturation_engine/ledger_bm-a.jsonl', 'f208aa6fb')
heal_jsonl('results/pool_core_samples.jsonl', 'f208aa6fb')

# round_reports: re-append r831 line (was lost when I rewrote to 81a480662 base during the false-positive heal)
R = 'round_reports-bm-a.md'
cur = io.open(R, encoding='utf-8', errors='replace').read()
assert '[r831 bm-a]' not in cur, 'r831 line already present'
r831_line = (
"\n2026-10-07T16:20:00+08:00 | r831 bm-a W175 判决批全链收口+rebase 三窗治愈 (dept:研究/工程/舰队) | [watermark verdict: 绿 red=false; satengine alive rc0 queue0 idle 12/12 burned] | "
"当前活: S0 第一段 rebase 治愈（r825 族 6 面：deep-ts origin-freshest+live-wins 超集+history 三方 union 131 行）→ W175 pre-finalize 三恒等门 GREEN（半开 tiling 语义首遇判读修正=r831 新坑律直写 pit-engine-finalize.md）→ finalize one-pass ledger 788,212+2,200=790,412 EXACT/K 382,920 EXACT/skill_line 1.1845→1.1844 → §5 四预键全过 → §7/§8 机械回填（9+/2- 删除恰=占位两行=冻结面零改）→ push-race 三窗批解（19/22 面 lane resolver+孪生同侧+js-wrapper 字节侧+r220 shard-11 暂移）→ 中窗 add -A 标记残留（ledger/pool_core 两件）被 pre-commit claw 拦截→soft-reset 全链折叠重建零污染入史+round_reports claw 报= r511 历史引述行假阳性如实勘注 | "
"最近实物: results/perpetual_faces/n1_w175_results.json（15:57 finalize one-pass·账本 790,412 EXACT）+ research/PERPETUAL_N1_W175_PREREG.md §7/§8 回填 + 三门回执 _r831bma_w175_three_gate.json | "
"验证: r776 账本自证 PASS+缺省 selftest 复绿（r522）+smoke 48/48+S6 30 腿 rc0 黄金周 no-op 族+dualrun streak 51+attrition CLEAN+S7 四件套绿 | "
"计分: 2（能跑能看实物=W175 判决批收口）| 宝藏捕获问: 半开分片带语义判读修正已入域件·零新方法零新宝藏[nulls-deepening 例波] | "
"下轮指针: r832=W176 席位链（probe→seat MSG→freeze buildgen E41 血统）+复市 10-08 数据链首刷+O-1207 题材批 48h 窗 10-08 12:07 检查 | 本地未达 origin commit 数: 0（commit+push+fetch 复核） [r831 bm-a]\n"
)
with open(R, 'a', encoding='utf-8', newline='') as f:
    f.write(r831_line)
print('round_reports: r831 line re-appended')

# strict line-head marker scan over ALL staged faces (excludes embedded-citation false positives)
r = subprocess.run(['git', 'add', '-A'], capture_output=True)
r2 = subprocess.run(['git', 'diff', '--cached', '--name-only'], capture_output=True, text=True, encoding='utf-8')
bad = []
for p in r2.stdout.splitlines():
    if not p.strip():
        continue
    b = subprocess.run(['git', 'show', ':' + p], capture_output=True).stdout
    for ln in b.decode('utf-8', 'replace').splitlines():
        if ln.startswith('<<<<<<< ') or ln.startswith('>>>>>>> '):
            bad.append(p)
            break
print('STRICT staged-marker scan:', 'CLEAN (0 files)' if not bad else f'POLLUTED: {bad}')
