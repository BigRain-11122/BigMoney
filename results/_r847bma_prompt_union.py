# r847 prompt conflict union: canon-first (bm-c r704 first-landed step keeps
# position), bm-a r847 mechanical-carrier increments folded INTO the canon step
# (zero loss, zero duplicate steps). Base = theirs staged blob :2:.
import subprocess

t = subprocess.run(['git', 'show', ':2:Tools/iteration_prompt.txt'],
                   capture_output=True).stdout.decode('utf-8')

# 1) title paren: add bm-a carrier note
a1 = u'bm-c EngineTick 自承接〔r704 部署〕）**'
b1 = u'bm-c EngineTick 自承接〔r704 部署〕·bm-a 循环器轮首簿记腿〔r847 部署·Tools/idle_trigger.py 机队通用 machine_id-aware〕）**'
assert t.count(a1) == 1, 'a1=%d' % t.count(a1)
t = t.replace(a1, b1)

# 2) verdict read leg: bm-a carrier face
a2 = u'**闲置硬触发自检步（O-20261007-2315·C-20261007-05 过会 7/7·resource-chain §二.九.6·bm-c EngineTick 自承接〔r704 部署〕·bm-a 循环器轮首簿记腿〔r847 部署·Tools/idle_trigger.py 机队通用 machine_id-aware〕）**：每轮读本机 verdict'
b2 = a2 + u'（bm-a 载体面=循环器轮首已自动跑 python Tools\\idle_trigger.py 落本机 results\\idle_trigger.<本机id>.json+心跳 idle_rounds/agenda_starved 两字段，读该件即得）'
assert t.count(a2) == 1, 'a2=%d' % t.count(a2)
t = t.replace(a2, b2)

# 3) clear-on-work leg: --claimed/--worked flags
a3 = u'（领单即清零·值守轮消费即当日 RED 处置）——检出到动作延迟天级→轮级根治'
b3 = u'（领单即清零·值守轮消费即当日 RED 处置；领单或有实际产出工→同轮 python Tools\\idle_trigger.py --claimed 或 --worked 即清零——bm-a 载体面·他机无载体按本步语义手工清零心跳）——检出到动作延迟天级→轮级根治'
assert t.count(a3) == 1, 'a3=%d' % t.count(a3)
t = t.replace(a3, b3)

# sanity: single line law (no newlines introduced), no conflict markers, key faces present
assert t.count('\n') == 9, 'newline count %d' % t.count('\n')
assert '<<<<<<<' not in t and '>>>>>>>' not in t
for probe in (u'闲置硬触发自检步', u'--worked', u'results\\idle_trigger.<本机id>.json', u'> 其他一切', u'> 修红'):
    assert probe in t, probe
with open('Tools/iteration_prompt.txt', 'w', encoding='utf-8') as f:
    f.write(t)
print('union written, len:', len(t))
