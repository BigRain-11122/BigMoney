# r1000 append recovered B.7 memory line to CODELY.md (ASCII only per encoding law)
import os

line = ('[2026-10-18 02:2x r998 bm-b] IndexTTS-2.5 许可面登记（drama-dept 配音线长期合规面·'
        '正身=R-20261016-drama-sfx-tts-deploy-01.md B.7·bilibili Model Use License Agreement）：'
        '①双量级门槛 §2.2=月活>1亿或年营收>10亿元才需商业授权（未触发=协议直接可用）；'
        '②模型改进禁令 §3.4c=禁用 indextts2/其 Derivative Work 输出去改进其他商业 AI 模型——'
        '角色音色固化一律走 GPT-SoVITS（MIT）路线禁碰 indextts2 权重；'
        '③附加义务 §3.4a/b=发布页与文档显著标注「基于原模型许可」+每份拷贝保留版权声明与协议副本；'
        '④内容合规 §4.1c/d=输出遵守地方法律+AIGC 标识合规。'
        'How to apply：drama 配音线一切产出件发布前过此四条；EP001-003 试产 51 件已按此口径登记（media gitignored 不上链·交付地址走正文直给）。')

raw = open('CODELY.md', 'rb').read()
if not raw.endswith(b'\n'):
    raw += b'\n'
raw += line.encode('utf-8') + b'\n'
with open('CODELY.md.tmp', 'wb') as f:
    f.write(raw)
os.replace('CODELY.md.tmp', 'CODELY.md')

after = open('CODELY.md', 'r', encoding='utf-8', errors='replace').read()
assert line in after, 'verification failed'
assert 'IndexTTS' in after
print('B.7 line appended and verified; new size:', os.path.getsize('CODELY.md'))
