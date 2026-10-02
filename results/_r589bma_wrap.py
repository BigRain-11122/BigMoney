# -*- coding: utf-8 -*-
"""r589 bm-a wrap part 1: state + round report + pit-git lessons (bytes-safe)."""
import json, datetime, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
NOW = datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat(timespec='seconds')

# ---- 1. state (round_no 589, did/verify, true D-19 timestamp) ----
s = json.load(open('state-bm-a.json', encoding='utf-8'))
s['round_no'] = 589
s['last_decisions_at'] = NOW
s['did'] = ("r589: W110 FREEZE five-face + ignition (100th engine wave by machine-derive, bm-a 31st owned; "
            "A 263_004..265_003 / B 61_201..61_400 both-sides arithmetic continuation from W109 tails hops 0/0; "
            "seat MSG-20261002-1829-bma f457e1c4f; freeze-window gate re-run rc0 bitwise identical to r588 "
            "seat-window; surgical push ff0b1869b after bm-b r588 mid-window advance) + W107 FINALIZE one-pass "
            "first-run (prev 597,748 W106 bm-b + 2,200 = 599,948, K=233,320, merged mu -0.09276018 sigma "
            "0.24483467, skill_line 1.1702->1.17 K-lift -0.0002, S5 four gates ALL PASS on W101 anchors, "
            "SS7/SS8 backfilled same-round r307 law) + D-19 phantom-key re-anchor 13DCB81A->937A373D "
            "(content-face verified, zero re-consume)")
s['verify'] = ("smoke 47/47; n1 selftest PASS (W2..W110 materializer legs, default-wave r522 law); pf 9/9; "
               "banned gate ADMIT 0; FIX-A fresh + FIX-B 107 rows survive + AST + FIX-C pure-insertion "
               "+29/+181/+2; attrition CLEAN; dualrun ZERO-DRIFT 51/3; S6 36 legs rc0 (scorecard/clock/heat/"
               "repo/futures/options/lhb/ths/ahpanel host legs green, lane guards honest no-op, t35 PASS 0 "
               "breach, t24 22/22, daily report + CEO live page + build status regenerated); WM py_low_board_clear "
               "legal (engine lane W110 burn in flight); orders 143/143 double-scan; W110 ignition product-growth "
               "face (shards ~1/min, r325 law)")
