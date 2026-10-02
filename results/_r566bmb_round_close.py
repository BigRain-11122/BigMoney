# -*- coding: utf-8 -*-
"""r566 bm-b round-close bookkeeping: state round_no (skip dead 564/565 per r529),
round report line, heartbeat (int epoch + T-format clock, R170/R178/R262 laws)."""
import json, time, datetime, psutil

# 1. state.json round_no 563 -> 566 (skip dead-session self-claims 564/565, r529 law)
sp = r'C:\Fluxgroup\FluxGroup\quant\bigmoney\state.json'
st = json.load(open(sp, encoding='utf-8'))
prev = st.get('round_no')
st['round_no'] = 566
json.dump(st, open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('state round_no:', prev, '->', 566, '(skips dead 564/565)')

# 2. round report line (bm-b uses logs/iteration-loop/round_reports.md)
rp = r'C:\Fluxgroup\FluxGroup\quant\bigmoney\logs\iteration-loop\round_reports.md'
now = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()
line = (f"{now} | r566 | dept:研究/工程 W64同带双冻让路收口(r565猝死遗产:杀活烧pid级+冻结稿全弃+10片复制品验属弃置零账本污染+MSG-0919回执) "
        f"+ W65 FREEZE同窗交付(第54枚引擎波·bm-b第20自有·席位MSG-0919公示·ADMIT 64键机证A 173_004..175_003/B 49_601..49_800零跳位·prereg锚W63落账链头503,148·W64在飞席FAIL-CLOSED r307·selftest W2..W65全绿) "
        f"+ 引擎psutil竞态崩tick红项同轮修复(_py_cpu_pct一采死pid守卫·9:14:01实弹+手工复现双证) + 点火实证shard-0..5落盘tick自续 "
        f"+ S6 30腿全绿(假期no-op面·dualrun streak11零漂·审计旗=池饿引擎道活跃注记) | 证据: commit c97e04a49(外科推送删除集空+19/19)+dcae6d6f0(引擎修复)·n1_w65/shard-0..5产物·selftest PASS全链 | "
        f"下轮指针: W65烧录12/12后finalize(W64 bm-a落账后链序one-pass·r538一过律)+守tick健康(psutil补丁观察窗) | 本地未达 origin commit 数=0\n")
with open(rp, 'a', encoding='utf-8') as f:
    f.write(line)
print('round report appended (r566)')

# 3. heartbeat fleet/machines/bm-b.json (int epoch + T clock)
hp = r'C:\Fluxgroup\FluxGroup\quant\bigmoney\fleet\machines\bm-b.json'
h = json.load(open(hp, encoding='utf-8'))
vm = psutil.virtual_memory()
cores = psutil.cpu_count() or 1
try:
    import subprocess
    g = subprocess.check_output(['nvidia-smi', '--query-gpu=memory.free',
                                 '--format=csv,noheader,nounits'], text=True)
    vram = int(g.splitlines()[0].strip())
except Exception:
    vram = h.get('gpu_free_vram_mb', 0)
h['last_seen'] = now
h['current_task'] = 'W65 burn in flight via engine tick (12 shards, self-continuing); r566 yield+freeze delivered'
h['cpu_cores'] = cores
h['free_ram_gb'] = round(vm.available / (1024 ** 3), 1)
h['gpu_free_vram_mb'] = vram
h['verdict'] = 'loaded_ok'
h['heartbeat_epoch_utc'] = int(time.time())
h['clock_read'] = now
json.dump(h, open(hp, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
# self-verify (R170/R178/R262: int epoch + T-format)
chk = json.load(open(hp, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
assert 'T' in chk['clock_read'], 'clock_read must be ISO 8601 T-separated'
print('heartbeat written: epoch int ok, clock T-format ok, vram_free_mb=', vram)
