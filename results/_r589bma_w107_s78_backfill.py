# -*- coding: utf-8 -*-
# r589 bm-a W107 finalize closeout: prereg S7/S8 mechanical backfill (bytes-safe, r530 law)
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
P = 'research/PERPETUAL_N1_W107_PREREG.md'
raw = open(P, 'rb').read()
ph = ("## §7 跑后实证。【跑前必须为空——占位纪律：写数字即造假】\n"
      "\n- （finalize 落账后机械回填；两态腿断言在场=r307 律）\n"
      "\n## §8 批后复盘。【必填·终 7-T】\n"
      "\n- （finalize 落账后机械回填）\n").encode('utf-8')
ph_crlf = ph.replace(b'\n', b'\r\n')
if ph in raw:
    eol = b'\n'; old = ph
elif ph_crlf in raw:
    eol = b'\r\n'; old = ph_crlf
else:
    print('PLACEHOLDER NOT FOUND'); sys.exit(1)
NB = eol
S7 = ("## §7 跑后实证。【r587 冻结占位·r589 bm-a finalize 收口机械回填】").encode('utf-8')
S8 = ("## §8 批后复盘。【必填·终 7-T】").encode('utf-8')
L = [
 "- 12/12 分片 bm-a 引擎烧毕（r587 冻结 a554dedd3 窗后引擎 tick 自燃·12/12 分片交付 origin 254b9d3f0〔r588 窗外科〕·finalize 前 12/12 完备 r310 律）；finalize one-pass（r538 律·首跑禁重跑·r589 首跑=唯一一跑）。",
 "- ledger：prev_total 597,748（W106 bm-b r588 落账解锁·链序 W104 593,348 bm-a→W105 595,548 bm-c→W106 597,748 bm-b）+ batch_trials 2,200 = **599,948**；voids_applied=LOWAMP-P1/P2。",
 "- w107-only：n=2,200·mu=−0.09942518181818182·sigma=0.24344672754394164；merged：K=233,320·mu=−0.0927601842962455·sigma=0.24483467386933913。",
 "- skill_line_v2 @n_eff_held 597,748：1.1702→**1.17**（K-lift delta −0.0002 ≥ −0.02 门内·正负交替如实报〔W103 +0.0005→W104 −0.0001→W105 −0.0002→W106 +0.0002→W107 −0.0002〕）；se_mu @K233,320=0.000507（收窄链持续 W105 0.000512→W106 0.000509→W107 0.000507）；canon_flip 未执行（治理提案面·K2200 同法）。",
 "- §5 预测四门全过（冻结锚=W101 finalize 实测键·起草窗最新已落账面·r576 锚滚动律）：|Δmu|=0.0067<0.02（W107-only −0.09942518 · 单波偏离面如实报·门内）；σ 变化 +0.0164%<±10%（锚 0.24479446526118412·本波 merged 0.24483467386933913）；A 档 p95 差 +0.0156<0.05（锚 0.2953·本波 0.3109）；K-lift −0.0002≥−0.02。",
 "- W108+ 链面披露：本波 finalize 时点在飞上游=W108 bm-c（烧毕 finalize 待）+W109 bm-b（烧毕 finalize 待·12/12 交付 bm-b r588 窗）+W110 bm-a（本窗冻结+点火在飞）——finalize 合并环跑时按 registry 键 derive 复核·FAIL-CLOSED r307 两态律恒在。",
]
S8L = [
 "- 首跑唯一一跑律执行面零违例（r538：finalize 产物 n1_w107_results.json 落盘前不在树·零双计面；append_ledger 持久化块随 family summary 落盘后写 guard=r509 幻影记账律序）。",
 "- 两态腿断言验证：n1 selftest（默认 --wave 调用 r522 律）W107 materializer 腿跑后态 PASS（dep=W17..W101 outputs ALL PRESENT 断言在 finalize 落账后合法成立）；pf 9/9。",
 "- 预注册纪律：§1-§6 判据面零触碰（冻结后禁改判据），本腿只机械回填 §7/§8（r307 同轮回填律）。",
]
new = (S7 + NB +
       b"".join(x.encode('utf-8') + NB for x in L[:1]) +
       L[1].encode('utf-8') + NB + NB +
       L[2].encode('utf-8') + NB +
       L[3].encode('utf-8') + NB +
       L[4].encode('utf-8') + NB +
       L[5].encode('utf-8') + NB + NB +
       S8 + NB +
       b"".join(x.encode('utf-8') + NB for x in S8L))
raw = raw.replace(old, new)
open(P, 'wb').write(raw)
print('S7/S8 backfill landed for', P)
