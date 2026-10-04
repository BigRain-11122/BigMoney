# r703 bm-b S7 closeout writer: state.json round 703 + heartbeat dynamic fields + round-report line
# (r583 law: heartbeat updates dynamic fields only; epoch must be JSON int; T-separated clock_read)
import json, io, time, datetime

NOW = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
EPOCH = int(time.time())

STATE_NOTE = ("r703: salvage-adopt of dead r702 closeout (session crashed between S7 writes 00:56 and closeout commit; "
              "landed as 950d4dd2e: state 702 + heartbeat + S6 33-leg faces + evidence trio + r702 round-report line) "
              "+ D-06 batch-2 main work: pit-engine three-way sub-split (63,226B/54 entries -> pit-engine.md 19,304B/16 "
              "[satengine+registry] + pit-engine-freeze.md 27,222B/21 [wave freeze window] + pit-engine-finalize.md 19,131B/17 "
              "[finalize chain+runner family]; all <=30KB; 60,812B entries zero-loss verbatim; receipt "
              "results/_r703bmb_pit_engine_split_receipt.json; prescan rc3 acknowledged + TREASURE_REGISTRY in/out row + "
              "CODELY pointer rerouted; r439/r441 ceremony) -- remaining >30KB domain files = pit-pool 52,337B / pit-protocol "
              "50,756B / pit-git-netpath 46,328B / pit-git-surgery 45,114B (batch-3+ before 10-07 12:00 closeout); "
              "smoke 48/48; S0.5 orders 154/154 zero unacked; D-19 dual hash unchanged (decisions 755428F8 / orders E79E15F9, "
              "_r702bmb_d19_read.py reuse); S6 34/34 rc0 (legs 25-28 golden-week honest skip, cutoff 09-30 unchanged; dualrun "
              "ZERO-DRIFT; compute_audit CLEAN burning-healthy); S7 quartet 4/4 (loop pin=2 no-op, watchdog re-registered, "
              "both claws LF-match); attrition CLEAN; board zero open; satengine alive (RAM gate legal trio-held).")

NEXT = ("(a) D-06 batch-3: remaining four oversized domain files (pit-pool/pit-protocol/pit-git-netpath/pit-git-surgery) "
        "sub-split to <=30KB per r703 recipe, before 10-07 12:00 closeout; (b) trio NULLS V/Q/D burn to 10-06T17/10-07T11/"
        "10-08T0x then RAM window opens: pool JUDGE-PREP auto-ignites -> 12 judge shard entries -> pool burn <=10-12; "
        "(c) W3 judge finalize landing verify (bm-c seat, ETA ~02:00 passed -> next rounds verify + adopt); "
        "(d) 10-09 post-holiday data-chain check.")

RR_LINE = ("2026-10-05T{now} | round 703 (bm-b·dept:工程+舰队·r702 salvage 收编+D-06 batch-2) | [watermark verdict: GREEN "
           "(red=false lane=healthy·py_low_with_work_cands=合法 RAM 窗·trio NULLS 三族在烧持闸 r691 帽律)] | 当前活=trio NULLS "
           "V/Q/D 烧录在飞（至 10-06T17/10-07T11/10-08T0x）+N2-W15 judge 链候 RAM 窗（JUDGE-PREP 池条目自动重试） | 最近实物="
           "pit-engine 三路 sub-split（research/pit-engine.md 63,226B/54 条→19,304B+pit-engine-freeze.md 27,222B+"
           "pit-engine-finalize.md 19,131B·全 ≤30KB·60,812B 条目零丢失 verbatim·receipt=results/_r703bmb_pit_engine_split_receipt.json）"
           "+r702 salvage 落库（commit 950d4dd2e·state 702+心跳+S6 33 腿面+轮账本 r702 行补写） | 下个里程碑=D-06 域件 ≤30KB "
           "全线收口 10-07 12:00（余四件 pit-pool 52,337B/pit-protocol 50,756B/pit-git-netpath 46,328B/pit-git-surgery 45,114B）"
           "→judge 池烧 ≤10-12；trio V 收口 10-06T17 | S0=身份锚定 bm-b+fetch origin 零落后（HEAD==origin/main cd192b23f）+轮首脏树"
           "定性=死会话 r702 收口件（进程三证：唯一 Bigmoney codely=本会话·S6 输出面 00:55-00:57 mtime·state 702 完整在树）→按 "
           "F-20260923-03 增量检查点律 salvage-adopt 定向落库（非吞活跃会话） | S0.5=orders 154/154 零未回执（轮首扫） | D-19=双哈希不变"
           "（decisions 755428F8/orders E79E15F9·r702 修正后水位键自洽）零动作 | S1 smoke 48/48 | S2=板空（job_list 0+票板 0 open·"
           "bma/bmc state next 双探针=D-06 域面无人认领零撞车） | S3=水闸 red=false+satengine alive（RAM 门 3.1GB<4.0 合法）+"
           "post_review ✓45/✗0 | 主活=D-06 batch-2 pit-engine sub-split（D-20261002-06 域件 ≤30KB·收口窗 10-07·prescan rc3 留痕+"
           "登记册出入行+零丢失断言三件齐=迁移仪式） | S6=34/34 rc0（腿 25-28 黄金周诚实跳·dualrun ZERO-DRIFT·compute_audit CLEAN "
           "burning-healthy py 85%） | S7=quartet 4/4（loop pin=2 no-op·watchdog 重注册·双爪 LF 归一 match）+attrition 4 台账 CLEAN | "
           "本地未达 origin commit 数=0（收口 push_verify 自证） | 产品分=1（记忆基建实件·无新算法批=RAM 门下合法） | 下轮指针="
           "(a)D-06 batch-3 四域件 sub-split（r703 配方复刻） (b)W3 judge finalize 验收（bm-c 座已过 ETA） (c)trio V 收口 10-06T17 候 RAM 窗 "
           "(d)10-09 节后数据链核验").format(now=NOW[11:19])


