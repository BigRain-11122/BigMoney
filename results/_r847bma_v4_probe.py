import os, datetime
mg = r'C:\Users\sjs20\Desktop\FluxGroup\gaming\MiniGame'
dj = os.path.join(mg, '硅基生命元宇宙-data.js')
t = open(dj, encoding='utf-8').read()
print('data.js bytes:', os.path.getsize(dj), '| mtime:', datetime.datetime.fromtimestamp(os.path.getmtime(dj)))
print('has gen_ts:', 'gen_ts' in t)
print('SILICON_DATA marker:', 'window.SILICON_DATA' in t)
for probe in ['board_top', 'live_strip', 'fleet_pulse', 'mchips2', 'await_review', 'commit_pulse']:
    print('data key', probe, ':', probe in t)
c = open(os.path.join(mg, 'tools', 'siliconwatch', 'canonical.html'), encoding='utf-8').read()
print('canonical references data.js:', '硅基生命元宇宙-data.js' in c)
print('canonical v4 markers board_top/fleet_pulse/gen_ts:', 'board_top' in c, 'fleet_pulse' in c, 'gen_ts' in c)
