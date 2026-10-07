# _r853bma_oss_s345_scan3.py -- round-3: S4 web-channel evidence fold (joinquant/myquant knowledge rows)
# + final rc seal. Appends 'round3' face into s345-20261008.json; prints ledger-ready row digest.
import json, os, sys, io, datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, 'results', 'oss_eng_scan', 's345-20261008.json')

ev = json.load(io.open(OUT, encoding='utf-8'))
r3 = {'ts': datetime.datetime.now().isoformat(timespec='seconds') + '+08:00'}
r3['channel_note'] = ('joinquant.com/community direct fetch = JS-rendered empty body (honest disclosure); '
                      'evidence via search-channel snippets, dual-registered links')
r3['s4_rows'] = [
    dict(id='S4-01', name='聚宽因子看板(情绪类因子 taxonomy)',
         src='https://test.demo.joinquant.com/view/factorlib/list', star_face='n/a(平台文档·无star面)',
         license='商业平台文档(vendor registry)', fit='A股原生因子分类正典:情绪类/动量类/风格/技术类因子族',
         reuse='知识REF(分类学+因子命名采纳候选)', maturity='在线', cost_h=2,
         verdict='REGISTRY(knowledge)', dup_check='与在役引擎因子族无重叠;动量类=judged-out族仅分类学引用不准入'),
    dict(id='S4-02', name='聚宽 get_billboard_list 龙虎榜游资生态',
         src='https://devpress.csdn.net/v1/article/detail/155556423', star_face='n/a(社区教程)',
         license='社区知识', fit='龙虎榜营业部维度:知名游资买入跟踪/跟随策略判据',
         reuse='知识REF(与在役LHB链互补=营业部维度扩展候选)', maturity='在线', cost_h=4,
         verdict='REGISTRY(knowledge)', dup_check='update_lhb.py在役取数面;营业部维度=增量非重复'),
    dict(id='S4-03', name='掘金智能策略:涨停开板/网格/条件单',
         src='https://www.myquant.cn/docs2/tools/', star_face='n/a(平台功能文档)',
         license='商业平台文档(vendor registry)', fit='涨停开板策略=A股原生连板情绪族判据;网格策略在役对照',
         reuse='知识REF(涨停开板判据形式化候选)', maturity='在线', cost_h=4,
         verdict='REGISTRY(knowledge)', dup_check='GRID sleeve在役(网格=对照参考);涨停开板=新判据非重复'),
    dict(id='S4-04', name='游资龙虎榜驱动短线策略(风格切换判据)',
         src='https://www.stockapi.com.cn/blog/22', star_face='n/a(社区博客)',
         license='社区知识', fit='弱势市场游资快速兑现/连板概率骤降/T+1数据滞后三判据披露',
         reuse='知识REF(情绪周期状态机判据候选)', maturity='在线', cost_h=2,
         verdict='REGISTRY(knowledge)', dup_check='与在役REGIME_GUARD三轴门互补(状态切换判据)'),
]
r3['s5_dup_note'] = ('S5全族=情绪族(涨停/连板/龙虎榜/散户情绪)非judged-out族; mom-index=宝妈指数(散户情绪)'
                     '非MOM动量族(名称撞面如实披露); 时间序/野路子零涉及')
r3['s5_top'] = dict(first='simonlin1212/vibe-astock (Apache-2.0, 667★) REGIME-5情绪工具供给候选#1',
                    second='mihang123/mom-index (MIT, 384★) 散户反向情绪登记观察',
                    exit='QuantMind AGPL触顶退出; go-stock GPL=REF-ONLY; crewai项目无license=不可用')
ev['round3'] = r3
ev['rc'] = 0  # S3 404s cured in round2; S4 folded; all sections evidence-complete
with io.open(OUT, 'w', encoding='utf-8') as f:
    json.dump(ev, f, ensure_ascii=False, indent=1)
print('round3 sealed; rc=0; s4 rows:', len(r3['s4_rows']))