def main():
    # 1) state.json
    st = json.load(io.open('state.json', encoding='utf-8'))
    st['round_no'] = 703
    st['note'] = STATE_NOTE
    st['last_round_at'] = NOW
    st['ts'] = NOW
    st['updated'] = NOW
    st['last_seen'] = NOW
    st['round_no_label'] = 'round 703 (bm-b)'
    st['clock_read'] = NOW
    st['last_decisions_at'] = NOW
    st['last_decisions_read_at'] = NOW
    st['next'] = NEXT
    io.open('state.json', 'w', encoding='utf-8', newline='').write(
        json.dumps(st, ensure_ascii=False, indent=1))
    chk = json.load(io.open('state.json', encoding='utf-8'))
    assert chk['round_no'] == 703

    # 2) heartbeat (dynamic fields only; orders_ack untouched per r583 law)
    hb = json.load(io.open('fleet/machines/bm-b.json', encoding='utf-8'))
    hb['last_seen'] = NOW
    hb['heartbeat_epoch_utc'] = EPOCH
    hb['clock_read'] = NOW
    hb['round_no'] = 703
    hb['round_no_label'] = 'round 703 (bm-b)'
    hb['current_task'] = ('r703 done: r702 closeout salvage-adopted (950d4dd2e) + D-06 batch-2 pit-engine three-way '
                          'sub-split (all pit-engine family files <=30KB, zero-loss receipt); remaining D-06 batch-3: '
                          'pit-pool/pit-protocol/pit-git-netpath/pit-git-surgery before 10-07 12:00')
    hb['verdict'] = ('healthy burning (trio NULLS three-family RAM-held = legal cap window; judge chain freeze-gated '
                     'awaiting RAM window ~10-06T17+; py_low_with_work_cands legal per r691)')
    hb['ts'] = NOW
    hb['updated'] = NOW
    hb['updated_at'] = NOW
    io.open('fleet/machines/bm-b.json', 'w', encoding='utf-8', newline='').write(
        json.dumps(hb, ensure_ascii=False, indent=1))
    chk = json.load(io.open('fleet/machines/bm-b.json', encoding='utf-8'))
    assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be JSON int (R170/R178 law)'
    assert 'T' in chk['clock_read'], 'clock_read must be T-separated (R262 law)'
    assert chk['orders_ack_count'] == 154

    # 3) round report line (LF host convention)
    with open('logs/iteration-loop/round_reports.md', 'ab') as f:
        f.write((RR_LINE + '\n').encode('utf-8'))
    b = open('logs/iteration-loop/round_reports.md', 'rb').read()
    assert b.count(RR_LINE.encode('utf-8')) == 1
    print('closeout writes ok: state 703, heartbeat epoch', EPOCH)


if __name__ == '__main__':
    main()
