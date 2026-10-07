# r840 bm-a direct-write pit entries (main-file 200B redline headroom -> r830 domain-direct precedent)
# Entry 1 -> research/pit-spawn.md (kill-gate law); Entry 2 -> research/pit-ps.md (slice reversal)
import json, os, hashlib

E1 = """- [2026-10-07 20:1x r840 bm-a] **共享 CEO 机孤儿探针单快照击杀面过宽坑（r840 O-1300 执法实弹·10 面误杀·当场治愈）**: v1.0 探针把「父死+无隐藏宿主祖先+CPU 停滞」单 5s 快照即入击杀集——在 CEO 共享机上该判据把健康基础设施全打成僵尸：9 个 stdio MCP 服务器（mcp-for-unity/duckduckgo-mcp：launcher 分离 spawn 后父死=正常态，stdin 阻塞等待=零 CPU 稳态）+1 个 serve_forever 常驻门（BigDomain frontdoor.py）全被杀（幸 MCP 宿主自愈复活+frontdoor pythonw 隐藏重启 pid 41108 零业务损失）。正法三闸=①击杀集=WATCH_RE 算力面 ONLY（judge/burn/runner 族——其本职=烧 CPU，停滞才是真死）；非 watch 孤儿（服务器/hook/杂项 python）一律只报不杀②stdio 服务器带（--transport stdio|uv-tools 路径）单列 idle_server 永不杀③持久性门：孤儿+停滞须 >=2 连续扫描才准杀，首见=只记证据。How to apply：未来任何「进程活性判定→自动击杀」工具上共享 CEO 机必带三闸；判死!=杀，先观察后行动（r340 三面活性律的正确推广=多快照）。
"""

E2 = """- [2026-10-07 20:2x r840 bm-a] **PS 单元素数组 [1..($parts.Length-1)] 反转域切片坑（r840 S6 批 harness 实弹·6 假 rc=2）**: $parts 为单元素（Length=1）时 $parts[1..0] 取 index 1（越界=$null）与 index 0=脚本名自身——拼接后把脚本文件名当子命令传给脚本 -> 6 个 gate 脚本齐报「unknown subcommand: <script>.py」rc=2 假机制故障（真默认入口=bare 调用 sys.argv[1] 缺省='gate'，重跑零参 6/6 rc0 治愈）。正法=拆参前先判 $parts.Length -gt 1 再切片，或 @() 包裹+$null 过滤。How to apply：批处理参数切片必带长度守卫；「unknown subcommand」报文含脚本名自身=切片反转铁证。
"""

def append_entry(path, entry):
    add = entry.encode('utf-8')
    with open(path, 'rb') as fh:
        before = fh.read()
    if add in before:
        return len(before), len(before), 0, add  # already present (crash-replay guard)
    if before and not before.endswith(b'\n'):
        before += b'\n'
    with open(path, 'wb') as fh:
        fh.write(before + add)
    return len(before), len(before) + len(add), len(add), add

r = {'ts': '2026-10-07T20:18:00+08:00', 'machine': 'bm-a', 'round': 'r840',
     'law_ref': 'r830 direct-write precedent (main-file redline headroom 200B)',
     'entries': []}
for path, entry in [('research/pit-spawn.md', E1), ('research/pit-ps.md', E2)]:
    b0, b1, addlen, addbytes = append_entry(path, entry)
    sha = hashlib.sha256(addbytes).hexdigest()[:16]
    r['entries'].append({'path': path, 'bytes_before': b0, 'bytes_after': b1,
                        'appended_bytes': addlen, 'sha16_appended': sha})
with open('results/_r840bma_pit_directwrite.json', 'w', encoding='utf-8', newline='\n') as fh:
    json.dump(r, fh, ensure_ascii=False, indent=2)
for e in r['entries']:
    print(e['path'], e['bytes_before'], '->', e['bytes_after'], '+', e['appended_bytes'], 'B sha16', e['sha16_appended'])
print('receipt: results/_r840bma_pit_directwrite.json')