json.dump(s, open('state-bm-a.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('state r589 written')

# ---- 2. pit-git lessons (bytes-safe, EOL-aware per r530) ----
P = 'research/pit-git.md'
raw = open(P, 'rb').read()
eol = b'\r\n' if raw.count(b'\r\n') * 2 > raw.count(b'\n') else b'\n'
L1 = ("- [2026-10-02 19:0x r589 bm-a] D-19 水位键幻影值坑（r585 族第 3 例·r588 遗产当场收口）：r589 首扫假 "
      "CHANGED——state last_decisions_sha=13DCB81A 与 origin decisions.md 真值 937A373D 不符，且该值与集团树 "
      "origin/main reflog 全历史版本（12 版逐版 sha256）零匹配=纯幻影值（r588 写键未按 r532 律从 git show "
      "origin/main blob 现取——疑取自瞬态脏工作树版或错缓冲·工作树现版 FD869D91 亦不匹配）。正法=r585 内容面先核："
      "回读 r588 轮报告确认 10-02 批（D-05/06/07/08/09）已完整消费→只更键零重扫（禁直接重消费=重复 ack 面·"
      "也禁直接信真值=漏消费面）。How to apply：水位键写入值必须当拍从 git show origin/main:docs/decisions.md "
      "raw bytes 现 derive（禁转抄上轮值·禁读工作树·禁读 HEAD 本地面）；下轮遇键不符先内容面对账再定性。").encode('utf-8')
L2 = ("- [2026-10-02 19:0x r589 bm-a] 外科后 realign M 面分类 raw hash-object 误判坑（r530/r373 autocrlf 族新面）："
      "reset --mixed 后 M 面分类用「hash-object 工作树文件 vs rev-parse 旧基 blob」比较——工作树 CRLF 裸哈希恒≠LF "
      "blob sha（checkin 滤镜未过）→ stale 复制品全被误判 live-write 保留（state.json/token_usage 等 9 件）。"
      "正法=git diff --quiet <旧基> -- <路径>（git 侧滤过比较·CRLF 免疫）判 stale；文件移动对（D processed/+?? inbox/）"
      "按 r586 blob 恒等证明→恢复正主位+删 untracked 副本。How to apply：一切「工作树 vs blob」内容比较走 git diff/"
      "cat-file 滤过面，禁裸 hash-object 对 rev-parse（r373 blob 空间律的 realign 执行面变体）。").encode('utf-8')
if b'r589 bm-a' not in raw:
    if not raw.endswith(eol):
        raw += eol
    raw += L1 + eol + L2 + eol
    open(P, 'wb').write(raw)
    print('pit-git lessons appended (2)')
else:
    print('pit-git lessons already present')

# ---- 3. round report line ----
RR = 'round_reports-bm-a.md'
line = (f"{NOW} | r589 bm-a: dept:研究/工程 | (1) S0: FF 对齐 ad932f6b8（脏=4 活写件·零冲突）+ D-19 幻影键收口"
        "（13DCB81A 与集团 reflog 全史零匹配=r588 写键违 r532 律·内容面核 r588 已消费 10-02 批→只更键 937A373D 零重扫 r585 律）"
        "(2) W110 五面冻结（第一百枚引擎波·bm-a 第三十一枚自有波·A 263_004..265_003/B 61_201..61_400 双侧算术续带 W109 尾 hops 0/0"
        "·席位窗 r588+冻结窗 r589 gate 双跑逐位恒等 ADMIT rc0·禁向闸 ADMIT 0·prereg 冻结=锚 W105 实测值链头 595,548/K=228,920 r576 锚滚律"
        "·四在飞上游席 W106..W109 FAIL-CLOSED r307·FIX-A 零删/FIX-B 107 行全存/AST/FIX-C 纯插入+29/+181/+2）"
        "(3) push 撞拒（bm-b r588 同窗前进=W106 finalize 落账 597,748/K=231,120+W109 12/12 交付+我 W110 席位 MSG 已消费归档）"
        "→r523 外科 ff0b1869b（13 件 payload·删集空+tree-delta==payload 双断言·attrition 证据件交集让 origin·活写面 r532 律）"
        "+r578 realign（51 stale 复原·6 活写保全·席位 MSG 移动对 r586 律恒等删副本）"
        "(4) W107 FINALIZE one-pass（我自有波·r538 首跑唯一：prev 597,748+2,200=599,948·K=233,320·merged mu −0.09276018 σ 0.24483467"
        "·skill_line@597,748 1.1702→1.17 K-lift −0.0002·S5 四门全过〔|Δμ| 0.0067<0.02·σ +0.016%<±10%·A-p95 差 0.0156<0.05·K-lift ≥−0.02·锚=W101〕"
        "·SS7/SS8 机械回填同轮 r307 律）(5) W110 点火=产物增长面（18:57 起 ~1 片/min·19:03 7/12 在飞）"
        "(6) S6 36 腿全 rc0（dualrun ZERO-DRIFT 51/3·host 腿全绿·车道护栏诚实 no-op·t35 PASS·t24 22/22·REPORT/LIVE/面板再生"
        "·WM=py_low_board_clear 合法闲〔板清+引擎车道在烧〕·audit 旗 pool_starvation=引擎车道供给在飞法定态 W75 先例）"
        "(7) S7 自愈 4/4（loop pin=8 no-op·watchdog·双爪）+ 心跳 epoch int/ack 143 携带 r583 律 | "
        "验证=smoke 47/47+n1 selftest PASS（W2..W110 腿）+pf 9/9+attrition CLEAN+送达自证 ff0b1869b=origin/main | "
        "水位 verdict=绿（red=false）| 本地未达 origin commit 数=0（外科后复核）| 当前活=W110 烧录收尾（7/12·烧毕产物下轮交付）| "
        "最近实物=results/perpetual_faces/n1_w107_results.json（19:0x）+ff0b1869b（W110 注册上 origin）| "
        "下个里程碑=W110 12/12 烧毕交付+W108 bm-c finalize 监测+下波席位按表尾机闸 derive（W111+ 投影 A 265_004..267_003/B 61_401..61_600 CLEAN·窗 ≤48h） "
        "[via bm-a r589]\n")
with open(RR, 'a', encoding='utf-8') as f:
    f.write(line)
print('round report line appended')
