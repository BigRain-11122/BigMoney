# -*- coding: utf-8 -*-
# r418 bm-c closeout: state + heartbeat + round-report line, one shot.
import json, time, subprocess, os

REPO = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
NOW = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
EPOCH = int(time.time())

def sys_metrics():
    cpu, ram, vram = None, None, None
    try:
        r = subprocess.run(['powershell', '-NoProfile', '-Command',
            '(Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average'],
            capture_output=True, creationflags=0x08000000)
        cpu = float(r.stdout.decode('utf-8', 'replace').strip())
    except Exception:
        pass
    try:
        r = subprocess.run(['powershell', '-NoProfile', '-Command',
            '[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,1)'],
            capture_output=True, creationflags=0x08000000)
        ram = float(r.stdout.decode('utf-8', 'replace').strip())
    except Exception:
        pass
    try:
        r = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
            capture_output=True, creationflags=0x08000000)
        vram = int(float(r.stdout.decode('utf-8', 'replace').strip().splitlines()[0]))
    except Exception:
        pass
    return cpu, ram, vram

cpu, ram, vram = sys_metrics()

# --- state-bm-c.json ---
sp = os.path.join(REPO, 'state-bm-c.json')
st = json.load(open(sp, encoding='utf-8'))
st['round_no'] = 418
st['did'] = ('r418 bm-c: (1) S0 rebase absorb: daemon-churn pre-absorb commit + pull --rebase origin 7 commits (bm-a r618/r625 inherit+close + bm-b merge chain), zero conflict. '
             '(2) S0.5 orders 151/151 zero-unacked full-scan + D-19 4167b784 MATCH zero-consume; group orders.md 3 new CEO rows adjudicated: GitHub-harvest=CPH4, fleet-Qwen3+cleanup=C-machine self-executed already (O-20261003-1210-bm-c registered+acked), model-freshness=CPH4 radar -- zero new BM face, watermark updated (sha1 68947C17). '
             '(3) smoke 47/47. (4) SatEngine rc0 alive (W114). (5) Pool: 5 ready all-FUND family zero-touchable on bm-c (T-156 p1c croc in flight bm-b->bm-a camping pid67588, DIVLOWVOL fuse-locked off-caliber r615 family), legal idle; next_pick moneyflow-IC claimed source-blocked. '
             '(6) MAIN DELIVERABLE T-144(c) D-06 pre-split survivors batch-1: 7 hot-layer entries verbatim -> pit-pool +3 (r489/r511/r327), pit-engine +2 (r307/r494), pit-git +2 (r294 union-dedup/amend-hijack); CODELY 30,858->24,961B closed-account (-6,411B lines +514B pointer receipts); all assertions PASS + diff surgical (CODELY 0+/7-; pools 5+/4+/4+); receipt _r418bmc_survivors_batch1.json; v1 join-CRLF-over-strip whole-file corruption caught by post-write diff surgical assertion (r289/r500 family), clean rollback + v2 rewrite -- law worked. '
             '(7) S6 chain 29 legs rc0 (Saturday golden-week honest no-op faces). (8) S7 4/4 self-heal + attrition CLEAN. (9) T-143 four faces frozen (capture window open, assembly waits 10-09). (10) bm-a heartbeat recovered r625 -- stall escalation cancelled.')
st['verify'] = ('smoke 47/47 rc0; S6 29/29 legs rc0; orders 151/151 full-scan zero-unacked; D-19 4167b784 MATCH; attrition CLEAN rc0; '
                'batch-1 zero-loss PASS (verbatim-in-place + source-zero-residue + byte-account 6,411B closed + LF md5 pool=2088a8e7a6bb562bfd224bf78c1e9876 engine=e6d259989d4d21a79c0dc9c78fdc282b git=fafac19d277c5ae9f730ed9fb23bc800); SatEngine rc0 alive')
