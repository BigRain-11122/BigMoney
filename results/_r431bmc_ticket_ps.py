# -*- coding: utf-8 -*-
# r431 bm-c closeout legs: (1) T-144 ticket progress_r431_bmc field (JSON surgery, reload-verified);
# (2) pit-ps.md +1 direct-write entry (post-split convention, assertions before write).
import hashlib, json, sys, datetime

REPO = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
TICKET = REPO + r'\fleet\tasks\T-2026-10-02-144-P1.json'
PITPS = REPO + r'\research\pit-ps.md'
ROUND_TAG = 'r431 bm-c'

PROGRESS = ("POST-SPLIT INCREMENT SWEEP + FLOW-SINK (r431, D-06 window): 4 hot-layer pit entries verbatim -> "
    "domain files -- pit-spawn +2 (r422 three-generation executor behead-adoption law / r426 CreateNoWindow "
    "multi-child driver ignition law), pit-git +1 (r423 merge-window triple trap: origin-side residual marker "
    "whole-repo scan + porcelain UU full scan + pre-push triple fetch recheck), pit-tooling +1 (r629 rehearsal/"
    "harness mirror = call-site-guard replication law); +1 flow-sink (r628 bm-b sec.4 pin receipt -> "
    "research/memory-archive/202610.md r431 section + cold-ptr line per r444 paradigm); 3 domain-pointer receipt "
    "extensions; CODELY.md 30442 -> 25418 B = BELOW the D-06 <=30KB main-file target (first time); byte recon "
    "delta 5024 == removed 5793 - ext 503 - coldptr 266; zero-loss independent verify 10/10 (verbatim in-place "
    "+ source zero-residue + utf-8 strict + lone-CR=0) + surgical numstat (CODELY 4+/8-, pit-git 3+/0-, "
    "pit-tooling 3+/0-, pit-spawn 5+/1- [r625 no-trailing-newline position pair, content byte-identical], "
    "archive 6+/0-); +1 pit-ps direct-write (wrapper multiline-output single-string-item parsing pit, in-round "
    "live catch); receipt results/_r431bmc_pit_sweep.json + script results/_r431bmc_sweep.py. "
    "REMAINING for D-06 closure (10-07): hot-layer increment sweep of the 10-03 afternoon accumulation "
    "(r627/r630/r631-bma/r631-bmb/r632; r633 = active adjudication case, stays hot) + pit-data CRLF-face decision "
    "+ pit-git 107KB over-30KB-limit sub-split ruling + flow-sinking of remaining receipt faces + final "
    "full-reconciliation pass.")

# --- leg 1: ticket JSON surgery ---
raw = open(TICKET, 'rb').read()
tk = json.loads(raw.decode('utf-8'))
if 'progress_r431_bmc' in tk:
    print('FAIL idempotency: progress_r431_bmc already present')
    sys.exit(2)
tk['progress_r431_bmc'] = PROGRESS
out = json.dumps(tk, ensure_ascii=False, indent=1)
json.loads(out)  # round-trip validation before write
open(TICKET, 'wb').write(out.encode('utf-8'))
chk = json.loads(open(TICKET, 'rb').read().decode('utf-8'))
assert chk['progress_r431_bmc'] == PROGRESS
print('TICKET UPDATED progress_r431_bmc (%dB)' % len(PROGRESS.encode('utf-8')))

# --- leg 2: pit-ps direct-write ---
ENTRY_TS = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')[:-1] + 'x'
ENTRY = ('- [' + ENTRY_TS + ' r431 bm-c] silent-git/Invoke-SilentExe 包装器多行输出=单一 PS 字符串项坑'
 '（本窗 pit-spawn diff 复核实弹）：包装器把 git stdout+stderr 合并后 Write-Output 一个多行字符串——调用侧 '
 '`$d = & $sg -GitArgs \"diff ...\"` 得到的是**单个多行 string**而非行数组，直接 `$d | Where-Object {$_ -match '
 '\"^[+-]\"}` 整块字符串单点匹配=恒零命中假空结果（本窗首查 0 行实弹）；正法=先 `($d -split \"`r?`n\")` 行化再'
 '过滤/计数，行数自检先行（TOTAL_DIFF_LINES 类计数）；族=r409 ConvertFrom-Json/r413 ArgString 的「PS 输出形态'
 '直觉错配」族新面（wrapper 面首例）。How to apply：一切下游按行解析 silent-git/Invoke-SilentExe 输出前必先 '
 'split 行化；解析面自检=先打印行数再过滤。')

def load_logical(path):
    text = open(path, 'rb').read().decode('utf-8')
    trailing = text.endswith('\r\n')
    lines = [ln.rstrip('\r') for ln in text.split('\n')]
    if trailing and lines and lines[-1] == '':
        lines.pop()
    return lines, trailing

dl, dtrailing = load_logical(PITPS)
if any('r431 bm-c' in ln for ln in dl):
    print('FAIL idempotency: r431 already in pit-ps')
    sys.exit(2)
if any(ln.lstrip(' ').startswith('- [' + ENTRY_TS[:16]) for ln in dl):
    print('FAIL needle furniture collision')
    sys.exit(2)
core_b = len(ENTRY.encode('utf-8')) + 1
core_md5 = hashlib.md5((ENTRY + '\n').encode('utf-8')).hexdigest()
DIRECT = ('> 直写行（' + ROUND_TAG + '·post-split convention direct-write）：+1 条（包装器多行输出单一字符串项'
 '×按行过滤恒空——本窗 pit-spawn diff 复核 0 命中实弹·r409/r413 PS 输出形态错配族 wrapper 面新例）·追加核 '
 + str(core_b) + ' B（LF blob 面·md5=' + core_md5 + '）·尾部整行追加·件内对账行为准。')
last_gt = max(i for i, ln in enumerate(dl) if ln.startswith('>'))
dl.insert(last_gt + 1, DIRECT)
while dl and dl[-1] == '':
    dl.pop()
dl.append('')
dl.append(ENTRY)
new_text = '\r\n'.join(dl) + ('\r\n' if dtrailing else '')
ndl = new_text.split('\r\n')
assert ENTRY in ndl, 'verbatim-present FAIL'
assert '\r\r\n' not in new_text, 'CRLF-corruption FAIL'
open(PITPS, 'wb').write(new_text.encode('utf-8'))
print('PIT-PS +1 direct-write (core %dB md5=%s) pre_insert_gt=%d' % (core_b, core_md5, last_gt))
print('CLOSEOUT LEGS DONE')
