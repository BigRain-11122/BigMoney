import re

codely=open('CODELY.md',encoding='utf-8').read()
arc=open('research/memory-archive/202609.md',encoding='utf-8').read()
lines=codely.split('\n')

already_in_arc=[
 ('r345','deep-ts 探针键族完备性'),('r100','deep-ts 探针第三缺陷族'),
 ('r350','deep-ts 探针第四缺陷变体'),('r101','树重建后 lane-local'),
 ('r340bmb','池批 checkpoint 保尾'),('r351a','rebase 重放窗的 resolver 侧位映射'),
 ('r351b','rebase UU 停点窗内本机 watchdog tick 照打'),('r353','resolver ts 探针键 normalize 字面 strip 陷阱'),
 ('r355','同轮连续风暴的 resolver 重跑防护'),('r96','机钟步回拨窗内收尾件复用轮中取时串'),
]
to_move=[('r342','PS Start-Job 作业块不继承调用处 CWD')]

remove=[]
for tag,frag in already_in_arc:
    hits=[l for l in lines if frag in l and l.lstrip().startswith('- [')]
    assert len(hits)==1, f'{tag}: expected 1 full line, got {len(hits)}'
    ln=hits[0]; assert ln in arc, f'{tag}: NOT in archive -- ABORT'
    remove.append(ln); print(f'{tag}: verified-in-archive, folding ({len(ln.encode("utf-8"))}B)')
r342_line=None
for tag,frag in to_move:
    hits=[l for l in lines if frag in l and l.lstrip().startswith('- [')]
    assert len(hits)==1, f'{tag}: expected 1 full line, got {len(hits)}'
    r342_line=hits[0]; remove.append(r342_line); print(f'{tag}: moving verbatim to 三十批节 ({len(r342_line.encode("utf-8"))}B)')

assert '三十批' not in arc
sec_header='## 坑律归档 2026-09-27 三十批（r110 bm-c 当窗整编·行级零丢失）'
arc_new=arc.rstrip('\n')+f'\n\n{sec_header}\n\n- r342 bm-b 原行 verbatim：{r342_line}\n'
open('research/memory-archive/202609.md','w',encoding='utf-8',newline='').write(arc_new)

new_lines=[l for l in lines if l not in remove]
r342_ptr='- [2026-09-27 21:15 r342 bm-b] 坑律（三十批外迁·指针）：PS Start-Job 作业块不继承调用处 CWD——全文 verbatim=research/memory-archive/202609.md『坑律归档 2026-09-27 三十批』节。指针=results/_r110bmc_codely_archive.py。'
r110_law='- [2026-09-27 22:1x r110 bm-c] 坑律：孪生面单腿 UU 的 :3: 探针空串险——md+json 孪生仅一腿 UU 时（r110 实弹：daily_report md UU·json 已 auto-merge=stage 0 无 :3: 面），对非 UU 件起 git show :3: 得空串 rc≠0，盲比较（工作树≠空串）即以空串覆写好件（json 当场被打空）；r185 parse-verify 拦截+git checkout -- 从 index stage 0 恢复零损。正典=①resolver 每面 git show 后必验 returncode==0 且非空才动手（空=探针面不存在非内容空）；②孪生同侧律非 UU 腿真身=index stage 0 automerge 或原 commit hash（git show <commit>:<path>），禁对非 UU 件起 :2:/:3: 探针；③误写恢复径=git checkout -- <path>（stage 0=无损真身）。指针=results/_r110bmc_resolve.py（v1 肇事 v2 修复双留）+_r110bmc_resolve.json。'
batch_note='- 三十批外迁（r110 bm-c·2026-09-27·超线 14,690B 当窗整编·行级零丢失）：r342 bm-b 全文 verbatim=archive 202609.md『坑律归档 2026-09-27 三十批』节；r96/r345/r100/r350/r101/r340bmb/r351×2/r353/r355 十条=二十九批节（r96 二十八批双记）已录全文本行同窗 union 吸收回潮再折叠（archive 在位核验 10/10 全过）；保留=User 元律+法行 2+冷层指针+批指针行族+r109 律+r110 律。'
new_lines.append(r342_ptr)
new_lines.append(r110_law)
new_lines.append(batch_note)
new_codely='\n'.join(new_lines)
open('CODELY.md','w',encoding='utf-8',newline='').write(new_codely)

sz=len(new_codely.encode('utf-8'))
arc_check=open('research/memory-archive/202609.md',encoding='utf-8').read()
assert all(ln in arc_check for ln in remove), 'zero-loss FAILED (incl r342 post-move)'
assert 'S0 轮首脏树=autofill' in new_codely and '孪生面单腿 UU' in new_codely
print(f'CODELY {len(codely.encode("utf-8"))}B -> {sz}B (<10240: {sz<10240}); zero-loss 11/11 OK (10 pre-verified + r342 moved); archive 三十批节 written')