st['next'] = ('(a) D-06 remaining before 10-07: batch-2 survivors 5 entries (r570 data-domain, r294-3 lane_io protocol-domain, r300/r303/r304 census+tooling trio), pit-data CRLF-face decision, flow-sinking sweep; '
              '(b) T-143 assembly window opens post-10-09 (phase machine: SYSTEM-V1 bm-a primary + REV-OSC assembly), deliverable 10-29; '
              '(c) T-156 p1c croc transfer in flight -- FUND family re-claims queue after landing+verify; '
              '(d) W14 line zero-touch pending GM dual-ruling (MSG-0436 thread).')
st['current_task'] = 'r418 closed: D-06 survivors batch-1 delivered (7 entries -> 3 domain files); next: batch-2 + CRLF-face decision + flow-sinking before 10-07'
st['last_round'] = 'r418 bm-c: D-06 pre-split survivors batch-1 (7 entries zero-loss to pit-pool/engine/git) + S0 rebase absorb + S6 29 legs + S7 4/4'
st['last_round_at'] = NOW
st['last_round_ts'] = NOW
st['last_seen'] = NOW
st['last_ts'] = NOW
st['updated'] = NOW
st['updated_at'] = NOW
st['clock_read'] = NOW
st['last_orders_sha'] = '68947C178D21814FBB5B20C3497F1DC28D42D50C'
st['last_orders_sha_method'] = 'python subprocess raw-blob bytes SHA-1 (group-tree origin/main git show, 2026-10-03 5449b5b face)'
json.dump(st, open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('STATE rc0 round_no=%d' % st['round_no'])

# --- heartbeat fleet/machines/bm-c.json ---
hp = os.path.join(REPO, 'fleet', 'machines', 'bm-c.json')
hb = json.load(open(hp, encoding='utf-8'))
hb['last_seen'] = NOW
hb['clock_read'] = NOW
hb['heartbeat_epoch_utc'] = EPOCH
if cpu is not None: hb['cpu_pct'] = cpu
if ram is not None: hb['idle_ram_gb'] = ram
if vram is not None: hb['gpu_free_vram_mib'] = vram
hb['current_task'] = 'r418 closed: D-06 survivors batch-1 (7 entries -> pit-pool/engine/git zero-loss); next: batch-2 + CRLF decision + flow-sinking by 10-07'
hb['verdict'] = 'healthy'
json.dump(hb, open(hp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int (R170/R178 law)'
print('HEARTBEAT rc0 epoch=%d(int) cpu=%s ram=%s vram=%s' % (chk['heartbeat_epoch_utc'], cpu, ram, vram))

# --- round report line ---
rp = os.path.join(REPO, 'round_reports-bm-c.md')
line = ('%s | r418 bm-c | dept:工程/舰队 | D-06 pre-split survivors 批次一交付：热层 7 条 verbatim 迁入域件（pit-pool +3：r489 池翻面双层/r511 worker initializer/r327 亚百ms池化IPC；pit-engine +2：r307 波带撞值跳位/r494 波runner键漂移；pit-git +2：r294 union去重域/r294 amend撞劫）·CODELY 30,858→24,961B 闭合账（-6,411 行字节+514 指针回执）·全断言 PASS+diff 外科（0+/7-·5+/4+/4+）·v1 脚本 join-CRLF 叠加整文件污染被写后 diff 外科断言当场抓获（r289/r500 族律生效实录）→git checkout 干净回滚→v2 重写零残留 | 验证：smoke 47/47·S6 29 腿 rc0·orders 151/151 全扫零未回执·D-19 4167b784 MATCH·attrition CLEAN·SatEngine rc0 活 | 下轮：批次二 5 条（r570 data 域/r294-3 lane_io protocol 域/r300/r303/r304 census-tooling 三条）+pit-data CRLF 面裁定+流水下沉扫描（due 10-07）；T-143 组装窗 10-09 后；T-156 croc 在途 FUND 族再认领排队 | 本地未达 origin commit 数=0（收轮时点）' % NOW)
with open(rp, 'a', encoding='utf-8') as f:
    f.write(line + '\n')
print('ROUND_REPORT rc0')
