"""R362 bm-a: CODELY.md 35th-batch hot-cold fold (over 10KB hard line: 10,322B).
Migrates aged pointer/meta rows verbatim -> research/memory-archive/202609.md
section '坑律归档 2026-09-27 三十五批'; keeps active law pointers + User meta-law
+ the two law lines; appends this fold's meta line. Zero line loss: every
migrated line lands verbatim in the archive, verified by exact-match count.
"""
import io

SRC = 'CODELY.md'
ARC = 'research/memory-archive/202609.md'

raw = io.open(SRC, 'r', encoding='utf-8', newline='').read()
lines = raw.split('\n')

MIGRATE_KEYS = [
    '二十七批外迁（r101 bm-c',
    '二十六批外迁（r341 bm-a',
    '[r93 bm-c] 坑律：S0 stash-pop',
    '19:11 r98 bm-c] 坑律：轮首机器身份锚定',
    '19:4x r99 bm-c] 坑律：git 数据面双死窗',
    '二十九批外迁（r109 bm-c',
    '21:3x r109 bm-c] 坑律（三十一批外迁·指针）：轮首脏树',
    '17:3x r334 bm-b] 坑律（二十六批外迁·指针）：rolling-ledger',
    '17:5x r335 bm-b] 坑律（二十六批外迁·指针）：tick git',
    '17:5x r341 bm-a] 坑律（二十六批外迁·指针）：池批 stale-takeover',
    '17:2x r91 bm-c] 坑律（二十三批外迁·指针）：S0 pull',
    '17:4x r339 bm-a] 坑律（二十三批外迁·指针）：共享 JSON',
    '17:5x r340 bm-a] 坑律（二十四批外迁·指针）：round_no',
    '17:3x r334 bm-b] 坑律（二十三批外迁·指针）：rolling-ledger',
    '17:5x r335 bm-b] 坑律（二十五批外迁·指针）：tick add/stash',
    '21:15 r342 bm-b] 坑律（三十批外迁·指针）：PS Start-Job',
    '22:1x r110 bm-c] 坑律（三十二批外迁·指针）：孪生面',
    '三十批外迁（r110 bm-c',
    '三十一批外迁（r359 bm-a',
    '三十三批外迁（r112 bm-c',
]

migrated, kept = [], []
for ln in lines:
    hit = False
    for k in MIGRATE_KEYS:
        if ln.startswith('- ' + k) or ln.startswith('- [' + k) or (k in ln and ln.startswith('- ')):
            migrated.append(ln)
            hit = True
            break
    if not hit:
        kept.append(ln)

assert len(migrated) == len(MIGRATE_KEYS), \
    f"migration mismatch: {len(migrated)} vs {len(MIGRATE_KEYS)} -- {migrated}"

# --- append verbatim block to archive ---
arc = io.open(ARC, 'r', encoding='utf-8', newline='').read()
block = ('\n## 坑律归档 2026-09-27 三十五批（r362 bm-a·CODELY.md 超 10KB 硬线'
         '（10,322B）当窗整编·行级零丢失）\n')
block += '\n'.join(migrated) + '\n'
block += ('三十五批记录：上列 ' + str(len(migrated)) + ' 行=CODELY.md 原样 verbatim '
          '外迁（各所指 verbatim 皆在对应批节在位·检索按日期段）；保留=User 元律+法行 2+'
          '活跃指针行族（r344×2/r359/r360/r346）+本批 meta 行；CODELY.md 同窗加 T-94 R362 '
          '执行记录行。\n')
io.open(ARC, 'w', encoding='utf-8', newline='').write(arc + block)

# --- rewrite CODELY.md: kept lines + fold meta + execution record ---
meta = ('- 三十五批外迁（r362 bm-a·2026-09-27·超线 10,322B>10,000B 当窗整编·行级零丢失·'
        '撞批号核（origin 三十四批=bm-b r346 已在位·本批让号取三十五））：'
        '二十七/二十六/二十九/三十/三十一/三十三批 meta 行 6+r93/r98/r99/r109/r334×2/'
        'r335×2/r341/r91/r339/r340/r342/r110 指针行 14（共 20 行）verbatim='
        'archive 202609.md『坑律归档 2026-09-27 三十五批』节；保留=User 元律+法行 2+'
        '活跃指针 r344×2/r359/r360/r346。')

exec_line = ('- [2026-09-27 23:1x r362 bm-a] 执行记录：CEO 双令 O-2026-09-27-2245（千人试用期'
             '大考）+O-2026-09-27-2250（常设律）同轮回执执行——T-94 认领即开跑（900e90eb），'
             'MASS_TRIAL_W1 预注册+语法冻结（c638f8cf·R99·seed 20283000），stage-1 初筛 '
             '975 候选→166 存活（null p95 0.533<0.60·熊门轴 36.7% vs 9.0%），s3 全量判决'
             '=次轮段冻结后烧，48h 呈报 09-29 22:45 截止；详指针=research/MASS_TRIAL_W1_PREREG.md'
             '+fleet/tasks/T-2026-09-27-94-P1.json progress_r362。')

# insert meta + exec before EOF, keeping trailing structure
out = '\n'.join(kept)
if not out.endswith('\n'):
    out += '\n'
out += meta + '\n' + exec_line + '\n'
io.open(SRC, 'w', encoding='utf-8', newline='').write(out)

import os
print('migrated rows:', len(migrated))
print('kept rows:', len([l for l in kept if l.strip()]))
print('CODELY.md new size:', os.path.getsize(SRC))
print('archive new size:', os.path.getsize(ARC))
