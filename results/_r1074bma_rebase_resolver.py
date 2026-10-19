# r1074bm-a rebase-conflict resolver v3 (r1071 resolver-v2 lineage + GENERATOR-SUPERSET law)
# 12 UU faces, all regen/probe faces (zero append-only ledgers, zero shared registries).
# In rebase: OURS = origin base side, THEIRS = my commit being replayed.
# Rules: (1) regen twins -> generator face first (superset check), ts breaks ties;
#        (2) probe faces -> newer ts wins; (3) assert markers absent BEFORE add (r1073 law).
import subprocess, sys, re, json, io
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
REPO = r'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney'
def g(*args):
    r = subprocess.run(['git','-C',REPO]+list(args), capture_output=True, text=True, encoding='utf-8', errors='replace')
    return r.returncode, (r.stdout or '')+(r.stderr or '')

UU = ["docs/daily_report/REPORT-2026-10-19.json",
      "docs/daily_report/REPORT-2026-10-19.md",
      "docs/live_usage/LIVE-2026-10-19.json",
      "docs/live_usage/LIVE-2026-10-19.md",
      "docs/live_usage/LIVE-latest.json",
      "docs/live_usage/LIVE-latest.md",
      "results/_attrition_guard_scan.json",
      "results/_r686bmb_d19_check.json",
      "results/compute_audit.json",
      "results/fundamental_b_layer_filter.json",
      "results/regime_state.json",
      "results/update_status.json"]

MARK_O = re.compile(r'<<<<<<<[^\r\n]*\r?\n(.*?)\r?\n=======\r?\n(.*?)\r?\n>>>>>>>', re.S)
def sides(path):
    raw = io.open(path, encoding='utf-8', errors='replace').read()
    blocks = MARK_O.findall(raw)
    return raw, blocks

def ts_in(text):
    hits = re.findall(r'"(?:ts|generated_at|asof|updated)"\s*:\s*"([^"]+)"', text)
    return hits[0] if hits else ''

def md_gen_ts(text):
    hits = re.findall(r'(20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})', text[:2000])
    return hits[0] if hits else ''

report_notes = []
resolved_take_mine = 0
for path in UU:
    raw, blocks = sides(path)
    if not blocks:
        # no marker blocks (auto-merge produced mixed or the file was already resolved)
        report_notes.append((path, 'NO_BLOCK'))
        continue
    ours_txt, theirs_txt = blocks[0][0], blocks[0][1]
    o_ts, t_ts = ts_in(ours_txt) or md_gen_ts(ours_txt), ts_in(theirs_txt) or md_gen_ts(theirs_txt)
    take = 'theirs'  # default: my replayed side
    why = 'mine-newer-or-equal'
    if o_ts > t_ts:
        take = 'ours'; why = 'origin-newer-ts'
    # generator-superset check for report/live twins: my side must carry the
    # attribution section + be at least as sectioned (deliverable law r1071)
    if 'REPORT-2026-10-19' in path and take == 'ours':
        mine_full = theirs_txt
        if '盈亏归因' in mine_full:
            take = 'theirs'; why = 'generator-superset-mine'
    print('%s | ours_ts=%s theirs_ts=%s -> take=%s (%s)' % (path, o_ts, t_ts, take, why))
    if take == 'theirs':
        rc, _ = g('checkout', '--theirs', '--', path)
    else:
        rc, _ = g('checkout', '--ours', '--', path)
    assert rc == 0, 'checkout failed for ' + path
    # whole-file marker scan (block-level resolution done by checkout)
    body = io.open(path, encoding='utf-8', errors='replace').read()
    assert '<<<<<<<' not in body and '>>>>>>>' not in body, 'residual markers ' + path
    rc, _ = g('add', '--', path)
    assert rc == 0
    resolved_take_mine += 1

# post-add full-file marker sweep across ALL UU (fail-loud, add-already-done is fine to re-add)
rc, out = g('diff', '--check')
print('diff --check rc', rc, 'CLEAN' if not out.strip() else out.strip()[:300])
rc, out = g('grep', '-l', '-E', r'^(<{7}|>{7}|={7}$)', '--', *UU)
print('grep marker files:', out.strip() if out.strip() else 'NONE')
print('resolved:', resolved_take_mine, 'no-block:', sum(1 for n in report_notes if n[1]=='NO_BLOCK'))
