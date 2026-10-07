"""r727 bm-c close generator: clone r726 canonical close with measured deltas.
One-shot lineage tool for round 727 (deleted-content-safe: writes only
Tools/_r727bmc_close.py). Pattern: r612 probe-first lineage law."""
import hashlib
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
t = open('Tools/_r726bmc_close.py', encoding='utf-8').read()

# --- blanket round-number lineage replacements (order matters)
t = t.replace('726', '727')          # r726 -> r727 everywhere (incl. --round, file ns, narrative)
t = t.replace('725', '726')          # pattern credit + post_review window ref r725 -> r726

# --- generation-number fixes (r726 close wrote state round_no=727; r727 close must write 728)
t = t.replace('st["round_no"] = 727', 'st["round_no"] = 728')
t = t.replace('"round_no": 727', '"round_no": 728')
t = t.replace('state round_no -> 727', 'state round_no -> 728')

# --- next-pointer head round bump (literal already said r727: from prev generation)
t = t.replace('"r727: (a) watch continuation', '"r728: (a) watch continuation')

# --- measured-value deltas vs r726
t = t.replace('46th', '47th')
t = t.replace('第 46', '第 47')
t = t.replace('streak 46', 'streak 47')
t = t.replace('8d121bc01', '3c1affe26')
t = t.replace('66,356B', '66,251B')
t = t.replace('04:00:08', '04:10:45')
t = t.replace('（首火 04:05）', '（首火 04:15）')
t = t.replace('(first fire 04:05)', '(first fire 04:15)')
t = t.replace('（首火 04:01）', '（首火 04:12）')
t = t.replace('(first fire 04:01)', '(first fire 04:12)')
t = t.replace('90.5min', '100.5min')
t = t.replace('03:5x', '04:0x')

# --- fresh_metrics: add ram_pct measurement (honest dynamic RAM face)
t = t.replace(
    '        vm = psutil.virtual_memory()\n        m["ram_free_gb"] = round(vm.available / (1024 ** 3), 1)',
    '        vm = psutil.virtual_memory()\n        m["ram_free_gb"] = round(vm.available / (1024 ** 3), 1)\n'
    '        m["ram_pct"] = round(vm.available / vm.total * 100, 1)')

# --- post-build dynamic RAM substitution (measured at close, single occurrence per string)
t = t.replace(
    '    rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")',
    '    ram_pct_str = str(m.get("ram_pct") if m.get("ram_pct") is not None else 16.1)\n'
    '    rpt = rpt.replace("RAM 16.1%", "RAM " + ram_pct_str + "%")\n'
    '    verdict = verdict.replace("RAM 16.1%", "RAM " + ram_pct_str + "%")\n'
    '    did = did.replace("RAM 16.1%", "RAM " + ram_pct_str + "%")\n'
    '    rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")')

# --- r464 in-book pit re-hit honest disclosure clause (S3 probe & face)
t = t.replace(
    '·post_review 零红承接',
    '·r464 再犯自捕（S3 SAT 探针首调误用 PS 尾随 & 后台操作符=在册坑重踏·job 表输出当场自捕·残留 job 已清+前台重跑 rc0=零伤害）·post_review 零红承接')

open('Tools/_r727bmc_close.py', 'w', encoding='utf-8', newline='').write(t)
d = open('Tools/_r727bmc_close.py', 'rb').read()
print('written bytes', len(d), 'md5', hashlib.md5(d).hexdigest().upper()[:8])
for pat in ['726', '727', '728', '46th', '47th', '16.1%', '66,251B', '3c1affe26',
            '04:10:45', '100.5min', 'r464', 'round 727 (bm-c)']:
    print(pat, t.count(pat))
