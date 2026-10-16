# -*- coding: utf-8 -*-
# r1054 bm-c: sina 510300 daily-bar presence probe (update_daily expected-date gate diagnosis)
import urllib.request, re, json
u = 'https://quotes.sina.cn/cn/api/jsonp_v2.php/var%20_=/CN_MarketDataService.getKLineData?symbol=sh510300&scale=240&ma=no&datalen=3'
t = urllib.request.urlopen(u, timeout=30).read().decode('utf-8', 'replace')
days = re.findall(r'"day":"(\d{4}-\d{2}-\d{2})"', t)
out = {"sina_last_days": days, "has_2026_10_16": "2026-10-16" in days, "ts": __import__('time').strftime('%Y-%m-%dT%H:%M:%S')}
print(json.dumps(out, ensure_ascii=False))
json.dump(out, open(r'K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r1054bmc_sina_bar_probe.json', 'w', encoding='utf-8'), ensure_ascii=False)
