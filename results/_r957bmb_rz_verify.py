# r957 bm-b rz post-verify + CCPC copy for POOL-0011 B机10款 (after src dual-candidate fix).
# Mirrors r956 driver step-7 verification; writes results/_r957bmb_rz_receipt.json.
import datetime, importlib.util, json, os, re, shutil

WS = r'C:\Fluxgroup\MiniGame\MiniGame\软著申请材料'
BM = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
REC = BM + r'\results\_r957bmb_rz_receipt.json'
B10 = ['G04', 'G05', 'G07', 'G08', 'G13', 'G14', 'G20', 'G23', 'G26', 'G28']

spec = importlib.util.spec_from_file_location('gcc', os.path.join(WS, 'generate_copyright.py'))
gcc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gcc)

res = {}
for k in B10:
    cfg = gcc.PROJECTS[k]
    src = gcc.resolve_src(cfg)
    out_dir = os.path.join(WS, cfg.get('out_dir', '%s_%s' % (k, cfg['name_en'])))
    txt = os.path.join(out_dir, '%s_%s_源程序.txt' % (cfg['name_en'], cfg['version']))
    pdf = os.path.join(out_dir, '%s_%s_源程序.pdf' % (cfg['name_en'], cfg['version']))
    pdf_ok = os.path.exists(pdf) and os.path.getsize(pdf) > 10000
    pages = lines = cs_files = None
    guide_synced = None
    if os.path.exists(txt):
        t = open(txt, encoding='utf-8-sig', errors='replace').read()
        pages = t.count(' 页 共 ')
    gm = os.path.join(out_dir, '申请表填写指南.md')
    if os.path.exists(gm):
        g = open(gm, encoding='utf-8-sig', errors='replace').read()
        m = re.search(r'\| 源程序量 \| (\d+)行（(\d+)个\.cs文件）', g)
        if m:
            lines = int(m.group(1)); cs_files = int(m.group(2)); guide_synced = True
        else:
            guide_synced = False
    ccpc_ok = None
    if pdf_ok:
        ccpc = os.path.join(out_dir, 'CCPC 提交材料')
        os.makedirs(ccpc, exist_ok=True)
        try:
            shutil.copy2(pdf, os.path.join(ccpc, os.path.basename(pdf)))
            ccpc_ok = True
        except Exception as e:
            ccpc_ok = 'copy fail %s' % e
    res[k] = {'src': src, 'txt': os.path.exists(txt), 'pdf_ok': pdf_ok, 'pages': pages,
              'lines': lines, 'cs_files': cs_files, 'guide_synced': guide_synced, 'ccpc': ccpc_ok}

all_ok = all(v['pdf_ok'] and v['txt'] and v['pages'] and v['guide_synced'] and v['ccpc'] is True and v['src'] for v in res.values())
receipt = {
    'driver': 'r957bmb rz post-verify (POOL-0011 B机10款 after dual-candidate src fix)',
    'ts': datetime.datetime.now().astimezone().isoformat(timespec='seconds'),
    'status': 'GEN_DONE_OK' if all_ok else 'FAIL',
    'fix': 'generate_copyright.py r957: SRC_ROOTS += C:/Fluxgroup/MiniGame (bare-name root); B机10款 src_rel -> dual candidates [G-prefixed, bare] (C机 G09Y/G10 precedent)',
    'keys': res,
    'next': 'r957: group-repo tree-surgery commit (overlay onto freshest origin/main 软著申请材料 subtree; fetch-first; push) -> POOL-0011 done receipt (card ID + done + group commit sha)',
}
json.dump(receipt, open(REC, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps({k: {kk: v[kk] for kk in ('pages', 'lines', 'cs_files', 'guide_synced')} for k, v in res.items()}, ensure_ascii=False, indent=1))
print('STATUS=' + receipt['status'])
