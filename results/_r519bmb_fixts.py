import io

p = 'logs/iteration-loop/round_reports.md'
data = open(p, 'rb').read()

new = data.replace('5/12 分片落盘@20:0x'.encode('utf-8'),
                  '5/12 分片落盘@19:5x'.encode('utf-8'))
new = new.replace('（5/12@20:0x·引擎 idle 队列'.encode('utf-8'),
                  '（5/12@19:5x·引擎 idle 队列'.encode('utf-8'))
new = new.replace('shard-0..4-of-12.json（20:0x 逐片落盘）'.encode('utf-8'),
                  'shard-0..4-of-12.json（19:5x 逐片落盘）'.encode('utf-8'))

assert new != data, 'no replacement made'
open(p, 'wb').write(new)
print('fixed 3 clock refs -> 19:5x')
