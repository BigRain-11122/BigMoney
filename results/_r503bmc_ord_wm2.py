# r503 bm-c: state targeted update for orders delta #2 (F06E044F -> 3BF0F16E, orphan-chain rows 3rd clobber+re-add, receipts not re-litigated)
import json
sp = r'K:\Fluxgroup\FluxGroup\quant\bigmoney\state-bm-c.json'
raw = open(sp, 'rb').read().decode('utf-8')
eol = '\r\n' if raw.count('\r\n') >= (raw.count('\n') - raw.count('\r\n')) else '\n'
obj = json.loads(raw)
redump = json.dumps(obj, ensure_ascii=False, indent=1)
assert raw == (redump if eol == '\n' else redump.replace('\n', '\r\n')), 'roundtrip gate FAIL'
assert obj['last_orders_sha'] == 'F06E044FD6DD854C7D1256EC63D7F0CBB4DE3A1C', 'unexpected prior watermark'
obj['last_orders_sha'] = '3BF0F16E3C40673FC6DBA0264B4725E88BE56253'
obj['note'] = obj['note'] + (" | orders delta#2 in-round: F06E044F->3BF0F16E = O-2026-0930-027~030 orphan-chain rows 3rd clobber+re-add "
                             "(r502-consumed content, receipts not re-litigated; HQ concurrent-writer churn family, MSG-2330 in adjudication window).")
s = json.dumps(obj, ensure_ascii=False, indent=1)
if eol == '\r\n':
    s = s.replace('\n', '\r\n')
open(sp, 'wb').write(s.encode('utf-8'))
chk = json.load(open(sp, encoding='utf-8'))
assert chk['last_orders_sha'] == '3BF0F16E3C40673FC6DBA0264B4725E88BE56253'
print('state orders watermark -> 3BF0F16E OK')
